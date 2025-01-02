"""
Input validation and sanitization module.
"""
from typing import Any, Dict, List, Optional, Union
import re
from dataclasses import dataclass
from loguru import logger
from functools import wraps

@dataclass
class ValidationRule:
    """Validation rule with constraints."""
    field_type: type
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None

class InputValidator:
    """Input validation and sanitization."""
    
    def __init__(self):
        """Initialize input validator."""
        self.logger = logger.bind(module="input_validator")
        self.rules: Dict[str, ValidationRule] = {}
    
    def add_rule(self, field: str, rule: ValidationRule):
        """Add a validation rule for a field."""
        self.rules[field] = rule
        self.logger.debug(f"Added validation rule for {field}")
    
    def validate_field(self, field: str, value: Any) -> List[str]:
        """Validate a single field against its rules."""
        errors = []
        rule = self.rules.get(field)
        
        if not rule:
            return []
        
        # Type validation
        if not isinstance(value, rule.field_type):
            errors.append(f"{field} must be of type {rule.field_type.__name__}")
            return errors
        
        # Length validation for strings
        if isinstance(value, str):
            if rule.min_length and len(value) < rule.min_length:
                errors.append(f"{field} must be at least {rule.min_length} characters")
            if rule.max_length and len(value) > rule.max_length:
                errors.append(f"{field} must be at most {rule.max_length} characters")
        
        # Pattern validation
        if rule.pattern and isinstance(value, str):
            if not re.match(rule.pattern, value):
                errors.append(f"{field} does not match required pattern")
        
        # Allowed values validation
        if rule.allowed_values is not None and value not in rule.allowed_values:
            errors.append(f"{field} must be one of {rule.allowed_values}")
        
        # Custom validation
        if rule.custom_validator:
            try:
                if not rule.custom_validator(value):
                    errors.append(f"{field} failed custom validation")
            except Exception as e:
                errors.append(f"{field} validation error: {str(e)}")
        
        return errors
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate all fields in data."""
        errors = []
        
        for field, value in data.items():
            field_errors = self.validate_field(field, value)
            errors.extend(field_errors)
        
        return errors
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32)
        
        # Convert to proper string
        value = str(value)
        
        # Basic HTML escape
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        
        return value
    
    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all string values in data."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_string(v) if isinstance(v, str)
                    else self.sanitize(v) if isinstance(v, dict)
                    else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized

def validate_input(validator: InputValidator):
    """Decorator for input validation."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Combine args and kwargs into a single dict
            all_args = {}
            if args:
                # Assume first arg is the main input dict
                if isinstance(args[0], dict):
                    all_args.update(args[0])
            all_args.update(kwargs)
            
            # Validate
            errors = validator.validate(all_args)
            if errors:
                raise ValidationError(errors)
            
            # Sanitize
            sanitized = validator.sanitize(all_args)
            
            # Call function with sanitized input
            if args:
                if isinstance(args[0], dict):
                    args = (sanitized,) + args[1:]
            else:
                kwargs = sanitized
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__('; '.join(errors))
