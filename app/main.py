from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.models import MathQuery, MathResponse
from app.pattern_matcher import PatternMatcher
from app.nlp_processor import NLPProcessor

app = FastAPI(
    title="Math NLP Parser API",
    description="Convert natural language mathematical expressions to LaTeX",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
pattern_matcher = PatternMatcher()
nlp_processor = NLPProcessor()

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Math NLP Parser API",
        "status": "running",
        "docs": "/docs",
        "ui": "/ui"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/parse", response_model=MathResponse)
def parse_math_expression(query: MathQuery):
    """
    Parse natural language mathematical expression to LaTeX
    
    Tries pattern matching first, then falls back to NLP if needed
    """
    text = query.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Empty query text")
    
    # Step 1: Try pattern matching (fast and accurate for common patterns)
    result = pattern_matcher.parse(text)
    
    if result:
        return MathResponse(**result)
    
    # Step 2: Fall back to NLP processing (for complex/ambiguous queries)
    result = nlp_processor.parse(text)
    
    if result:
        return MathResponse(**result)
    
    # Step 3: If both fail, return error
    raise HTTPException(
        status_code=422,
        detail="Could not parse the mathematical expression. Please try rephrasing."
    )

@app.post("/parse/pattern-only", response_model=MathResponse)
def parse_pattern_only(query: MathQuery):
    """Parse using only pattern matching (for testing)"""
    result = pattern_matcher.parse(query.text)
    
    if result:
        return MathResponse(**result)
    
    raise HTTPException(
        status_code=422,
        detail="Pattern matching failed. Try the main /parse endpoint."
    )

@app.post("/parse/nlp-only", response_model=MathResponse)
def parse_nlp_only(query: MathQuery):
    """Parse using only NLP (for testing)"""
    result = nlp_processor.parse(query.text)
    
    if result:
        return MathResponse(**result)
    
    raise HTTPException(
        status_code=422,
        detail="NLP parsing failed. Try the main /parse endpoint."
    )

@app.get("/ui")
def serve_ui():
    """Serve the HTML UI"""
    # Get the project root directory (parent of app folder)
    base_path = Path(__file__).parent.parent
    html_path = base_path / "index.html"
    return FileResponse(html_path)
