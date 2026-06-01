from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db, get_tenant_id
from . import crud, schemas

router = APIRouter()

# ==================== CLASSES ====================

@router.get("/classes", response_model=List[schemas.AcademicClass])
def get_classes(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return crud.get_classes(db, tenant_id=tenant_id)

@router.post("/classes", response_model=schemas.AcademicClass)
def create_class(class_data: schemas.AcademicClassCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return crud.create_class(db, class_data=class_data, tenant_id=tenant_id)

@router.put("/classes/{class_id}", response_model=schemas.AcademicClass)
def update_class(class_id: int, class_data: schemas.AcademicClassUpdate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db_class = crud.update_class(db, class_id=class_id, class_data=class_data, tenant_id=tenant_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.delete("/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    success = crud.delete_class(db, class_id=class_id, tenant_id=tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}

# ==================== SECTIONS ====================

@router.get("/sections", response_model=List[schemas.AcademicSection])
def get_sections(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return crud.get_sections(db, tenant_id=tenant_id)

@router.post("/sections", response_model=schemas.AcademicSection)
def create_section(section_data: schemas.AcademicSectionCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return crud.create_section(db, section_data=section_data, tenant_id=tenant_id)

@router.put("/sections/{section_id}", response_model=schemas.AcademicSection)
def update_section(section_id: int, section_data: schemas.AcademicSectionUpdate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db_section = crud.update_section(db, section_id=section_id, section_data=section_data, tenant_id=tenant_id)
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

@router.delete("/sections/{section_id}")
def delete_section(section_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    success = crud.delete_section(db, section_id=section_id, tenant_id=tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"message": "Section deleted successfully"}
