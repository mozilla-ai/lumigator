from uuid import UUID

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.api.deps import DBSessionDep
from app.crud import user as crud
from app.schemas.user import ListUsers, UserCreate, UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(db: DBSessionDep, request: UserCreate):
    existing_user = await crud.get_user_by_name(db, name=request.name)
    if existing_user is not None:
        raise HTTPException(status_code=409, detail=f"User with name '{request.name}' exists.")
    user = await crud.create_user(db, name=request.name)
    return user


@router.get("/{id}", response_model=UserSchema)
async def get_user(db: DBSessionDep, id: UUID):
    record = await crud.get_user_by_id(db, id=id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"User '{id}' not found.")
    return record


@router.get("/", response_model=ListUsers)
async def list_users(db: DBSessionDep, skip: int = 0, limit: int = 100):
    users = await crud.get_users(db, skip=skip, limit=limit)
    logger.info(f"Users: {users}")
    count = await crud.count_users(db)
    return ListUsers(users=users, count=count)
