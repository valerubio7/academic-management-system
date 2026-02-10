import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import Career, Faculty, Subject
from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from grading.models import Grade
from users.models import Administrator, CustomUser, Professor, Student

DEFAULT_PASSWORD = "password123"


class Command(BaseCommand):
    help = (
        "Seed the database with realistic test data: faculties, careers, subjects, "
        "users (admins, professors, students), final exams, inscriptions, and grades."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing seed-able data before inserting new data.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        self.stdout.write("\n=== Seeding database ===\n")

        faculties = self._create_faculties()
        careers = self._create_careers(faculties)
        subjects = self._create_subjects(careers)
        admins = self._create_administrators()
        professors = self._create_professors(subjects)
        students = self._create_students(careers)
        finals = self._create_final_exams(subjects, professors)
        subject_inscriptions = self._create_subject_inscriptions(students, subjects)
        final_inscriptions = self._create_final_exam_inscriptions(students, finals)
        grades = self._create_grades(subject_inscriptions)

        self._print_summary(
            faculties,
            careers,
            subjects,
            admins,
            professors,
            students,
            finals,
            subject_inscriptions,
            final_inscriptions,
            grades,
        )

    # ------------------------------------------------------------------
    # Flush
    # ------------------------------------------------------------------

    def _flush(self):
        self.stdout.write("Flushing existing data...")
        Grade.objects.all().delete()
        FinalExamInscription.objects.all().delete()
        SubjectInscription.objects.all().delete()
        FinalExam.objects.all().delete()
        Professor.objects.all().delete()
        Student.objects.all().delete()
        Administrator.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        Subject.objects.all().delete()
        Career.objects.all().delete()
        Faculty.objects.all().delete()
        self.stdout.write(self.style.WARNING("  All seed data deleted.\n"))

    # ------------------------------------------------------------------
    # Faculties
    # ------------------------------------------------------------------

    def _create_faculties(self):
        self.stdout.write("Creating faculties...")
        data = [
            {
                "code": "FING",
                "name": "Facultad de Ingenieria",
                "address": "Av. Las Heras 2214, Buenos Aires",
                "phone": "011-4514-3300",
                "email": "info@fing.edu.ar",
                "website": "https://www.fing.edu.ar",
                "dean": "Dr. Carlos Alberto Mendez",
                "established_date": datetime.date(1865, 6, 16),
                "description": "Facultad dedicada a las ciencias de la ingenieria y tecnologia.",
            },
            {
                "code": "FCEN",
                "name": "Facultad de Ciencias Exactas y Naturales",
                "address": "Intendente Guiraldes 2160, Buenos Aires",
                "phone": "011-4576-3300",
                "email": "info@fcen.edu.ar",
                "website": "https://www.fcen.edu.ar",
                "dean": "Dra. Maria Laura Fernandez",
                "established_date": datetime.date(1874, 3, 12),
                "description": "Facultad orientada a las ciencias exactas, naturales y computacion.",
            },
            {
                "code": "FCE",
                "name": "Facultad de Ciencias Economicas",
                "address": "Av. Cordoba 2122, Buenos Aires",
                "phone": "011-4370-6100",
                "email": "info@fce.edu.ar",
                "website": "https://www.fce.edu.ar",
                "dean": "Dr. Ricardo Jose Pahlen",
                "established_date": datetime.date(1913, 9, 20),
                "description": "Facultad enfocada en economia, administracion y contabilidad.",
            },
        ]
        faculties = [Faculty(**d) for d in data]
        Faculty.objects.bulk_create(faculties)
        self.stdout.write(self.style.SUCCESS(f"  {len(faculties)} faculties created."))
        return faculties

    # ------------------------------------------------------------------
    # Careers
    # ------------------------------------------------------------------

    def _create_careers(self, faculties):
        self.stdout.write("Creating careers...")
        fing, fcen, fce = faculties
        data = [
            {
                "code": "ISI",
                "name": "Ingenieria en Sistemas de Informacion",
                "faculty": fing,
                "director": "Ing. Roberto Garcia",
                "duration_years": 5,
                "description": "Carrera orientada al desarrollo de software y sistemas.",
            },
            {
                "code": "IC",
                "name": "Ingenieria Civil",
                "faculty": fing,
                "director": "Ing. Patricia Lopez",
                "duration_years": 5,
                "description": "Carrera enfocada en construccion e infraestructura.",
            },
            {
                "code": "LCC",
                "name": "Licenciatura en Ciencias de la Computacion",
                "faculty": fcen,
                "director": "Dr. Fernando Martinez",
                "duration_years": 5,
                "description": "Carrera orientada a los fundamentos teoricos de la computacion.",
            },
            {
                "code": "LM",
                "name": "Licenciatura en Matematica",
                "faculty": fcen,
                "director": "Dra. Silvia Gomez",
                "duration_years": 5,
                "description": "Carrera dedicada al estudio avanzado de la matematica.",
            },
            {
                "code": "CP",
                "name": "Contador Publico",
                "faculty": fce,
                "director": "Cr. Miguel Angel Torres",
                "duration_years": 5,
                "description": "Carrera orientada a contabilidad, auditoria y finanzas.",
            },
            {
                "code": "LA",
                "name": "Licenciatura en Administracion",
                "faculty": fce,
                "director": "Lic. Ana Beatriz Ruiz",
                "duration_years": 4,
                "description": "Carrera enfocada en gestion y administracion de organizaciones.",
            },
        ]
        careers = [Career(**d) for d in data]
        Career.objects.bulk_create(careers)
        self.stdout.write(self.style.SUCCESS(f"  {len(careers)} careers created."))
        return careers

    # ------------------------------------------------------------------
    # Subjects
    # ------------------------------------------------------------------

    def _create_subjects(self, careers):
        self.stdout.write("Creating subjects...")
        isi, ic, lcc, lm, cp, la = careers

        data = [
            # --- ISI (Ing. en Sistemas) ---
            {
                "code": "ISI-AM1",
                "name": "Analisis Matematico I",
                "career": isi,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 8,
            },
            {
                "code": "ISI-ALG",
                "name": "Algebra y Geometria Analitica",
                "career": isi,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "ISI-PRG",
                "name": "Programacion I",
                "career": isi,
                "year": 1,
                "category": "obligatory",
                "period": "annual",
                "semanal_hours": 8,
            },
            {
                "code": "ISI-FIS",
                "name": "Fisica I",
                "career": isi,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            {
                "code": "ISI-BDD",
                "name": "Bases de Datos",
                "career": isi,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            # --- IC (Ing. Civil) ---
            {
                "code": "IC-AM1",
                "name": "Analisis Matematico I",
                "career": ic,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 8,
            },
            {
                "code": "IC-FIS1",
                "name": "Fisica I",
                "career": ic,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "IC-EST",
                "name": "Estatica y Resistencia de Materiales",
                "career": ic,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 8,
            },
            {
                "code": "IC-HID",
                "name": "Hidraulica",
                "career": ic,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "IC-GEO",
                "name": "Geotecnia",
                "career": ic,
                "year": 3,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            # --- LCC (Lic. en Cs. de la Computacion) ---
            {
                "code": "LCC-ALG",
                "name": "Algoritmos y Estructuras de Datos I",
                "career": lcc,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 10,
            },
            {
                "code": "LCC-AM1",
                "name": "Analisis Matematico I",
                "career": lcc,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 8,
            },
            {
                "code": "LCC-LOQ",
                "name": "Logica y Computabilidad",
                "career": lcc,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            {
                "code": "LCC-SO",
                "name": "Sistemas Operativos",
                "career": lcc,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "LCC-IA",
                "name": "Inteligencia Artificial",
                "career": lcc,
                "year": 3,
                "category": "elective",
                "period": "first",
                "semanal_hours": 6,
            },
            # --- LM (Lic. en Matematica) ---
            {
                "code": "LM-AM1",
                "name": "Analisis Matematico I",
                "career": lm,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 10,
            },
            {
                "code": "LM-ALG",
                "name": "Algebra Lineal",
                "career": lm,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 8,
            },
            {
                "code": "LM-TOP",
                "name": "Topologia",
                "career": lm,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            {
                "code": "LM-PRB",
                "name": "Probabilidad y Estadistica",
                "career": lm,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "LM-ANF",
                "name": "Analisis Funcional",
                "career": lm,
                "year": 3,
                "category": "elective",
                "period": "annual",
                "semanal_hours": 4,
            },
            # --- CP (Contador Publico) ---
            {
                "code": "CP-CON1",
                "name": "Contabilidad I",
                "career": cp,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            {
                "code": "CP-ECO",
                "name": "Economia I",
                "career": cp,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "CP-DER",
                "name": "Derecho Comercial",
                "career": cp,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 4,
            },
            {
                "code": "CP-AUD",
                "name": "Auditoria",
                "career": cp,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "CP-IMP",
                "name": "Impuestos",
                "career": cp,
                "year": 3,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            # --- LA (Lic. en Administracion) ---
            {
                "code": "LA-ADM1",
                "name": "Administracion General",
                "career": la,
                "year": 1,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 6,
            },
            {
                "code": "LA-ECO",
                "name": "Economia I",
                "career": la,
                "year": 1,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 6,
            },
            {
                "code": "LA-MKT",
                "name": "Marketing",
                "career": la,
                "year": 2,
                "category": "obligatory",
                "period": "first",
                "semanal_hours": 4,
            },
            {
                "code": "LA-RRHH",
                "name": "Recursos Humanos",
                "career": la,
                "year": 2,
                "category": "obligatory",
                "period": "second",
                "semanal_hours": 4,
            },
            {
                "code": "LA-FIN",
                "name": "Finanzas",
                "career": la,
                "year": 3,
                "category": "elective",
                "period": "first",
                "semanal_hours": 6,
            },
        ]
        subjects = [Subject(**d) for d in data]
        Subject.objects.bulk_create(subjects)
        self.stdout.write(self.style.SUCCESS(f"  {len(subjects)} subjects created."))
        return subjects

    # ------------------------------------------------------------------
    # Administrators
    # ------------------------------------------------------------------

    def _create_administrators(self):
        self.stdout.write("Creating administrators...")
        data = [
            {
                "username": "admin1",
                "first_name": "Jorge",
                "last_name": "Ramirez",
                "email": "jorge.ramirez@ams.edu.ar",
                "dni": "20345678",
                "phone": "011-4555-1001",
                "birth_date": datetime.date(1975, 3, 15),
                "address": "Av. Rivadavia 4500, Buenos Aires",
                "profile": {
                    "administrator_id": "ADM-001",
                    "position": "Director de Asuntos Academicos",
                    "hire_date": datetime.date(2010, 3, 1),
                },
            },
            {
                "username": "admin2",
                "first_name": "Laura",
                "last_name": "Suarez",
                "email": "laura.suarez@ams.edu.ar",
                "dni": "25678901",
                "phone": "011-4555-1002",
                "birth_date": datetime.date(1980, 7, 22),
                "address": "Calle Defensa 1200, Buenos Aires",
                "profile": {
                    "administrator_id": "ADM-002",
                    "position": "Secretaria Academica",
                    "hire_date": datetime.date(2015, 8, 15),
                },
            },
        ]
        admins = []
        for d in data:
            profile_data = d.pop("profile")
            user = CustomUser.objects.create_user(
                password=DEFAULT_PASSWORD, role=CustomUser.Role.ADMIN, **d
            )
            admins.append(Administrator.objects.create(user=user, **profile_data))
        self.stdout.write(
            self.style.SUCCESS(f"  {len(admins)} administrators created.")
        )
        return admins

    # ------------------------------------------------------------------
    # Professors
    # ------------------------------------------------------------------

    def _create_professors(self, subjects):
        self.stdout.write("Creating professors...")

        # Build a dict for quick lookup: code -> Subject instance
        subj_map = {s.code: s for s in subjects}

        data = [
            {
                "username": "prof1",
                "first_name": "Ricardo",
                "last_name": "Gonzalez",
                "email": "ricardo.gonzalez@ams.edu.ar",
                "dni": "18234567",
                "phone": "011-4555-2001",
                "birth_date": datetime.date(1968, 5, 10),
                "address": "Calle Florida 800, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-001",
                    "degree": "Doctor en Matematica",
                    "hire_date": datetime.date(2005, 3, 1),
                    "category": "titular",
                },
                "subject_codes": ["ISI-AM1", "IC-AM1", "LCC-AM1", "LM-AM1"],
            },
            {
                "username": "prof2",
                "first_name": "Marta",
                "last_name": "Dominguez",
                "email": "marta.dominguez@ams.edu.ar",
                "dni": "20456789",
                "phone": "011-4555-2002",
                "birth_date": datetime.date(1972, 11, 3),
                "address": "Av. Santa Fe 3200, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-002",
                    "degree": "Doctora en Fisica",
                    "hire_date": datetime.date(2008, 7, 15),
                    "category": "titular",
                },
                "subject_codes": ["ISI-FIS", "IC-FIS1"],
            },
            {
                "username": "prof3",
                "first_name": "Alejandro",
                "last_name": "Vega",
                "email": "alejandro.vega@ams.edu.ar",
                "dni": "22567890",
                "phone": "011-4555-2003",
                "birth_date": datetime.date(1976, 8, 25),
                "address": "Calle Lavalle 1500, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-003",
                    "degree": "Ingeniero en Sistemas",
                    "hire_date": datetime.date(2012, 3, 1),
                    "category": "adjunct",
                },
                "subject_codes": ["ISI-PRG", "ISI-BDD", "LCC-ALG"],
            },
            {
                "username": "prof4",
                "first_name": "Carolina",
                "last_name": "Herrera",
                "email": "carolina.herrera@ams.edu.ar",
                "dni": "24678901",
                "phone": "011-4555-2004",
                "birth_date": datetime.date(1979, 1, 14),
                "address": "Av. Callao 1800, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-004",
                    "degree": "Doctora en Computacion",
                    "hire_date": datetime.date(2014, 8, 1),
                    "category": "adjunct",
                },
                "subject_codes": ["LCC-LOQ", "LCC-SO", "LCC-IA"],
            },
            {
                "username": "prof5",
                "first_name": "Daniel",
                "last_name": "Moreno",
                "email": "daniel.moreno@ams.edu.ar",
                "dni": "21789012",
                "phone": "011-4555-2005",
                "birth_date": datetime.date(1974, 4, 30),
                "address": "Calle Belgrano 900, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-005",
                    "degree": "Ingeniero Civil",
                    "hire_date": datetime.date(2010, 3, 1),
                    "category": "titular",
                },
                "subject_codes": ["IC-EST", "IC-HID", "IC-GEO"],
            },
            {
                "username": "prof6",
                "first_name": "Gabriela",
                "last_name": "Castro",
                "email": "gabriela.castro@ams.edu.ar",
                "dni": "23890123",
                "phone": "011-4555-2006",
                "birth_date": datetime.date(1977, 9, 8),
                "address": "Av. Pueyrredon 500, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-006",
                    "degree": "Doctora en Matematica",
                    "hire_date": datetime.date(2016, 3, 1),
                    "category": "auxiliar",
                },
                "subject_codes": ["ISI-ALG", "LM-ALG", "LM-TOP", "LM-PRB", "LM-ANF"],
            },
            {
                "username": "prof7",
                "first_name": "Eduardo",
                "last_name": "Navarro",
                "email": "eduardo.navarro@ams.edu.ar",
                "dni": "19901234",
                "phone": "011-4555-2007",
                "birth_date": datetime.date(1970, 12, 20),
                "address": "Calle Tucuman 700, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-007",
                    "degree": "Contador Publico Nacional",
                    "hire_date": datetime.date(2007, 8, 1),
                    "category": "titular",
                },
                "subject_codes": ["CP-CON1", "CP-AUD", "CP-IMP"],
            },
            {
                "username": "prof8",
                "first_name": "Susana",
                "last_name": "Molina",
                "email": "susana.molina@ams.edu.ar",
                "dni": "25012345",
                "phone": "011-4555-2008",
                "birth_date": datetime.date(1980, 6, 5),
                "address": "Av. Corrientes 3000, Buenos Aires",
                "profile": {
                    "professor_id": "PROF-008",
                    "degree": "Licenciada en Administracion",
                    "hire_date": datetime.date(2018, 3, 1),
                    "category": "adjunct",
                },
                "subject_codes": [
                    "CP-ECO",
                    "CP-DER",
                    "LA-ADM1",
                    "LA-ECO",
                    "LA-MKT",
                    "LA-RRHH",
                    "LA-FIN",
                ],
            },
        ]

        professors = []
        for d in data:
            profile_data = d.pop("profile")
            subject_codes = d.pop("subject_codes")
            user = CustomUser.objects.create_user(
                password=DEFAULT_PASSWORD, role=CustomUser.Role.PROFESSOR, **d
            )
            prof = Professor.objects.create(user=user, **profile_data)
            prof.subjects.set([subj_map[c] for c in subject_codes])
            professors.append(prof)

        self.stdout.write(
            self.style.SUCCESS(f"  {len(professors)} professors created.")
        )
        return professors

    # ------------------------------------------------------------------
    # Students
    # ------------------------------------------------------------------

    def _create_students(self, careers):
        self.stdout.write("Creating students...")
        career_map = {c.code: c for c in careers}

        # 20 students distributed across careers
        data = [
            # ISI students (5)
            {
                "username": "student1",
                "first_name": "Lucas",
                "last_name": "Martinez",
                "email": "lucas.martinez@ams.edu.ar",
                "dni": "40100001",
                "birth_date": datetime.date(2000, 2, 15),
                "career_code": "ISI",
                "student_id": "STU-001",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student2",
                "first_name": "Valentina",
                "last_name": "Lopez",
                "email": "valentina.lopez@ams.edu.ar",
                "dni": "40100002",
                "birth_date": datetime.date(2001, 5, 20),
                "career_code": "ISI",
                "student_id": "STU-002",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student3",
                "first_name": "Mateo",
                "last_name": "Garcia",
                "email": "mateo.garcia@ams.edu.ar",
                "dni": "40100003",
                "birth_date": datetime.date(2000, 8, 10),
                "career_code": "ISI",
                "student_id": "STU-003",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student4",
                "first_name": "Sofia",
                "last_name": "Rodriguez",
                "email": "sofia.rodriguez@ams.edu.ar",
                "dni": "40100004",
                "birth_date": datetime.date(2001, 11, 30),
                "career_code": "ISI",
                "student_id": "STU-004",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student5",
                "first_name": "Benjamin",
                "last_name": "Fernandez",
                "email": "benjamin.fernandez@ams.edu.ar",
                "dni": "40100005",
                "birth_date": datetime.date(2002, 1, 5),
                "career_code": "ISI",
                "student_id": "STU-005",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
            # IC students (3)
            {
                "username": "student6",
                "first_name": "Camila",
                "last_name": "Alvarez",
                "email": "camila.alvarez@ams.edu.ar",
                "dni": "40100006",
                "birth_date": datetime.date(2000, 4, 12),
                "career_code": "IC",
                "student_id": "STU-006",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student7",
                "first_name": "Tomas",
                "last_name": "Diaz",
                "email": "tomas.diaz@ams.edu.ar",
                "dni": "40100007",
                "birth_date": datetime.date(2001, 7, 18),
                "career_code": "IC",
                "student_id": "STU-007",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student8",
                "first_name": "Isabella",
                "last_name": "Romero",
                "email": "isabella.romero@ams.edu.ar",
                "dni": "40100008",
                "birth_date": datetime.date(2002, 3, 25),
                "career_code": "IC",
                "student_id": "STU-008",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
            # LCC students (3)
            {
                "username": "student9",
                "first_name": "Nicolas",
                "last_name": "Sosa",
                "email": "nicolas.sosa@ams.edu.ar",
                "dni": "40100009",
                "birth_date": datetime.date(2000, 6, 8),
                "career_code": "LCC",
                "student_id": "STU-009",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student10",
                "first_name": "Martina",
                "last_name": "Torres",
                "email": "martina.torres@ams.edu.ar",
                "dni": "40100010",
                "birth_date": datetime.date(2001, 9, 14),
                "career_code": "LCC",
                "student_id": "STU-010",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student11",
                "first_name": "Joaquin",
                "last_name": "Ruiz",
                "email": "joaquin.ruiz@ams.edu.ar",
                "dni": "40100011",
                "birth_date": datetime.date(2002, 12, 1),
                "career_code": "LCC",
                "student_id": "STU-011",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
            # LM students (3)
            {
                "username": "student12",
                "first_name": "Emilia",
                "last_name": "Flores",
                "email": "emilia.flores@ams.edu.ar",
                "dni": "40100012",
                "birth_date": datetime.date(2000, 10, 22),
                "career_code": "LM",
                "student_id": "STU-012",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student13",
                "first_name": "Santiago",
                "last_name": "Acosta",
                "email": "santiago.acosta@ams.edu.ar",
                "dni": "40100013",
                "birth_date": datetime.date(2001, 3, 7),
                "career_code": "LM",
                "student_id": "STU-013",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student14",
                "first_name": "Catalina",
                "last_name": "Medina",
                "email": "catalina.medina@ams.edu.ar",
                "dni": "40100014",
                "birth_date": datetime.date(2002, 6, 19),
                "career_code": "LM",
                "student_id": "STU-014",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
            # CP students (3)
            {
                "username": "student15",
                "first_name": "Felipe",
                "last_name": "Herrera",
                "email": "felipe.herrera@ams.edu.ar",
                "dni": "40100015",
                "birth_date": datetime.date(2000, 1, 28),
                "career_code": "CP",
                "student_id": "STU-015",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student16",
                "first_name": "Renata",
                "last_name": "Vargas",
                "email": "renata.vargas@ams.edu.ar",
                "dni": "40100016",
                "birth_date": datetime.date(2001, 4, 16),
                "career_code": "CP",
                "student_id": "STU-016",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student17",
                "first_name": "Agustin",
                "last_name": "Castro",
                "email": "agustin.castro@ams.edu.ar",
                "dni": "40100017",
                "birth_date": datetime.date(2002, 8, 3),
                "career_code": "CP",
                "student_id": "STU-017",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
            # LA students (3)
            {
                "username": "student18",
                "first_name": "Victoria",
                "last_name": "Rios",
                "email": "victoria.rios@ams.edu.ar",
                "dni": "40100018",
                "birth_date": datetime.date(2000, 11, 9),
                "career_code": "LA",
                "student_id": "STU-018",
                "enrollment_date": datetime.date(2023, 3, 1),
            },
            {
                "username": "student19",
                "first_name": "Facundo",
                "last_name": "Gutierrez",
                "email": "facundo.gutierrez@ams.edu.ar",
                "dni": "40100019",
                "birth_date": datetime.date(2001, 2, 26),
                "career_code": "LA",
                "student_id": "STU-019",
                "enrollment_date": datetime.date(2024, 3, 1),
            },
            {
                "username": "student20",
                "first_name": "Julieta",
                "last_name": "Pereyra",
                "email": "julieta.pereyra@ams.edu.ar",
                "dni": "40100020",
                "birth_date": datetime.date(2002, 5, 14),
                "career_code": "LA",
                "student_id": "STU-020",
                "enrollment_date": datetime.date(2025, 3, 1),
            },
        ]

        students = []
        for d in data:
            career_code = d.pop("career_code")
            student_id = d.pop("student_id")
            enrollment_date = d.pop("enrollment_date")
            user = CustomUser.objects.create_user(
                password=DEFAULT_PASSWORD, role=CustomUser.Role.STUDENT, **d
            )
            students.append(
                Student.objects.create(
                    student_id=student_id,
                    user=user,
                    career=career_map[career_code],
                    enrollment_date=enrollment_date,
                )
            )

        self.stdout.write(self.style.SUCCESS(f"  {len(students)} students created."))
        return students

    # ------------------------------------------------------------------
    # Final Exams
    # ------------------------------------------------------------------

    def _create_final_exams(self, subjects, professors):
        self.stdout.write("Creating final exams...")
        subj_map = {s.code: s for s in subjects}
        prof_map = {p.professor_id: p for p in professors}

        # Each entry: subject_code, date, location, duration_minutes, call_number, professor_ids
        data = [
            (
                "ISI-AM1",
                datetime.date(2026, 2, 15),
                "Aula 101 - FING",
                180,
                1,
                ["PROF-001"],
            ),
            (
                "ISI-AM1",
                datetime.date(2026, 3, 10),
                "Aula 101 - FING",
                180,
                2,
                ["PROF-001"],
            ),
            (
                "ISI-ALG",
                datetime.date(2026, 2, 18),
                "Aula 102 - FING",
                180,
                1,
                ["PROF-006"],
            ),
            (
                "ISI-PRG",
                datetime.date(2026, 2, 20),
                "Lab 1 - FING",
                120,
                1,
                ["PROF-003"],
            ),
            (
                "ISI-BDD",
                datetime.date(2026, 2, 22),
                "Lab 2 - FING",
                120,
                1,
                ["PROF-003"],
            ),
            (
                "IC-AM1",
                datetime.date(2026, 2, 16),
                "Aula 201 - FING",
                180,
                1,
                ["PROF-001"],
            ),
            (
                "IC-FIS1",
                datetime.date(2026, 2, 25),
                "Aula 202 - FING",
                180,
                1,
                ["PROF-002"],
            ),
            (
                "IC-EST",
                datetime.date(2026, 3, 5),
                "Aula 203 - FING",
                180,
                1,
                ["PROF-005"],
            ),
            (
                "LCC-ALG",
                datetime.date(2026, 2, 17),
                "Aula 301 - FCEN",
                180,
                1,
                ["PROF-003"],
            ),
            (
                "LCC-SO",
                datetime.date(2026, 2, 24),
                "Aula 302 - FCEN",
                120,
                1,
                ["PROF-004"],
            ),
            (
                "LM-AM1",
                datetime.date(2026, 2, 19),
                "Aula 303 - FCEN",
                180,
                1,
                ["PROF-001"],
            ),
            (
                "LM-ALG",
                datetime.date(2026, 2, 26),
                "Aula 304 - FCEN",
                180,
                1,
                ["PROF-006"],
            ),
            (
                "CP-CON1",
                datetime.date(2026, 2, 14),
                "Aula 401 - FCE",
                120,
                1,
                ["PROF-007"],
            ),
            (
                "CP-ECO",
                datetime.date(2026, 2, 21),
                "Aula 402 - FCE",
                120,
                1,
                ["PROF-008"],
            ),
            (
                "LA-ADM1",
                datetime.date(2026, 2, 23),
                "Aula 403 - FCE",
                120,
                1,
                ["PROF-008"],
            ),
        ]

        finals = []
        for subj_code, date, location, duration_min, call_num, prof_ids in data:
            final = FinalExam.objects.create(
                subject=subj_map[subj_code],
                date=date,
                location=location,
                duration=datetime.timedelta(minutes=duration_min),
                call_number=call_num,
            )
            final.professors.set([prof_map[pid] for pid in prof_ids])
            finals.append(final)

        self.stdout.write(self.style.SUCCESS(f"  {len(finals)} final exams created."))
        return finals

    # ------------------------------------------------------------------
    # Subject Inscriptions
    # ------------------------------------------------------------------

    def _create_subject_inscriptions(self, students, subjects):
        self.stdout.write("Creating subject inscriptions...")
        subj_map = {s.code: s for s in subjects}

        # Map student index (0-based) to list of subject codes to enroll in
        enrollment_map = {
            # ISI students -> ISI subjects
            0: ["ISI-AM1", "ISI-ALG", "ISI-PRG"],
            1: ["ISI-AM1", "ISI-ALG", "ISI-PRG", "ISI-FIS"],
            2: ["ISI-AM1", "ISI-PRG"],
            3: ["ISI-AM1", "ISI-ALG", "ISI-PRG"],
            4: ["ISI-AM1"],
            # IC students -> IC subjects
            5: ["IC-AM1", "IC-FIS1", "IC-EST"],
            6: ["IC-AM1", "IC-FIS1"],
            7: ["IC-AM1"],
            # LCC students -> LCC subjects
            8: ["LCC-ALG", "LCC-AM1", "LCC-LOQ", "LCC-SO"],
            9: ["LCC-ALG", "LCC-AM1"],
            10: ["LCC-ALG"],
            # LM students -> LM subjects
            11: ["LM-AM1", "LM-ALG", "LM-TOP", "LM-PRB"],
            12: ["LM-AM1", "LM-ALG"],
            13: ["LM-AM1"],
            # CP students -> CP subjects
            14: ["CP-CON1", "CP-ECO", "CP-DER"],
            15: ["CP-CON1", "CP-ECO"],
            16: ["CP-CON1"],
            # LA students -> LA subjects
            17: ["LA-ADM1", "LA-ECO", "LA-MKT"],
            18: ["LA-ADM1", "LA-ECO"],
            19: ["LA-ADM1"],
        }

        inscriptions = []
        for idx, codes in enrollment_map.items():
            for code in codes:
                inscriptions.append(
                    SubjectInscription(
                        student=students[idx],
                        subject=subj_map[code],
                    )
                )
        SubjectInscription.objects.bulk_create(inscriptions)
        self.stdout.write(
            self.style.SUCCESS(f"  {len(inscriptions)} subject inscriptions created.")
        )
        return inscriptions

    # ------------------------------------------------------------------
    # Final Exam Inscriptions
    # ------------------------------------------------------------------

    def _create_final_exam_inscriptions(self, students, finals):
        self.stdout.write("Creating final exam inscriptions...")

        # Build a lookup: subject_code -> list of FinalExam (use first one per subject)
        final_by_subject = {}
        for f in finals:
            final_by_subject.setdefault(f.subject.code, []).append(f)

        # Map student index -> list of subject codes for which to enroll in a final
        # Only students who are already inscribed in the subject and "advanced enough"
        final_enrollment_map = {
            0: ["ISI-AM1", "ISI-ALG"],
            1: ["ISI-AM1", "ISI-PRG", "ISI-ALG"],
            5: ["IC-AM1", "IC-FIS1"],
            6: ["IC-AM1"],
            8: ["LCC-ALG", "LCC-SO"],
            9: ["LCC-ALG"],
            11: ["LM-AM1", "LM-ALG"],
            12: ["LM-AM1"],
            14: ["CP-CON1", "CP-ECO"],
            15: ["CP-CON1"],
            17: ["LA-ADM1"],
            18: ["LA-ADM1"],
        }

        inscriptions = []
        for idx, codes in final_enrollment_map.items():
            for code in codes:
                # Pick the first available final for this subject
                available_finals = final_by_subject.get(code, [])
                if available_finals:
                    inscriptions.append(
                        FinalExamInscription(
                            student=students[idx],
                            final_exam=available_finals[0],
                        )
                    )
        FinalExamInscription.objects.bulk_create(inscriptions)
        self.stdout.write(
            self.style.SUCCESS(
                f"  {len(inscriptions)} final exam inscriptions created."
            )
        )
        return inscriptions

    # ------------------------------------------------------------------
    # Grades
    # ------------------------------------------------------------------

    def _create_grades(self, subject_inscriptions):
        self.stdout.write("Creating grades...")

        # Pre-defined grade data cycling through varied statuses
        # Pattern: promoted, regular, free, promoted, promoted, regular, free, ...
        grade_patterns = [
            # (promotion_grade, final_grade, notes)
            (Decimal("8.50"), Decimal("7.00"), "Buen desempeno en cursada y final."),
            (Decimal("5.00"), Decimal("4.00"), "Aprobo cursada, desaprobo final."),
            (None, None, "Libre por inasistencias."),
            (Decimal("9.00"), Decimal("8.00"), "Excelente rendimiento."),
            (Decimal("7.00"), Decimal("6.00"), "Rendimiento aceptable."),
            (Decimal("6.00"), Decimal("5.00"), "Aprobo cursada, desaprobo final."),
            (None, None, "No rindio examen final."),
            (Decimal("10.00"), Decimal("10.00"), "Rendimiento sobresaliente."),
            (Decimal("7.50"), Decimal("7.50"), "Buen rendimiento general."),
            (Decimal("4.00"), Decimal("3.00"), "Desaprobo cursada y final."),
        ]

        grades = []
        for i, insc in enumerate(subject_inscriptions):
            pattern = grade_patterns[i % len(grade_patterns)]
            promotion_grade, final_grade, notes = pattern

            # Determine status
            if final_grade is not None:
                status = (
                    Grade.StatusSubject.PROMOTED
                    if final_grade >= Decimal("6.0")
                    else Grade.StatusSubject.REGULAR
                )
            else:
                status = Grade.StatusSubject.FREE

            grades.append(
                Grade(
                    student=insc.student,
                    subject=insc.subject,
                    promotion_grade=promotion_grade,
                    final_grade=final_grade,
                    status=status,
                    notes=notes,
                )
            )

        Grade.objects.bulk_create(grades)
        self.stdout.write(self.style.SUCCESS(f"  {len(grades)} grades created."))
        return grades

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _print_summary(
        self,
        faculties,
        careers,
        subjects,
        admins,
        professors,
        students,
        finals,
        subject_inscriptions,
        final_inscriptions,
        grades,
    ):
        promoted = sum(1 for g in grades if g.status == Grade.StatusSubject.PROMOTED)
        regular = sum(1 for g in grades if g.status == Grade.StatusSubject.REGULAR)
        free = sum(1 for g in grades if g.status == Grade.StatusSubject.FREE)

        self.stdout.write("\n" + "=" * 55)
        self.stdout.write(self.style.SUCCESS(" DATABASE SEEDED SUCCESSFULLY"))
        self.stdout.write("=" * 55)
        self.stdout.write(f"\n  Faculties:                {len(faculties)}")
        self.stdout.write(f"  Careers:                  {len(careers)}")
        self.stdout.write(f"  Subjects:                 {len(subjects)}")
        self.stdout.write(f"  Administrators:           {len(admins)}")
        self.stdout.write(f"  Professors:               {len(professors)}")
        self.stdout.write(f"  Students:                 {len(students)}")
        self.stdout.write(f"  Final exams:              {len(finals)}")
        self.stdout.write(f"  Subject inscriptions:     {len(subject_inscriptions)}")
        self.stdout.write(f"  Final exam inscriptions:  {len(final_inscriptions)}")
        self.stdout.write(f"  Grades:                   {len(grades)}")
        self.stdout.write(
            f"    Promoted: {promoted}  |  Regular: {regular}  |  Free: {free}"
        )

        self.stdout.write(f"\n  Password for all users:   {DEFAULT_PASSWORD}")

        self.stdout.write(self.style.WARNING("\n  Administrators:"))
        for a in admins:
            self.stdout.write(f"    {a.user.username:<15} ({a.user.get_full_name()})")

        self.stdout.write(self.style.WARNING("\n  Professors:"))
        for p in professors:
            n_subj = p.subjects.count()
            self.stdout.write(
                f"    {p.user.username:<15} ({p.user.get_full_name()}) - {n_subj} subjects"
            )

        self.stdout.write(self.style.WARNING("\n  Students:"))
        for s in students:
            self.stdout.write(
                f"    {s.user.username:<15} ({s.user.get_full_name()}) - {s.career.name}"
            )

        self.stdout.write("\n" + "=" * 55 + "\n")
