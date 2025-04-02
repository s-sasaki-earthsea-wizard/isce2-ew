FROM python:3.11-slim

# Install system dependencies for GDAL
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
RUN export GDAL_VERSION=$(gdal-config --version) && \
    echo "GDAL version: $GDAL_VERSION" && \
    echo "export GDAL_VERSION=$GDAL_VERSION" >> /etc/profile

# Set environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV LIBRARY_PATH=/usr/lib

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    GDAL_VERSION=$(gdal-config --version) && \
    sed -i "s/gdal/gdal==$GDAL_VERSION/" requirements.txt && \
    pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Create directory for mount points
RUN mkdir -p /app/results /app/src /app/visualize-outputs

# Default command to run bash
CMD ["bash"]
