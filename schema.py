import datetime

from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Record(Base):
    """
    Represents a single, simplified table holding essential information
    from Parlamint, Lens, and Google Scholar sources.
    """

    __tablename__ = "records"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    original_source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    original_source_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    record_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    publication_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )
    authors_speakers_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    source_venue_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    record_created_warehouse: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    record_last_updated_warehouse: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("records.record_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunking_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ChunkClassification(Base):
    __tablename__ = "chunk_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chunks.chunk_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_relevant: Mapped[bool] = mapped_column(Boolean, nullable=False)
    HLTP: Mapped[str | None] = mapped_column(String(200), nullable=True)
    second_level_TE: Mapped[str | None] = mapped_column(
        "2nd_level_TE",
        String(200),
        nullable=True,
    )
    third_level_TE: Mapped[str | None] = mapped_column(
        "3rd_level_TE",
        String(200),
        nullable=True,
    )

    relevant_text_spans: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=True, default=list
    )

    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)

    model: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


engine = create_engine(
    "postgresql+psycopg2://postgres:GoNKJWp64NkMr9UdgCnT@138.201.62.161:5432/cognitive_warfare"
)
metadata = Base.metadata
metadata.create_all(engine)