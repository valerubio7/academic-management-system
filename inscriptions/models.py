"""Enrollment models for the Inscriptions app.

Defines:
- SubjectInscription: links a Student to a Subject (course) with an inscription date.
- FinalExamInscription: links a Student to a FinalExam session.

Notes:
    - Uniqueness constraints enforce one inscription per (student, subject) and (student, final_exam).
    - on_delete=CASCADE removes inscriptions when the related student/subject/final_exam is deleted.
    - inscription_date is set automatically on creation (auto_now_add).
"""

from django.db import models


class SubjectInscription(models.Model):
    """
    Enrollment record for a subject (course).

    Attributes:
        student (users.Student): Student who enrolls in the subject.
        subject (academics.Subject): Target subject of the enrollment.
        inscription_date (date): Creation date; auto-populated.

    Meta:
        unique_together: Ensures a student cannot enroll in the same subject twice.
    """
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='subjects_inscriptions')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='subject_inscriptions')
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """Human-readable representation used in admin and logs."""
        return f"{self.student.user.username} - {self.subject.name} ({self.inscription_date})"

    class Meta:
        unique_together = ('student', 'subject')


class FinalExamInscription(models.Model):
    """
    Enrollment record for a final exam session.

    Attributes:
        student (users.Student): Student who enrolls in the final exam.
        final_exam (academics.FinalExam): Final exam session being enrolled.
        inscription_date (date): Creation date; auto-populated.

    Meta:
        unique_together: Ensures a student cannot enroll in the same final exam twice.
    """
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='final_exam_inscriptions')
    final_exam = models.ForeignKey('academics.FinalExam', on_delete=models.CASCADE, related_name='final_exam_inscriptions')
    inscription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """Human-readable representation used in admin and logs."""
        return f"{self.student.user.username} - {self.final_exam.subject.name} ({self.inscription_date})"

    class Meta:
        unique_together = ('student', 'final_exam')
