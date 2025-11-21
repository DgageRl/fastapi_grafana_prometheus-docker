from fastapi import FastAPI, Response, HTTPException, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


import time



app = FastAPI(title="FastAPI Demo")

# --- 4 Golden Signals ---
REQUEST_COUNT = Counter("request_count", "Number of requests", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency", ["endpoint"])
ERROR_COUNT = Counter("error_count", "Number of errors", ["endpoint", "status_code"])
ACTIVE_REQUESTS = Gauge("active_requests", "Active requests in system")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    ACTIVE_REQUESTS.inc()
    method = request.method
    endpoint = request.url.path

    try:
        response = await call_next(request)
        status_code = response.status_code

        # Логируем успешные запросы
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()

    except HTTPException as http_exc:
        # Перехватываем HTTPException (400, 500 ошибки)
        status_code = http_exc.status_code
        ERROR_COUNT.labels(endpoint=endpoint, status_code=str(status_code)).inc()
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        raise

    except Exception as e:
        # Перехватываем все остальные исключения
        ERROR_COUNT.labels(endpoint=endpoint, status_code="500").inc()
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code="500").inc()
        raise

    finally:
        # Всегда обновляем метрики латенси и активных запросов
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
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
        detail="Bad Request: a 400 error"
    )


@app.get("/500")
async def return_500_error():
    raise HTTPException(
        status_code=500,
        detail="Internal Server Error: a 500 error"
    )
#

# Добавьте эндпоинт для тестирования успешных запросов
@app.get("/success")
async def success_endpoint():
    return {"message": "This is a successful request"}









