from django.db import models


class Faculty(models.Model):
    """Model representing a faculty."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, primary_key=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField()
    dean = models.CharField(max_length=100)
    established_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Career(models.Model):
    """Model representing a career."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='careers')
    director = models.CharField(max_length=100)
    duration_years = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.faculty.name}"


class Subject(models.Model):
    """Model representing a subject."""
    class Category(models.TextChoices):
        """Category choices for subjects."""
        OBLIGATORY = 'obligatory', 'Obligatory'
        ELECTIVE = 'elective', 'Elective'

    class Period(models.TextChoices):
        """Period choices for subjects."""
        FIRST = 'first', 'First'
        SECOND = 'second', 'Second'
        ANNUAL = 'annual', 'Annual'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, primary_key=True)
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='subjects')
    year = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=10, choices=Category.choices)
    period = models.CharField(max_length=10, choices=Period.choices)
    semanal_hours = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.career.name}"


class FinalExam(models.Model):
    """Model representing a final exam"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='final_exams')
    date = models.DateField()
    location = models.CharField(max_length=255)
    duration = models.DurationField()
    call_number = models.PositiveSmallIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject.name} Final Exam on {self.date.strftime('%Y-%m-%d')}"


class Grade(models.Model):
    class StatusSubject(models.TextChoices):
        """Status choices for subjects."""
        FREE = 'free', 'Free'
        REGULAR = 'regular', 'Regular'
        PROMOTED = 'promoted', 'Promoted'

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    promotion_grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=StatusSubject.choices, default=StatusSubject.REGULAR)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} ({self.status})"

    def update_status(self):
        """Update the status of the subject based on the final grade."""
        if self.final_grade is not None:
            if self.final_grade >= 6.0:
                self.status = self.StatusSubject.PROMOTED
            else:
                self.status = self.StatusSubject.REGULAR
        else:
            self.status = self.StatusSubject.FREE
        self.save()
