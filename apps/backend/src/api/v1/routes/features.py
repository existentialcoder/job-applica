from fastapi import APIRouter
from ....core.config import get_feature_flags

router = APIRouter()


@router.get('/features')
def list_features() -> dict[str, bool]:
    return get_feature_flags()
