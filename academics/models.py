from django.db import models


class Faculty(models.Model):
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
    class Category(models.TextChoices):
        OBLIGATORY = "obligatory", "Obligatory"
        ELECTIVE = "elective", "Elective"

    class Period(models.TextChoices):
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
