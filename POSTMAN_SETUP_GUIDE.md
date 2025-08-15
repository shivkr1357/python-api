# 📮 Postman Collection Setup Guide

This guide will help you set up and use the Postman collection for the PDF to PowerPoint Converter API.

## 📋 Prerequisites

1. **Postman Desktop App** (Download from https://www.postman.com/downloads/)
2. **Python API Server** running (see main README.md for setup instructions)
3. **Postman Collection Files**:
   - `PDF_to_PowerPoint_API.postman_collection.json`
   - `PDF_to_PowerPoint_API.postman_environment.json`

## 🚀 Quick Setup (5 minutes)

### Step 1: Start the API Server
```bash
# Navigate to your project directory
cd /Users/pratikranpariya/Documents/code/own/python-api

# Activate virtual environment
source venv/bin/activate

# Start the server
python -m app.main
```

### Step 2: Import Collection into Postman

1. **Open Postman**
2. **Click "Import"** (top left)
3. **Drag & Drop** or **Browse** for the file:
   - `PDF_to_PowerPoint_API.postman_collection.json`
4. **Click "Import"**

### Step 3: Import Environment

1. **Click "Import"** again
2. **Drag & Drop** or **Browse** for the file:
   - `PDF_to_PowerPoint_API.postman_environment.json`
3. **Click "Import"**

### Step 4: Select Environment

1. **Click the environment dropdown** (top right)
2. **Select** "PDF to PowerPoint Converter API - Environment"
3. **Verify** `base_url` is set to `http://localhost:8000`

## 🧪 Testing the API

### Test 1: Health Check
1. **Expand** "System" folder
2. **Click** "Health Check"
3. **Click** "Send"
4. **Expected Result**: `{"status":"healthy"}`

### Test 2: Create PDF
1. **Expand** "PDF Operations" folder
2. **Click** "Create PDF"
3. **Review** the request body (sample data is pre-filled)
4. **Click** "Send"
5. **Expected Result**: Success response with PDF path

### Test 3: List PDFs
1. **Click** "List PDFs"
2. **Click** "Send"
3. **Expected Result**: List of PDF files

### Test 4: Convert to PowerPoint
1. **Expand** "Conversion Operations" folder
2. **Click** "Convert PDF to PowerPoint"
3. **Update** the `pdf_path` in the request body (use the path from Test 2)
4. **Click** "Send"
5. **Expected Result**: Success response with PowerPoint path

## 🔧 Environment Variables

The collection uses these environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `base_url` | API base URL | `http://localhost:8000` |
| `pdf_filename` | PDF filename for operations | (auto-filled) |
| `pptx_filename` | PowerPoint filename for operations | (auto-filled) |
| `pdf_path` | Full path to PDF file | (auto-filled) |
| `api_version` | API version | `1.0.0` |
| `content_type` | Content type for requests | `application/json` |

## 📁 Collection Structure

```
PDF to PowerPoint Converter API
├── System
│   ├── Get API Information
│   └── Health Check
├── PDF Operations
│   ├── Create PDF
│   ├── List PDFs
│   ├── Get PDF Info
│   ├── Download PDF
│   └── Delete PDF
└── Conversion Operations
    ├── Convert PDF to PowerPoint
    ├── List PowerPoint Files
    ├── Download PowerPoint
    ├── Delete PowerPoint
    └── Create Sample PowerPoint
```

## 🎯 Workflow Examples

### Complete PDF to PowerPoint Workflow

1. **Create PDF** → Get `pdf_path` from response
2. **List PDFs** → Verify PDF was created
3. **Convert PDF to PowerPoint** → Use `pdf_path` from step 1
4. **List PowerPoint Files** → Verify PowerPoint was created
5. **Download PowerPoint** → Get the file

### Testing Workflow

1. **Health Check** → Verify API is running
2. **Create Sample PowerPoint** → Quick test of PowerPoint creation
3. **List PowerPoint Files** → See the sample file
4. **Download PowerPoint** → Get the sample file

## 🔄 Dynamic Variables

The collection automatically updates these variables:

- **`pdf_filename`**: Set from "List PDFs" response
- **`pptx_filename`**: Set from "List PowerPoint Files" response
- **`pdf_path`**: Set from "Create PDF" response

## 📝 Request Examples

### Create PDF Request
```json
{
  "title": "My Document",
  "content": "This is the content of my document.",
  "author": "John Doe",
  "subject": "Sample Document",
  "keywords": ["sample", "document", "pdf"]
}
```

### Convert PDF to PowerPoint Request
```json
{
  "pdf_path": "outputs/pdfs/My_Document_20250815_130000.pdf",
  "output_name": "my_presentation",
  "include_images": true
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Connection refused"**
   - Make sure the API server is running
   - Check if port 8000 is available

2. **"404 Not Found"**
   - Verify the `base_url` is correct
   - Check if the API server is running on the right port

3. **"500 Internal Server Error"**
   - Check the API server logs
   - Verify all dependencies are installed

4. **Environment variables not working**
   - Make sure the environment is selected
   - Check if variables are properly set

### Debug Steps

1. **Test the API directly**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check server logs** for error messages

3. **Verify file paths** in the request bodies

4. **Check Postman console** for detailed error information

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Health check returns `{"status":"healthy"}`
- ✅ PDF creation returns success with a file path
- ✅ PDF listing shows your created files
- ✅ PowerPoint conversion completes successfully
- ✅ File downloads work properly

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Swagger Specification**: `swagger.yaml` and `swagger.json`
- **Main README**: `README.md`
- **Test Script**: `test_api.py`

## 🔗 Quick Links

- **Postman Download**: https://www.postman.com/downloads/
- **Postman Documentation**: https://learning.postman.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

---

**Happy Testing! 🚀**

If you encounter any issues, check the troubleshooting section or refer to the main README.md file.
