from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    table: str
    record_id: str
    field: str
    message: str

    def __str__(self) -> str:
        return (
            f"{self.severity.value} | {self.table} | {self.record_id} | "
            f"{self.field} | {self.message}"
        )


@dataclass
class ValidationReport:
    table_counts: dict[str, int] = field(default_factory=dict)
    issues: list[ValidationIssue] = field(default_factory=list)

    def extend(self, issues: list[ValidationIssue]) -> None:
        self.issues.extend(issues)

    def counts_by_severity(self) -> Counter[str]:
        return Counter(item.severity.value for item in self.issues)

    @property
    def error_count(self) -> int:
        return self.counts_by_severity()[Severity.ERROR.value]

    @property
    def warning_count(self) -> int:
        return self.counts_by_severity()[Severity.WARNING.value]

    @property
    def info_count(self) -> int:
        return self.counts_by_severity()[Severity.INFO.value]

    @property
    def has_errors(self) -> bool:
        return self.error_count > 0


def issue(
    severity: Severity,
    table: str,
    record_id: str,
    field: str,
    message: str,
) -> ValidationIssue:
    return ValidationIssue(
        severity=severity,
        table=table,
        record_id=str(record_id),
        field=field,
        message=message,
    )

