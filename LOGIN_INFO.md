# 🔐 Credenciales de Acceso al Sistema

## 🌐 URL de Acceso

**http://localhost:8000/login/**

---

## 👥 Usuarios de Prueba

### 1. 👨‍💼 ADMINISTRADOR

- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Rol:** Administrador del Sistema
- **Dashboard:** http://localhost:8000/admin/dashboard/
- **Permisos:**
  - Gestión de usuarios (crear, editar, eliminar)
  - Gestión de facultades y carreras
  - Gestión de materias y finales
  - Asignación de profesores

### 2. 👨‍🏫 PROFESOR

- **Usuario:** `profesor1`
- **Contraseña:** `profesor123`
- **Rol:** Profesor
- **Nombre:** Carlos Rodríguez
- **Dashboard:** http://localhost:8000/professor/dashboard/
- **Permisos:**
  - Ver materias asignadas
  - Gestionar calificaciones de estudiantes
  - Ver inscripciones a finales

### 3. 👨‍🎓 ESTUDIANTE

- **Usuario:** `estudiante1`
- **Contraseña:** `estudiante123`
- **Rol:** Estudiante
- **Nombre:** Ana Martínez
- **Carrera:** Ingeniería en Sistemas de Información
- **Dashboard:** http://localhost:8000/student/dashboard/
- **Permisos:**
  - Inscribirse a materias
  - Inscribirse a finales
  - Ver calificaciones

---

## 📚 Datos de Prueba Creados

### Facultad

- **Código:** FI
- **Nombre:** Facultad de Ingeniería
- **Decano:** Dr. Juan Pérez

### Carrera

- **Código:** ISI
- **Nombre:** Ingeniería en Sistemas de Información
- **Duración:** 5 años

### Materias Disponibles

1. **Álgebra (ALG)** - Año 1, Primer Cuatrimestre
2. **Programación I (PRG)** - Año 1, Primer Cuatrimestre
3. **Bases de Datos (BDD)** - Año 2, Segundo Cuatrimestre

### Final Programado

- **Materia:** Álgebra
- **Fecha:** 30 días desde hoy
- **Llamado:** 1
- **Ubicación:** Aula 101

---

## 🚀 Cómo Probar el Sistema

### Como Administrador:

1. Ir a http://localhost:8000/login/
2. Ingresar: `admin` / `admin123`
3. Explorar el dashboard de administración
4. Crear nuevos usuarios, facultades, carreras, etc.
5. Asignar profesores a materias

### Como Profesor:

1. Ir a http://localhost:8000/login/
2. Ingresar: `profesor1` / `profesor123`
3. Ver dashboard de profesor
4. Gestionar calificaciones (cuando haya estudiantes inscriptos)

### Como Estudiante:

1. Ir a http://localhost:8000/login/
2. Ingresar: `estudiante1` / `estudiante123`
3. Ver materias disponibles de tu carrera
4. Inscribirte a materias
5. Ver tus calificaciones

---

## 🔧 Comandos Útiles

```bash
# Ver logs del sistema
docker compose logs -f backend

# Acceder a la shell de Django
docker compose exec backend python manage.py shell

# Ver estado de contenedores
docker compose ps

# Reiniciar el backend
docker compose restart backend

# Ver endpoint de salud
curl http://localhost:8000/health/
```

---

## 📊 Flujo de Prueba Completo

1. **Login como Admin** → Crear una nueva materia → Asignar profesor
2. **Login como Estudiante** → Inscribirse a la materia
3. **Login como Profesor** → Poner calificaciones al estudiante
4. **Login como Estudiante** → Ver las calificaciones

---

## ⚠️ Notas Importantes

- Estos son datos de **prueba** para desarrollo
- En producción, cambia todas las contraseñas
- El usuario `admin` tiene acceso total al sistema
- Para crear más usuarios, usa el dashboard de administrador

---

## 🆘 Solución de Problemas

**Si no puedes acceder:**

```bash
# Verificar que los contenedores estén corriendo
docker compose ps

# Si no están corriendo, iniciarlos
docker compose up -d

# Verificar logs
docker compose logs backend
```

**Si olvidaste la contraseña:**

```bash
# Resetear contraseña del admin
docker compose exec backend python manage.py changepassword admin
```

---

**Sistema listo para usar! 🎉**
