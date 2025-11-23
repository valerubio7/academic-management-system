# Generated manually for production readiness
# This migration adds database indexes for improved query performance

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        # Add indexes to Grade model
        migrations.AddIndex(
            model_name="grade",
            index=models.Index(
                fields=["student", "subject"], name="app_grade_student_subject_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="grade",
            index=models.Index(fields=["status"], name="app_grade_status_idx"),
        ),
        migrations.AddIndex(
            model_name="grade",
            index=models.Index(
                fields=["student", "status"], name="app_grade_student_status_idx"
            ),
        ),
        # Add indexes to SubjectInscription model
        migrations.AddIndex(
            model_name="subjectinscription",
            index=models.Index(fields=["student"], name="app_subjectinscr_student_idx"),
        ),
        migrations.AddIndex(
            model_name="subjectinscription",
            index=models.Index(fields=["subject"], name="app_subjectinscr_subject_idx"),
        ),
        migrations.AddIndex(
            model_name="subjectinscription",
            index=models.Index(
                fields=["inscription_date"], name="app_subjectinscr_date_idx"
            ),
        ),
        # Add indexes to FinalExamInscription model
        migrations.AddIndex(
            model_name="finalexaminscription",
            index=models.Index(
                fields=["student"], name="app_finalexaminsc_student_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="finalexaminscription",
            index=models.Index(
                fields=["final_exam"], name="app_finalexaminsc_exam_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="finalexaminscription",
            index=models.Index(
                fields=["inscription_date"], name="app_finalexaminsc_date_idx"
            ),
        ),
    ]
