from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from utils.parse_pdf import extract_info_from_pdf
from graph_flow import run_vc_analysis
from typing import Dict, Any
from langchain_core.messages import AIMessage
import json

app = FastAPI(title="VC Pitch Deck Analyzer API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_aimessages_to_strings(obj):
    """Recursively convert AIMessage objects to strings for JSON serialization"""
    if isinstance(obj, AIMessage):
        return str(obj.content)
    elif isinstance(obj, dict):
        return {key: convert_aimessages_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_aimessages_to_strings(item) for item in obj]
    else:
        return obj

@app.post("/analyze-pitch-deck")
async def analyze_pitch_deck(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze a pitch deck PDF and return insights with feedback mapped to slide coordinates.

    Returns:
        JSON with analysis results including:
        - matched_feedback: List of feedback items with coordinates and status
        - tam_sam_info: Market size analysis
        - team_feedback: Team analysis
        - general_context: Overall deck summary
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Extract PDF content
            page_content, whole_text = extract_info_from_pdf(temp_file_path)

            # Run the analysis
            analysis_result = run_vc_analysis(page_content, whole_text)

            # Debug: Print the structure to identify AIMessage objects
            print("Analysis result keys:", list(analysis_result.keys()))
            for key, value in analysis_result.items():
                print(f"Key: {key}, Type: {type(value)}")
                if hasattr(value, 'content'):
                    print(f"  Has content attribute: {type(value.content)}")

            # Convert AIMessage objects to strings for JSON serialization
            analysis_result = convert_aimessages_to_strings(analysis_result)
            print(analysis_result)

            # Prepare response for frontend
            response_data = {
                "success": True,
                "formated_feedback": analysis_result.keys(),
                "matched_feedback": analysis_result.get("matched_feedback", []),
                "tam_sam_info": analysis_result.get("tam_sam_info", ""),
                "tam_sam_sources": analysis_result.get("tam_sam_sources", []),
                "team_feedback": analysis_result.get("page_feedback", {}),
                "general_context": analysis_result.get("general_context", ""),
                "topics": analysis_result.get("topics", []),
                "total_pages": len(page_content)
            }
            # convert to json
            response_data = json.dumps(response_data)
            return JSONResponse(content=response_data)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "VC Pitch Deck Analyzer"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VC Pitch Deck Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze-pitch-deck",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)