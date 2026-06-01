from sqlalchemy.orm import Session
from . import models, schemas

# ==================== CLASSES ====================

def get_classes(db: Session, tenant_id: str):
    return db.query(models.AcademicClass).filter(models.AcademicClass.tenant_id == tenant_id).all()

def create_class(db: Session, class_data: schemas.AcademicClassCreate, tenant_id: str):
    data = class_data.dict(by_alias=False)
    data = {k: (None if v == "" else v) for k, v in data.items()}
    db_class = models.AcademicClass(**data, tenant_id=tenant_id)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(db: Session, class_id: int, class_data: schemas.AcademicClassUpdate, tenant_id: str):
    db_class = db.query(models.AcademicClass).filter(
        models.AcademicClass.id == class_id,
        models.AcademicClass.tenant_id == tenant_id
    ).first()
    if db_class:
        data = class_data.dict(exclude_unset=True, by_alias=False)
        for key, value in data.items():
            setattr(db_class, key, None if value == "" else value)
        db.commit()
        db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int, tenant_id: str):
    db_class = db.query(models.AcademicClass).filter(
        models.AcademicClass.id == class_id,
        models.AcademicClass.tenant_id == tenant_id
    ).first()
    if db_class:
        db.delete(db_class)
        db.commit()
        return True
    return False

# ==================== SECTIONS ====================

def get_sections(db: Session, tenant_id: str):
    return db.query(models.AcademicSection).filter(models.AcademicSection.tenant_id == tenant_id).all()

def create_section(db: Session, section_data: schemas.AcademicSectionCreate, tenant_id: str):
    data = section_data.dict(by_alias=False)
    data = {k: (None if v == "" else v) for k, v in data.items()}
    db_section = models.AcademicSection(**data, tenant_id=tenant_id)
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def update_section(db: Session, section_id: int, section_data: schemas.AcademicSectionUpdate, tenant_id: str):
    db_section = db.query(models.AcademicSection).filter(
        models.AcademicSection.id == section_id,
        models.AcademicSection.tenant_id == tenant_id
    ).first()
    if db_section:
        data = section_data.dict(exclude_unset=True, by_alias=False)
        for key, value in data.items():
            setattr(db_section, key, None if value == "" else value)
        db.commit()
        db.refresh(db_section)
    return db_section

def delete_section(db: Session, section_id: int, tenant_id: str):
    db_section = db.query(models.AcademicSection).filter(
        models.AcademicSection.id == section_id,
        models.AcademicSection.tenant_id == tenant_id
    ).first()
    if db_section:
        db.delete(db_section)
        db.commit()
        return True
    return False
