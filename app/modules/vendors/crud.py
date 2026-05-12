from sqlalchemy.orm import Session
from . import models, schemas

def get_vendors(db: Session, tenant_id: str, skip: int = 0, limit: int = 100):
    if not tenant_id or tenant_id == "default":
        return []
    return db.query(models.Vendor).filter(models.Vendor.tenant_id == tenant_id).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate, tenant_id: str):
    db_vendor = models.Vendor(**vendor.dict(), tenant_id=tenant_id)
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def update_vendor(db: Session, vendor_id: int, vendor: schemas.VendorCreate, tenant_id: str):
    db_vendor = db.query(models.Vendor).filter(
        models.Vendor.id == vendor_id,
        models.Vendor.tenant_id == tenant_id
    ).first()
    if db_vendor:
        for key, value in vendor.dict().items():
            setattr(db_vendor, key, value)
        db.commit()
        db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int, tenant_id: str):
    db_vendor = db.query(models.Vendor).filter(
        models.Vendor.id == vendor_id,
        models.Vendor.tenant_id == tenant_id
    ).first()
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
    return db_vendor
