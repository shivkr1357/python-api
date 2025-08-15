# Dockerfile for PDF to PowerPoint API
# Optimized for Amazon Linux (uses yum package manager)

FROM amazonlinux:2

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV HOST=0.0.0.0

# Install system dependencies using yum (Amazon Linux package manager)
RUN yum update -y && \
    yum install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        curl \
        wget \
        tar \
        gzip \
        unzip \
        which \
        # Image processing dependencies
        libjpeg-devel \
        libpng-devel \
        freetype-devel \
        # PDF processing dependencies
        poppler-utils \
        tesseract \
        tesseract-langpack-eng \
        # OpenCV dependencies
        atlas-devel \
        blas-devel \
        lapack-devel \
        # Cleanup
    && yum clean all \
    && rm -rf /var/cache/yum

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY app/main.py ./app/main.py

# Create output directories
RUN mkdir -p outputs/pdfs outputs/pptx

# Set permissions
RUN chmod +x app/main.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
