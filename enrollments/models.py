from django.db import models


class FinalExam(models.Model):
    """
    Final exam call (session) for a Subject.

    Attributes:
        subject (Subject): Subject being examined (FK).
        date (date): Exam date.
        location (str): Where the exam takes place.
        duration (timedelta): Expected duration.
        call_number (int): Call identifier/ordinal within the period.
        notes (str | None): Optional remarks for logistics or scope.
    """

    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.CASCADE, related_name="final_exams"
    )
    date = models.DateField()
    location = models.CharField(max_length=255)
    duration = models.DurationField()
    call_number = models.PositiveSmallIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject.name} Final Exam on {self.date.strftime('%Y-%m-%d')}"


class SubjectInscription(models.Model):
    """
    Enrollment record for a subject (course).

    Attributes:
        student (Student): Student who enrolls in the subject.
        subject (Subject): Target subject of the enrollment.
        inscription_date (date): Creation date; auto-populated.

    Meta:
        unique_together: Ensures a student cannot enroll in the same subject twice.
    """

    student = models.ForeignKey(
        "users.Student", on_delete=models.CASCADE, related_name="subjects_inscriptions"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="subject_inscriptions",
    )
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """Human-readable representation used in admin and logs."""
        return f"{self.student.user.username} - {self.subject.name} ({self.inscription_date})"

    class Meta:
        unique_together = ("student", "subject")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["subject"]),
            models.Index(fields=["inscription_date"]),
        ]


class FinalExamInscription(models.Model):
    """
    Enrollment record for a final exam session.

    Attributes:
        student (Student): Student who enrolls in the final exam.
        final_exam (FinalExam): Final exam session being enrolled.
        inscription_date (date): Creation date; auto-populated.

    Meta:
        unique_together: Ensures a student cannot enroll in the same final exam twice.
    """

    student = models.ForeignKey(
        "users.Student",
        on_delete=models.CASCADE,
        related_name="final_exam_inscriptions",
    )
    final_exam = models.ForeignKey(
        FinalExam, on_delete=models.CASCADE, related_name="final_exam_inscriptions"
    )
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """Human-readable representation used in admin and logs."""
        return f"{self.student.user.username} - {self.final_exam.subject.name} ({self.inscription_date})"

    class Meta:
        unique_together = ("student", "final_exam")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["final_exam"]),
            models.Index(fields=["inscription_date"]),
        ]
