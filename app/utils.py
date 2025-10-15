import re
from typing import Dict, List

class TextNormalizer:
    """Normalize and clean mathematical text input"""
    
    def __init__(self):
        # Common typos and variations
        self.typo_corrections = {
            'square': 'squared',
            'cube': 'cubed',
            'sqaure': 'squared',  # typo
            'sqared': 'squared',  # typo
            'intergrate': 'integrate',  # typo
            'integrat': 'integrate',  # typo
            'derivate': 'derivative',  # typo
            'diferentiate': 'differentiate',  # typo
            'diferential': 'differential',  # typo
            'summaton': 'summation',  # typo
            'sumation': 'summation',  # typo
        }
        
        # Synonyms for operations
        self.synonyms = {
            'diff': 'derivative',
            'deriv': 'derivative',
            'd/dx': 'derivative',
            'int': 'integrate',
            'sigma': 'sum',
            'Σ': 'sum',
        }
        
        # Word normalizations
        self.normalizations = {
            r'\bwrt\b': 'with respect to',
            r'\bw\.r\.t\.?\b': 'with respect to',
            r'\brt\b': 'with respect to',
            r'\^': ' to the power of ',
        }
    
    def normalize(self, text: str) -> str:
        """Apply all normalizations to text"""
        text = text.lower().strip()
        
        # Fix common typos
        for typo, correct in self.typo_corrections.items():
            text = re.sub(r'\b' + typo + r'\b', correct, text)
        
        # Replace synonyms
        for synonym, standard in self.synonyms.items():
            text = re.sub(r'\b' + re.escape(synonym) + r'\b', standard, text)
        
        # Apply normalizations
        for pattern, replacement in self.normalizations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_math_entities(self, text: str) -> Dict:
        """Extract mathematical entities from text"""
        entities = {
            'functions': [],
            'variables': [],
            'numbers': [],
            'operations': []
        }
        
        # Extract trig functions
        trig_funcs = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'sinh', 'cosh', 'tanh']
        for func in trig_funcs:
            if func in text:
                entities['functions'].append(func)
        
        # Extract variables (single letters)
        variables = re.findall(r'\b([a-zA-Z])\b', text)
        entities['variables'] = list(set(variables))
        
        # Extract numbers
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
        entities['numbers'] = numbers
        
        return entities
