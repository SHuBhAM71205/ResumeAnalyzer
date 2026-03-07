import uvicorn
from dotenv import load_dotenv
from backend.Core.config import settings
from backend.app import app

# Load environment variables from .env file
load_dotenv()


def main():
    """Start the FastAPI application"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.APP_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()

