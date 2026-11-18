"""Shared completion checks before interpreting or dispatching tool calls."""

RESPONSE_VALIDATION_VERSION = "T022-v1"


def response_failure_reason(response) -> str | None:
    """Recognize known response failures, without inferring a catalog refusal.

    Optional metadata may be absent in older fixtures. Text in content is
    never treated as metadata, a tool call, or a reason for refusing a query.
    """
    if not response.choices:
        return "empty_choices"
    choice = response.choices[0]
    finish_reason = getattr(choice, "finish_reason", None)
    if finish_reason == "length":
        return "truncated_response"
    if finish_reason == "content_filter":
        return "filtered_response"
    if getattr(choice.message, "refusal", None):
        return "provider_refusal"
    return None
