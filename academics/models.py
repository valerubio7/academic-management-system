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
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="careers"
    )
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

        OBLIGATORY = "obligatory", "Obligatory"
        ELECTIVE = "elective", "Elective"

    class Period(models.TextChoices):
        """Academic period options."""

        FIRST = "first", "First"
        SECOND = "second", "Second"
        ANNUAL = "annual", "Annual"

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, primary_key=True)
    career = models.ForeignKey(
        Career, on_delete=models.CASCADE, related_name="subjects"
    )
    year = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=10, choices=Category.choices)
    period = models.CharField(max_length=10, choices=Period.choices)
    semanal_hours = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.career.name}"
