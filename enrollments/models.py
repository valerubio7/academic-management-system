from django.db import models


class FinalExam(models.Model):
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
    student = models.ForeignKey(
        "users.Student", on_delete=models.CASCADE, related_name="subjects_inscriptions"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="subject_inscriptions",
    )
    inscription_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "subject")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["subject"]),
            models.Index(fields=["inscription_date"]),
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} ({self.inscription_date})"


class FinalExamInscription(models.Model):
    student = models.ForeignKey(
        "users.Student",
        on_delete=models.CASCADE,
        related_name="final_exam_inscriptions",
    )
    final_exam = models.ForeignKey(
        FinalExam, on_delete=models.CASCADE, related_name="final_exam_inscriptions"
    )
    inscription_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "final_exam")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["final_exam"]),
            models.Index(fields=["inscription_date"]),
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.final_exam.subject.name} ({self.inscription_date})"
