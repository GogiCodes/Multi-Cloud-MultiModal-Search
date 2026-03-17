import asyncio
import time
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.models import (
    SearchRequest, SearchResponse, SearchResult, AddProductRequest,
    Product, VisionResult
)
from app.azure_vision import azure_vision
from app.google_embedding import google_embedding
from app.aws_claude import aws_claude
from app.database import lancedb_service
from app.cache import cache_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_products(
    image: UploadFile = File(None),
    text_query: str = Form(None),
    confidence_threshold: float = Form(0.7),
    max_results: int = Form(10),
    brand_filter: str = Form(None),
    price_min: float = Form(None),
    price_max: float = Form(None)
):
    """
    Search for products using image and/or text query.
    """
    start_time = time.time()

    try:
        # Validate input
        if not image and not text_query:
            raise HTTPException(status_code=400, detail="Either image or text_query must be provided")

        # Check cache first
        image_bytes = await image.read() if image else None
        cached_result = await cache_service.get_search_cache(image_bytes, text_query)
        if cached_result:
            logger.info("Returning cached search result")
            return SearchResponse(**cached_result)

        # Process image and text in parallel
        vision_task = None
        embedding_task = None

        if image_bytes:
            vision_task = azure_vision.analyze_image(image_bytes)
            embedding_task = google_embedding.generate_image_embedding(image_bytes)

        text_embedding_task = None
        if text_query:
            text_embedding_task = google_embedding.generate_text_embedding(text_query)

        # Execute parallel tasks
        tasks = []
        if vision_task:
            tasks.append(vision_task)
        if embedding_task:
            tasks.append(embedding_task)
        if text_embedding_task:
            tasks.append(text_embedding_task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        vision_result = None
        query_embedding = None

        result_idx = 0
        if vision_task:
            vision_result = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            result_idx += 1

        if embedding_task:
            image_embedding = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            result_idx += 1
            if image_embedding:
                query_embedding = image_embedding

        if text_embedding_task:
            text_embedding = results[result_idx] if not isinstance(results[result_idx], Exception) else None
            if text_embedding and not query_embedding:
                query_embedding = text_embedding
            elif text_embedding and query_embedding:
                # Combine embeddings (simple average)
                query_embedding = [(a + b) / 2 for a, b in zip(query_embedding, text_embedding)]

        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")

        # Search database
        similar_products = await lancedb_service.search_similar(
            query_embedding=query_embedding,
            limit=max_results,
            confidence_threshold=confidence_threshold,
            brand_filter=brand_filter,
            price_min=price_min,
            price_max=price_max
        )

        # Generate explanations using Claude
        search_results = []
        if similar_products and vision_result:
            claude_response = await aws_claude.generate_recommendations(
                vision_result=vision_result,
                similar_products=similar_products,
                user_text=text_query or "",
                top_k=len(similar_products)
            )

            # Match recommendations to products
            for product in similar_products:
                explanation = f"Matches your search for {text_query or 'similar products'}"
                if 'recommendations' in claude_response:
                    for rec in claude_response['recommendations']:
                        if rec.get('product_id') == product.id:
                            explanation = rec.get('reason', explanation)
                            break

                search_results.append(SearchResult(
                    product=product,
                    similarity_score=getattr(product, 'similarity_score', 0.8),
                    explanation=explanation,
                    match_details={
                        "vision_brands": vision_result.brands if vision_result else [],
                        "vision_colors": vision_result.colors if vision_result else [],
                        "vision_objects": vision_result.objects if vision_result else []
                    }
                ))
        else:
            # Fallback without Claude
            for product in similar_products:
                search_results.append(SearchResult(
                    product=product,
                    similarity_score=getattr(product, 'similarity_score', 0.8),
                    explanation="Similar product found",
                    match_details={}
                ))

        processing_time = time.time() - start_time
        api_cost_estimate = 0.02  # Rough estimate per request

        response = SearchResponse(
            results=search_results,
            total_found=len(search_results),
            processing_time=processing_time,
            api_cost_estimate=api_cost_estimate,
            query_embedding=query_embedding
        )

        # Cache the result
        await cache_service.set_search_cache(image_bytes, text_query, response.dict())

        return response

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/products")
async def add_products(request: AddProductRequest):
    """
    Add products to the database.
    """
    try:
        # Generate embeddings for products that don't have them
        for product in request.products:
            if not product.embedding:
                text_for_embedding = f"{product.name} {product.brand} {product.description} {product.category}"
                embedding = await google_embedding.generate_text_embedding(text_for_embedding)
                if embedding:
                    product.embedding = embedding

        success = await lancedb_service.add_products(request.products)
        if success:
            return {"message": f"Added {len(request.products)} products successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add products")
    except Exception as e:
        logger.error(f"Add products failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add products: {str(e)}")

@router.get("/products")
async def get_products():
    """
    Get all products from database.
    """
    try:
        products = await lancedb_service.get_all_products()
        return {"products": [p.dict() for p in products], "total": len(products)}
    except Exception as e:
        logger.error(f"Get products failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get products: {str(e)}")