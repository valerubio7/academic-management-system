"""Data models for the Academics app.

Defines core academic entities and their relationships:
- Faculty -> Career -> Subject hierarchy.
- FinalExam sessions per Subject.
- Grade linking a Student to a Subject with status and grades.

Notes:
    - String representations (__str__) are optimized for admin readability.
    - Uniqueness of (student, subject) is enforced at the Grade model level.
"""

from django.db import models


class Faculty(models.Model):
    """
    Academic faculty or school within the institution.

    Attributes:
        name (str): Human-readable name.
        code (str): Unique short code (primary key).
        address (str): Postal address.
        phone (str): Contact phone number.
        email (str): Official contact email.
        website (str): Public website URL.
        dean (str): Dean or authority in charge.
        established_date (date): Founding or establishment date.
        description (str | None): Optional free-form notes.
    """
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
    """
    Academic program (degree) offered by a Faculty.

    Attributes:
        name (str): Program name.
        code (str): Unique program code (primary key).
        faculty (Faculty): Owning faculty (FK).
        director (str): Program director.
        duration_years (int): Nominal duration in years.
        description (str | None): Optional description.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='careers')
    director = models.CharField(max_length=100)
    duration_years = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.faculty.name}"


class Subject(models.Model):
    """
    Course within a Career curriculum.

    Attributes:
        name (str): Course name.
        code (str): Unique subject code (primary key).
        career (Career): Career this subject belongs to (FK).
        year (int): Recommended year in the plan.
        category (str): One of Category choices.
        period (str): One of Period choices.
        semanal_hours (int): Weekly contact hours.
        description (str | None): Optional description.
    """

    class Category(models.TextChoices):
        """Category options for curriculum classification."""
        OBLIGATORY = 'obligatory', 'Obligatory'
        ELECTIVE = 'elective', 'Elective'

    class Period(models.TextChoices):
        """Academic period options."""
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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='final_exams')
    date = models.DateField()
    location = models.CharField(max_length=255)
    duration = models.DurationField()
    call_number = models.PositiveSmallIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject.name} Final Exam on {self.date.strftime('%Y-%m-%d')}"


class Grade(models.Model):
    """
    Student performance and academic status for a Subject.

    Links a Student to a Subject, tracking promotion and final grades and a derived status.

    Attributes:
        student (users.Student): Student owning this record (FK).
        subject (Subject): Subject graded (FK).
        promotion_grade (Decimal | None): Continuous assessment/commission grade.
        status (str): One of StatusSubject choices (FREE, REGULAR, PROMOTED).
        final_grade (Decimal | None): Final exam grade, if applicable.
        last_updated (datetime): Auto-updated timestamp on save.
        notes (str | None): Optional comments.

    Notes:
        - Uniqueness of (student, subject) is enforced via Meta.unique_together.
        - Status transitions are maintained by update_status().
    """

    class StatusSubject(models.TextChoices):
        """Academic status of the student for the subject."""
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
        """
        Update and persist the status based on current final_grade.

        Logic:
            - If final_grade is not None and >= 6.0 -> PROMOTED.
            - If final_grade is not None and < 6.0 -> REGULAR.
            - If final_grade is None -> FREE.

        Side Effects:
            Saves the instance (self.save()).

        Raises:
            TypeError: If final_grade is not a number when provided.
        """
        if self.final_grade is not None:
            if self.final_grade >= 6.0:
                self.status = self.StatusSubject.PROMOTED
            else:
                self.status = self.StatusSubject.REGULAR
        else:
            self.status = self.StatusSubject.FREE
        self.save()
