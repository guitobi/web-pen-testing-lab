from typing import List
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

class ReviewCreate(BaseModel):
    product_id: int
    author: str
    text: str

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]
    total: float
