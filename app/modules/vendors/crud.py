from sqlalchemy.orm import Session
from . import models, schemas

def get_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vendor).offset(skip).limit(limit).all()

def create_vendor(db: Session, vendor: schemas.VendorCreate):
    db_vendor = models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def update_vendor(db: Session, vendor_id: int, vendor: schemas.VendorCreate):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if db_vendor:
        for key, value in vendor.dict().items():
            setattr(db_vendor, key, value)
        db.commit()
        db.refresh(db_vendor)
    return db_vendor

def delete_vendor(db: Session, vendor_id: int):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if db_vendor:
        db.delete(db_vendor)
        db.commit()
    return db_vendor
