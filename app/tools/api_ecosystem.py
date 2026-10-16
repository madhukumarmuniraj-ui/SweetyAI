"""
SweetyAI API Ecosystem Tools
OAuth2, webhooks, REST API wrappers, rate limiting, API key management
"""

import time
import hashlib
import hmac
import json
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from urllib.parse import urlencode, parse_qs

# OAuth2
try:
    from requests_oauthlib import OAuth2Session
    OAUTH2_AVAILABLE = True
except ImportError:
    OAUTH2_AVAILABLE = False
    print("[API Ecosystem] OAuth2 not available. Run: pip install requests-oauthlib")


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """Token bucket rate limiter with configurable limits."""

    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default 60s)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str = "default") -> bool:
        """Check if request is allowed under rate limit."""
        with self.lock:
            current_time = time.time()

            # Remove old requests outside time window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if current_time - req_time < self.time_window
            ]

            # Check if under limit
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(current_time)
                return True

            return False

    def get_wait_time(self, key: str = "default") -> float:
        """Get time to wait before next request is allowed."""
        with self.lock:
            if not self.requests[key]:
                return 0.0

            current_time = time.time()
            oldest_request = min(self.requests[key])
            wait_time = self.time_window - (current_time - oldest_request)

            return max(0.0, wait_time)

    def reset(self, key: str = "default"):
        """Reset rate limit for a key."""
        with self.lock:
            self.requests[key] = []


# =============================================================================
# RETRY LOGIC
# =============================================================================

class RetryStrategy:
    """Configurable retry strategy with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retry_on_status: List[int] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_status = retry_on_status or [429, 500, 502, 503, 504]

    def should_retry(self, attempt: int, status_code: int = None) -> bool:
        """Check if should retry based on attempt number and status code."""
        if attempt >= self.max_retries:
            return False

        if status_code and status_code not in self.retry_on_status:
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for next retry attempt."""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


def with_retry(func: Callable, retry_strategy: RetryStrategy = None):
    """Decorator to add retry logic to functions."""
    retry_strategy = retry_strategy or RetryStrategy()

    def wrapper(*args, **kwargs):
        attempt = 0

        while True:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None

                if not retry_strategy.should_retry(attempt, status_code):
                    raise

                delay = retry_strategy.get_delay(attempt)
                print(f"Retry attempt {attempt + 1} after {delay}s...")
                time.sleep(delay)
                attempt += 1

    return wrapper


# =============================================================================
# REST API CLIENT
# =============================================================================

class RESTAPIClient:
    """Generic REST API client with rate limiting and retry logic."""

    def __init__(
        self,
        base_url: str,
        api_key: str = None,
        rate_limiter: RateLimiter = None,
        retry_strategy: RetryStrategy = None,
        default_headers: Dict[str, str] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=60, time_window=60)
        self.retry_strategy = retry_strategy or RetryStrategy()
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'SweetyAI/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

        if default_headers:
            self.session.headers.update(default_headers)

        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        headers: Dict = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting and retry."""
        # Check rate limit
        if not self.rate_limiter.is_allowed():
            wait_time = self.rate_limiter.get_wait_time()
            time.sleep(wait_time)

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        attempt = 0
        while True:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )

                response.raise_for_status()

                return {
                    'status_code': response.status_code,
                    'data': response.json() if response.content else None,
                    'headers': dict(response.headers)
                }

            except requests.exceptions.RequestException as e:
                status_code = e.response.status_code if hasattr(e, 'response') else None

                if not self.retry_strategy.should_retry(attempt, status_code):
                    return {
                        'error': str(e),
                        'status_code': status_code
                    }

                delay = self.retry_strategy.get_delay(attempt)
                time.sleep(delay)
                attempt += 1

    def get(self, endpoint: str, params: Dict = None, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return self._make_request('GET', endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        """POST request."""
        return self._make_request('POST', endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        """PUT request."""
        return self._make_request('PUT', endpoint, data=data, **kwargs)

    def patch(self, endpoint: str, data: Dict = None, **kwargs) -> Dict[str, Any]:
        """PATCH request."""
        return self._make_request('PATCH', endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request."""
        return self._make_request('DELETE', endpoint, **kwargs)


# =============================================================================
# OAUTH2 CLIENT
# =============================================================================

class OAuth2Client:
    """OAuth2 authentication client."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_uri: str = 'http://localhost:8080/callback',
        scope: List[str] = None
    ):
        if not OAUTH2_AVAILABLE:
            raise ImportError("requests-oauthlib not installed")

        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scope = scope or []
        self.token = None

    def get_authorization_url(self) -> str:
        """Get OAuth2 authorization URL."""
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )

        auth_url, state = oauth.authorization_url(self.authorization_url)
        return auth_url

    def fetch_token(self, authorization_response: str) -> Dict[str, Any]:
        """Fetch access token from authorization response."""
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri)

        try:
            self.token = oauth.fetch_token(
                self.token_url,
                authorization_response=authorization_response,
                client_secret=self.client_secret
            )
            return self.token
        except Exception as e:
            return {'error': str(e)}

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        oauth = OAuth2Session(self.client_id, token={'refresh_token': refresh_token})

        try:
            self.token = oauth.refresh_token(
                self.token_url,
                refresh_token=refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            return self.token
        except Exception as e:
            return {'error': str(e)}

    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        """Make authenticated request."""
        if not self.token:
            return {'error': 'Not authenticated'}

        oauth = OAuth2Session(self.client_id, token=self.token)

        try:
            response = oauth.request(method, url, **kwargs)
            return {
                'status_code': response.status_code,
                'data': response.json() if response.content else None
            }
        except Exception as e:
            return {'error': str(e)}


# =============================================================================
# WEBHOOK LISTENER
# =============================================================================

class WebhookListener:
    """Simple webhook listener (requires FastAPI/Flask in production)."""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key
        self.handlers = {}

    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for webhook event type."""
        self.handlers[event_type] = handler

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature using HMAC."""
        if not self.secret_key:
            return True  # Skip verification if no secret key

        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def handle_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any],
        signature: str = None
    ) -> Dict[str, Any]:
        """Handle incoming webhook."""
        # Verify signature
        if signature:
            payload_bytes = json.dumps(payload).encode()
            if not self.verify_signature(payload_bytes, signature):
                return {'error': 'Invalid signature', 'status': 401}

        # Get handler
        handler = self.handlers.get(event_type)
        if not handler:
            return {'error': f'No handler for event type: {event_type}', 'status': 404}

        # Execute handler
        try:
            result = handler(payload)
            return {'status': 200, 'result': result}
        except Exception as e:
            return {'error': str(e), 'status': 500}


# =============================================================================
# API KEY MANAGER
# =============================================================================

class APIKeyManager:
    """Secure API key storage and management."""

    def __init__(self, storage_path: str = 'api_keys.json'):
        self.storage_path = storage_path
        self.keys = {}
        self.load_keys()

    def load_keys(self):
        """Load API keys from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                self.keys = json.load(f)
        except FileNotFoundError:
            self.keys = {}

    def save_keys(self):
        """Save API keys to storage."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.keys, f, indent=2)

    def add_key(self, service: str, api_key: str, metadata: Dict = None):
        """Add API key for service."""
        self.keys[service] = {
            'key': api_key,
            'metadata': metadata or {},
            'added_at': datetime.now().isoformat()
        }
        self.save_keys()

    def get_key(self, service: str) -> Optional[str]:
        """Get API key for service."""
        if service in self.keys:
            return self.keys[service]['key']
        return None

    def remove_key(self, service: str):
        """Remove API key for service."""
        if service in self.keys:
            del self.keys[service]
            self.save_keys()

    def list_services(self) -> List[str]:
        """List all services with stored keys."""
        return list(self.keys.keys())


# =============================================================================
# API WRAPPER GENERATOR
# =============================================================================

class APIWrapperGenerator:
    """Generate Python client for REST APIs from OpenAPI/Swagger spec."""

    @staticmethod
    def generate_from_openapi(spec_url: str, output_file: str = None) -> str:
        """Generate API client from OpenAPI spec."""
        try:
            # Fetch spec
            response = requests.get(spec_url)
            spec = response.json()

            # Extract API info
            base_url = spec.get('servers', [{}])[0].get('url', '')
            paths = spec.get('paths', {})

            # Generate client code
            code_lines = [
                '"""Auto-generated API client"""',
                'import requests',
                '',
                'class APIClient:',
                f'    def __init__(self, api_key: str = None):',
                f'        self.base_url = "{base_url}"',
                '        self.session = requests.Session()',
                '        if api_key:',
                '            self.session.headers["Authorization"] = f"Bearer {api_key}"',
                ''
            ]

            # Generate methods for each endpoint
            for path, methods in paths.items():
                for method, details in methods.items():
                    method_name = details.get('operationId', f'{method}_{path.replace("/", "_")}')
                    summary = details.get('summary', '')

                    code_lines.extend([
                        f'    def {method_name}(self, **kwargs):',
                        f'        """{summary}"""',
                        f'        url = f"{{self.base_url}}{path}"',
                        f'        return self.session.{method}(url, **kwargs).json()',
                        ''
                    ])

            client_code = '\n'.join(code_lines)

            # Save to file if specified
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(client_code)

            return client_code

        except Exception as e:
            return f"Error generating client: {e}"


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_usage():
    """Example usage of API ecosystem tools."""

    # Rate limiting
    limiter = RateLimiter(max_requests=10, time_window=60)

    # REST API client
    api = RESTAPIClient(
        base_url='https://api.example.com',
        api_key='your-api-key'
    )

    # Make requests
    response = api.get('/users')
    print(response)

    # Webhook listener
    listener = WebhookListener(secret_key='webhook-secret')

    def handle_payment(payload):
        print(f"Payment received: {payload}")

    listener.register_handler('payment.success', handle_payment)

    # API key management
    key_manager = APIKeyManager()
    key_manager.add_key('openai', 'sk-...')
    api_key = key_manager.get_key('openai')


__all__ = [
    'RateLimiter',
    'RetryStrategy',
    'with_retry',
    'RESTAPIClient',
    'OAuth2Client',
    'WebhookListener',
    'APIKeyManager',
    'APIWrapperGenerator'
]
