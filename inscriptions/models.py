from django.db import models


# Create your models here.
class SubjectInscription(models.Model):
    """Model representing a subject inscription."""
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='subjects_inscriptions')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='subject_inscriptions')
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} ({self.inscription_date})"


class FinalExamInscription(models.Model):
    """Model representing a final exam inscription."""
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='final_exam_inscriptions')
    final_exam = models.ForeignKey('academics.FinalExam', on_delete=models.CASCADE, related_name='final_exam_inscriptions')
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.final_exam.subject.name} ({self.inscription_date})"
