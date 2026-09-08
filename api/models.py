from sqlalchemy import Column, Integer, String, Float

from database import Base


class Medicao(Base):

    __tablename__ = "medicoes_esp32"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    timestamp = Column(
        String,
        nullable=False
    )

    temperatura = Column(
        Float,
        nullable=False
    )

    umidade = Column(
        Float,
        nullable=False
    )