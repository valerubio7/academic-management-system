from django.db import models


class Grade(models.Model):
    class StatusSubject(models.TextChoices):
        FREE = "free", "Free"
        REGULAR = "regular", "Regular"
        PROMOTED = "promoted", "Promoted"

    student = models.ForeignKey(
        "users.Student", on_delete=models.CASCADE, related_name="grades"
    )
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.CASCADE, related_name="grades"
    )
    promotion_grade = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(
        max_length=10, choices=StatusSubject.choices, default=StatusSubject.REGULAR
    )
    final_grade = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "subject")
        indexes = [
            models.Index(fields=["student", "subject"]),
            models.Index(fields=["status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} ({self.status})"

    def update_status(self):
        """Update status based on final_grade: >=6.0→PROMOTED, <6.0→REGULAR, None→FREE."""
        if self.final_grade is not None:
            self.status = (
                self.StatusSubject.PROMOTED
                if self.final_grade >= 6.0
                else self.StatusSubject.REGULAR
            )
        else:
            self.status = self.StatusSubject.FREE
        self.save()
