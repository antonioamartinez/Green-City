# 1. Base image 
FROM python:3.11.9-slim

# 2. Prep & install system libs for GDAL/rasterio, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gdal-bin \
      libgdal-dev && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /app

# 4. Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project code
COPY . .

# 6. Drop into bash by default
CMD ["bash"]
