FROM continuumio/miniconda3:latest

LABEL maintainer="Econ-ARK Team"
LABEL description="Aiyagari (1994) QJE Model Replication Environment"
LABEL version="1.0"

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install mamba for faster package resolution
RUN conda install -n base -c conda-forge mamba

# Copy environment specification
COPY binder/environment.yml /tmp/environment.yml

# Create conda environment using mamba
RUN mamba env create -f /tmp/environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "Aiyagari1994QJE", "/bin/bash", "-c"]

# Copy all project files
COPY . /workspace/

# Make scripts executable
RUN chmod +x reproduce.sh reproduce_min.sh run_baseline.sh run_full.sh

# Verify environment setup
RUN python -c "import HARK; print(f'HARK version: {HARK.__version__}')" && \
    python -c "import numpy, pandas, matplotlib; print('Core packages imported successfully')"

# Set default conda environment
ENV CONDA_DEFAULT_ENV=Aiyagari1994QJE
ENV PATH=/opt/conda/envs/Aiyagari1994QJE/bin:$PATH

# Expose Jupyter port
EXPOSE 8888

# Default command runs Jupyter Lab
CMD ["conda", "run", "-n", "Aiyagari1994QJE", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"] 