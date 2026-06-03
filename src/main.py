"""
Pipeline entry point.

Runs ingestion → fact build → dimension build → quality checks in order.
Catches all exceptions, logs them with full traceback, and exits with code 1
so any scheduler or CI system can detect the failure.
"""

from __future__ import annotations

import sys
import time

from ingest import ingest_files
from quality_checks import run_quality_checks
from transform import build_dimensions, build_fact_table
from utils import setup_logging

log = setup_logging("main")


def main() -> None:
    log.info("Pipeline starting")
    t0 = time.perf_counter()

    try:
        ingest_files()

        fact_df = build_fact_table()

        # build_dimensions is called here, not inside build_fact_table, so
        # that function has a single responsibility and is easier to test.
        build_dimensions(fact_df)

        run_quality_checks(fact_df)

    except Exception as exc:
        log.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)

    elapsed = time.perf_counter() - t0
    log.info("Pipeline completed successfully in %.2fs", elapsed)


if __name__ == "__main__":
    main()
