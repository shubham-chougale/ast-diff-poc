"""Main FastAPI application for AST Diff API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.diff_routes import router as diff_router

# Create FastAPI app
app = FastAPI(
    title="AST Diff API",
    description="API for computing AST-based diffs between Java-style property files",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diff_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AST Diff API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
