import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# BANCO DE DADOS
#
# A URL do PostgreSQL NÃO deve ser colocada neste arquivo.
#
# No Render:
# 1. Entre no serviço da API
# 2. Vá em Environment
# 3. Crie a variável:
#
#    DATABASE_URL = URL INTERNA DO POSTGRES
#
# Como a API e o PostgreSQL estão no Render, usamos a
# INTERNAL DATABASE URL.
#
# A URL EXTERNA não será necessária para a API.
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")


# Conexão com PostgreSQL
engine = create_engine(DATABASE_URL)


# Criação das sessões
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