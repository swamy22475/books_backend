from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db, get_tenant_id
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Vendor)
async def create_vendor(
    vendor: schemas.VendorCreate, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    return crud.create_vendor(db=db, vendor=vendor, tenant_id=tenant_id)

@router.get("/", response_model=List[schemas.Vendor])
async def read_vendors(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    vendors = crud.get_vendors(db, tenant_id=tenant_id, skip=skip, limit=limit)
    return vendors

@router.put("/{vendor_id}", response_model=schemas.Vendor)
async def update_vendor(
    vendor_id: int, 
    vendor: schemas.VendorCreate, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    db_vendor = crud.update_vendor(db=db, vendor_id=vendor_id, vendor=vendor, tenant_id=tenant_id)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor

@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    crud.delete_vendor(db=db, vendor_id=vendor_id, tenant_id=tenant_id)
    return {"message": "Vendor deleted successfully"}
