import asyncio
import logging
from typing import List, Optional
import lancedb
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pyarrow as pa
from app.config import settings
from app.models import Product
import pandas as pd

logger = logging.getLogger(__name__)

class LanceDBService:
    def __init__(self):
        self.db = lancedb.connect(settings.lancedb_uri)
        self.table_name = "products"
        self._ensure_table()

    def _ensure_table(self):
        """Create table if it doesn't exist."""
        try:
            self.table = self.db.open_table(self.table_name)
        except Exception:
            # Create table with schema
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("name", pa.string()),
                pa.field("brand", pa.string()),
                pa.field("category", pa.string()),
                pa.field("price", pa.float64()),
                pa.field("image_url", pa.string()),
                pa.field("description", pa.string()),
                pa.field("embedding", pa.list_(pa.float32())),
            ])
            self.table = self.db.create_table(self.table_name, schema=schema)

    async def add_products(self, products: List[Product]) -> bool:
        """Add products with their embeddings to the database."""
        try:
            data = []
            for product in products:
                if product.embedding:
                    data.append({
                        "id": product.id,
                        "name": product.name,
                        "brand": product.brand,
                        "category": product.category.value,
                        "price": product.price,
                        "image_url": product.image_url,
                        "description": product.description,
                        "embedding": product.embedding
                    })

            if data:
                df = pd.DataFrame(data)
                self.table.add(df)
                logger.info(f"Added {len(data)} products to database")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add products: {str(e)}")
            return False

    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        confidence_threshold: float = 0.7,
        brand_filter: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None
    ) -> List[Product]:
        """Search for similar products using vector similarity."""
        try:
            # Convert to numpy array
            query_vec = np.array(query_embedding).astype('float32')

            # Build filter conditions
            filter_conditions = []
            if brand_filter:
                filter_conditions.append(f"brand = '{brand_filter}'")
            if price_min is not None:
                filter_conditions.append(f"price >= {price_min}")
            if price_max is not None:
                filter_conditions.append(f"price <= {price_max}")

            where_clause = " AND ".join(filter_conditions) if filter_conditions else None

            # Perform vector search
            results = self.table.search(query_vec).limit(limit * 2).to_pandas()

            # Filter by confidence threshold
            similarities = []
            for _, row in results.iterrows():
                emb = np.array(row['embedding'])
                sim = cosine_similarity([query_vec], [emb])[0][0]
                if sim >= confidence_threshold:
                    similarities.append((row, sim))

            # Sort by similarity and take top limit
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:limit]

            # Convert back to Product objects
            products = []
            for row, sim in top_results:
                product = Product(
                    id=row['id'],
                    name=row['name'],
                    brand=row['brand'],
                    category=row['category'],
                    price=row['price'],
                    image_url=row['image_url'],
                    description=row['description']
                )
                # Attach similarity score
                product.similarity_score = sim
                products.append(product)

            return products

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []

    async def get_all_products(self) -> List[Product]:
        """Get all products from database."""
        try:
            df = self.table.to_pandas()
            products = []
            for _, row in df.iterrows():
                product = Product(
                    id=row['id'],
                    name=row['name'],
                    brand=row['brand'],
                    category=row['category'],
                    price=row['price'],
                    image_url=row['image_url'],
                    description=row['description'],
                    embedding=row['embedding']
                )
                products.append(product)
            return products
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}")
            return []

lancedb_service = LanceDBService()