import sys
import uvicorn
from dayguard.backend.config import settings, logger

def run_server():
    """Run FastAPI server using uvicorn."""
    logger.info(f"Starting DayGuard FastAPI server on port {settings.port}...")
    uvicorn.run("dayguard.backend.main:app", host="0.0.0.0", port=settings.port, reload=True)

if __name__ == "__main__":
    run_server()
