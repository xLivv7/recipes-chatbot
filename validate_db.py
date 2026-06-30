from core.database import SessionLocal
from core.validation.formatting import format_report
from core.validation.runner import run_database_validation


def main() -> int:
    db = SessionLocal()
    try:
        report = run_database_validation(db)
        print(format_report(report))
        return 1 if report.has_errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
