from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db, get_tenant_id
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Book)
async def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return crud.create_book(db=db, tenant_id=tenant_id, book=book)

@router.get("/", response_model=List[schemas.Book])
async def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    print(f"DEBUG: Reading books for tenant_id: {tenant_id}")
    return crud.get_books(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/{book_id}", response_model=schemas.Book)
async def read_book(book_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db_book = crud.get_book(db, tenant_id=tenant_id, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=schemas.Book)
async def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db_book = crud.update_book(db=db, tenant_id=tenant_id, book_id=book_id, book=book)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    crud.delete_book(db=db, tenant_id=tenant_id, book_id=book_id)
    return {"message": "Book deleted successfully"}
