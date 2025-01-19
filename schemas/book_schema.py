from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import date


class BookBase(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    genre: Optional[str] = None
    published_date: date = None

    class Config:
        extra = "forbid"

class BookCreate(BookBase):
    @validator('title', 'author', 'summary', 'genre', 'published_date')
    def validate_required_fields(cls, value, field):
        valid_fields = {"title", "author", "summary", "genre", "published_date"}
        if field.name not in valid_fields:
            raise ValueError(
                f"Invalid field name: {field.name}. "
                f"Valid fields are: {', '.join(valid_fields)}"
            )
        return value

class BookOut(BookBase):
    id: int = Field(..., example=1, description="The unique identifier of the book")
    title: str = Field(..., example="The Great Gatsby", description="The title of the book")
    author: Optional[str] = Field(None, example="F. Scott Fitzgerald", description="The author of the book")
    summary: Optional[str] = Field(None, example="A story of love and loss", description="A brief summary of the book")
    genre: Optional[str] = Field(None, example="Fiction", description="The genre of the book")
    published_date: Optional[date] = Field(..., example="1925-04-10", description="The date the book was published")
    
    class Config:
        orm_mode = True

# NEW: Paginated response schema
class PaginatedBooks(BaseModel):
    page: int = Field(..., example=1, description="The current page number")
    max_items: int = Field(..., example=10, description="The maximum number of items per page")
    total_pages: int = Field(..., example=10, description="The total number of pages")  
    total_count: int = Field(..., example=100, description="The total number of books")
    data: List[BookOut] = Field(..., example=[BookOut(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", summary="A story of love and loss", genre="Fiction", published_date=date(1925, 4, 10))], description="The list of books on the current page")

    class Config:
        orm_mode = True