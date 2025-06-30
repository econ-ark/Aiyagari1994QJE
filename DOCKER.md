# Docker Usage Guide - Aiyagari (1994) QJE Model

This guide explains how to use Docker to run the Aiyagari (1994) QJE model replication in a containerized environment.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)
- Git (to clone the repository)

## Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd Aiyagari1994QJE
```

### 2. Run with Docker Compose (Recommended)

#### Start Jupyter Lab Environment
```bash
docker-compose up aiyagari-notebook
```
Then open http://localhost:8888 in your browser.

#### Run Baseline Reproduction (~30 seconds)
```bash
docker-compose --profile baseline up aiyagari-baseline
```

#### Run Full Reproduction (~10-15 minutes)
```bash
docker-compose --profile full up aiyagari-full
```

### 3. Alternative: Direct Docker Commands

#### Build the Image
```bash
docker build -t aiyagari1994qje .
```

#### Run Jupyter Lab
```bash
docker run -p 8888:8888 -v $(pwd):/workspace aiyagari1994qje
```

#### Run Baseline Test
```bash
docker run -v $(pwd):/workspace aiyagari1994qje conda run -n Aiyagari1994QJE ./run_baseline.sh
```

#### Run Full Reproduction
```bash
docker run -v $(pwd):/workspace aiyagari1994qje conda run -n Aiyagari1994QJE ./run_full.sh
```

## Development Container (VS Code)

If you use VS Code, you can use the `.devcontainer` configuration:

1. Install the "Dev Containers" extension
2. Open the repository in VS Code
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
4. Select "Dev Containers: Reopen in Container"

This will automatically:
- Build the development environment
- Install all dependencies
- Set up the Python interpreter
- Configure Jupyter integration

## Container Features

### Included Software
- **Python 3.11** with conda environment management
- **HARK 0.13.0** - Heterogeneous Agents Resources and toolKit
- **Jupyter Lab** for interactive notebook execution
- **Scientific Python stack** (NumPy, Pandas, Matplotlib, SciPy)
- **All dependencies** specified in `binder/environment.yml`

### Exposed Ports
- **8888**: Jupyter Lab interface

### Volume Mounts
- **Current directory** mounted to `/workspace` in container
- **Results volume** for persistent output storage

## Usage Examples

### Interactive Development
```bash
# Start Jupyter Lab
docker-compose up aiyagari-notebook

# Access at http://localhost:8888
# Edit and run notebooks interactively
```

### Automated Execution
```bash
# Quick CI test (30 seconds)
docker-compose --profile baseline up aiyagari-baseline

# Full parameter sweep (10-15 minutes)  
docker-compose --profile full up aiyagari-full

# View results
ls -la results/
```

### Custom Commands
```bash
# Run specific Python script
docker run -v $(pwd):/workspace aiyagari1994qje \
  conda run -n Aiyagari1994QJE python your_script.py

# Access bash shell in container
docker run -it -v $(pwd):/workspace aiyagari1994qje \
  conda run -n Aiyagari1994QJE bash
```

## Troubleshooting

### Build Issues
```bash
# Clean build (no cache)
docker build --no-cache -t aiyagari1994qje .

# Check build logs
docker-compose build --no-cache
```

### Permission Issues
```bash
# Fix file permissions after container run
sudo chown -R $USER:$USER results/
```

### Port Conflicts
```bash
# Use different port if 8888 is busy
docker run -p 8889:8888 -v $(pwd):/workspace aiyagari1994qje
# Then access http://localhost:8889
```

### Memory Issues
```bash
# Increase Docker memory limit in Docker Desktop settings
# Recommended: At least 4GB RAM for full reproduction
```

## Environment Variables

The container sets these environment variables:
- `CONDA_DEFAULT_ENV=Aiyagari1994QJE`
- `PATH` includes conda environment binaries
- `JUPYTER_ENABLE_LAB=yes`

## Data Persistence

- **Results**: Stored in named Docker volume `aiyagari-results`
- **Source code**: Mounted from host directory (live updates)
- **Notebooks**: Changes persist in host directory

## Performance Notes

- **First build**: 5-10 minutes (downloads and installs dependencies)
- **Subsequent builds**: 1-2 minutes (uses Docker cache)
- **Baseline execution**: ~30 seconds
- **Full reproduction**: ~10-15 minutes
- **Memory usage**: ~2-4GB during execution

## Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi aiyagari1994qje

# Remove volumes (WARNING: deletes results)
docker volume rm aiyagari1994qje_aiyagari-results
```

## Integration with CI/CD

The Docker setup is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Aiyagari Baseline Test
  run: |
    docker build -t aiyagari1994qje .
    docker run -v $(pwd):/workspace aiyagari1994qje \
      conda run -n Aiyagari1994QJE ./run_baseline.sh
```

## Support

For issues with Docker setup:
1. Check Docker and Docker Compose versions
2. Ensure sufficient disk space (>5GB)
3. Verify port 8888 is available
4. Review container logs: `docker-compose logs` 