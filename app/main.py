from fastapi import FastAPI, Response, HTTPException
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


import time



app = FastAPI(title="FastAPI Demo")

# --- 4 Golden Signals ---
REQUEST_COUNT = Counter("request_count", "Number of requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])
ERROR_COUNT = Counter("error_count", "Number of errors", ["endpoint"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active requests in system")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    ACTIVE_REQUESTS.inc()
    method = request.method
    endpoint = request.url.path

    try:
        response = await call_next(request)
    except Exception:
        ERROR_COUNT.labels(endpoint=endpoint).inc()
        raise
    finally:
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        ACTIVE_REQUESTS.dec()

    return response

@app.get("/")
async def main():
    return {"status": "UP"}

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)

@app.get("/400")
async def return_400_error():
    raise HTTPException(
        status_code=400,
        detail="Bad Request: an 400 error"
    )

@app.get("/500")
async def return_500_error():
    raise HTTPException(
        status_code=500,
        detail="Bad Request: an 500 error"
    )









