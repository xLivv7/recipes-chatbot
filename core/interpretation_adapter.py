"""SDK response boundary for IR-1. No catalog or application imports."""
from dataclasses import asdict, dataclass

from openai import APIError, OpenAI

from core.interpretation_contract import (CLIENT_CONFIGURATION, CONTRACT_VERSION, TOOL_NAME,
    InterpretationError, parse_interpretation_arguments)
from core.interpretation_compiler import compile_interpretation
from core.llm_response_validation import RESPONSE_VALIDATION_VERSION, response_failure_reason


@dataclass(frozen=True)
class InterpretationOutcome:
    action: str
    arguments: dict | None
    diagnostics: dict


def empty_diagnostics():
    return dict(interpretation_mode="facts_v1", interpretation_contract_version=CONTRACT_VERSION,
        response_validation_version=RESPONSE_VALIDATION_VERSION, api_calls=0,
        interpretation_tool_calls=0, tool_call_count=None, backend_calls=0, model_action=None,
        model_decision_correct=None, request_kind=None, validation_status="not_attempted",
        compiler_action=None, effective_action=None, guard=None, failure_stage=None,
        response_failure_reason=None, finish_reason=None, response_model=None, request_id=None, usage=None)


def _failure(diagnostics, stage, reason):
    diagnostics.update(failure_stage=stage, error=reason, effective_action="error", validation_status="error")
    return InterpretationOutcome("error", None, diagnostics)


def decode_interpretation_response(response, user_message, *, schema=None):
    diagnostics = empty_diagnostics()
    diagnostics.update(response_model=getattr(response, "model", None), request_id=getattr(response, "_request_id", None))
    usage = getattr(response, "usage", None)
    if usage is not None:
        diagnostics["usage"] = {name: getattr(usage, name, None)
                                for name in ("prompt_tokens", "completion_tokens", "total_tokens")}
    choices = getattr(response, "choices", None)
    if not choices:
        diagnostics["response_failure_reason"] = "empty_choices"
        return _failure(diagnostics, "protocol", "empty_choices")
    message = getattr(choices[0], "message", None)
    if message is None:
        return _failure(diagnostics, "protocol", "missing_message")
    diagnostics["finish_reason"] = getattr(choices[0], "finish_reason", None)
    calls = getattr(message, "tool_calls", None) or []
    if not isinstance(calls, (list, tuple)):
        return _failure(diagnostics, "protocol", "invalid_tool_calls")
    diagnostics["tool_call_count"] = len(calls)
    diagnostics["interpretation_tool_calls"] = sum(
        getattr(getattr(call, "function", None), "name", None) == TOOL_NAME for call in calls)
    failure = response_failure_reason(response)
    if failure:
        diagnostics["response_failure_reason"] = failure
        return _failure(diagnostics, "protocol", failure)
    if len(calls) != 1 or getattr(getattr(calls[0], "function", None), "name", None) != TOOL_NAME:
        return _failure(diagnostics, "protocol", "invalid_interpretation_call")
    try:
        interpretation = parse_interpretation_arguments(getattr(calls[0].function, "arguments", None),
                                                       user_message, schema=schema)
    except InterpretationError as exc:
        return _failure(diagnostics, "interpretation", exc.reason)
    diagnostics.update(request_kind=interpretation.request_kind, validation_status="valid",
        interpretation=dict(contract_version=interpretation.contract_version,
                            request_kind=interpretation.request_kind,
                            facts=[asdict(fact) for fact in interpretation.facts]))
    result = compile_interpretation(interpretation)
    diagnostics.update(compiler_action=result.action,
                       effective_action="tool" if result.action == "search" else "no_tool")
    return InterpretationOutcome(result.action, result.arguments, diagnostics)


def execute_interpretation_request(client, user_message, request):
    """Execute one request built by build_interpretation_request; never retry."""
    if isinstance(client, OpenAI) and (client.max_retries != 0 or client.timeout != 30
            or str(client.base_url).rstrip("/") != CLIENT_CONFIGURATION["base_url"]):
        return _failure(empty_diagnostics(), "configuration", "invalid_ir_client_configuration")
    try:
        response = client.chat.completions.create(**request)
    except APIError as exc:
        diagnostics = empty_diagnostics()
        diagnostics["api_calls"] = 1
        return _failure(diagnostics, "api", type(exc).__name__)
    result = decode_interpretation_response(response, user_message,
        schema=request["tools"][0]["function"]["parameters"])
    result.diagnostics["api_calls"] = 1
    return result
