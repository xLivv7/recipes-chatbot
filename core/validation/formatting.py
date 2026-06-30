from __future__ import annotations

from core.validation.models import Severity, ValidationReport


def format_report(report: ValidationReport) -> str:
    lines: list[str] = []
    counts = report.counts_by_severity()

    lines.append("Database validation report")
    lines.append("=" * 60)
    lines.append("Table counts:")
    for table, count in report.table_counts.items():
        lines.append(f"  - {table}: {count}")

    lines.append("")
    lines.append("Issue summary:")
    lines.append(f"  - ERROR: {counts[Severity.ERROR.value]}")
    lines.append(f"  - WARNING: {counts[Severity.WARNING.value]}")
    lines.append(f"  - INFO: {counts[Severity.INFO.value]}")

    lines.append("")
    if not report.issues:
        lines.append("No validation issues found.")
        return "\n".join(lines)

    lines.append("Issues:")
    for validation_issue in report.issues:
        lines.append(str(validation_issue))

    return "\n".join(lines)

