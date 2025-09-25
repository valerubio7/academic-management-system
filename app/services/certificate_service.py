"""
Certificate Service Module.

Handles certificate generation business logic using repository pattern.
Services only access data through repositories, not directly from models.
"""

from typing import Optional
from datetime import date
from io import BytesIO
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from docxtpl import DocxTemplate

from app.repositories.students import StudentRepository


class CertificateError(Exception):
    """Exception for certificate operations."""
    pass


class CertificateService:
    """
    Service for generating student certificates.

    Handles the business logic for certificate generation,
    using repositories for data access.
    """

    def __init__(self, student_repository: StudentRepository = None):
        """
        Initialize the service with repositories.

        Args:
            student_repository: Repository for student operations
        """
        self.student_repository = student_repository or StudentRepository()

    def generate_regular_certificate(self, user) -> BytesIO:
        """
        Generate a regular student certificate.

        Args:
            user: Django user instance

        Returns:
            BytesIO object containing the generated certificate

        Raises:
            CertificateError: If generation fails for any reason
        """
        # Get student profile using repository
        student = self.student_repository.by_user_id_with_career_faculty(user.id)
        if not student:
            raise CertificateError("Tu perfil de estudiante no está configurado. Contactá a un administrador.")

        # Check template exists
        template_path = Path(settings.BASE_DIR) / "regular_certificate.docx"
        if not template_path.exists():
            raise CertificateError("No se encontró la plantilla de certificado.")

        # Prepare context
        today = timezone.localdate()
        context = self._prepare_regular_certificate_context(user, student, today)

        # Generate certificate
        try:
            doc = DocxTemplate(str(template_path))
            doc.render(context)
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            return output
        except Exception as e:
            raise CertificateError(f"Ocurrió un error al generar el certificado: {str(e)}")

    def get_regular_certificate_filename(self, user, date_suffix: Optional[date] = None) -> str:
        """
        Generate filename for regular certificate.

        Args:
            user: Django user instance
            date_suffix: Optional date for filename (defaults to today)

        Returns:
            Certificate filename
        """
        date_str = (date_suffix or timezone.localdate()).strftime('%Y%m%d')
        last_name = user.last_name or user.username
        return f"certificado-regular-{last_name}-{date_str}.docx"

    def _prepare_regular_certificate_context(self, user, student, today: date) -> dict:
        """
        Prepare context data for regular certificate template.

        Args:
            user: Django user instance
            student: Student model instance
            today: Current date

        Returns:
            Dictionary with template context
        """
        return {
            "full_name": user.get_full_name() or user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dni": user.dni,
            "student_id": student.student_id,
            "career_name": student.career.name if student.career else "",
            "career_code": student.career.code if student.career else "",
            "faculty_name": (
                student.career.faculty.name
                if getattr(student, "career", None) and student.career and student.career.faculty
                else ""
            ),
            "enrollment_date": student.enrollment_date.strftime("%d/%m/%Y") if student.enrollment_date else "",
            "today_date": today.strftime("%d/%m/%Y"),
            "today_day": f"{today.day:02d}",
            "today_month": f"{today.month:02d}",
            "today_year": f"{today.year}",
        }

    @classmethod
    def create_default(cls):
        """
        Create service instance with default repositories.

        Returns:
            CertificateService instance with default dependencies
        """
        return cls()
