from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated
from sqlalchemy.orm import Session
import TablasDB
from DB import engine, get_db
from fastapi import UploadFile, File
import GestorFotos
import GestorDynamoDB
import GestorSNS
from typing import cast


TablasDB.Base.metadata.create_all(bind=engine)
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
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    matricula : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    promedio : float = Field(gt=0.0, description="El promedio debe ser mayor a 0")
    password: str

class Respuesta_Alumno(BaseModel):
    id : int = Field(gt=0, description="El id debe se r mayor a 0")
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    matricula : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    promedio : float = Field(gt=0.0, description="El promedio debe ser mayor a 0")
    fotoPerfilUrl: str | None = None
    class Config:
        from_attributes = True

class Profesor(BaseModel):
    numeroEmpleado : int = Field(gt=0, description="El número de empleado debe ser mayor a 0")
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    horasClase : int = Field(gt=0, description="Las horas de clase deben ser mayor a 0")

class Respuesta_Profesor(BaseModel):
    id : int = Field(gt=0, description="El id debe ser mayor a 0")
    numeroEmpleado : int = Field(gt=0, description="El número de empleado debe ser mayor a 0")
    nombres : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    apellidos: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    horasClase : int = Field(gt=0, description="Las horas de clase deben ser mayor a 0")
    class Config:
        from_attributes = True

class SessionString(BaseModel):
    sessionString: str

class LoginRequest(BaseModel):
	password: str

# ENDPOINTS ALUMNOS
@app.get("/alumnos", response_model=list[Respuesta_Alumno])
def obtenerAlumnos(db: Session = Depends(get_db)):
    return db.query(TablasDB.AlumnoDB).all()

@app.get("/alumnos/{id}", response_model=Respuesta_Alumno)
def buscarAlumno(id : int, db: Session = Depends(get_db)):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno 

@app.post("/alumnos", response_model=Respuesta_Alumno, status_code=status.HTTP_201_CREATED)
def agregarAlumno(alumno : Alumno, db: Session = Depends(get_db)):
    nuevoAlumno = TablasDB.AlumnoDB(
        nombres = alumno.nombres,
        apellidos = alumno.apellidos,
        matricula = alumno.matricula,
        promedio = alumno.promedio,
        password = alumno.password
    )

    db.add(nuevoAlumno)
    db.commit()
    db.refresh(nuevoAlumno)
    
    return nuevoAlumno

@app.post("/alumnos/{id}/email")
def enviar_correo_alumno(id: int, db: Session = Depends(get_db)):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    GestorSNS.notificar_alumno(
        nombres=str(alumno.nombres),
        apellidos=str(alumno.apellidos),
        promedio=cast(float, alumno.promedio)
    )
    return {"mensaje": "Notificación enviada"}

@app.post("/alumnos/{id}/fotoPerfil", response_model=Respuesta_Alumno)
def subir_foto_alumno(id: int, foto: UploadFile = File(...), db: Session = Depends(get_db)):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    contenido = foto.file.read()
    llave_s3 = GestorFotos.subir_foto_perfil(contenido, foto.filename) #type: ignore
    
    url_completa = GestorFotos.generar_url_publica(llave_s3) #type: ignore
    
    alumno.fotoPerfilUrl = url_completa #type: ignore
    db.commit()
    db.refresh(alumno)
    
    return alumno

@app.put("/alumnos/{id}", response_model=Respuesta_Alumno)
def actualizarAlumno(id : int, alumnoActualizado : Alumno, db: Session = Depends(get_db) ):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    alumno.nombres = alumnoActualizado.nombres #type: ignore
    alumno.apellidos = alumnoActualizado.apellidos #type: ignore
    alumno.matricula = alumnoActualizado.matricula #type: ignore
    alumno.promedio = alumnoActualizado.promedio #type: ignore
    alumno.password = alumnoActualizado.password #type: ignore

    db.commit()
    db.refresh(alumno)
    return alumno

@app.delete("/alumnos/{id}")
def borrarAlumno(id : int, db: Session = Depends(get_db)):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    db.delete(alumno)
    db.commit()
    return {"mensaje": "alumno eliminado exitosamente"}

@app.post("/alumnos/{id}/session/login", status_code=status.HTTP_200_OK)
def login_alumno(id: int, credenciales: LoginRequest, db: Session = Depends(get_db)):
    alumno = db.query(TablasDB.AlumnoDB).filter(TablasDB.AlumnoDB.id == id).first()
    if not alumno or str(alumno.password) != credenciales.password:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    
    nueva_sesion = GestorDynamoDB.crear_sesion(alumno_id=id)
    
    return \
        {
        "id": nueva_sesion["id"],
        "fecha": nueva_sesion["fecha"],
        "alumnoId": nueva_sesion["alumnoId"],
        "active": nueva_sesion["active"],
        "sessionString": nueva_sesion["sessionString"]
        }

@app.post("/alumnos/{id}/session/verify")
def verificar_sesion(id: int, cuerpo: SessionString):
    sesion = GestorDynamoDB.buscar_sesion_por_string(cuerpo.sessionString)
    
    if sesion and sesion.get('active') is True and sesion.get('alumnoId') == id:
        return \
            {
            "mensaje": "Sesión válida y activa"
            }
            
    raise HTTPException(status_code=400, detail="Sesión no válida o inactiva")

@app.post("/alumnos/{id}/session/logout")
def cerrar_sesion(id: int, cuerpo: SessionString):
    sesion = GestorDynamoDB.buscar_sesion_por_string(cuerpo.sessionString)
    if not sesion or sesion.get('alumnoId') != id:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    GestorDynamoDB.desactivar_sesion_por_id(sesion['id'])
    
    return \
        {
        "mensaje": "Sesión cerrada exitosamente"
        }

# ENDPOINTS PROFESORES
@app.get("/profesores", response_model=list[Respuesta_Profesor])
def obtenerProfesor(db: Session = Depends(get_db)):
    return db.query(TablasDB.ProfesorDB).all()

@app.get("/profesores/{id}", response_model=Respuesta_Profesor)
def buscarProfesor(id : int, db: Session = Depends(get_db)):
    profesor = db.query(TablasDB.ProfesorDB).filter(TablasDB.ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@app.post("/profesores", response_model=Respuesta_Profesor, status_code=status.HTTP_201_CREATED)
def agregarProfesor(profesor : Profesor, db: Session = Depends(get_db)):
    nuevoProfesor = TablasDB.ProfesorDB(
        numeroEmpleado=profesor.numeroEmpleado,
        nombres=profesor.nombres,
        apellidos=profesor.apellidos,
        horasClase=profesor.horasClase
    )

    db.add(nuevoProfesor)
    db.commit()
    db.refresh(nuevoProfesor)

    return nuevoProfesor

@app.put("/profesores/{id}")
def editarProfesor(id : int, profesorActualizado : Profesor, db: Session = Depends(get_db)):
    profesor = db.query(TablasDB.ProfesorDB).filter(TablasDB.ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    profesor.numeroEmpleado = profesorActualizado.numeroEmpleado #type: ignore
    profesor.nombres = profesorActualizado.nombres #type: ignore
    profesor.apellidos = profesorActualizado.apellidos #type: ignore
    profesor.horasClase = profesorActualizado.horasClase #type: ignore
    
    db.commit()
    db.refresh(profesor)
    return profesor

@app.delete("/profesores/{id}")
def borrarProfesor(id : int, db: Session = Depends(get_db)):
    profesor = db.query(TablasDB.ProfesorDB).filter(TablasDB.ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    db.delete(profesor)
    db.commit()
    return {"mensaje": "Profesor eliminado exitosamente"}
