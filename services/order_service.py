# services/order_service.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.post("/api/v3/orders/create")
def initialize_order():
    # Structural Connection 1: Inter-service HTTP call
    payment_endpoint = "http://payment-service.internal:8080/api/v1/charge/execute"
    payload = {"order_id": 9942, "total_usd": 150.00}
    response = requests.post(payment_endpoint, json=payload)
    
    # Structural Connection 2: Dependency on inventory database
    inventory_db_connection = "postgresql://reader_bot:view_only@rds-cluster-99.internal:5432/inventory_db"
    
    return {"status": "order_pending_payment", "upstream_receipt": response.json()}