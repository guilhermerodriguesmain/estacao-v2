from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Medicao
from schemas import Leitura


# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def root():
    return {
        "mensagem": "API da estação meteorológica funcionando"
    }


@app.get("/medicoes")
def listar_medicoes(db: Session = Depends(get_db)):

    medicoes = (
        db.query(Medicao)
        .order_by(Medicao.id)
        .all()
    )

    return medicoes


@app.get("/medicoes/{id_medicao}")
def buscar_medicao(
    id_medicao: int,
    db: Session = Depends(get_db)
):

    medicao = (
        db.query(Medicao)
        .filter(Medicao.id == id_medicao)
        .first()
    )

    if medicao is None:
        raise HTTPException(
            status_code=404,
            detail="Leitura não encontrada"
        )

    return medicao


@app.post("/medicoes")
def receber_leitura(
    leitura: Leitura,
    db: Session = Depends(get_db)
):

    medicao = Medicao(
        timestamp=leitura.timestamp,
        temperatura=leitura.temperatura,
        umidade=leitura.umidade
    )

    db.add(medicao)
    db.commit()
    db.refresh(medicao)

    return {
        "mensagem": "Leitura recebida e armazenada com sucesso",
        "id": medicao.id,
        "dados": leitura
    }


@app.put("/medicoes/{id_medicao}")
def atualizar_leitura(
    id_medicao: int,
    leitura: Leitura,
    db: Session = Depends(get_db)
):

    medicao = (
        db.query(Medicao)
        .filter(Medicao.id == id_medicao)
        .first()
    )

    if medicao is None:
        raise HTTPException(
            status_code=404,
            detail="Leitura não encontrada"
        )

    medicao.timestamp = leitura.timestamp
    medicao.temperatura = leitura.temperatura
    medicao.umidade = leitura.umidade

    db.commit()
    db.refresh(medicao)

    return {
        "mensagem": "Leitura atualizada com sucesso",
        "id": medicao.id,
        "dados": leitura
    }


@app.delete("/medicoes/{id_medicao}")
def excluir_leitura(
    id_medicao: int,
    db: Session = Depends(get_db)
):

    medicao = (
        db.query(Medicao)
        .filter(Medicao.id == id_medicao)
        .first()
    )

    if medicao is None:
        raise HTTPException(
            status_code=404,
            detail="Leitura não encontrada"
        )

    db.delete(medicao)
    db.commit()

    return {
        "mensagem": "Leitura excluída com sucesso",
        "id": id_medicao
    }