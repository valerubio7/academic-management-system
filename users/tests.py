from django.test import TestCase
from users.models import CustomUser, Student, Professor, Administrator
from academics.models import Career, Faculty


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass',
            role=CustomUser.Role.STUDENT,
            dni='12345678'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertEqual(user.dni, '12345678')


class StudentModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='student1',
            password='testpass',
            role=CustomUser.Role.STUDENT,
            dni='87654321'
        )
        self.faculty = Faculty.objects.create(
            code='F1',
            name='Facultad de Ingeniería',
            dean='Decano Ejemplo',
            established_date='1950-01-01'
        )
        self.career = Career.objects.create(
            name='Ingeniería',
            code='ING',
            faculty_id='F1',
            director='Director',
            duration_years=5
        )

    def test_create_student(self):
        student = Student.objects.create(
            student_id='S1',
            user=self.user,
            career=self.career,
            enrollment_date='2022-01-01'
        )
        self.assertEqual(student.user.username, 'student1')
        self.assertEqual(student.career.name, 'Ingeniería')


class ProfessorModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='prof1',
            password='testpass',
            role=CustomUser.Role.PROFESSOR,
            dni='11223344'
        )

    def test_create_professor(self):
        professor = Professor.objects.create(
            professor_id='P1',
            user=self.user,
            degree='PhD',
            hire_date='2020-01-01',
            category=Professor.Category.TITULAR
        )
        self.assertEqual(professor.user.username, 'prof1')
        self.assertEqual(professor.category, Professor.Category.TITULAR)


class AdministratorModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='admin1',
            password='testpass',
            role=CustomUser.Role.ADMIN,
            dni='99887766'
        )

    def test_create_administrator(self):
        admin = Administrator.objects.create(
            administrator_id='A1',
            user=self.user,
            position='Manager',
            hire_date='2021-01-01'
        )
        self.assertEqual(admin.user.username, 'admin1')
        self.assertEqual(admin.position, 'Manager')
