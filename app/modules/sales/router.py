from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Sale)
async def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    return crud.create_sale(db=db, sale=sale)

@router.get("/", response_model=List[schemas.Sale])
async def read_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sales(db, skip=skip, limit=limit)

@router.get("/{sale_id}", response_model=schemas.Sale)
async def read_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = crud.get_sale(db, sale_id=sale_id)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale

@router.put("/{sale_id}", response_model=schemas.Sale)
async def update_sale(sale_id: int, sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    db_sale = crud.update_sale(db=db, sale_id=sale_id, sale=sale)
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale

@router.delete("/{sale_id}")
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    crud.delete_sale(db=db, sale_id=sale_id)
    return {"message": "Sale deleted successfully"}
