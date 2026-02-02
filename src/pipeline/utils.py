"""
Pipeline Utilities.

Helper functions and classes for the pipeline.
"""

class LinkedInURL:
    """Helper for constructing properly formatted LinkedIn URLs."""
    
    BASE = "https://linkedin.com"
    
    @staticmethod
    def company(name: str) -> str:
        """Generate a company page URL from a company name."""
        if not name:
            return ""
        slug = name.strip().replace(' ', '-').lower()
        return f"{LinkedInURL.BASE}/company/{slug}"

    @staticmethod
    def person(name: str) -> str:
        """Generate a profile URL from a person's name."""
        if not name:
            return ""
        slug = name.strip().replace(' ', '-').lower()
        return f"{LinkedInURL.BASE}/in/{slug}"
