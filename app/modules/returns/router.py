from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from . import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ReturnEntry)
async def create_return(return_data: schemas.ReturnCreate, db: Session = Depends(get_db)):
    return crud.create_return(db=db, return_data=return_data)

@router.get("/", response_model=List[schemas.ReturnEntry])
async def read_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_returns(db, skip=skip, limit=limit)

@router.get("/{return_id}", response_model=schemas.ReturnEntry)
async def read_return(return_id: int, db: Session = Depends(get_db)):
    db_return = crud.get_return(db, return_id=return_id)
    if not db_return:
        raise HTTPException(status_code=404, detail="Return entry not found")
    return db_return

@router.put("/{return_id}", response_model=schemas.ReturnEntry)
async def update_return(return_id: int, return_data: schemas.ReturnUpdate, db: Session = Depends(get_db)):
    db_return = crud.update_return(db=db, return_id=return_id, return_data=return_data)
    if not db_return:
        raise HTTPException(status_code=404, detail="Return entry not found")
    return db_return

@router.delete("/{return_id}")
async def delete_return(return_id: int, db: Session = Depends(get_db)):
    success = crud.delete_return(db=db, return_id=return_id)
    if not success:
        raise HTTPException(status_code=404, detail="Return entry not found")
    return {"message": "Return entry deleted successfully"}
