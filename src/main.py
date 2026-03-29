from ingest import ingest_files
from transform import build_fact_table
from quality_checks import run_quality_checks


def main() -> None:
    ingest_files()
    build_fact_table()
    run_quality_checks()
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
