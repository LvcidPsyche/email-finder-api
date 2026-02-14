"""
Python client example for Email Finder API
"""
import requests
from typing import List, Dict, Optional


class EmailFinderClient:
    """Email Finder API Python client."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def find_email(
        self,
        domain: str,
        first_name: str,
        last_name: str
    ) -> Dict:
        """Find email patterns for a person."""
        response = requests.post(
            f"{self.base_url}/api/find-email",
            headers=self.headers,
            json={
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        response.raise_for_status()
        return response.json()
    
    def verify_email(self, email: str) -> Dict:
        """Verify if an email address is deliverable."""
        response = requests.post(
            f"{self.base_url}/api/verify-email",
            headers=self.headers,
            json={"email": email}
        )
        response.raise_for_status()
        return response.json()
    
    def verify_domain(self, domain: str) -> Dict:
        """Check if domain has valid mail configuration."""
        response = requests.post(
            f"{self.base_url}/api/verify-domain",
            headers=self.headers,
            json={"domain": domain}
        )
        response.raise_for_status()
        return response.json()
    
    def bulk_find(
        self,
        domain: str,
        names: List[Dict[str, str]]
    ) -> Dict:
        """Find emails for multiple people at once."""
        response = requests.post(
            f"{self.base_url}/api/bulk-find",
            headers=self.headers,
            json={
                "domain": domain,
                "names": names
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage(self) -> Dict:
        """Get current API usage statistics."""
        response = requests.get(
            f"{self.base_url}/api/usage",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = EmailFinderClient(api_key="your_api_key_here")
    
    # Find email for a person
    result = client.find_email(
        domain="example.com",
        first_name="John",
        last_name="Doe"
    )
    print("Found emails:", result["emails"])
    
    # Verify an email
    verification = client.verify_email("john.doe@example.com")
    print("Email deliverable:", verification["deliverable"])
    
    # Bulk find
    bulk_result = client.bulk_find(
        domain="example.com",
        names=[
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Smith"}
        ]
    )
    print(f"Processed {bulk_result['total_people']} people")
    
    # Check usage
    usage = client.get_usage()
    print(f"Requests today: {usage['total_calls']}/{usage['rate_limit']}")
