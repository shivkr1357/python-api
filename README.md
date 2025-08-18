# PDF Unlock API

A simple and lightweight Python API built with FastAPI for unlocking and locking password-protected PDF files.

## Features

- **PDF Unlocking**: Automatically unlock password-protected PDF files (no password required)
- **PDF Locking**: Password-protect PDF files
- **File Download**: Download unlocked/locked PDF files
- **File Management**: Delete PDF files
- **FastAPI**: Modern, fast web framework for building APIs
- **PyPDF2**: PDF processing library for unlocking and locking encrypted PDFs
- **Auto-documentation**: Interactive API documentation with Swagger UI

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   └── utils/
│       ├── __init__.py
│       └── pdf_processor.py # PDF processing utilities
├── uploads/                 # Directory for temporary PDF files
├── requirements_simple.txt  # Python dependencies
├── start_server.py         # Simple startup script
└── README.md              # This file
```

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_simple.txt
```

### 2. Run the Application

```bash
# Development server
python start_server.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /health` - Application health status

### PDF Processing
- `POST /unlock-pdf` - Automatically unlock password-protected PDF and get download link
- `POST /lock-pdf` - Lock PDF with password and get download link
- `GET /download-pdf/{file_id}` - Download PDF by file ID
- `DELETE /download-pdf/{file_id}` - Delete PDF file

## Usage Examples

### Unlock a PDF (Automatic - No Password Required)

```bash
curl -X POST "http://localhost:8000/unlock-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "pdf_file=@protected.pdf"
```

Response:
```json
{
  "success": true,
  "message": "PDF unlocked successfully",
  "download_url": "http://localhost:8000/download-pdf/123e4567-e89b-12d3-a456-426614174000",
  "filename": "unlocked_document.pdf",
  "file_size": 1024000,
  "expires_at": "2024-01-02T12:00:00",
  "file_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Lock a PDF

```bash
curl -X POST "http://localhost:8000/lock-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "pdf_file=@document.pdf" \
  -F "password=your_password"
```

Response:
```json
{
  "success": true,
  "message": "PDF locked successfully",
  "download_url": "http://localhost:8000/download-pdf/123e4567-e89b-12d3-a456-426614174000",
  "filename": "locked_document.pdf",
  "file_size": 1024000,
  "expires_at": "2024-01-02T12:00:00",
  "file_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Download the PDF

```bash
curl -X GET "http://localhost:8000/download-pdf/123e4567-e89b-12d3-a456-426614174000" \
  --output document.pdf
```

### Delete the PDF file

```bash
curl -X DELETE "http://localhost:8000/download-pdf/123e4567-e89b-12d3-a456-426614174000"
```

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **python-multipart**: File upload support
- **PyPDF2**: PDF processing library

## File Management

- PDF files are stored temporarily in the `uploads/` directory
- Files expire after 24 hours and are automatically cleaned up
- You can manually delete files using the DELETE endpoint

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/
```

## License

This project is licensed under the MIT License.
