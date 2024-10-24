from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_experiments():
    return {"message": "Experiments"}
