from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import os
import json
import glob
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import numpy as np

# Import the recommendation engine from main.py
from main import OptimizedRecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Strategy Agent 3.0 API",
    description="API for generating customer recommendations and reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
logger.info("✅ CORS middleware configured to allow all origins")

# Initialize the recommendation engine
try:
    engine = OptimizedRecommendationEngine()
    logger.info("✅ Recommendation engine initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize recommendation engine: {str(e)}")
    engine = None

# Enum for customer IDs
class CustomerID(str, Enum):
    C001 = "C001"
    C002 = "C002"
    C003 = "C003"

# Pydantic models for request/response
class RecommendationRequest(BaseModel):
    customer_id: CustomerID
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "C001"
            }
        }

class RecommendationResponse(BaseModel):
    success: bool
    message: str
    customer_id: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool
    message: str
    error: str
    timestamp: str

# Global storage for recommendations (in production, use a database)
recommendations_storage = {}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Strategy Agent 3.0 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "available_customers": ["C001", "C002", "C003"]
    }

@app.post("/generate-recommendations", response_model=Dict[str, Any])
async def generate_recommendations(request: RecommendationRequest, background_tasks: BackgroundTasks):
    """
    Generate recommendations for a specific customer
    
    - **customer_id**: Customer ID (C001, C002, or C003)
    
    Returns the complete recommendations data including:
    - Customer information and classification
    - Accepted recommendations
    - Rejected recommendations  
    - Already purchased recommendations
    - Summary statistics
    - Generated file paths
    """
    if not engine:
        raise HTTPException(
            status_code=500, 
            detail="Recommendation engine not available"
        )
    
    try:
        logger.info(f"🚀 Generating recommendations for customer: {request.customer_id}")
        
        # Generate recommendations using the existing engine
        result = engine.generate_recommendations(request.customer_id)
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate recommendations"
            )
        
        recommendations, rejected_recommendations, already_purchased_recommendations, customer_classification = result
        
        # Store recommendations in memory (in production, use a database)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recommendations_data = {
            "customer_id": request.customer_id,
            "timestamp": timestamp,
            "CustomerInfo": {
                "CustomerID": request.customer_id,
                "CustomerName": get_customer_name(request.customer_id)
            },
            "CustomerClassification": customer_classification,
            "AcceptedRecommendations": recommendations,
            "RejectedRecommendations": rejected_recommendations,
            "AlreadyPurchasedRecommendations": already_purchased_recommendations,
            "Summary": {
                "TotalUpSell": 0,  # Up-sell is currently disabled
                "TotalCrossSell": len(recommendations),
                "TotalRejected": len(rejected_recommendations),
                "TotalAlreadyPurchased": len(already_purchased_recommendations),
                "TotalRecommendations": len(recommendations)
            }
        }
        
        # Store in global storage
        recommendations_storage[request.customer_id] = recommendations_data
        
        # Save to file
        save_recommendations_to_file(request.customer_id, recommendations_data)
        
        # Generate PDF report
        pdf_success = generate_pdf_report(request.customer_id, recommendations_data)
        
        logger.info(f"✅ Successfully generated recommendations for {request.customer_id}")
        logger.info(f"📄 PDF generation: {'Success' if pdf_success else 'Failed'}")
        
        # Prepare the response data
        response_data = {
            "success": True,
            "message": f"Recommendations generated successfully for customer {request.customer_id}",
            "customer_id": request.customer_id,
            "timestamp": timestamp,
            "CustomerInfo": {
                "CustomerID": request.customer_id,
                "CustomerName": get_customer_name(request.customer_id)
            },
            "CustomerClassification": customer_classification,
            "AcceptedRecommendations": recommendations,
            "RejectedRecommendations": rejected_recommendations,
            "AlreadyPurchasedRecommendations": already_purchased_recommendations,
            "Summary": recommendations_data["Summary"],
            "files_generated": {
                "json_file": f"recommendations/recommendations_{request.customer_id}_{timestamp}.json",
                "pdf_file": f"reports/analysis_report_{request.customer_id}_{timestamp}.pdf",
                "pdf_generated": pdf_success
            }
        }
        
        # Convert numpy types to native Python types for JSON serialization
        response_data = convert_numpy_types(response_data)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating recommendations for {request.customer_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/recommendations/{customer_id}/json", response_model=Dict[str, Any])
async def get_recommendations_json(customer_id: CustomerID):
    """
    Get recommendations in JSON format for a specific customer
    
    - **customer_id**: Customer ID (C001, C002, or C003)
    
    Returns the complete recommendations data in JSON format.
    """
    if customer_id not in recommendations_storage:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for customer {customer_id}. Please generate recommendations first using POST /generate-recommendations"
        )
    
    try:
        recommendations_data = recommendations_storage[customer_id]
        
        # Also try to load from file if available
        timestamp = recommendations_data.get("timestamp", "")
        json_file_path = f"recommendations/recommendations_{customer_id}_{timestamp}.json"
        
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                file_data = json.load(f)
                return file_data
        else:
            # Return from memory storage
            return {
                "CustomerInfo": recommendations_data["CustomerInfo"],
                "CustomerClassification": recommendations_data["CustomerClassification"],
                "AcceptedRecommendations": recommendations_data["AcceptedRecommendations"],
                "RejectedRecommendations": recommendations_data["RejectedRecommendations"],
                "AlreadyPurchasedRecommendations": recommendations_data["AlreadyPurchasedRecommendations"],
                "Summary": recommendations_data["Summary"],
                "GeneratedAt": recommendations_data["timestamp"]
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving JSON recommendations for {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving recommendations: {str(e)}"
        )

@app.get("/recommendations/{customer_id}/download")
async def download_report(customer_id: CustomerID):
    """
    Download the PDF report for a specific customer
    
    - **customer_id**: Customer ID (C001, C002, or C003)
    
    Returns the PDF report file for download.
    """
    if customer_id not in recommendations_storage:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for customer {customer_id}. Please generate recommendations first using POST /generate-recommendations"
        )
    
    try:
        recommendations_data = recommendations_storage[customer_id]
        timestamp = recommendations_data.get("timestamp", "")
        
        # Look for the PDF file
        pdf_file_path = f"reports/analysis_report_{customer_id}_{timestamp}.pdf"
        
        if not os.path.exists(pdf_file_path):
            # Try to find the most recent PDF for this customer
            pdf_pattern = f"reports/analysis_report_{customer_id}_*.pdf"
            pdf_files = glob.glob(pdf_pattern)
            
            if not pdf_files:
                # If no PDF found, try to generate it
                if customer_id in recommendations_storage:
                    recommendations_data = recommendations_storage[customer_id]
                    pdf_success = generate_pdf_report(customer_id, recommendations_data)
                    
                    if pdf_success:
                        # Try again after generation
                        pdf_files = glob.glob(pdf_pattern)
                        if not pdf_files:
                            raise HTTPException(
                                status_code=404,
                                detail=f"PDF report generation failed for customer {customer_id}. File was not created."
                            )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"PDF report generation failed for customer {customer_id}. Check if pdf_report_generator.py exists and reportlab is installed."
                        )
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No recommendations found for customer {customer_id}. Please generate recommendations first using POST /generate-recommendations"
                    )
            
            # Get the most recent file
            pdf_file_path = max(pdf_files, key=os.path.getctime)
        
        # Return the file
        return FileResponse(
            path=pdf_file_path,
            media_type='application/pdf',
            filename=f"analysis_report_{customer_id}_{timestamp}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading report for {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading report: {str(e)}"
        )

@app.get("/customers", response_model=Dict[str, Any])
async def get_available_customers():
    """
    Get list of available customers and their information
    
    Returns information about all available customers in the system.
    """
    if not engine:
        raise HTTPException(
            status_code=500,
            detail="Recommendation engine not available"
        )
    
    try:
        customers_info = []
        for _, customer in engine.customers.iterrows():
            customers_info.append({
                "customer_id": customer['CustomerID'],
                "customer_name": customer['CustomerName'],
                "customer_type": customer['CustomerType'],
                "country": customer['Country'],
                "region": customer['Region'],
                "total_stores": customer['TotalStores']
            })
        
        return {
            "success": True,
            "customers": customers_info,
            "total_customers": len(customers_info)
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving customers: {str(e)}"
        )

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the API and recommendation engine.
    """
    engine_status = "healthy" if engine else "unhealthy"
    
    return {
        "status": "healthy",
        "engine_status": engine_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Helper functions
def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def save_recommendations_to_file(customer_id: str, recommendations_data: Dict[str, Any]):
    """Save recommendations to file in background"""
    try:
        timestamp = recommendations_data["timestamp"]
        filename = f"recommendations/recommendations_{customer_id}_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs("recommendations", exist_ok=True)
        
        # Convert numpy types and save to file
        converted_data = convert_numpy_types(recommendations_data)
        with open(filename, 'w') as f:
            json.dump(converted_data, f, indent=2, default=str)
        
        logger.info(f"💾 Recommendations saved to: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Error saving recommendations to file: {str(e)}")

def generate_pdf_report(customer_id: str, recommendations_data: Dict[str, Any]):
    """Generate PDF report"""
    try:
        timestamp = recommendations_data["timestamp"]
        json_filename = f"recommendations/recommendations_{customer_id}_{timestamp}.json"
        pdf_filename = f"reports/analysis_report_{customer_id}_{timestamp}.pdf"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Check if pdf_report_generator.py exists
        pdf_generator_path = "pdf_report_generator.py"
        if not os.path.exists(pdf_generator_path):
            logger.warning(f"⚠️  PDF report generation skipped (pdf_report_generator.py not found at {os.path.abspath(pdf_generator_path)})")
            logger.info(f"📁 Current working directory: {os.getcwd()}")
            logger.info(f"📁 Files in current directory: {os.listdir('.')}")
            return False
        
        # Import and use the PDF generator
        try:
            from pdf_report_generator import PDFReportGenerator
            generator = PDFReportGenerator()
            success = generator.generate_pdf_report(json_filename, pdf_filename)
            
            if success:
                logger.info(f"📄 PDF report generated: {pdf_filename}")
                return True
            else:
                logger.error(f"❌ Failed to generate PDF report: {pdf_filename}")
                return False
                
        except ImportError as import_err:
            logger.error(f"❌ Import error for PDF generator: {str(import_err)}")
            logger.info("💡 Make sure reportlab is installed: pip install reportlab")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error generating PDF report: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        return False

def get_customer_name(customer_id: str) -> str:
    """Get customer name from the engine"""
    if not engine:
        return "Unknown"
    
    try:
        customer_info = engine.customers[engine.customers['CustomerID'] == customer_id]
        if not customer_info.empty:
            return customer_info['CustomerName'].iloc[0]
        return "Unknown"
    except:
        return "Unknown"

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message="Request failed",
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error="An unexpected error occurred",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Strategy Agent 3.0 API Server")
    print("=" * 50)
    print("📚 API Documentation: http://localhost:8001/docs")
    print("📖 ReDoc Documentation: http://localhost:8001/redoc")
    print("🔍 Health Check: http://localhost:8001/health")
    print("=" * 50)
    
    uvicorn.run(
        "api_endpoint:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
