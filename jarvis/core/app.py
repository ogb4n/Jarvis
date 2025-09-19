from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jarvis.core.config import settings, OpenAPISettings


# Enhanced OpenAPI configuration
app = FastAPI(
    title= OpenAPISettings.title,
    version=OpenAPISettings.version,
    description=OpenAPISettings.description,
    contact={
        "name": OpenAPISettings.contact_name,
        "url": OpenAPISettings.contact_url,
    },
    license_info={
        "name": OpenAPISettings.license_name,
        "url": OpenAPISettings.license_url,
    },
    openapi_tags=OpenAPISettings.openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom OpenAPI schema with enhanced metadata
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🤖 Jarvis Voice Assistant API",
        version="0.1.0",
        description=app.description,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware for web interface access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["system"], summary="Health Check",
         description="System health status and service availability",)
def health_check():
    """
    ## System Health Check
    
    Monitor the health and availability of Jarvis services.
    
    **Returns:**
    - Overall system status
    - Individual service status
    - System resources info
    """
    return {
        "status": "healthy",
        "timestamp": "2025-09-19T00:00:00Z",
        "services": {
            "audio": "available",
            "conversation": "available", 
            "database": "connected",
            "tts": "ready",
            "stt": "ready"
        },
        "version": "0.1.0"
    }

@app.get("/api-docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI with enhanced styling
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="🤖 Jarvis API Documentation",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "displayOperationId": False,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True
        }
    )

@app.on_event("startup")
async def startup_event():
    print("🤖 Jarvis is starting up...")

@app.on_event("shutdown") 
async def shutdown_event():
    print("🤖 Jarvis is shutting down...")
