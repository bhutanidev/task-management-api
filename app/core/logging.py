import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
from fastapi import Request

# Configure the root logger
logger = logging.getLogger("deeplure_research")

def setup_logging(log_level: str = "INFO"):
    """Configure the application logging"""
    
    # Set log level based on string input
    level = getattr(logging, log_level.upper())
    
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(handler)
    
    # Disable propagation to prevent duplicate logs
    logger.propagate = False
    
    return logger

async def log_request_details(request: Request, error: Optional[Exception] = None):
    """Log detailed request information, especially useful for debugging errors"""
    try:
        # Get request details
        request_details = {
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else "unknown",
            "headers": dict(request.headers),
            "path_params": request.path_params,
            "query_params": dict(request.query_params),
        }
        
        # Try to get the request body if available
        if hasattr(request, "body"):
            try:
                body = await request.body()
                if body:
                    try:
                        # Try to decode as JSON
                        request_details["body"] = json.loads(body.decode("utf-8"))
                    except:
                        # If not JSON, store as raw string
                        request_details["body"] = body.decode("utf-8", errors="replace")
            except:
                pass
                
        # Log error details if provided
        if error:
            error_details = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            }
            logger.error(
                f"Request error: {error_details['error_type']}: {error_details['error_message']}\n"
                f"Request details: {json.dumps(request_details, default=str)}\n"
                f"Traceback: {error_details['traceback']}"
            )
        else:
            # Regular request logging
            logger.info(f"Request: {json.dumps(request_details, default=str)}")
    
    except Exception as logging_error:
        # Fallback if there's an error during logging
        logger.error(f"Error during request logging: {logging_error}")
        if error:
            logger.error(f"Original error: {error} - {traceback.format_exc()}")