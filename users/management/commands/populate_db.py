import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import Career, Faculty, Subject
from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from grading.models import Grade
from users.models import Administrator, CustomUser, Professor, Student


class Command(BaseCommand):
    help = "Populate database with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS("Starting data population..."))

        with transaction.atomic():
            # Create data in order of dependencies
            faculties = self.create_faculties()
            careers = self.create_careers(faculties)
            subjects = self.create_subjects(careers)

            # Create users
            admins = self.create_administrators()
            professors = self.create_professors(subjects)
            students = self.create_students(careers)

            # Create enrollments and grades
            self.create_subject_inscriptions(students, subjects)
            self.create_grades(students, subjects)

            # Create final exams and inscriptions
            final_exams = self.create_final_exams(subjects, professors)
            self.create_final_exam_inscriptions(students, final_exams)

        self.stdout.write(
            self.style.SUCCESS("Successfully populated database with sample data!")
        )
        self.print_summary()

    def clear_data(self):
        """Clear all data from the database"""
        Grade.objects.all().delete()
        FinalExamInscription.objects.all().delete()
        SubjectInscription.objects.all().delete()
        FinalExam.objects.all().delete()
        Student.objects.all().delete()
        Professor.objects.all().delete()
        Administrator.objects.all().delete()
        CustomUser.objects.all().delete()
        Subject.objects.all().delete()
        Career.objects.all().delete()
        Faculty.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Data cleared successfully!"))

    def create_faculties(self):
        """Create sample faculties"""
        self.stdout.write("Creating faculties...")
        faculties_data = [
            {
                "name": "Facultad de Ingeniería",
                "code": "FI",
                "address": "Av. Universitaria 1234",
                "phone": "+54-261-4135000",
                "email": "contacto@fi.edu.ar",
                "website": "https://fi.edu.ar",
                "dean": "Dr. Carlos Mendoza",
                "established_date": date(1960, 4, 15),
                "description": "Facultad dedicada a la formación de ingenieros",
            },
            {
                "name": "Facultad de Ciencias Exactas",
                "code": "FCE",
                "address": "Av. San Martín 5678",
                "phone": "+54-261-4290000",
                "email": "info@fce.edu.ar",
                "website": "https://fce.edu.ar",
                "dean": "Dra. María González",
                "established_date": date(1955, 8, 20),
                "description": "Facultad de Ciencias Exactas y Naturales",
            },
            {
                "name": "Facultad de Ciencias Económicas",
                "code": "FCEC",
                "address": "Calle Belgrano 910",
                "phone": "+54-261-4490000",
                "email": "contacto@fcec.edu.ar",
                "website": "https://fcec.edu.ar",
                "dean": "Dr. Roberto Fernández",
                "established_date": date(1965, 3, 10),
                "description": "Facultad de Ciencias Económicas",
            },
        ]

        faculties = []
        for data in faculties_data:
            faculty = Faculty.objects.create(**data)
            faculties.append(faculty)

        self.stdout.write(self.style.SUCCESS(f"Created {len(faculties)} faculties"))
        return faculties

    def create_careers(self, faculties):
        """Create sample careers"""
        self.stdout.write("Creating careers...")
        careers_data = [
            # Engineering careers
            {
                "name": "Ingeniería en Sistemas",
                "code": "IS",
                "faculty": faculties[0],
                "director": "Ing. Juan Pérez",
                "duration_years": 5,
                "description": "Carrera de grado en Ingeniería en Sistemas de Información",
            },
            {
                "name": "Ingeniería Industrial",
                "code": "II",
                "faculty": faculties[0],
                "director": "Ing. Ana Martínez",
                "duration_years": 5,
                "description": "Carrera de grado en Ingeniería Industrial",
            },
            {
                "name": "Ingeniería Civil",
                "code": "IC",
                "faculty": faculties[0],
                "director": "Ing. Pedro López",
                "duration_years": 6,
                "description": "Carrera de grado en Ingeniería Civil",
            },
            # Science careers
            {
                "name": "Licenciatura en Matemática",
                "code": "LM",
                "faculty": faculties[1],
                "director": "Dr. Laura Rodríguez",
                "duration_years": 5,
                "description": "Licenciatura en Matemática",
            },
            {
                "name": "Licenciatura en Física",
                "code": "LF",
                "faculty": faculties[1],
                "director": "Dr. Martín Silva",
                "duration_years": 5,
                "description": "Licenciatura en Física",
            },
            # Economic careers
            {
                "name": "Contador Público",
                "code": "CP",
                "faculty": faculties[2],
                "director": "Cont. Patricia Gómez",
                "duration_years": 5,
                "description": "Carrera de Contador Público",
            },
        ]

        careers = []
        for data in careers_data:
            career = Career.objects.create(**data)
            careers.append(career)

        self.stdout.write(self.style.SUCCESS(f"Created {len(careers)} careers"))
        return careers

    def create_subjects(self, careers):
        """Create sample subjects for each career"""
        self.stdout.write("Creating subjects...")
        subjects = []

        # Subjects for Ingeniería en Sistemas
        is_subjects = [
            ("Algoritmos y Estructuras de Datos", "AED", 1, "obligatory", "annual", 6),
            ("Matemática I", "MAT1", 1, "obligatory", "first", 6),
            ("Física I", "FIS1", 1, "obligatory", "second", 4),
            ("Programación Orientada a Objetos", "POO", 2, "obligatory", "first", 6),
            ("Base de Datos", "BD", 2, "obligatory", "annual", 6),
            ("Sistemas Operativos", "SO", 3, "obligatory", "first", 4),
            ("Redes de Computadoras", "RC", 3, "obligatory", "second", 4),
            ("Ingeniería de Software", "IS", 4, "obligatory", "annual", 6),
            ("Inteligencia Artificial", "IA", 4, "elective", "second", 4),
            ("Seguridad Informática", "SI", 5, "elective", "first", 4),
        ]

        for name, code, year, category, period, hours in is_subjects:
            subject = Subject.objects.create(
                name=name,
                code=code,
                career=careers[0],  # Ingeniería en Sistemas
                year=year,
                category=category,
                period=period,
                semanal_hours=hours,
                description=f"Asignatura {name} de {year}° año",
            )
            subjects.append(subject)

        # Subjects for Ingeniería Industrial
        ii_subjects = [
            ("Química General", "QG", 1, "obligatory", "first", 4),
            ("Introducción a la Ingeniería", "II", 1, "obligatory", "annual", 4),
            ("Termodinámica", "TERM", 2, "obligatory", "first", 5),
            ("Gestión de Operaciones", "GO", 3, "obligatory", "annual", 6),
            ("Control de Calidad", "CC", 4, "obligatory", "second", 4),
        ]

        for name, code, year, category, period, hours in ii_subjects:
            subject = Subject.objects.create(
                name=name,
                code=f"II-{code}",
                career=careers[1],  # Ingeniería Industrial
                year=year,
                category=category,
                period=period,
                semanal_hours=hours,
                description=f"Asignatura {name} de {year}° año",
            )
            subjects.append(subject)

        # Subjects for Licenciatura en Matemática
        lm_subjects = [
            ("Análisis Matemático I", "AM1", 1, "obligatory", "annual", 6),
            ("Álgebra Lineal", "AL", 1, "obligatory", "first", 6),
            ("Geometría Analítica", "GA", 2, "obligatory", "second", 4),
            ("Cálculo Numérico", "CN", 3, "obligatory", "annual", 6),
            ("Topología", "TOP", 4, "elective", "first", 4),
        ]

        for name, code, year, category, period, hours in lm_subjects:
            subject = Subject.objects.create(
                name=name,
                code=f"LM-{code}",
                career=careers[3],  # Licenciatura en Matemática
                year=year,
                category=category,
                period=period,
                semanal_hours=hours,
                description=f"Asignatura {name} de {year}° año",
            )
            subjects.append(subject)

        self.stdout.write(self.style.SUCCESS(f"Created {len(subjects)} subjects"))
        return subjects

    def create_administrators(self):
        """Create sample administrators"""
        self.stdout.write("Creating administrators...")
        admins_data = [
            {
                "username": "admin1",
                "first_name": "Carlos",
                "last_name": "Ruiz",
                "email": "carlos.ruiz@university.edu.ar",
                "dni": "20123456",
                "phone": "+54-261-4000001",
                "position": "Director de Asuntos Estudiantiles",
                "hire_date": date(2015, 1, 15),
            },
            {
                "username": "admin2",
                "first_name": "Lucía",
                "last_name": "Torres",
                "email": "lucia.torres@university.edu.ar",
                "dni": "25987654",
                "phone": "+54-261-4000002",
                "position": "Secretaria Académica",
                "hire_date": date(2018, 3, 20),
            },
        ]

        admins = []
        for i, data in enumerate(admins_data, 1):
            user = CustomUser.objects.create_user(
                username=data["username"],
                password="admin123",
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=CustomUser.Role.ADMIN,
                dni=data["dni"],
                phone=data["phone"],
                birth_date=date(1980, 1, 1),
                address=f"Dirección {i}, Mendoza",
            )

            admin = Administrator.objects.create(
                administrator_id=f"ADM{i:03d}",
                user=user,
                position=data["position"],
                hire_date=data["hire_date"],
            )
            admins.append(admin)

        self.stdout.write(self.style.SUCCESS(f"Created {len(admins)} administrators"))
        return admins

    def create_professors(self, subjects):
        """Create sample professors"""
        self.stdout.write("Creating professors...")
        professors_data = [
            ("Jorge", "Martínez", "jorge.martinez", "PhD in Computer Science"),
            ("Ana", "Sánchez", "ana.sanchez", "MSc in Software Engineering"),
            ("Roberto", "González", "roberto.gonzalez", "PhD in Mathematics"),
            ("María", "Fernández", "maria.fernandez", "MSc in Industrial Engineering"),
            ("Luis", "Ramírez", "luis.ramirez", "PhD in Physics"),
            ("Carolina", "López", "carolina.lopez", "MSc in Computer Science"),
            ("Diego", "Herrera", "diego.herrera", "PhD in Applied Mathematics"),
            ("Valeria", "Castro", "valeria.castro", "MSc in Database Systems"),
            ("Sebastián", "Morales", "sebastian.morales", "PhD in Networks"),
            ("Gabriela", "Vega", "gabriela.vega", "MSc in AI"),
        ]

        professors = []
        categories = ["titular", "adjunct", "auxiliar"]

        for i, (first_name, last_name, username, degree) in enumerate(
            professors_data, 1
        ):
            user = CustomUser.objects.create_user(
                username=username,
                password="prof123",
                email=f"{username}@university.edu.ar",
                first_name=first_name,
                last_name=last_name,
                role=CustomUser.Role.PROFESSOR,
                dni=f"3{i:07d}",
                phone=f"+54-261-420{i:04d}",
                birth_date=date(1975 + i, 1, 1),
                address=f"Calle Profesor {i}, Mendoza",
            )

            professor = Professor.objects.create(
                professor_id=f"PROF{i:03d}",
                user=user,
                degree=degree,
                hire_date=date(2010 + i % 10, 1, 1),
                category=categories[i % 3],
            )

            # Assign random subjects to professors
            assigned_subjects = random.sample(
                subjects, min(3, len(subjects))
            )  # Each professor teaches 1-3 subjects
            professor.subjects.set(assigned_subjects)

            professors.append(professor)

        self.stdout.write(self.style.SUCCESS(f"Created {len(professors)} professors"))
        return professors

    def create_students(self, careers):
        """Create sample students"""
        self.stdout.write("Creating students...")
        first_names = [
            "Juan",
            "María",
            "Carlos",
            "Ana",
            "Pedro",
            "Laura",
            "Diego",
            "Sofía",
            "Martín",
            "Valentina",
            "Lucas",
            "Camila",
            "Mateo",
            "Victoria",
            "Santiago",
            "Florencia",
            "Nicolás",
            "Martina",
            "Tomás",
            "Lucía",
            "Benjamín",
            "Emma",
            "Joaquín",
            "Isabella",
            "Agustín",
            "Catalina",
            "Felipe",
            "Antonella",
            "Manuel",
            "Julia",
        ]

        last_names = [
            "García",
            "Rodríguez",
            "Martínez",
            "Fernández",
            "López",
            "González",
            "Pérez",
            "Sánchez",
            "Romero",
            "Torres",
            "Díaz",
            "Álvarez",
            "Ruiz",
            "Moreno",
            "Jiménez",
        ]

        students = []
        student_count = 50  # Create 50 students

        for i in range(1, student_count + 1):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{i}"

            user = CustomUser.objects.create_user(
                username=username,
                password="student123",
                email=f"{username}@estudiantes.edu.ar",
                first_name=first_name,
                last_name=last_name,
                role=CustomUser.Role.STUDENT,
                dni=f"4{i:07d}",
                phone=f"+54-261-15{i:06d}",
                birth_date=date(1998 + random.randint(0, 5), random.randint(1, 12), 1),
                address=f"Calle Estudiante {i}, Mendoza",
            )

            # Randomly assign career
            career = random.choice(careers)

            # Random enrollment date within last 5 years
            enrollment_year = random.randint(2019, 2024)
            enrollment_date = date(enrollment_year, 3, random.randint(1, 28))

            student = Student.objects.create(
                student_id=f"EST{i:05d}",
                user=user,
                career=career,
                enrollment_date=enrollment_date,
            )
            students.append(student)

        self.stdout.write(self.style.SUCCESS(f"Created {len(students)} students"))
        return students

    def create_subject_inscriptions(self, students, subjects):
        """Create subject inscriptions for students"""
        self.stdout.write("Creating subject inscriptions...")
        inscriptions = []

        for student in students:
            # Get subjects from student's career
            career_subjects = [s for s in subjects if s.career == student.career]

            if not career_subjects:
                continue

            # Each student enrolls in 3-6 subjects
            num_subjects = random.randint(3, min(6, len(career_subjects)))
            enrolled_subjects = random.sample(career_subjects, num_subjects)

            for subject in enrolled_subjects:
                inscription = SubjectInscription.objects.create(
                    student=student, subject=subject
                )
                inscriptions.append(inscription)

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(inscriptions)} subject inscriptions")
        )
        return inscriptions

    def create_grades(self, students, subjects):
        """Create grades for students"""
        self.stdout.write("Creating grades...")
        grades = []

        for student in students:
            # Get inscriptions for this student
            inscriptions = SubjectInscription.objects.filter(student=student)

            for inscription in inscriptions:
                # 70% chance of having a grade
                if random.random() < 0.7:
                    # Random promotion grade between 4.0 and 10.0
                    promotion_grade = Decimal(str(round(random.uniform(4.0, 10.0), 2)))

                    # 80% chance of having a final grade
                    final_grade = None
                    if random.random() < 0.8:
                        final_grade = Decimal(str(round(random.uniform(4.0, 10.0), 2)))

                    # Determine status
                    if final_grade:
                        status = (
                            Grade.StatusSubject.PROMOTED
                            if final_grade >= 6.0
                            else Grade.StatusSubject.REGULAR
                        )
                    else:
                        status = Grade.StatusSubject.REGULAR

                    grade = Grade.objects.create(
                        student=student,
                        subject=inscription.subject,
                        promotion_grade=promotion_grade,
                        final_grade=final_grade,
                        status=status,
                        notes=f"Calificación para {inscription.subject.name}",
                    )
                    grades.append(grade)

        self.stdout.write(self.style.SUCCESS(f"Created {len(grades)} grades"))
        return grades

    def create_final_exams(self, subjects, professors):
        """Create final exams"""
        self.stdout.write("Creating final exams...")
        final_exams = []

        # Create 2-3 final exam dates for each subject
        for subject in subjects:
            num_exams = random.randint(2, 3)

            for call in range(1, num_exams + 1):
                # Random date in the next 6 months
                days_ahead = random.randint(30, 180)
                exam_date = date.today() + timedelta(days=days_ahead)

                # Random duration between 2-4 hours
                duration_hours = random.randint(2, 4)

                locations = [
                    "Aula Magna",
                    "Aula 101",
                    "Aula 202",
                    "Laboratorio A",
                    "Sala de Conferencias",
                ]

                final_exam = FinalExam.objects.create(
                    subject=subject,
                    date=exam_date,
                    location=random.choice(locations),
                    duration=timedelta(hours=duration_hours),
                    call_number=call,
                    notes=f"Examen final - Llamado {call}",
                )

                # Assign 1-3 professors to the exam
                exam_professors = random.sample(
                    professors, min(random.randint(1, 3), len(professors))
                )
                final_exam.professors.set(exam_professors)

                final_exams.append(final_exam)

        self.stdout.write(self.style.SUCCESS(f"Created {len(final_exams)} final exams"))
        return final_exams

    def create_final_exam_inscriptions(self, students, final_exams):
        """Create final exam inscriptions"""
        self.stdout.write("Creating final exam inscriptions...")
        inscriptions = []

        for student in students:
            # Get subjects the student is enrolled in
            student_subjects = SubjectInscription.objects.filter(
                student=student
            ).values_list("subject", flat=True)

            # Get final exams for those subjects
            available_exams = [
                exam for exam in final_exams if exam.subject_id in student_subjects
            ]

            if not available_exams:
                continue

            # Each student registers for 0-3 final exams
            num_exams = random.randint(0, min(3, len(available_exams)))

            if num_exams > 0:
                selected_exams = random.sample(available_exams, num_exams)

                for final_exam in selected_exams:
                    inscription = FinalExamInscription.objects.create(
                        student=student, final_exam=final_exam
                    )
                    inscriptions.append(inscription)

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(inscriptions)} final exam inscriptions")
        )
        return inscriptions

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("DATABASE POPULATION SUMMARY"))
        self.stdout.write("=" * 60)

        self.stdout.write(f"Faculties: {Faculty.objects.count()}")
        self.stdout.write(f"Careers: {Career.objects.count()}")
        self.stdout.write(f"Subjects: {Subject.objects.count()}")
        self.stdout.write(f"Administrators: {Administrator.objects.count()}")
        self.stdout.write(f"Professors: {Professor.objects.count()}")
        self.stdout.write(f"Students: {Student.objects.count()}")
        self.stdout.write(f"Subject Inscriptions: {SubjectInscription.objects.count()}")
        self.stdout.write(f"Grades: {Grade.objects.count()}")
        self.stdout.write(f"Final Exams: {FinalExam.objects.count()}")
        self.stdout.write(
            f"Final Exam Inscriptions: {FinalExamInscription.objects.count()}"
        )
        self.stdout.write(f"Total Users: {CustomUser.objects.count()}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("DEFAULT CREDENTIALS"))
        self.stdout.write("=" * 60)
        self.stdout.write("Administrators: username: admin1/admin2, password: admin123")
        self.stdout.write(
            "Professors: username: [firstname].[lastname], password: prof123"
        )
        self.stdout.write(
            "Students: username: [firstname].[lastname][number], password: student123"
        )
        self.stdout.write("=" * 60 + "\n")
