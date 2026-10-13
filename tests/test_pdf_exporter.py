import os
import pytest
from datetime import datetime
from utils.pdf_exporter import PDFExporter
from models.pet_report import PetReport


@pytest.fixture
def sample_pet_report():
    return PetReport(
        report_id=101,
        user_id=1,
        category="Lost",
        pet_name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        gender="Male",
        primary_color="Golden",
        secondary_color="White",
        distinguishing_marks="Black spot on left ear",
        incident_date=datetime.now(),
        location="Quezon City",
        photo_path=""
    )


def test_export_pet_report_pdf(tmp_path, sample_pet_report):
    output_file = str(tmp_path / "test_pet_report.pdf")
    generated_path = PDFExporter.export_pet_report(sample_pet_report, output_file)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 0


def test_export_audit_logs_pdf(tmp_path):
    output_file = str(tmp_path / "test_audit_logs.pdf")
    sample_logs = [
        {
            "log_id": 1,
            "timestamp": "2026-10-07 10:00:00",
            "user_id": 5,
            "action": "LOGIN",
            "details": "User logged in successfully"
        },
        {
            "log_id": 2,
            "timestamp": "2026-10-07 10:05:00",
            "user_id": 5,
            "action": "REPORT_CREATED",
            "details": "Created lost pet report #101"
        }
    ]

    generated_path = PDFExporter.export_audit_logs(sample_logs, output_file)

    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 0