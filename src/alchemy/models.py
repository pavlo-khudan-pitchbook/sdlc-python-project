from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class ClassifierModelRegistry(Base):
    __tablename__ = "classifier_model_registry"
    __table_args__ = (
        UniqueConstraint(
            "model_name", "model_version", name="classifier_model_registry_uniq"
        ),
        {"schema": "retraining"},
    )

    model_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    model_name = Column(Text, nullable=False)
    model_version = Column(Text, nullable=False)
    training_job_name = Column(Text, nullable=False)
    artifact_s3_uri = Column(Text, nullable=False)
    training_data_s3_uri = Column(Text, nullable=False)
    metrics = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    is_champion = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    promoted_at = Column(TIMESTAMP(timezone=True))
