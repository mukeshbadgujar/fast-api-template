from typing import Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


class Page(BaseModel, Generic[T]):
    """Paginated response."""
    
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "Page[T]":
        """Create a Page from items, total count, and pagination parameters."""
        pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=pages,
        ) 