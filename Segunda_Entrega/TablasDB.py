from sqlalchemy import Column, Integer, String, Float
from DB import Base

class AlumnoDB(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    matricula = Column(String(20), unique=True, index=True, nullable=False)
    promedio = Column(Float, nullable=False)
    password = Column(String(255), nullable=False)
    fotoPerfilUrl = Column(String(500), nullable=True)

class ProfesorDB(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numeroEmpleado = Column(Integer, unique=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    horasClase = Column(Integer, nullable=False)