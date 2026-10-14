"""
SweetyAI LinkedIn Integration Connector
Publishes posts and compliance summaries programmatically via LinkedIn REST API (/rest/posts).
"""

import os
import json
import requests
import logging

logging.basicConfig(level=logging.INFO, format="[SweetyAI LinkedIn] %(levelname)s: %(message)s")

class LinkedInConnector:
    def __init__(self):
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        self.api_url = "https://api.linkedin.com/rest/posts"
        self.version_header = "202610" # Current LinkedIn API version header

    def publish_post(self, author_urn: str, commentary: str):
        """
        Publishes a text post to a personal profile (urn:li:person:{id}) 
        or company page (urn:li:organization:{id}).
        """
        if not self.access_token:
            logging.warning("LINKEDIN_ACCESS_TOKEN environment variable not set. Running in dry-run simulation mode.")
            return {
                "status": "simulated_success",
                "author": author_urn,
                "commentary": commentary
            }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": self.version_header
        }

        payload = {
            "author": author_urn,
            "commentary": commentary,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                logging.info("Successfully published post to LinkedIn!")
                return {"status": "success", "response_code": response.status_code}
            else:
                logging.error(f"Failed to publish to LinkedIn: {response.status_code} - {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}
        except Exception as e:
            logging.error(f"Exception during LinkedIn API request: {e}")
            return {"status": "exception", "error": str(e)}

if __name__ == "__main__":
    connector = LinkedInConnector()
    test_message = "Automated legal compliance insight generated via SweetyAI Enterprise Workstation (BNS / BNSS Framework)."
    result = connector.publish_post("urn:li:person:YOUR_PERSON_ID", test_message)
    print(json.dumps(result, indent=2))
