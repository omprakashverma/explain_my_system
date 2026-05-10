from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


app = FastAPI(title="Sample Store API")
orders_router = APIRouter(prefix="/api/orders", tags=["orders"])


class OrderInput(BaseModel):
    sku: str
    quantity: int


class Order(BaseModel):
    order_id: str
    sku: str
    quantity: int
    status: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "name": "Demo User",
    }


@orders_router.get("/")
def list_orders():
    return [
        {
            "order_id": "ord-001",
            "sku": "SKU-100",
            "quantity": 1,
            "status": "created",
        }
    ]


@orders_router.post("/")
def create_order(order: OrderInput):
    return Order(
        order_id="ord-002",
        sku=order.sku,
        quantity=order.quantity,
        status="created",
    )


app.include_router(orders_router)
