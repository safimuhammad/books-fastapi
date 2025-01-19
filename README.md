
# Books FastAPI

Books FastAPI is a RESTful API built with Python’s FastAPI framework, designed to manage a collection of books. It provides endpoints to perform CRUD (Create, Read, Update, Delete) operations on book data.

## Features
- **Create**: Add new books to the collection.
- **Read**: Retrieve details of all books or a specific book by its ID.
- **Update**: Modify information of an existing book.
- **Delete**: Remove a book from the collection.

## Prerequisites
- **Python 3.8+**: Ensure that Python is installed on your system.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Uvicorn**: An ASGI server implementation, using uvloop and httptools.
- **SQLAlchemy**: A SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **PostgreSQL**: A powerful, open-source object-relational database system.

## Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/safimuhammad/books-fastapi.git
    cd books-fastapi
    ```

2. **Set Up a Virtual Environment (Optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scriptsctivate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the Database**:
    - Create a new database named `bookdb`.
    - Update the `DATABASE_URL` in `.env` with your Sqlite credentials.



## Running the Application
Start the Uvicorn server to run the FastAPI application:
```bash
uvicorn main:app --reload
```
The API will be accessible at `http://localhost:8000`.

## API Endpoints
- **Get All Books**:
    ```http
    GET /books/get_books?page=1&max_items=10
    ```

- **Get a Specific Book**:
    ```http
    GET /books/get_book/{book_id}
    ```

- **Create a New Book**:
    ```http
    POST /books/create_book
    ```
    **Request Body**:
    ```json
    {
      "title": "Book Title",
      "author": "Author Name",
      "published_year": 2025,
      "publisher": "Publisher Name",
      "description": "Book Description"
    }
    ```

- **Update an Existing Book**:
    ```http
    PUT /books/update_book/{book_id}
    ```
    **Request Body**:
    ```json
    {
      "title": "Updated Title",
      "author": "Updated Author",
      "published_year": 2025,
      "publisher": "Updated Publisher",
      "description": "Updated Description"
    }
    ```

- **Delete a Book**:
    ```http
    DELETE /books/delete_book/{book_id}
    ```

## Testing the API
You can use tools like [curl](https://curl.se/) or [Postman](https://www.postman.com/) to test the API endpoints.

**Example**: Create a new book using `curl`:
```bash
curl -X POST "http://localhost:8000/books/create_book" -H "accept: application/json" -H "Content-Type: application/json" -d '{"title":"The Lord of the Rings", "author": "J.R.R. Tolkien", "published_year": 1954, "publisher": "George Allen & Unwin", "description": "An epic fantasy novel."}'
```

## License
This project is licensed under the terms of the MIT license.

## Acknowledgments
This project is inspired by various FastAPI tutorials and examples available in the community.
