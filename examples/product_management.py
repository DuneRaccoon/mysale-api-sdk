#!/usr/bin/env python3
"""
Example: Product Management with the MySale API SDK

This example demonstrates how to:
1. Create products and group SKUs
2. Manage product information
3. Handle product images
4. List and search products
"""

import asyncio
from uuid import uuid4

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import (
    ProductCreateWrite, ProductWrite, ProductSKU,
    ProductImages, ProductImage
)

# Configuration
API_TOKEN = "your_api_token_here"


def create_product_with_skus():
    """Create a new product and associate SKUs with it."""
    print("🏷️ Creating a new product with SKUs...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Create product data with associated SKUs
        product_data = ProductCreateWrite(
            merchant_product_id="COLLECTION-TSHIRT-001",
            name="Premium T-Shirt Collection",
            description="""
            <h2>Premium Cotton T-Shirt Collection</h2>
            <p>Our premium t-shirt collection features:</p>
            <ul>
                <li>100% organic cotton fabric</li>
                <li>Pre-shrunk for lasting fit</li>
                <li>Available in multiple colors and sizes</li>
                <li>Comfortable crew neck design</li>
                <li>Machine washable</li>
            </ul>
            <p>Perfect for casual wear, layering, or as a gift!</p>
            """,
            skus=[
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-S"),
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-M"),
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-L"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-S"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-M"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-L"),
            ]
        )
        
        # Create the product
        new_product = client.products.create_product(product_data)
        print(f"✅ Successfully created product: {new_product.merchant_product_id}")
        print(f"   MySale Product ID: {new_product.product_id}")
        print(f"   Name: {new_product.name}")
        print(f"   Associated SKUs: {len(new_product.skus)}")
        
        # Display associated SKUs
        for sku in new_product.skus:
            print(f"     - {sku.merchant_sku_id}")
        
        return new_product.merchant_product_id
        
    except Exception as e:
        print(f"❌ Error creating product: {e}")
        return None


def update_product_information(merchant_product_id: str):
    """Update product information."""
    print(f"\n📝 Updating product information for: {merchant_product_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Update product with new information
        update_data = ProductWrite(
            name="Premium Organic T-Shirt Collection - Updated",
            description="""
            <h2>Premium Organic Cotton T-Shirt Collection</h2>
            <p><strong>Now with improved fabric blend!</strong></p>
            <p>Our updated premium t-shirt collection features:</p>
            <ul>
                <li>100% certified organic cotton fabric</li>
                <li>Pre-shrunk for lasting fit</li>
                <li>Available in multiple colors and sizes</li>
                <li>Reinforced crew neck design</li>
                <li>Machine washable (cold water recommended)</li>
                <li>Eco-friendly packaging</li>
            </ul>
            <p>Perfect for casual wear, layering, or as a sustainable gift choice!</p>
            
            <h3>Care Instructions:</h3>
            <ul>
                <li>Machine wash cold with like colors</li>
                <li>Use mild detergent</li>
                <li>Tumble dry low heat</li>
                <li>Iron inside out if needed</li>
            </ul>
            """,
            # We can also add/remove SKUs during update
            skus=[
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-S"),
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-M"),
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-L"),
                ProductSKU(merchant_sku_id="TSHIRT-BLUE-XL"),  # Added XL
                ProductSKU(merchant_sku_id="TSHIRT-RED-S"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-M"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-L"),
                ProductSKU(merchant_sku_id="TSHIRT-RED-XL"),   # Added XL
                ProductSKU(merchant_sku_id="TSHIRT-GREEN-M"),  # Added new color
                ProductSKU(merchant_sku_id="TSHIRT-GREEN-L"),
            ]
        )
        
        # Update the product
        updated_product = client.products.update_by_merchant_id(merchant_product_id, update_data)
        print(f"✅ Successfully updated product")
        print(f"   New name: {updated_product.name}")
        print(f"   Updated SKUs count: {len(updated_product.skus)}")
        
        # Show changes in SKUs
        print("   Associated SKUs after update:")
        for sku in updated_product.skus:
            print(f"     - {sku.merchant_sku_id}")
            
        return updated_product
        
    except Exception as e:
        print(f"❌ Error updating product: {e}")
        return None


def manage_product_images(merchant_product_id: str):
    """Manage product images."""
    print(f"\n🖼️ Managing images for product: {merchant_product_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get current product images
        try:
            current_images = client.products.get_images(merchant_product_id)
            print(f"Current images: {len(current_images.images)}")
            
            for i, image in enumerate(current_images.images, 1):
                if image.url:
                    print(f"   {i}. {image.url}")
                elif image.error:
                    print(f"   {i}. Error: {image.error}")
                    
        except Exception as e:
            print(f"No existing images or error retrieving them: {e}")
        
        # Note: MySale API documentation shows image endpoints for products,
        # but the actual implementation might vary. This is a demonstration
        # of how it would work based on the pattern from SKUs.
        
        print("💡 Product image management follows similar patterns to SKU images")
        print("   Use client.products.get_images() to retrieve existing images")
        print("   Image upload might be available through separate endpoints")
        
    except Exception as e:
        print(f"❌ Error managing images: {e}")


def list_and_search_products():
    """List products and demonstrate filtering."""
    print("\n📋 Listing and searching products...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # List products with pagination
        products_page = client.products.list_products(offset=0, limit=20, paginated=True)
        print(f"📊 Found {len(products_page.items)} products (Total: {products_page.total_count})")
        
        for product in products_page.items[:10]:  # Show first 10
            print(f"   - {product.merchant_product_id}: {product.name}")
            print(f"     Product ID: {product.product_id}")
            print(f"     SKUs: {len(product.skus)}")
            
            # Show first few SKUs
            for sku in product.skus[:3]:
                print(f"       • {sku.merchant_sku_id}")
            if len(product.skus) > 3:
                print(f"       ... and {len(product.skus) - 3} more")
        
        # Demonstrate pagination
        if products_page.has_more:
            print(f"\n⏭️ Getting next page...")
            next_page = client.products.list_products(
                offset=products_page.next_offset,
                limit=10,
                paginated=True
            )
            print(f"   Next page has {len(next_page.items)} products")
            
    except Exception as e:
        print(f"❌ Error listing products: {e}")


def get_product_details(merchant_product_id: str):
    """Get detailed product information."""
    print(f"\n🔍 Getting detailed information for product: {merchant_product_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get product details
        product = client.products.get_by_merchant_id(merchant_product_id)
        
        print(f"Product Details:")
        print(f"   Merchant ID: {product.merchant_product_id}")
        print(f"   MySale ID: {product.product_id}")
        print(f"   Name: {product.name}")
        print(f"   Description length: {len(product.description)} characters")
        
        # Display first part of description (without HTML)
        desc_preview = product.description.replace('<p>', '').replace('</p>', '').replace('<h2>', '').replace('</h2>', '').replace('<ul>', '').replace('</ul>', '').replace('<li>', '• ').replace('</li>', '\n')
        preview_lines = desc_preview.split('\n')[:5]
        print(f"   Description preview:")
        for line in preview_lines:
            if line.strip():
                print(f"     {line.strip()}")
        
        print(f"\n   Associated SKUs ({len(product.skus)}):")
        for sku in product.skus:
            status = f" (ID: {sku.sku_id})" if sku.sku_id else " (No MySale ID)"
            print(f"     - {sku.merchant_sku_id}{status}")
            
    except Exception as e:
        print(f"❌ Error getting product details: {e}")


def demonstrate_product_sku_relationship():
    """Demonstrate the relationship between products and SKUs."""
    print("\n🔗 Demonstrating Product-SKU relationships...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get a few products
        products = client.products.list_products(limit=5)
        
        if not products:
            print("No products found to demonstrate relationships")
            return
        
        print("Product-SKU Relationship Analysis:")
        
        total_skus = 0
        products_with_skus = 0
        
        for product in products:
            sku_count = len(product.skus)
            total_skus += sku_count
            
            if sku_count > 0:
                products_with_skus += 1
            
            print(f"\n📦 {product.merchant_product_id}")
            print(f"   SKUs: {sku_count}")
            
            # Try to get detailed info about some SKUs
            for sku in product.skus[:2]:  # Check first 2 SKUs
                try:
                    sku_detail = client.skus.get_by_merchant_id(sku.merchant_sku_id)
                    print(f"     ✅ {sku.merchant_sku_id}: {sku_detail.name}")
                    print(f"        Enabled: {sku_detail.enabled}")
                except Exception as e:
                    print(f"     ❌ {sku.merchant_sku_id}: Could not retrieve details")
        
        print(f"\n📊 Summary:")
        print(f"   Products analyzed: {len(products)}")
        print(f"   Products with SKUs: {products_with_skus}")
        print(f"   Total SKUs across products: {total_skus}")
        print(f"   Average SKUs per product: {total_skus / len(products):.1f}")
        
    except Exception as e:
        print(f"❌ Error analyzing relationships: {e}")


async def async_product_operations():
    """Demonstrate async product operations."""
    print("\n🔄 Demonstrating async product operations...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get multiple product lists concurrently
        tasks = [
            client.products.list_products_async(offset=0, limit=5),
            client.products.list_products_async(offset=5, limit=5),
            client.products.list_products_async(offset=10, limit=5)
        ]
        
        page1, page2, page3 = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful results
        successful_pages = [page for page in [page1, page2, page3] if not isinstance(page, Exception)]
        total_products = sum(len(page) for page in successful_pages)
        
        print(f"📊 Async results:")
        print(f"   Successfully retrieved {len(successful_pages)} pages")
        print(f"   Total products: {total_products}")
        
        # Get detailed info for some products concurrently
        all_products = []
        for page in successful_pages:
            all_products.extend(page)
        
        if all_products:
            detail_tasks = [
                client.products.get_by_merchant_id_async(product.merchant_product_id)
                for product in all_products[:3]
            ]
            
            detailed_products = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            print("\n🔍 Detailed product info:")
            for result in detailed_products:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.merchant_product_id}: {len(result.skus)} SKUs")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def create_product_variants():
    """Create a product with multiple variants (different SKUs for same base product)."""
    print("\n🎨 Creating product with variants...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Create a product representing a base item with multiple variants
        product_data = ProductCreateWrite(
            merchant_product_id="HOODIE-COLLECTION-001",
            name="Premium Hooded Sweatshirt",
            description="""
            <h2>Premium Hooded Sweatshirt</h2>
            <p>Comfort meets style in our premium hooded sweatshirt collection.</p>
            
            <h3>Features:</h3>
            <ul>
                <li>80% cotton, 20% polyester blend</li>
                <li>Fleece-lined interior for warmth</li>
                <li>Adjustable drawstring hood</li>
                <li>Kangaroo front pocket</li>
                <li>Ribbed cuffs and hem</li>
            </ul>
            
            <h3>Available Variants:</h3>
            <ul>
                <li><strong>Colors:</strong> Black, Navy, Gray, Burgundy</li>
                <li><strong>Sizes:</strong> Small, Medium, Large, X-Large</li>
            </ul>
            """,
            skus=[
                # Black variants
                ProductSKU(merchant_sku_id="HOODIE-BLACK-S"),
                ProductSKU(merchant_sku_id="HOODIE-BLACK-M"),
                ProductSKU(merchant_sku_id="HOODIE-BLACK-L"),
                ProductSKU(merchant_sku_id="HOODIE-BLACK-XL"),
                
                # Navy variants
                ProductSKU(merchant_sku_id="HOODIE-NAVY-S"),
                ProductSKU(merchant_sku_id="HOODIE-NAVY-M"),
                ProductSKU(merchant_sku_id="HOODIE-NAVY-L"),
                ProductSKU(merchant_sku_id="HOODIE-NAVY-XL"),
                
                # Gray variants
                ProductSKU(merchant_sku_id="HOODIE-GRAY-S"),
                ProductSKU(merchant_sku_id="HOODIE-GRAY-M"),
                ProductSKU(merchant_sku_id="HOODIE-GRAY-L"),
                ProductSKU(merchant_sku_id="HOODIE-GRAY-XL"),
                
                # Burgundy variants
                ProductSKU(merchant_sku_id="HOODIE-BURGUNDY-S"),
                ProductSKU(merchant_sku_id="HOODIE-BURGUNDY-M"),
                ProductSKU(merchant_sku_id="HOODIE-BURGUNDY-L"),
                ProductSKU(merchant_sku_id="HOODIE-BURGUNDY-XL"),
            ]
        )
        
        # Create the product
        new_product = client.products.create_product(product_data)
        print(f"✅ Created product with variants: {new_product.merchant_product_id}")
        print(f"   Total variants (SKUs): {len(new_product.skus)}")
        
        # Group variants by attribute
        colors = {}
        sizes = {}
        
        for sku in new_product.skus:
            # Extract color and size from SKU ID (assuming HOODIE-COLOR-SIZE format)
            parts = sku.merchant_sku_id.split('-')
            if len(parts) >= 3:
                color = parts[1]
                size = parts[2]
                
                colors[color] = colors.get(color, 0) + 1
                sizes[size] = sizes.get(size, 0) + 1
        
        print(f"   Colors: {', '.join(colors.keys())} ({len(colors)} total)")
        print(f"   Sizes: {', '.join(sizes.keys())} ({len(sizes)} total)")
        print(f"   Color × Size matrix: {len(colors)} × {len(sizes)} = {len(colors) * len(sizes)} combinations")
        
        return new_product.merchant_product_id
        
    except Exception as e:
        print(f"❌ Error creating product variants: {e}")
        return None


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Product Management Example")
    print("=" * 50)
    
    # Create a new product
    product_id = create_product_with_skus()
    
    if product_id:
        # Update product information
        updated_product = update_product_information(product_id)
        
        # Manage product images
        manage_product_images(product_id)
        
        # Get detailed product information
        get_product_details(product_id)
    
    # List and search products
    list_and_search_products()
    
    # Demonstrate product-SKU relationships
    demonstrate_product_sku_relationship()
    
    # Create product with variants
    variant_product_id = create_product_variants()
    
    # Demonstrate async operations
    asyncio.run(async_product_operations())
    
    print("\n✨ Product management example completed!")


if __name__ == "__main__":
    main()
