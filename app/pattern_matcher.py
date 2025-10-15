import re
from typing import Optional, Dict, Tuple
import sympy as sp
from app.utils import TextNormalizer

class PatternMatcher:
    """Rule-based pattern matching for common mathematical expressions"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
        
        # Common word-to-symbol mappings
        self.word_to_symbol = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiply': '*',
            'multiplied by': '*',
            'divided by': '/',
            'divide by': '/',
            'over': '/',
            'squared': '^2',
            'square': '^2',  # Accept both!
            'cubed': '^3',
            'cube': '^3',  # Accept both!
            'square root': 'sqrt',
            'cube root': 'cbrt',
            'sqrt': 'sqrt',
        }
        
        # Trig function mappings
        self.trig_functions = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 
                               'sinh', 'cosh', 'tanh', 'arcsin', 'arccos', 'arctan',
                               'asin', 'acos', 'atan']
        
        # Define patterns with their handlers
        self.patterns = [
            # Integration patterns - more flexible
            (r'integrate\s+(.+?)\s+(?:with\s+respect\s+to|wrt|w\.?r\.?t\.?)\s+([a-zA-Z])', self._handle_integral),
            (r'integral\s+of\s+(.+?)\s+(?:d|with\s+respect\s+to)\s*([a-zA-Z])', self._handle_integral),
            (r'integrate\s+(.+?)\s+d([a-zA-Z])', self._handle_integral),
            (r'int\s+(.+?)\s+d([a-zA-Z])', self._handle_integral),
            
            # Derivative patterns - more flexible
            (r'derivative\s+of\s+(.+?)\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z])', self._handle_derivative),
            (r'differentiate\s+(.+?)\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z])', self._handle_derivative),
            (r'deriv(?:ative)?\s+of\s+(.+?)\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z])', self._handle_derivative),
            (r'd/d([a-zA-Z])\s+(?:of\s+)?(.+)', self._handle_derivative_short),
            
            # Partial derivative patterns (NEW) - more specific ordering
            (r'partial\s+derivative\s+of\s+(.+?)\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z])', self._handle_partial),
            (r'partial\s+(.+?)\s+(?:with\s+respect\s+to|wrt)\s+([a-zA-Z])', self._handle_partial),
            
            # Summation patterns
            (r'sum\s+(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)\s+(?:of\s+)?(.+)', self._handle_summation),
            (r'summation\s+(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)\s+(?:of\s+)?(.+)', self._handle_summation),
            (r'sigma\s+(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)\s+(?:of\s+)?(.+)', self._handle_summation),
            
            # Product patterns (NEW)
            (r'product\s+(?:from|of)\s+([a-zA-Z])\s*(?:equals|=)\s*([a-zA-Z0-9]+)\s+to\s+([a-zA-Z0-9]+)\s+(?:of\s+)?(.+)', self._handle_product),
            
            # Limit patterns
            (r'limit\s+as\s+([a-zA-Z])\s+(?:approaches|goes\s+to|tends\s+to)\s+(.+?)\s+of\s+(.+)', self._handle_limit),
            (r'lim\s+([a-zA-Z])\s*->\s*(.+?)\s+(?:of\s+)?(.+)', self._handle_limit),
            
            # Fraction patterns (NEW) - Put this at the end to avoid conflicts
            (r'(.+?)\s+(?:divided\s+by|over)\s+(.+)', self._handle_fraction),
        ]
    
    def parse(self, text: str) -> Optional[Dict]:
        """Try to match text against patterns"""
        # First normalize the text
        text = self.normalizer.normalize(text)
        text = text.lower().strip()
        
        # Try each pattern
        for pattern, handler in self.patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result = handler(match)
                    if result:
                        return result
                except Exception as e:
                    print(f"Error in handler: {e}")
                    continue
        
        return None
    
    def _preprocess_expression(self, expr: str) -> str:
        """Preprocess expression to convert words to symbols"""
        expr = expr.strip()
        
        # Replace word representations with symbols
        for word, symbol in self.word_to_symbol.items():
            expr = re.sub(r'\b' + word + r'\b', symbol, expr, flags=re.IGNORECASE)
        
        # Handle "x squared", "x square", "y cubed", "y cube" etc
        expr = re.sub(r'([a-zA-Z0-9]+)\s+(?:squared|square)', r'\1^2', expr, flags=re.IGNORECASE)
        expr = re.sub(r'([a-zA-Z0-9]+)\s+(?:cubed|cube)', r'\1^3', expr, flags=re.IGNORECASE)
        expr = re.sub(r'([a-zA-Z0-9]+)\s+to\s+the\s+(?:power\s+of\s+)?(\d+)(?:th|rd|nd|st)?', r'\1^\2', expr, flags=re.IGNORECASE)
        
        # Handle trig functions: "sin x" -> "sin(x)"
        for func in self.trig_functions:
            expr = re.sub(rf'\b{func}\s+([a-zA-Z0-9]+)', rf'{func}(\1)', expr, flags=re.IGNORECASE)
        
        # Handle other common functions
        expr = re.sub(r'\blog\s+([a-zA-Z0-9]+)', r'log(\1)', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bln\s+([a-zA-Z0-9]+)', r'ln(\1)', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bexp\s+([a-zA-Z0-9]+)', r'exp(\1)', expr, flags=re.IGNORECASE)
        
        return expr
    
    def _handle_integral(self, match) -> Dict:
        """Handle integration patterns"""
        expr_str = match.group(1).strip()
        var = match.group(2).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\int {sp.latex(expr)} \\, d{var}"
            plain = f"Integral of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.9
            }
        except Exception as e:
            print(f"Integral error: {e}")
            return None
    
    def _handle_derivative(self, match) -> Dict:
        """Handle derivative patterns"""
        expr_str = match.group(1).strip()
        var = match.group(2).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\frac{{d}}{{d{var}}} {sp.latex(expr)}"
            plain = f"Derivative of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.9
            }
        except:
            return None
    
    def _handle_derivative_short(self, match) -> Dict:
        """Handle d/dx notation"""
        var = match.group(1).strip()
        expr_str = match.group(2).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\frac{{d}}{{d{var}}} {sp.latex(expr)}"
            plain = f"Derivative of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.85
            }
        except:
            return None
    
    def _handle_summation(self, match) -> Dict:
        """Handle summation patterns"""
        var = match.group(1).strip()
        start = match.group(2).strip()
        end = match.group(3).strip()
        expr_str = match.group(4).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        # Additional preprocessing for summation variable
        expr_str = re.sub(rf'\b{var}\s+(?:squared|square)', f'{var}^2', expr_str, flags=re.IGNORECASE)
        expr_str = re.sub(rf'\b{var}\s+(?:cubed|cube)', f'{var}^3', expr_str, flags=re.IGNORECASE)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\sum_{{{var}={start}}}^{{{end}}} {sp.latex(expr)}"
            plain = f"Sum from {var}={start} to {end} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.9
            }
        except Exception as e:
            print(f"Summation error: {e}")
            return None
    
    def _handle_product(self, match) -> Dict:
        """Handle product patterns (NEW)"""
        var = match.group(1).strip()
        start = match.group(2).strip()
        end = match.group(3).strip()
        expr_str = match.group(4).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\prod_{{{var}={start}}}^{{{end}}} {sp.latex(expr)}"
            plain = f"Product from {var}={start} to {end} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.9
            }
        except Exception as e:
            print(f"Product error: {e}")
            return None
    
    def _handle_limit(self, match) -> Dict:
        """Handle limit patterns"""
        var = match.group(1).strip()
        approach = match.group(2).strip()
        expr_str = match.group(3).strip()
        
        expr_str = self._preprocess_expression(expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            # Handle infinity
            if approach.lower() in ['infinity', 'inf', '∞']:
                approach = '\\infty'
            
            latex = f"\\lim_{{{var} \\to {approach}}} {sp.latex(expr)}"
            plain = f"Limit as {var} approaches {approach} of {expr}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.85
            }
        except:
            return None
    
    def _handle_partial(self, match) -> Dict:
        """Handle partial derivative patterns (IMPROVED)"""
        expr_str = match.group(1).strip()
        var = match.group(2).strip()
        
        # Remove "of" if it's at the start
        expr_str = re.sub(r'^of\s+', '', expr_str)
        
        expr_str = self._preprocess_expression(expr_str)
        
        # Handle implicit multiplication like "x squared y" -> "x^2*y"
        # Match patterns like "x^2 y" or "2 x" and insert multiplication
        expr_str = re.sub(r'(\d+|[a-zA-Z](?:\^\d+)?)\s+([a-zA-Z])', r'\1*\2', expr_str)
        
        try:
            var_sym = sp.Symbol(var)
            expr = sp.sympify(expr_str)
            
            latex = f"\\frac{{\\partial}}{{\\partial {var}}} {sp.latex(expr)}"
            plain = f"Partial derivative of {expr} with respect to {var}"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.85
            }
        except Exception as e:
            print(f"Partial derivative error: {e}")
            return None
    
    def _handle_fraction(self, match) -> Dict:
        """Handle fraction patterns (NEW)"""
        numerator = match.group(1).strip()
        denominator = match.group(2).strip()
        
        numerator = self._preprocess_expression(numerator)
        denominator = self._preprocess_expression(denominator)
        
        try:
            num_expr = sp.sympify(numerator)
            den_expr = sp.sympify(denominator)
            
            latex = f"\\frac{{{sp.latex(num_expr)}}}{{{sp.latex(den_expr)}}}"
            plain = f"({num_expr}) / ({den_expr})"
            
            return {
                'latex': latex,
                'plain_text': plain,
                'method_used': 'pattern_matching',
                'confidence': 0.8
            }
        except:
            return None
