# Math NLP Parser

A FastAPI-based web application that converts natural language mathematical expressions into LaTeX notation using a hybrid approach of pattern matching and NLP processing.

## Features

- **Hybrid Parsing**: Combines fast pattern matching with robust NLP fallback
- **Multiple Operations**: Supports integration, derivatives, limits, summations, products, and more
- **Typo Tolerant**: Handles common typos and variations in mathematical expressions
- **Beautiful UI**: Clean, responsive web interface with live LaTeX rendering
- **RESTful API**: Well-documented API with automatic Swagger documentation
- **High Confidence Scores**: Provides reliability indicators for parsed expressions

## Supported Mathematical Operations

| Operation | Example Input | LaTeX Output |
|-----------|---------------|--------------|
| Integration | "integrate x squared with respect to y" | `\int x^{2} \, dy` |
| Derivatives | "derivative of sin x with respect to x" | `\frac{d}{dx} \sin(x)` |
| Partial Derivatives | "partial derivative of x squared y wrt x" | `\frac{\partial}{\partial x} x^{2}y` |
| Limits | "limit as x approaches 0 of sin x over x" | `\lim_{x \to 0} \frac{\sin(x)}{x}` |
| Summations | "sum from i equals 1 to n of i squared" | `\sum_{i=1}^{n} i^{2}` |
| Products | "product from i equals 1 to n of i" | `\prod_{i=1}^{n} i` |
| Fractions | "x squared plus 1 over x minus 1" | `\frac{x^{2} + 1}{x - 1}` |

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/Avirral/math-nlp-parser.git
   cd math-nlp-parser
```

2. **Create and activate virtual environment**
```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate on Linux/Mac
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Download spaCy language model**
```bash
   python -m spacy download en_core_web_sm
```

5. **Create .env file**
```bash
   # Create a .env file with the following content:
   HOST=0.0.0.0
   PORT=8000
   RELOAD=True
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   APP_NAME="Math NLP Parser"
   APP_VERSION="1.0.0"
```

6. **Run the application**
```bash
   python run.py
```

7. **Access the application**
   - Web UI: http://localhost:8000/ui
   - API Documentation: http://localhost:8000/docs
   - API Root: http://localhost:8000

## Project Structure
```
math-nlp-parser/
├── app/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # FastAPI app with endpoints
│   ├── models.py                # Pydantic models
│   ├── pattern_matcher.py       # Pattern matching logic
│   ├── nlp_processor.py         # NLP fallback processor
│   └── utils.py                 # Text normalization utilities
├── tests/
│   ├── __init__.py
│   ├── test_patterns.py         # Pattern matching tests
│   └── test_api.py              # API endpoint tests
├── venv/                        # Virtual environment (not in git)
├── index.html                   # Frontend UI
├── requirements.txt             # Python dependencies
├── run.py                       # Server startup script
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## API Usage

### Parse Endpoint

**POST** `/parse`

Convert natural language to LaTeX.

**Request:**
```json
{
  "text": "integrate x squared with respect to y"
}
```

**Response:**
```json
{
  "latex": "\\int x^{2} \\, dy",
  "plain_text": "Integral of x**2 with respect to y",
  "method_used": "pattern_matching",
  "confidence": 0.9
}
```

### Example using curl:
```bash
curl -X POST "http://localhost:8000/parse" \
  -H "Content-Type: application/json" \
  -d '{"text": "derivative of sin x with respect to x"}'
```

### Example using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/parse",
    json={"text": "limit as x approaches 0 of sin x over x"}
)

result = response.json()
print(f"LaTeX: {result['latex']}")
print(f"Method: {result['method_used']}")
print(f"Confidence: {result['confidence']}")
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_patterns.py
```

## Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **NLP Library**: spaCy 3.7.2
- **Math Processing**: SymPy 1.12
- **Server**: Uvicorn (ASGI)
- **Frontend**: Vanilla JavaScript + MathJax
- **Python Version**: 3.8+

## How It Works

### Hybrid Approach

1. **Pattern Matching** (First Priority)
   - Fast regex-based matching
   - High confidence (0.85-0.9)
   - Handles well-formed expressions

2. **NLP Fallback** (If pattern fails)
   - Uses spaCy for natural language understanding
   - Handles typos and casual phrasing
   - Lower confidence (0.6-0.7)

### Text Normalization

The system automatically handles:
- Common typos: "intergrate" → "integrate"
- Synonyms: "diff" → "derivative", "sigma" → "sum"
- Abbreviations: "wrt" → "with respect to"
- Power notation: "squared" → "^2"

## Examples

### Working Examples:
```
✓ "integrate x squared with respect to y"
✓ "derivative of sin x wrt x"
✓ "lim x goes to 0 of x squared"
✓ "sum from i=1 to n of i cubed"
✓ "partial derivative of x squared y with respect to x"
✓ "I want to find the integral of cos x" (casual phrasing)
✓ "integrate x square wrt y" (typo: "square" instead of "squared")
```

## Contributing

This is a college project. If you're a teammate:

1. Create a new branch for your feature
```bash
   git checkout -b feature/your-feature-name
```

2. Make your changes and commit
```bash
   git add .
   git commit -m "Description of changes"
```

3. Push to the branch
```bash
   git push origin feature/your-feature-name
```

4. Create a Pull Request

## Team Members

- Avirral Singh 
- Aditya Induraj
- Kshiraj Nair

## Acknowledgments

- Built as part of NLP project
- spaCy for NLP capabilities
- SymPy for mathematical processing
- FastAPI for the excellent web framework