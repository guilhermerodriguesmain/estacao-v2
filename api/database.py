import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# URL interna do PostgreSQL configurada nas Environment Variables
# do serviço da API no Render.
DATABASE_URL = os.getenv("DATABASE_URL")


# Usa o driver psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )


# Conexão com PostgreSQL
engine = create_engine(DATABASE_URL)


# Sessões do banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Classe base dos modelos
Base = declarative_base()


# Dependência usada pela API
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()