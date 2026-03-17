import pytest
from app.models import Product, ProductCategory, SearchRequest

def test_product_model():
    """Test Product model creation."""
    product = Product(
        id="test-001",
        name="Test Product",
        brand="Test Brand",
        category=ProductCategory.SNEAKERS,
        price=99.99,
        image_url="https://example.com/image.jpg",
        description="A test product"
    )

    assert product.id == "test-001"
    assert product.name == "Test Product"
    assert product.brand == "Test Brand"
    assert product.category == ProductCategory.SNEAKERS
    assert product.price == 99.99

def test_search_request_model():
    """Test SearchRequest model."""
    request = SearchRequest(
        text_query="red sneakers",
        confidence_threshold=0.8,
        max_results=20
    )

    assert request.text_query == "red sneakers"
    assert request.confidence_threshold == 0.8
    assert request.max_results == 20
    assert request.brand_filter is None