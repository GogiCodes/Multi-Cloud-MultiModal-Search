#!/usr/bin/env python3
"""
Sample data generator for the product search database.
Creates 100+ products across different categories with realistic data.
"""

import asyncio
import json
from app.models import Product, ProductCategory
from app.database import lancedb_service
from app.google_embedding import google_embedding

async def create_sample_products():
    """Create sample products with embeddings."""

    products = [
        # Sneakers
        Product(
            id="sneaker-001",
            name="Air Jordan 1 High OG",
            brand="Nike",
            category=ProductCategory.SNEAKERS,
            price=170.00,
            image_url="https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            description="Classic basketball sneakers with high-top design and premium leather construction."
        ),
        Product(
            id="sneaker-002",
            name="Yeezy Boost 350 V2",
            brand="Adidas",
            category=ProductCategory.SNEAKERS,
            price=220.00,
            image_url="https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400",
            description="Modern lifestyle sneakers with Boost technology and Primeknit upper."
        ),
        Product(
            id="sneaker-003",
            name="Converse Chuck Taylor All Star",
            brand="Converse",
            category=ProductCategory.SNEAKERS,
            price=55.00,
            image_url="https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400",
            description="Iconic high-top sneakers with canvas upper and rubber sole."
        ),
        Product(
            id="sneaker-004",
            name="New Balance 574",
            brand="New Balance",
            category=ProductCategory.SNEAKERS,
            price=80.00,
            image_url="https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400",
            description="Classic running sneakers with suede and mesh construction."
        ),
        Product(
            id="sneaker-005",
            name="Puma Suede Classic",
            brand="Puma",
            category=ProductCategory.SNEAKERS,
            price=65.00,
            image_url="https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400",
            description="Retro-style sneakers with suede upper and rubber outsole."
        ),

        # Watches
        Product(
            id="watch-001",
            name="Rolex Submariner",
            brand="Rolex",
            category=ProductCategory.WATCHES,
            price=8500.00,
            image_url="https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400",
            description="Luxury dive watch with ceramic bezel and automatic movement."
        ),
        Product(
            id="watch-002",
            name="Omega Speedmaster",
            brand="Omega",
            category=ProductCategory.WATCHES,
            price=5200.00,
            image_url="https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=400",
            description="Professional chronograph watch, the first watch on the moon."
        ),
        Product(
            id="watch-003",
            name="Seiko Presage",
            brand="Seiko",
            category=ProductCategory.WATCHES,
            price=350.00,
            image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            description="Dress watch with automatic movement and enamel dial."
        ),
        Product(
            id="watch-004",
            name="Casio G-Shock",
            brand="Casio",
            category=ProductCategory.WATCHES,
            price=120.00,
            image_url="https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=400",
            description="Rugged digital watch with shock resistance and water resistance."
        ),
        Product(
            id="watch-005",
            name="Timex Weekender",
            brand="Timex",
            category=ProductCategory.WATCHES,
            price=45.00,
            image_url="https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400",
            description="Classic field watch with leather strap and quartz movement."
        ),

        # Bags
        Product(
            id="bag-001",
            name="Gucci Marmont Matelassé",
            brand="Gucci",
            category=ProductCategory.BAGS,
            price=2200.00,
            image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
            description="Luxury shoulder bag with GG Supreme canvas and matelassé leather."
        ),
        Product(
            id="bag-002",
            name="Louis Vuitton Neverfull",
            brand="Louis Vuitton",
            category=ProductCategory.BAGS,
            price=1850.00,
            image_url="https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
            description="Monogram canvas tote bag with leather trim and spacious interior."
        ),
        Product(
            id="bag-003",
            name="Prada Nylon Backpack",
            brand="Prada",
            category=ProductCategory.BAGS,
            price=2100.00,
            image_url="https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=400",
            description="Technical nylon backpack with logo plaque and adjustable straps."
        ),
        Product(
            id="bag-004",
            name="The North Face Borealis",
            brand="The North Face",
            category=ProductCategory.BAGS,
            price=99.00,
            image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
            description="Hiking backpack with 30L capacity and multiple compartments."
        ),
        Product(
            id="bag-005",
            name="Herschel Little America",
            brand="Herschel",
            category=ProductCategory.BAGS,
            price=85.00,
            image_url="https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
            description="Canvas backpack with leather trim and vintage-inspired design."
        ),

        # Clothing
        Product(
            id="clothing-001",
            name="Levi's 501 Original Jeans",
            brand="Levi's",
            category=ProductCategory.CLOTHING,
            price=89.00,
            image_url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
            description="Classic straight-fit jeans with button fly and 5-pocket styling."
        ),
        Product(
            id="clothing-002",
            name="Supreme Box Logo Hoodie",
            brand="Supreme",
            category=ProductCategory.CLOTHING,
            price=248.00,
            image_url="https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400",
            description="Cotton fleece hoodie with box logo embroidery and kangaroo pocket."
        ),
        Product(
            id="clothing-003",
            name="Ralph Lauren Oxford Shirt",
            brand="Ralph Lauren",
            category=ProductCategory.CLOTHING,
            price=125.00,
            image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
            description="Classic oxford cloth button-down shirt with button-down collar."
        ),
        Product(
            id="clothing-004",
            name="Nike Sportswear Tech Fleece",
            brand="Nike",
            category=ProductCategory.CLOTHING,
            price=110.00,
            image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
            description="Athletic hoodie with brushed fleece interior and ribbed cuffs."
        ),
        Product(
            id="clothing-005",
            name="Uniqlo HeatTech Thermal",
            brand="Uniqlo",
            category=ProductCategory.CLOTHING,
            price=29.90,
            image_url="https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400",
            description="Thermal long-sleeve shirt with moisture-wicking technology."
        ),
    ]

    # Generate more products to reach 100+
    brands = {
        ProductCategory.SNEAKERS: ["Nike", "Adidas", "Puma", "New Balance", "Converse", "Reebok", "Vans", "Asics"],
        ProductCategory.WATCHES: ["Rolex", "Omega", "Seiko", "Casio", "Timex", "Tag Heuer", "IWC", "Hamilton"],
        ProductCategory.BAGS: ["Gucci", "Louis Vuitton", "Prada", "The North Face", "Herschel", "Patagonia", "Fjällräven", "Everlane"],
        ProductCategory.CLOTHING: ["Levi's", "Supreme", "Ralph Lauren", "Nike", "Uniqlo", "H&M", "Zara", "Patagonia"]
    }

    product_names = {
        ProductCategory.SNEAKERS: [
            "Running Shoes", "Basketball Sneakers", "Casual Sneakers", "High-Tops", "Low-Tops",
            "Retro Sneakers", "Athletic Shoes", "Lifestyle Sneakers", "Training Shoes", "Walking Shoes"
        ],
        ProductCategory.WATCHES: [
            "Dress Watch", "Dive Watch", "Chronograph", "Field Watch", "Smart Watch",
            "Pilot Watch", "Luxury Watch", "Sport Watch", "Automatic Watch", "Quartz Watch"
        ],
        ProductCategory.BAGS: [
            "Tote Bag", "Backpack", "Shoulder Bag", "Crossbody Bag", "Weekend Bag",
            "Laptop Bag", "Messenger Bag", "Clutch", "Wallet", "Duffle Bag"
        ],
        ProductCategory.CLOTHING: [
            "T-Shirt", "Hoodie", "Jeans", "Jacket", "Sweater",
            "Pants", "Shorts", "Dress", "Skirt", "Blouse"
        ]
    }

    # Generate additional products
    product_id = 6
    for category in ProductCategory:
        for i in range(20):  # 20 more per category = 80 additional
            brand = brands[category][i % len(brands[category])]
            name = product_names[category][i % len(product_names[category])]
            full_name = f"{brand} {name} {product_id}"

            # Price ranges
            price_ranges = {
                ProductCategory.SNEAKERS: (50, 300),
                ProductCategory.WATCHES: (40, 10000),
                ProductCategory.BAGS: (30, 3000),
                ProductCategory.CLOTHING: (20, 500)
            }
            min_price, max_price = price_ranges[category]
            price = round(min_price + (max_price - min_price) * (i / 20), 2)

            # Generic descriptions
            descriptions = {
                ProductCategory.SNEAKERS: f"Comfortable {name.lower()} with modern design and superior comfort.",
                ProductCategory.WATCHES: f"Elegant {name.lower()} with precise timekeeping and stylish design.",
                ProductCategory.BAGS: f"Versatile {name.lower()} perfect for everyday use and travel.",
                ProductCategory.CLOTHING: f"Stylish {name.lower()} made with high-quality materials and attention to detail."
            }

            product = Product(
                id=f"{category.value}-{product_id:03d}",
                name=full_name,
                brand=brand,
                category=category,
                price=price,
                image_url=f"https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",  # Generic product image
                description=descriptions[category]
            )

            products.append(product)
            product_id += 1

    # Generate embeddings for all products
    print(f"Generating embeddings for {len(products)} products...")
    for i, product in enumerate(products):
        text_for_embedding = f"{product.name} {product.brand} {product.description} {product.category.value}"
        embedding = await google_embedding.generate_text_embedding(text_for_embedding)
        if embedding:
            product.embedding = embedding
        else:
            print(f"Failed to generate embedding for {product.name}")

        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(products)} products")

    # Add to database
    print("Adding products to database...")
    success = await lancedb_service.add_products(products)
    if success:
        print(f"Successfully added {len(products)} products to the database")
    else:
        print("Failed to add products to database")

if __name__ == "__main__":
    asyncio.run(create_sample_products())