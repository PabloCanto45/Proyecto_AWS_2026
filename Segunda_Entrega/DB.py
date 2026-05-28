from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Formato: mysql+pymysql://USUARIO:PASSWORD@ENDPOINT_RDS:3306/NOMBRE_BD
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:AvenidaAlcorta@siceidb.cncta1grkkkn.us-east-1.rds.amazonaws.com:3306/siceidb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Esta función inyectará la sesión de la base de datos en tus endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()