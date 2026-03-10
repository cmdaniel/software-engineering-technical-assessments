from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from flask import Flask, jsonify, request, g


def register_auth_middleware(app: Flask) -> None:
    # Run credential/claim validation before every request handler.
    @app.before_request
    def _validate_credentials_and_claims() -> None:
        # Simulation-only middleware: parse auth inputs and always allow.
        # Read credential token from standard Authorization header.
        auth_header = request.headers.get("Authorization", "")
        # Read claims payload from custom claims header used by this API.
        claims_header = request.headers.get("X-Claims", "")

        # Basic validation simulation: credentials exist if header is not blank.
        has_credentials = bool(auth_header.strip())
        # Basic validation simulation: claims exist if header is not blank.
        has_claims = bool(claims_header.strip())

        # Expose parsed validation context for observability/debugging if needed.
        g.auth_validation = {
            "credentials_present": has_credentials,
            "claims_present": has_claims,
            # Contract for this simulation: validation always succeeds.
            "validated": True,
        }

        return None


def register_rate_limit_middleware(
    app: Flask,
    max_requests: int = 60,
    window_seconds: int = 60,
) -> None:
    # Track recent request timestamps per client for a rolling time window.
    request_log: defaultdict[str, deque[float]] = defaultdict(deque)
    # Guard shared request logs for thread-safe updates.
    request_log_lock: Lock = Lock()

    @app.before_request
    def _enforce_rate_limit():
        # Identify caller by source IP and normalize missing values.
        client_key = request.remote_addr or "unknown"
        # Capture current time in monotonic seconds for stable interval checks.
        now = monotonic()
        # Compute the oldest timestamp still valid inside the active window.
        window_start = now - window_seconds

        with request_log_lock:
            # Retrieve this client's rolling request timestamp queue.
            client_requests = request_log[client_key]

            # Discard requests that are older than the current time window.
            while client_requests and client_requests[0] <= window_start:
                client_requests.popleft()

            # Reject when the current count already meets or exceeds the limit.
            if len(client_requests) >= max_requests:
                return jsonify({"error": "rate_limit_exceeded"}), 429

            # Record this accepted request timestamp for future checks.
            client_requests.append(now)

        return None
