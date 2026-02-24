from fastapi import APIRouter
from app.core.settings import load_config, save_config

router = APIRouter(prefix="/api/config", tags=["config"])

@router.get("")
def get_config():
    return load_config()

@router.post("")
def update_config(data: dict):
    save_config(data)
    return {"status": "ok"}
