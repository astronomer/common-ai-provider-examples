"""
## example_llm_file_analysis

Demonstrates `@task.llm_file_analysis` / `LLMFileAnalysisOperator`. Reads the
shipped anomaly report through an ObjectStoragePath-style `file://` URL and
returns a structured `FileAnalysisReport`.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task

from include.models import FileAnalysisReport


FIXTURE_PATH = "file:///usr/local/airflow/include/fixtures/anomaly_report.log"


@dag(
    dag_id="example_llm_file_analysis",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    tags=["common-ai", "example", "space", "llm-file-analysis"],
    doc_md=__doc__,
)
def example_llm_file_analysis():
    @task
    def prepare_input() -> str:
        local = Path("/usr/local/airflow/include/fixtures/anomaly_report.log")
        assert local.exists(), f"missing fixture: {local}"
        print(f"Staging file: {local} (size={local.stat().st_size} bytes)")
        return FIXTURE_PATH

    @task.llm_file_analysis(
        llm_conn_id="pydanticai_default",
        file_path=FIXTURE_PATH,
        output_type=FileAnalysisReport,
    )
    def analyze_log() -> str:
        return (
            "Read the mission log and return a structured FileAnalysisReport "
            "containing every distinct anomaly with an anomaly_type, a "
            "confidence score in [0, 1], and free-form notes."
        )

    @task
    def consume_output(report: FileAnalysisReport | dict) -> None:
        if isinstance(report, dict):
            report = FileAnalysisReport.model_validate(report)
        print(f"Title: {report.title}")
        for finding in report.findings:
            print(
                f" - {finding.anomaly_type} "
                f"(confidence={finding.confidence:.2f}): {finding.notes}"
            )

    staged_path = prepare_input()
    analysis = analyze_log()
    staged_path >> analysis
    consume_output(analysis)


example_llm_file_analysis()
