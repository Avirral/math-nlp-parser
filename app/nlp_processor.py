import spacy
from typing import Optional, Dict, List
import sympy as sp
import re
from app.utils import TextNormalizer

class NLPProcessor:
    """NLP-based processor for complex mathematical expressions"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: spaCy model not loaded. NLP fallback will not work.")
            self.nlp = None
        
        self.normalizer = TextNormalizer()
        
        # Mathematical keywords mapping
        self.math_operations = {
            'integrate': 'integral',
            'integration': 'integral',
            'integral': 'integral',
            'derivative': 'derivative',
            'differentiate': 'derivative',
            'diff': 'derivative',
            'derive': 'derivative',
            'sum': 'summation',
            'summation': 'summation',
            'sigma': 'summation',
            'product': 'product',
            'limit': 'limit',
            'lim': 'limit',
            'partial': 'partial_derivative',
        }
        
        self.function_words = ['sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 
                               'sec', 'csc', 'cot', 'arcsin', 'arccos', 'arctan']
        
        # Power words
        self.power_indicators = ['squared', 'square', 'cubed', 'cube', 'power', 'exponent']
        
        # Common filler words to remove
        self.filler_words = ['i', 'want', 'to', 'find', 'the', 'please', 'can', 'you', 
                            'calculate', 'compute', 'determine', 'what', 'is', 'help', 
                            'me', 'solve', 'get', 'give', 'show']
    
    def parse(self, text: str) -> Optional[Dict]:
        """Use NLP to parse mathematical expressions"""
        if not self.nlp:
            return None
        
        # Normalize text first
        text = self.normalizer.normalize(text)
        text = text.lower().strip()
        
        doc = self.nlp(text)
        
        # Extract operation type
        operation = self._extract_operation(text)
        
        # Try to parse based on operation
        if operation == 'integral':
            return self._parse_integral_nlp(text, doc)
        elif operation == 'derivative':
            return self._parse_derivative_nlp(text, doc)
        elif operation == 'partial_derivative':
            return self._parse_partial_derivative_nlp(text, doc)
        elif operation == 'summation':
            return self._parse_summation_nlp(text, doc)
        elif operation == 'product':
            return self._parse_product_nlp(text, doc)
        elif operation == 'limit':
            return self._parse_limit_nlp(text, doc)
        else:
            # Try to parse as a simple expression
            return self._parse_simple_expression(text)
        
        return None
    
    def _extract_operation(self, text: str) -> Optional[str]:
        """Extract the main mathematical operation from text"""
        text_lower = text.lower()
        
        # Check for operation keywords
        for keyword, operation in self.math_operations.items():
            if keyword in text_lower:
                return operation
        
        return None
    
    def _extract_variable(self, text: str) -> str:
        """Extract variable name (usually single letter)"""
        # Look for "with respect to X", "wrt X", "dx", etc.
        patterns = [
            r'with\s+respect\s+to\s+([a-zA-Z])',
            r'wrt\s+([a-zA-Z])',
            r'w\.r\.t\.?\s+([a-zA-Z])',
            r'd([a-zA-Z])\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        # Look for single letters in the text (excluding filler words)
        single_letters = re.findall(r'\b([a-zA-Z])\b', text)
        if single_letters:
            # Filter out filler words
            valid_letters = [l for l in single_letters if l not in self.filler_words]
            
            if valid_letters:
                # Prefer x, y, z, t as common variables
                for var in ['x', 'y', 'z', 't', 'n', 'i', 'j', 'k']:
                    if var in valid_letters:
                        return var
                return valid_letters[0]
        
        return 'x'  # Default
    
    def _clean_expression(self, text: str, remove_words: List[str]) -> str:
        """Clean expression by removing operation keywords"""
        expr = text
        for word in remove_words:
            expr = re.sub(r'\b' + word + r'\b', ' ', expr, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        expr = re.sub(r'\s+', ' ', expr).strip()
        return expr
    
    def _preprocess_math_text(self, text: str) -> str:
        """Preprocess mathematical text for sympify"""
        # Handle power words
        text = re.sub(r'([a-zA-Z0-9]+)\s+(?:squared|square)', r'\1**2', text)
        text = re.sub(r'([a-zA-Z0-9]+)\s+(?:cubed|cube)', r'\1**3', text)
        text = re.sub(r'([a-zA-Z0-9]+)\s+to\s+the\s+(?:power\s+of\s+)?(\d+)', r'\1**\2', text)
        
        # Handle operations
        text = text.replace('plus', '+').replace('minus', '-')
        text = text.replace('times', '*').replace('multiply', '*')
        text = text.replace('divided by', '/').replace('over', '/')
        
        # Handle functions
        for func in self.function_words:
            text = re.sub(rf'\b{func}\s+([a-zA-Z0-9]+)', rf'{func}(\1)', text)
        
        # Handle implicit multiplication "2x" -> "2*x"
        text = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', text)
        
        # Handle "x y" -> "x*y" for implicit multiplication
        text = re.sub(r'([a-zA-Z](?:\*\*\d+)?)\s+([a-zA-Z])', r'\1*\2', text)
        
        return text
    
    def _parse_integral_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse integral using NLP"""
        try:
            var = self._extract_variable(text)
            
            # Remove operation words AND common filler words
            remove_words = ['integrate', 'integral', 'integration', 'of', 'with', 'respect', 'to', 'wrt', 
                            f'd{var}'] + self.filler_words
            expr_text = self._clean_expression(text, remove_words)
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            
            # Remove the variable reference at the end if present
            expr_text = re.sub(rf'\b{var}\s*$', '', expr_text).strip()
            
            if not expr_text:
                return None
            
            # Try to sympify
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\int {sp.latex(expr)} \\, d{var}"
            plain = f"Integral of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.7
            }
        except Exception as e:
            print(f"NLP integral parsing error: {e}")
            return None
    
    def _parse_derivative_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse derivative using NLP"""
        try:
            var = self._extract_variable(text)
            
            # Remove operation words AND common filler words
            remove_words = ['derivative', 'differentiate', 'diff', 'derive', 'of', 'with', 'respect', 'to', 'wrt',
                            f'd{var}'] + self.filler_words
            expr_text = self._clean_expression(text, remove_words)
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            
            # Remove the variable reference
            expr_text = re.sub(rf'\b{var}\s*$', '', expr_text).strip()
            
            if not expr_text:
                return None
            
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\frac{{d}}{{d{var}}} {sp.latex(expr)}"
            plain = f"Derivative of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.7
            }
        except Exception as e:
            print(f"NLP derivative parsing error: {e}")
            return None
    
    def _parse_partial_derivative_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse partial derivative using NLP"""
        try:
            var = self._extract_variable(text)
            
            # Remove operation words AND common filler words
            remove_words = ['partial', 'derivative', 'of', 'with', 'respect', 'to', 'wrt'] + self.filler_words
            expr_text = self._clean_expression(text, remove_words)
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            
            if not expr_text:
                return None
            
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\frac{{\\partial}}{{\\partial {var}}} {sp.latex(expr)}"
            plain = f"Partial derivative of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.65
            }
        except Exception as e:
            print(f"NLP partial derivative parsing error: {e}")
            return None
    
    def _parse_summation_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse summation using NLP"""
        try:
            # Extract summation variable
            var_match = re.search(r'(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)', text)
            
            if not var_match:
                return None
            
            var = var_match.group(1)
            start = var_match.group(2)
            end = var_match.group(3)
            
            # Extract expression
            remove_words = ['sum', 'summation', 'sigma', 'from', 'of', 'to', 'equals', start, end] + self.filler_words
            expr_text = self._clean_expression(text, remove_words)
            expr_text = expr_text.replace(var, '').replace('=', '').strip()
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            expr_text = expr_text.replace(var, f'{var}')  # Put var back
            
            if not expr_text:
                expr_text = var
            
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\sum_{{{var}={start}}}^{{{end}}} {sp.latex(expr)}"
            plain = f"Sum from {var}={start} to {end} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.65
            }
        except Exception as e:
            print(f"NLP summation parsing error: {e}")
            return None
    
    def _parse_product_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse product using NLP"""
        try:
            # Extract product variable
            var_match = re.search(r'(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)', text)
            
            if not var_match:
                return None
            
            var = var_match.group(1)
            start = var_match.group(2)
            end = var_match.group(3)
            
            # Extract expression
            remove_words = ['product', 'from', 'of', 'to', 'equals', start, end] + self.filler_words
            expr_text = self._clean_expression(text, remove_words)
            expr_text = expr_text.replace(var, '').replace('=', '').strip()
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            expr_text = expr_text.replace(var, f'{var}')
            
            if not expr_text:
                expr_text = var
            
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\prod_{{{var}={start}}}^{{{end}}} {sp.latex(expr)}"
            plain = f"Product from {var}={start} to {end} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.65
            }
        except Exception as e:
            print(f"NLP product parsing error: {e}")
            return None
    
    def _parse_limit_nlp(self, text: str, doc) -> Optional[Dict]:
        """Parse limit using NLP - FIXED v2"""
        try:
            # More flexible pattern
            var_match = re.search(r'(?:lim|limit|as)\s+([a-zA-Z])\s+(?:approaches|goes\s+to|tends\s+to|->)\s+([a-zA-Z0-9]+|infinity|inf)\s+(?:of\s+)?(.+)', text)
            
            if not var_match:
                return None
            
            var = var_match.group(1)
            approach = var_match.group(2)
            expr_text = var_match.group(3)  # Directly capture the expression part
            
            # Handle infinity
            if approach.lower() in ['infinity', 'inf']:
                approach = '\\infty'
            
            # Remove common filler words only
            remove_words = self.filler_words
            expr_text = self._clean_expression(expr_text, remove_words)
            
            # Preprocess the expression
            expr_text = self._preprocess_math_text(expr_text)
            expr_text = expr_text.strip()
            
            if not expr_text:
                return None
            
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_text)
            
            latex = f"\\lim_{{{var} \\to {approach}}} {sp.latex(expr)}"
            plain = f"Limit as {var} approaches {approach} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'nlp',
                'confidence': 0.7
            }
        except Exception as e:
            print(f"NLP limit parsing error: {e}")
            return None
    
    def _parse_simple_expression(self, text: str) -> Optional[Dict]:
        """Try to parse as a simple mathematical expression"""
        try:
            # Remove filler words first
            expr_text = self._clean_expression(text, self.filler_words)
            
            # Preprocess
            expr_text = self._preprocess_math_text(expr_text)
            
            expr = sp.sympify(expr_text)
            latex = sp.latex(expr)
            
            return {
                'latex': latex,
                'plain_text': str(expr),
                'method_used': 'nlp',
                'confidence': 0.6
            }
        except Exception as e:
            print(f"NLP simple expression parsing error: {e}")
            return None
