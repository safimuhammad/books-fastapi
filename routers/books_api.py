from schemas.book_schema import BookCreate, BookOut, PaginatedBooks
from models.user import User
from models.book import Book
from fastapi import APIRouter, Depends,Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from deps import get_db
from deps import get_db
from main import get_current_user
import math
from fastapi import HTTPException, status
import asyncio
router = APIRouter(tags=["Books"])


@router.get("/get_books", response_model=PaginatedBooks)
async def get_books(
    page: int = 1,
    max_items: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get books in a paginated form.

    - page: The current page number (default=1)
    - max_items: Max items per page (default=10)
    """
    try:
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be greater than 0",
            )
        if max_items < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max items must be greater than 0",
            )

        total_count = db.query(Book).count()
        total_pages = math.ceil(total_count / max_items) if total_count else 1

        if page > total_pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page} does not exist. Total pages: {total_pages}",
            )

        skip = (page - 1) * max_items
        books = db.query(Book).offset(skip).limit(max_items).all()

        return PaginatedBooks(
            page=page,
            max_items=max_items,
            total_pages=total_pages,
            total_count=total_count,
            data=books,
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving books: {str(e)}",
        )


@router.get("/get_book/{book_id}", response_model=BookOut)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a book by its ID.
    - book_id: The ID of the book to retrieve.
    """
    try:
        if book_id < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book ID must be greater than 0",
            )

        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )
        return book

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving book: {str(e)}",
        )


@router.post("/create_book", response_model=BookOut)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new book.
    
    - book: Book data containing title, author, summary, genre and published_date
    """
    try:
        new_book = Book(**book.dict())
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return new_book

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating book: {str(e)}",
        )


@router.put("/update_book/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int,
    book_update: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a book by its ID.
    
    - book_id: ID of the book to update
    - book_update: Updated book data containing title, author, summary, genre and published_date
    """
    try:
        existing_book = db.query(Book).filter(Book.id == book_id).first()
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found")

        existing_book.title = book_update.title or existing_book.title
        existing_book.author = book_update.author or existing_book.author
        existing_book.summary = book_update.summary or existing_book.summary
        existing_book.genre = book_update.genre or existing_book.genre
        existing_book.published_date = (
            book_update.published_date or existing_book.published_date
        )

        db.commit()
        db.refresh(existing_book)
        return existing_book
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating book: {str(e)}",
        )


@router.delete("/delete_book/{book_id}", response_model=BookOut)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a book by its ID.
    
    - book_id: ID of the book to delete
    """
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book_id < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book ID must be greater than 0",
            )
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        db.delete(book)
        db.commit()
        return book
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting book: {str(e)}",
        )



async def book_event_generator(db: Session = Depends(get_db)):
    """
    This generator function sends the total count of books to the client every 5 seconds.
    """
    counter = 1
    try:
        while True:
            total_count = db.query(Book).count()
            yield f"data: message_no: {counter} ,total_count = {total_count}\n\n"
            counter += 1
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        return
    
@router.get("/updates")
async def get_book_updates(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    SSE endpoint for real-time book updates.
    The response content type is `text/event-stream`.
    """
    return StreamingResponse(
        book_event_generator(db),
        media_type="text/event-stream"
    )