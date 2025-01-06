"""Utility functions for data validation."""

def is_structured_data(data):
    """
    Determine if the data follows the structured format.
    
    Args:
        data (dict): The data to validate
        
    Returns:
        bool: True if data is structured, False otherwise
    """
    return isinstance(data, dict) and "Meta Data" in data