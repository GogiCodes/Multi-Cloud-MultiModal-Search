from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ProductCategory(str, Enum):
    SNEAKERS = "sneakers"
    WATCHES = "watches"
    BAGS = "bags"
    CLOTHING = "clothing"

class Product(BaseModel):
    id: str
    name: str
    brand: str
    category: ProductCategory
    price: float
    image_url: str
    description: str
    embedding: Optional[List[float]] = None

class SearchRequest(BaseModel):
    image: Optional[bytes] = None
    text_query: Optional[str] = None
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=50)
    brand_filter: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None

class VisionResult(BaseModel):
    brands: List[str]
    colors: List[str]
    objects: List[str]
    text_extracted: str
    confidence: float

class SearchResult(BaseModel):
    product: Product
    similarity_score: float
    explanation: str
    match_details: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int
    processing_time: float
    api_cost_estimate: float
    query_embedding: Optional[List[float]] = None

class AddProductRequest(BaseModel):
    products: List[Product]

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, bool]