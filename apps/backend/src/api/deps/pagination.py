from fastapi import Query, HTTPException
from math import ceil
from typing import List, Optional, Type, Dict

from pydantic import BaseModel
from ...core.constants import Constants


async def pagination_params(
    page: Optional[int] = Query(1, ge=1, description='Page number (1-indexed)'),
    per_page: Optional[int] = Query(
        Constants.DEFAULT_PAGE_SIZE, ge=1, le=Constants.MAX_PAGE_SIZE, description='Items per page'
    ),
):
    '''
    Common dependency to extract pagination parameters from query string.
    Example: ?page=2&per_page=20
    '''
    return {'page': page, 'per_page': per_page}


def paginate_query(query, pagination: dict):
    '''
    Apply pagination to an SQLAlchemy query using page & per_page.
    '''
    page = pagination.get('page', 1)
    per_page = pagination.get('per_page', Constants.DEFAULT_PAGE_SIZE)

    if per_page > Constants.MAX_PAGE_SIZE:
        raise HTTPException(status_code=400, detail=f'per_page cannot exceed {Constants.MAX_PAGE_SIZE}')

    offset = (page - 1) * per_page
    return query.limit(per_page).offset(offset)


def build_paginated_response(items: list, total: int, page: int, per_page: int):
    '''
    Build a consistent paginated response payload with metadata.
    '''
    total_pages = ceil(total / per_page) if total > 0 else 1

    return {
        'meta': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
        },
        'results': items,
    }

def get_paginated_response_model(item_model: Type[BaseModel]) -> Type[BaseModel]:
    class PaginatedResponse(BaseModel):
        meta: Dict[str, int]
        results: List[item_model]

    return PaginatedResponse
