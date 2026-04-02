from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

app = FastAPI()
@app.exception_handler(RequestValidationError)
async def manejadorErroresValidacion(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "mensaje": "Error en la validación de los datos enviados (Bad Request)",
            "detalles": exc.errors()
        }
    )

class Alumno(BaseModel):
    id : int = Field(gt=0, description="El id debe ser mayor a 0")
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    matricula : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    promedio : float = Field(gt=0.0, description="El promedio debe ser mayor a 0")

class Profesor(BaseModel):
    id : int = Field(gt=0, description="El id debe ser mayor a 0")
    numeroEmpleado : int = Field(gt=0, description="El número de empleado debe ser mayor a 0")
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    horasClase : int = Field(gt=0, description="Las horas de clase deben ser mayor a 0")

listaAlumnos = []
listaProfesores = []

@app.get("/alumnos")
def obtenerAlumnos():
    return listaAlumnos

@app.get("/alumnos/{id}")
def buscarAlumno(id : int):
    for alumnoIndice in listaAlumnos:
        if(alumnoIndice.id == id):
            return alumnoIndice
        
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.post("/alumnos", status_code=status.HTTP_201_CREATED)
def agregarAlumno(alumno : Alumno):
    listaAlumnos.append(alumno)
    return alumno

@app.put("/alumnos/{id}")
def actualizarAlumno(id : int, alumnoActualizado : Alumno):
    for indice, alumnoIndice in enumerate(listaAlumnos):
        if(alumnoIndice.id == id):
            listaAlumnos[indice] = alumnoActualizado
            return alumnoActualizado
        
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.delete("/alumnos/{id}")
def borrarAlumno(id : int):
    for indice, alumnoIndice in enumerate(listaAlumnos):
        if(alumnoIndice.id == id):
            listaAlumnos.pop(indice)
            return {"mensaje": "alumno eliminado exitosamente"}
        
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.get("/profesores")
def obtenerProfesor():
    return listaProfesores

@app.get("/profesores/{id}")
def buscarProfesor(id : int):
    for profesorIndice in listaProfesores:
        if(profesorIndice.id == id):
            return profesorIndice
        
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.post("/profesores", status_code=status.HTTP_201_CREATED)
def agregarProfesor(profesor : Profesor):
    listaProfesores.append(profesor)
    return profesor

@app.put("/profesores/{id}")
def editarProfesor(id : int, profesorActualizado : Profesor):
    for indice, profesorIndice in enumerate(listaProfesores):
        if(profesorIndice.id == id):
            listaProfesores[indice] = profesorActualizado
            return profesorIndice
        
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.delete("/profesores/{id}")
def borrarProfesor(id : int):
    for indice, profesorIndice in enumerate(listaProfesores):
        if(profesorIndice.id == id):
            listaProfesores.pop(indice)
            return {"mensaje": "Profesor eliminado exitosamente"}
        
    raise HTTPException(status_code=404, detail="Profesor no encontrado")