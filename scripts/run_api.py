"""Script to run the AST Diff API server."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "ast_diff_poc.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
    )
