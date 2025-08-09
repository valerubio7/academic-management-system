from django.test import TestCase
from academics.models import Faculty, Career, Subject, FinalExam, Grade
from users.models import CustomUser, Student
import datetime


class FacultyModelTest(TestCase):
    def test_create_faculty(self):
        faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            address='Calle 123',
            phone='123456789',
            email='facu@uni.edu',
            website='https://facu.uni.edu',
            dean='Decano Ejemplo',
            established_date='1950-01-01',
            description='Facultad de ingeniería'
        )
        self.assertEqual(faculty.name, 'Facultad de Ingeniería')
        self.assertEqual(str(faculty), 'Facultad de Ingeniería')


class CareerModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            address='Calle 123',
            phone='123456789',
            email='facu@uni.edu',
            website='https://facu.uni.edu',
            dean='Decano Ejemplo',
            established_date='1950-01-01'
        )

    def test_create_career(self):
        career = Career.objects.create(
            name='Ingeniería',
            code='ING',
            faculty=self.faculty,
            director='Director',
            duration_years=5,
            description='Carrera de ingeniería'
        )
        self.assertEqual(career.name, 'Ingeniería')
        self.assertEqual(str(career), 'Ingeniería (ING) - Facultad de Ingeniería')


class SubjectModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            address='Calle 123',
            phone='123456789',
            email='facu@uni.edu',
            website='https://facu.uni.edu',
            dean='Decano Ejemplo',
            established_date='1950-01-01'
        )
        self.career = Career.objects.create(
            name='Ingeniería',
            code='ING',
            faculty=self.faculty,
            director='Director',
            duration_years=5
        )

    def test_create_subject(self):
        subject = Subject.objects.create(
            name='Matemática',
            code='MAT101',
            career=self.career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=6,
            description='Matemática básica'
        )
        self.assertEqual(subject.name, 'Matemática')
        self.assertEqual(str(subject), 'Matemática (MAT101) - Ingeniería')


class FinalExamModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            address='Calle 123',
            phone='123456789',
            email='facu@uni.edu',
            website='https://facu.uni.edu',
            dean='Decano Ejemplo',
            established_date='1950-01-01'
        )
        self.career = Career.objects.create(
            name='Ingeniería',
            code='ING',
            faculty=self.faculty,
            director='Director',
            duration_years=5
        )
        self.subject = Subject.objects.create(
            name='Matemática',
            code='MAT101',
            career=self.career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=6
        )

    def test_create_final_exam(self):
        final_exam = FinalExam.objects.create(
            subject=self.subject,
            date=datetime.date(2024, 7, 1),
            location='Aula 1',
            duration='02:00:00',
            call_number=1,
            notes='Primer llamado'
        )
        self.assertEqual(final_exam.subject.name, 'Matemática')
        self.assertIn('Matemática', str(final_exam))


class GradeModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            address='Calle 123',
            phone='123456789',
            email='facu@uni.edu',
            website='https://facu.uni.edu',
            dean='Decano Ejemplo',
            established_date='1950-01-01'
        )
        self.career = Career.objects.create(
            name='Ingeniería',
            code='ING',
            faculty=self.faculty,
            director='Director',
            duration_years=5
        )
        self.subject = Subject.objects.create(
            name='Matemática',
            code='MAT101',
            career=self.career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=6
        )
        self.user = CustomUser.objects.create_user(
            username='student1',
            password='testpass',
            role=CustomUser.Role.STUDENT,
            dni='12345678'
        )
        self.student = Student.objects.create(
            student_id='S1',
            user=self.user,
            career=self.career,
            enrollment_date='2022-01-01'
        )

    def test_create_grade(self):
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            promotion_grade=8.5,
            status=Grade.StatusSubject.REGULAR,
            final_grade=7.0,
            notes='Buen desempeño'
        )
        self.assertEqual(grade.student.user.username, 'student1')
        self.assertEqual(grade.subject.name, 'Matemática')
        self.assertEqual(str(grade), 'student1 - Matemática (regular)')

    def test_update_status(self):
        grade = Grade.objects.create(
            student=self.student,
            subject=self.subject,
            final_grade=None
        )
        grade.update_status()
        self.assertEqual(grade.status, Grade.StatusSubject.FREE)
        grade.final_grade = 7.0
        grade.update_status()
        self.assertEqual(grade.status, Grade.StatusSubject.PROMOTED)
        grade.final_grade = 5.0
        grade.update_status()
        self.assertEqual(grade.status, Grade.StatusSubject.REGULAR)
