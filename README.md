# PDF to PowerPoint Converter API

A FastAPI application that creates PDF files and converts them to PowerPoint presentations using proper MVC (Model-View-Controller) architecture.

## Features

- **PDF Creation**: Generate PDF files from text content with custom styling
- **PDF to PowerPoint Conversion**: Convert PDF files to PowerPoint presentations
- **RESTful API**: Clean and intuitive API endpoints
- **MVC Architecture**: Proper separation of concerns with Models, Views (Controllers), and Services
- **File Management**: Upload, download, list, and delete files
- **Automatic Cleanup**: Files are automatically deleted after 2 hours to manage storage
- **Advanced PDF Processing**: Enhanced PDF to PowerPoint conversion with multiple extraction methods
- **Unique File Naming**: Guaranteed unique filenames with timestamps and UUIDs
- **Error Handling**: Comprehensive error handling and validation
- **Documentation**: Auto-generated API documentation with Swagger UI

## PDF to PowerPoint Conversion

The API now includes enhanced PDF to PowerPoint conversion capabilities:

### **Text-Based PDFs**
- **Full Content Extraction**: Extracts all text content from PDF files
- **Image Extraction**: Extracts and embeds images from PDF into PowerPoint slides
- **Multiple Extraction Methods**: Uses `pdfplumber`, `PyPDF2`, and `PyMuPDF` for maximum compatibility
- **Smart Content Organization**: Automatically organizes content into slides
- **Professional Formatting**: Creates well-structured PowerPoint presentations

### **Image-Based PDFs (Scanned Documents)**
- **Intelligent Detection**: Automatically detects when a PDF contains images rather than text
- **Informative Output**: Creates PowerPoint slides explaining the limitation
- **Clear Guidance**: Provides information about OCR requirements for image-based PDFs

### **Conversion Process**
1. **Content Analysis**: Analyzes PDF structure and content type
2. **Image Extraction**: Extracts images using PyMuPDF with quality preservation
3. **Text Extraction**: Uses advanced libraries to extract text content
4. **Content Cleaning**: Removes artifacts and formats text properly
5. **Bullet Point Formatting**: Converts Unicode bullets to proper formatting
6. **Content Organization**: Separates metadata from main content
7. **Slide Generation**: Creates organized PowerPoint slides with proper structure
8. **Image Integration**: Embeds extracted images into dedicated slides
9. **Quality Assurance**: Ensures proper formatting and readability

### **Recent Improvements (Latest Version)**
- **✅ Fixed Bullet Points**: No more `(cid:127)` - proper bullet formatting
- **✅ Better Text Organization**: Content properly separated and structured
- **✅ Improved Slide Layout**: Limited content per slide for readability
- **✅ Enhanced Formatting**: Professional PowerPoint presentation structure
- **✅ Smart Content Splitting**: Long text automatically split into readable chunks
- **🆕 Image Support**: PDF images now extracted and included in PowerPoint slides

## Unique File Naming

The API ensures that every generated file has a unique name to prevent conflicts:

### **Naming Convention**
- **Format**: `{safe_title}_{timestamp}_{uuid}.{extension}`
- **Example**: `Sample_Document_20250815_135324_327250_e3753e17.pdf`

### **Components**
- **Safe Title**: Original title with special characters removed and spaces converted to underscores
- **Timestamp**: Includes date, time, and microseconds for precision (`YYYYMMDD_HHMMSS_microseconds`)
- **UUID**: First 8 characters of a UUID to ensure uniqueness even with identical timestamps
- **Extension**: File extension (`.pdf` or `.pptx`)

### **Benefits**
- **No Conflicts**: Guaranteed unique names even with simultaneous requests
- **Traceability**: Timestamp allows tracking when files were created
- **Safe Characters**: Special characters are handled safely for all operating systems
- **High Precision**: Microsecond precision prevents naming collisions

## Architecture

The application follows the MVC pattern:

- **Models** (`app/models/`): Pydantic models for data validation and structure
- **Controllers** (`app/controllers/`): Handle HTTP requests and responses
- **Services** (`app/services/`): Business logic for PDF and PowerPoint operations
- **Main App** (`app/main.py`): FastAPI application configuration and routing

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python -m app.main
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### OpenAPI/Swagger Specifications

The API also includes comprehensive OpenAPI 3.0.3 specifications:

- **YAML Format**: `swagger.yaml` - Human-readable specification
- **JSON Format**: `swagger.json` - Machine-readable specification

You can use these files with:
- **Swagger Editor**: https://editor.swagger.io/
- **Postman**: Import the JSON file for API testing
- **Code Generation**: Generate client libraries in various languages
- **API Testing Tools**: Use with tools like Insomnia, Paw, etc.

To validate the specifications:
```bash
python validate_swagger.py
```

## Postman Collection

A complete Postman collection is included for easy API testing:

- **Collection File**: `PDF_to_PowerPoint_API.postman_collection.json`
- **Environment File**: `PDF_to_PowerPoint_API.postman_environment.json`
- **Setup Guide**: `POSTMAN_SETUP_GUIDE.md`

### Quick Postman Setup:
1. Import both JSON files into Postman
2. Select the environment
3. Start testing the API endpoints

See `POSTMAN_SETUP_GUIDE.md` for detailed instructions.

## API Endpoints

### PDF Operations

#### Create PDF
```http
POST /pdf/create
Content-Type: application/json

{
  "title": "Sample Document",
  "content": "This is the main content of the document...",
  "author": "John Doe",
  "subject": "Sample Subject",
  "keywords": ["sample", "document", "pdf"]
}
```

#### List PDFs
```http
GET /pdf/list
```

#### Download PDF
```http
GET /pdf/download/{filename}
```

#### Get PDF Info
```http
GET /pdf/info/{filename}
```

#### Delete PDF
```http
DELETE /pdf/delete/{filename}
```

### Conversion Operations

#### Convert PDF to PowerPoint
```http
POST /convert/pdf-to-pptx
Content-Type: application/json

{
  "pdf_path": "outputs/pdfs/sample_document.pdf",
  "output_name": "converted_presentation",
  "include_images": true
}
```

#### List PowerPoint Files
```http
GET /convert/list-pptx
```

#### Download PowerPoint
```http
GET /convert/download-pptx/{filename}
```

#### Delete PowerPoint
```http
DELETE /convert/delete-pptx/{filename}
```

#### Create Sample PowerPoint
```http
POST /convert/create-sample-pptx
```

### Cleanup Operations

#### Start Cleanup Service
```http
POST /cleanup/start
```

#### Stop Cleanup Service
```http
POST /cleanup/stop
```

#### Get Cleanup Status
```http
GET /cleanup/status
```

#### Manual Cleanup
```http
POST /cleanup/manual
```

#### Get Cleanup Configuration
```http
GET /cleanup/config
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# Create a PDF
pdf_data = {
    "title": "My Document",
    "content": "This is a sample document created via API.",
    "author": "API User",
    "subject": "API Testing",
    "keywords": ["api", "test", "pdf"]
}

response = requests.post(f"{base_url}/pdf/create", json=pdf_data)
pdf_result = response.json()
print(f"PDF created: {pdf_result['pdf_path']}")

# Convert PDF to PowerPoint
conversion_data = {
    "pdf_path": pdf_result['pdf_path'],
    "output_name": "my_presentation",
    "include_images": True
}

response = requests.post(f"{base_url}/convert/pdf-to-pptx", json=conversion_data)
conversion_result = response.json()
print(f"PowerPoint created: {conversion_result['pptx_path']}")
```

### cURL Examples

#### Create PDF
```bash
curl -X POST "http://localhost:8000/pdf/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Document",
    "content": "This is the content of the document.",
    "author": "John Doe"
  }'
```

#### Convert PDF to PowerPoint
```bash
curl -X POST "http://localhost:8000/convert/pdf-to-pptx" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "outputs/pdfs/sample_document.pdf",
    "output_name": "converted_presentation"
  }'
```

## Project Structure

```
python-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── pdf_model.py        # Pydantic models
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── pdf_controller.py   # PDF operations
│   │   └── conversion_controller.py  # Conversion operations
│   └── services/
│       ├── __init__.py
│       ├── pdf_service.py      # PDF business logic
│       └── pptx_service.py     # PowerPoint business logic
├── outputs/
│   ├── pdfs/                   # Generated PDF files
│   └── pptx/                   # Generated PowerPoint files
├── requirements.txt            # Python dependencies
├── swagger.yaml               # OpenAPI specification (YAML)
├── swagger.json               # OpenAPI specification (JSON)
├── validate_swagger.py        # Swagger validation script
├── test_api.py                # API testing script
├── test_cleanup.py            # Cleanup service testing script
├── test_pdf_conversion.py     # PDF conversion testing script
├── test_pdf_extraction.py     # PDF extraction testing script
├── check_pptx_content.py      # PowerPoint content verification script
├── test_unique_names.py       # Unique naming verification script
├── PDF_to_PowerPoint_API.postman_collection.json    # Postman collection
├── PDF_to_PowerPoint_API.postman_environment.json   # Postman environment
├── POSTMAN_SETUP_GUIDE.md     # Postman setup guide
└── README.md                   # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **ReportLab**: PDF generation library
- **python-pptx**: PowerPoint creation and manipulation
- **Pydantic**: Data validation using Python type annotations
- **Pillow**: Image processing (for enhanced PDF/PPTX features)
- **aiofiles**: Async file operations

## Error Handling

The application includes comprehensive error handling:

- **HTTP Exceptions**: Proper HTTP status codes and error messages
- **Validation Errors**: Pydantic validation for request data
- **File Not Found**: Graceful handling of missing files
- **Global Exception Handler**: Catches and formats unexpected errors

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

You can test the API using the interactive documentation at `http://localhost:8000/docs` or use tools like Postman, cURL, or any HTTP client.

## Production Deployment

For production deployment:

1. Set appropriate CORS origins
2. Configure proper logging
3. Use a production ASGI server like Gunicorn
4. Set up proper file storage (consider cloud storage for large files)
5. Implement authentication and authorization
6. Add rate limiting
7. Configure environment variables for sensitive data

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
