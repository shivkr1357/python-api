# Dockerfile for PDF to PowerPoint API
# Optimized for Amazon Linux 2023 (uses dnf package manager)

FROM amazonlinux:2023

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000
ENV HOST=0.0.0.0

# Install system dependencies using dnf (Amazon Linux 2023 package manager)
RUN dnf update -y && \
    dnf install -y \
        python3.11 \
        python3.11-pip \
        python3.11-devel \
        gcc \
        gcc-c++ \
        make \
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
        # OpenCV dependencies
        atlas-devel \
        blas-devel \
        lapack-devel \
        # Cleanup
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Create symlink for python3 and pip3 to point to python3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/pip3.11 /usr/bin/pip3

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
