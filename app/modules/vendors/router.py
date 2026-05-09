from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Vendor)
async def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    return crud.create_vendor(db=db, vendor=vendor)

@router.get("/", response_model=List[schemas.Vendor])
async def read_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vendors = crud.get_vendors(db, skip=skip, limit=limit)
    return vendors

@router.put("/{vendor_id}", response_model=schemas.Vendor)
async def update_vendor(vendor_id: int, vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = crud.update_vendor(db=db, vendor_id=vendor_id, vendor=vendor)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor

@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    crud.delete_vendor(db=db, vendor_id=vendor_id)
    return {"message": "Vendor deleted successfully"}
