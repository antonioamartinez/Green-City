FROM nvcr.io/nvidia/tensorflow:24.02-tf2-py3
#FROM nvcr.io/nvidia/tensorflow:24.02-tf2-py3  # TF 2.15, CUDA 12, A100 support

WORKDIR /workspace

# Install system dependencies for rasterio, etc.
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev

# Optional: Install conda if you want (for geopandas, etc.), but pip works fine for most packages
# Otherwise just pip install
RUN pip install imageio rasterio geopandas h5py scipy tqdm scikit-image scikit-learn optuna matplotlib

# Clone the repo and copy your scripts
RUN git clone https://github.com/fengchenUCB/greencity-tree-location.git
WORKDIR /workspace/greencity-tree-location

# (optional) Copy your dataset into the image, or mount at runtime

# Default command (can override)
CMD ["/bin/bash"]
