

import re

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/user/", response_model_exclude_unset=True, tags=["User"], status_code=200)
def predict_class_sizes() -> str:

    return ":)"
