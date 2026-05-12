from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db, get_tenant_id
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.StockEntry)
async def add_stock(
    stock: schemas.StockCreate, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    return crud.add_stock(db=db, tenant_id=tenant_id, stock=stock)

@router.get("/", response_model=List[schemas.StockEntry])
async def read_stocks(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    return crud.get_stocks(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/{stock_id}", response_model=schemas.StockEntry)
async def read_stock(
    stock_id: int, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    db_stock = crud.get_stock(db, tenant_id=tenant_id, stock_id=stock_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    return db_stock

@router.put("/{stock_id}", response_model=schemas.StockEntry)
async def update_stock(
    stock_id: int, 
    stock: schemas.StockUpdate, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    db_stock = crud.update_stock(db=db, tenant_id=tenant_id, stock_id=stock_id, stock=stock)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    return db_stock

@router.delete("/{stock_id}")
async def delete_stock(
    stock_id: int, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    success = crud.delete_stock(db=db, tenant_id=tenant_id, stock_id=stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock entry not found")
    return {"message": "Stock entry deleted successfully"}
