from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ...core.database import Base

class AcademicClass(Base):
    __tablename__ = "academic_classes"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    numeric = Column(Integer, nullable=True)
    teacher_id = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)
    academic_status = Column(String(50), default="Active")

    sections = relationship("AcademicSection", back_populates="academic_class", cascade="all, delete-orphan")

class AcademicSection(Base):
    __tablename__ = "academic_sections"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey("academic_classes.id"), nullable=False)
    category = Column(String(100), nullable=True)
    capacity = Column(Integer, nullable=True)
    teacher_id = Column(Integer, nullable=True)
    note = Column(String(255), nullable=True)
    academic_status = Column(String(50), default="Active")

    academic_class = relationship("AcademicClass", back_populates="sections")
