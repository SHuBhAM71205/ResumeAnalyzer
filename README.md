# Resume Analyzer

A production-level scalable resume analyzer application built with FastAPI, utilizing RAG (Retrieval-Augmented Generation) for intelligent resume analysis and job matching.

## Overview

This application provides a comprehensive solution for resume analysis using AI-powered RAG systems. It processes PDF resumes, extracts text, generates embeddings, and matches them with relevant job opportunities using vector search.

## Features

- **Resume Upload & Storage**: Secure storage of PDF resumes using MinIO object storage
- **Text Extraction & Embeddings**: Automated text extraction and embedding generation
- **Vector Search**: Efficient job matching using Qdrant vector database
- **AI-Powered Analysis**: Integration with LLM for generating descriptions and insights
- **User Authentication**: Secure user management with JWT tokens and PostgreSQL
- **Rate Limiting**: Redis-based rate limiting to control user activity
- **Load Balancing**: Nginx for load distribution
- **Containerization**: Full Docker containerization for easy deployment
- **Observability**: Prometheus and Grafana for monitoring API latency, errors, and LLM token usage

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (users), Qdrant (vector search), Redis (caching/rate limiting)
- **Object Storage**: MinIO
- **Message Queue**: Celery with Redis
- **Load Balancer**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + Docker Compose
- **Package Management**: uv

## Project Structure

```
ResumeAnalizer/
├── backend/                    # FastAPI application
│   ├── app.py                 # Main FastAPI app
│   ├── Core/                  # Core configurations
│   │   ├── config.py          # App configuration
│   │   ├── db.py              # Database connection
│   │   ├── minio.py           # MinIO client
│   │   └── reddis.py          # Redis connection
│   ├── Middleware/            # Custom middleware
│   │   ├── limmiter.py        # Rate limiting
│   │   └── redis_cache.py     # Redis caching
│   ├── Model/                 # Database models
│   │   ├── auth_model.py      # Authentication models
│   │   └── model.py           # Main models
│   ├── Router/                # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── resume.py          # Resume analysis endpoints
│   │   └── user.py            # User management endpoints
│   └── Service/               # Business logic
│       ├── auth.py            # Auth services
│       └── resume.py          # Resume services
├── compose.yaml               # Docker Compose configuration
├── Dockerfile                 # Docker build instructions
├── main.py                    # Simple entry point (not used in production)
├── nginx.conf                 # Nginx configuration
├── prometheus.yml             # Prometheus configuration
├── pyproject.toml             # Project dependencies and metadata
├── uv.lock                    # uv lock file
├── .env                       # Environment variables (create from .env.example)
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager)
- Docker and Docker Compose (for containerized setup)

### Local Development Setup

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd ResumeAnalizer
   ```

2. **Install uv** (if not already installed):
   ```bash
   # On Windows
   winget install astral-sh.uv
   # Or using pip
   pip install uv
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   PG_DB_NAME=your_db_name
   PG_DB_USER=your_db_user
   PG_DB_PASSWORD=your_db_password
   MINIO_ROOT_USER=your_minio_user
   MINIO_ROOT_PASSWORD=your_minio_password
   # Add other required environment variables as per config.py
   ```

5. **Run the application**:
   ```bash
   uv run uvicorn backend.app:app --reload
   ```

   The API will be available at `http://localhost:8000`

## Docker Setup

### Development Environment

For development, you can run all services with ports exposed for easy access:

```bash
docker-compose up -d
```

This exposes all services for development purposes. However, in a real-world scenario, many ports should not be publicly accessible.

### Production Environment

In production, only essential ports should be exposed externally (nginx for the API and prometheus for monitoring). Internal services like databases and caches should not be exposed.

1. **Uncomment the `api` and `nginx` services in `compose.yaml`**:

   ```yaml
   api:
     container_name: RESUME_API
     build: .
     depends_on:
       db:
         condition: service_started
       redis:
         condition: service_healthy
     env_file:
       - .env
     environment:
       - DATABASE_URL=postgresql://${PG_DB_USER}:${PG_DB_PASSWORD}@RESUME_POSTGRES:5432/${PG_DB_NAME}
       - REDIS_URL=redis://RESUME_REDIS:6379

   nginx:
     container_name: RESUME_NGINX
     image: nginx:latest
     ports: 
       - "80:80"
     volumes: 
       - "./nginx.conf:/etc/nginx/nginx.conf"
     depends_on: 
       - api
   ```

2. **Remove or comment out port mappings for internal services** in production (db, redis, qdrant, minio, grafana) to prevent external access. Only keep ports for nginx (80) and prometheus (9090).

3. **Run in production mode**:
   ```bash
   docker-compose up -d --build
   ```

   - API accessible via nginx at `http://your-server:80`
   - Prometheus metrics at `http://your-server:9090`
   - All other services are internal to the Docker network

## API Documentation

Once the application is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI) or `http://localhost:8000/redoc` for ReDoc.

### Key Endpoints

- `GET /` - Welcome message
- Authentication endpoints (login, register)
- Resume upload and analysis endpoints
- User management endpoints

## Monitoring

- **Prometheus**: Metrics collection at `http://localhost:9090`
- **Grafana**: Dashboards at `http://localhost:3000`

Configure Grafana to connect to Prometheus as a data source to visualize metrics like API latency, error rates, and LLM token usage.

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

### Linting

```bash
uv run flake8 .
```

## Deployment

### Containerized Deployment

1. **Build and push Docker images** (optional, for custom registry):
   ```bash
   # Build the API image
   docker build -t your-registry/resume-analyzer:latest .
   
   # Push to registry
   docker push your-registry/resume-analyzer:latest
   ```

2. **Deploy using Docker Compose**:
   - Ensure `compose.yaml` is configured for production (ports restricted)
   - Set environment variables in `.env`
   - Run: `docker-compose up -d`

### Cloud Deployment Options

#### Docker Compose on VPS/Cloud Server

1. Provision a VPS (AWS EC2, DigitalOcean Droplet, etc.)
2. Install Docker and Docker Compose
3. Clone your repository
4. Configure `.env` with production values
5. Run `docker-compose up -d`

#### Kubernetes Deployment

For scalable production deployment:

1. Convert `compose.yaml` to Kubernetes manifests
2. Use Helm charts for easier management
3. Deploy to Kubernetes cluster (EKS, GKE, AKS, etc.)

Example Kubernetes considerations:
- Use ConfigMaps/Secrets for environment variables
- Persistent Volumes for databases
- Ingress for external access (expose only nginx)
- Service meshes for internal communication

#### Serverless/Container Platforms

- **Railway**: Connect GitHub repo, auto-deploys with Docker
- **Render**: Deploy from Docker image or GitHub
- **Fly.io**: Global deployment with Docker
- **Google Cloud Run**: Serverless containers

### Environment Configuration

For production, ensure these environment variables are set securely:

```env
# Database
PG_DB_NAME=resume_prod
PG_DB_USER=prod_user
PG_DB_PASSWORD=secure_password

# MinIO
MINIO_ROOT_USER=prod_minio_user
MINIO_ROOT_PASSWORD=secure_minio_password

# JWT
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256

# Other service URLs
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Security Considerations

- Use strong, unique passwords for all services
- Enable SSL/TLS for nginx (use certbot for Let's Encrypt)
- Regularly update Docker images
- Monitor logs and metrics
- Use secrets management (Docker secrets, Kubernetes secrets, etc.)
- Network segmentation (internal services not exposed)

### Scaling

- **Horizontal Scaling**: Increase replica count for API service
- **Database Scaling**: Use connection pooling, read replicas
- **Caching**: Redis cluster for high availability
- **Storage**: MinIO distributed setup
- **Vector DB**: Qdrant clustering for performance


## License
-
