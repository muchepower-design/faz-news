from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models._base import Base
import uuid

class BulkImportLog(Base):
    __tablename__ = "bulk_import_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String)
    file_name = Column(String)
    rows_imported = Column(Integer)
    errors = Column(Text, nullable=True)
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())

    importer = relationship("User")