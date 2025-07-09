#!/usr/bin/env python3
"""
Example: Managing SKUs with the MySale API SDK

This example demonstrates how to:
1. Create a new SKU
2. Update SKU details
3. Upload pricing information
4. Manage inventory
5. List and search SKUs
"""

import asyncio
from decimal import Decimal
from uuid import uuid4

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import (
    SKUCreateWrite, SKUWrite, Weight, Volume,
    SKUPrices, SKUPrice, PriceValue,
    SKUInventory, LocationQuantity,
    SKUImages, SKUImage
)

# Configuration
API_TOKEN = "your_api_token_here"
TAXONOMY_ID = "your_taxonomy_id_here"  # Replace with actual taxonomy ID


def create_new_sku():
    """Create a new SKU with all required information."""
    print("Creating a new SKU...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Create SKU data
    sku_data = SKUCreateWrite(
        merchant_sku_id="TSHIRT-BLUE-M-001",
        name="Premium Blue T-Shirt - Medium",
        description="High-quality cotton t-shirt in blue color, size medium. Perfect for casual wear.",
        country_of_origin="AU",
        weight=Weight(value=Decimal("0.3"), unit="kg"),
        volume=Volume(
            height=Decimal("30"),
            width=Decimal("40"), 
            length=Decimal("2"),
            unit="cm"
        ),
        taxonomy_id=TAXONOMY_ID,
        brand="Premium Wear",
        size="Medium"
    )
    
    try:
        new_sku = client.skus.create_sku(sku_data)
        print(f"✅ Successfully created SKU: {new_sku.merchant_sku_id}")
        print(f"   MySale SKU ID: {new_sku.sku_id}")
        print(f"   Name: {new_sku.name}")
        return new_sku.merchant_sku_id
    
    except Exception as e:
        print(f"❌ Error creating SKU: {e}")
        return None


def update_sku_pricing(merchant_sku_id: str):
    """Update SKU pricing information."""
    print(f"\nUpdating pricing for SKU: {merchant_sku_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Create pricing data
    price_data = SKUPrices(
        prices=SKUPrice(
            cost=PriceValue(currency="AUD", value=Decimal("12.50")),
            sell=PriceValue(currency="AUD", value=Decimal("29.99")),
            rrp=PriceValue(currency="AUD", value=Decimal("39.99"))
        )
    )
    
    try:
        client.skus.upload_prices(merchant_sku_id, price_data)
        print("✅ Successfully updated pricing")
        
        # Verify the update
        prices = client.skus.get_prices(merchant_sku_id)
        print(f"   Cost: {prices.prices.cost.currency} {prices.prices.cost.value}")
        print(f"   Sell: {prices.prices.sell.currency} {prices.prices.sell.value}")
        print(f"   RRP: {prices.prices.rrp.currency} {prices.prices.rrp.value}")
        
    except Exception as e:
        print(f"❌ Error updating pricing: {e}")


def update_sku_inventory(merchant_sku_id: str):
    """Update SKU inventory levels."""
    print(f"\nUpdating inventory for SKU: {merchant_sku_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Create inventory data
    inventory_data = SKUInventory(
        inventory=[
            LocationQuantity(location="Melbourne Warehouse", quantity=50),
            LocationQuantity(location="Sydney Store", quantity=25),
            LocationQuantity(location="Brisbane Outlet", quantity=15)
        ]
    )
    
    try:
        client.skus.upload_inventory(merchant_sku_id, inventory_data)
        print("✅ Successfully updated inventory")
        
        # Verify the update
        inventory = client.skus.get_inventory(merchant_sku_id)
        total_qty = sum(loc.quantity for loc in inventory.inventory)
        print(f"   Total quantity across all locations: {total_qty}")
        for location in inventory.inventory:
            print(f"   {location.location}: {location.quantity} units")
            
    except Exception as e:
        print(f"❌ Error updating inventory: {e}")


def upload_sku_images(merchant_sku_id: str):
    """Upload images for a SKU."""
    print(f"\nUploading images for SKU: {merchant_sku_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Create image data
    images_data = SKUImages(
        images=[
            SKUImage(merchant_url="https://example.com/images/tshirt-blue-front.jpg"),
            SKUImage(merchant_url="https://example.com/images/tshirt-blue-back.jpg"),
            SKUImage(merchant_url="https://example.com/images/tshirt-blue-detail.jpg")
        ]
    )
    
    try:
        client.skus.upload_images(merchant_sku_id, images_data)
        print("✅ Successfully uploaded images")
        
        # Verify the upload
        images = client.skus.get_images(merchant_sku_id)
        print(f"   Uploaded {len(images.images)} images:")
        for i, image in enumerate(images.images, 1):
            if image.url:
                print(f"   {i}. {image.url}")
            elif image.error:
                print(f"   {i}. Error: {image.error}")
                
    except Exception as e:
        print(f"❌ Error uploading images: {e}")


def list_and_search_skus():
    """List SKUs and demonstrate searching/filtering."""
    print("\nListing and searching SKUs...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get SKU statistics
        stats = client.skus.get_statistics()
        print(f"📊 SKU Statistics:")
        print(f"   Total SKUs: {stats.total}")
        print(f"   Archived SKUs: {stats.archived}")
        
        # List first page of SKUs
        skus_page = client.skus.list_skus(offset=0, limit=10, paginated=True)
        print(f"\n📝 First 10 SKUs (Total: {skus_page.total_count}):")
        
        for sku in skus_page.items:
            print(f"   - {sku.merchant_sku_id}: {sku.name}")
            print(f"     Status: {'Enabled' if sku.enabled else 'Disabled'}")
            
        # Demonstrate pagination
        if skus_page.has_more:
            print("\n⏭️  Getting next page...")
            next_page = client.skus.list_skus(
                offset=skus_page.next_offset, 
                limit=10, 
                paginated=True
            )
            print(f"   Next page has {len(next_page.items)} SKUs")
            
    except Exception as e:
        print(f"❌ Error listing SKUs: {e}")


def enable_disable_sku(merchant_sku_id: str):
    """Enable/disable a SKU for sale."""
    print(f"\nManaging SKU status: {merchant_sku_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Enable the SKU
        client.skus.enable(merchant_sku_id)
        print("✅ SKU enabled for sale")
        
        # Get updated SKU to verify
        sku = client.skus.get_by_merchant_id(merchant_sku_id)
        print(f"   Current status: {'Enabled' if sku.enabled else 'Disabled'}")
        
        # Optionally disable it
        # client.skus.disable(merchant_sku_id)
        # print("✅ SKU disabled")
        
    except Exception as e:
        print(f"❌ Error managing SKU status: {e}")


async def async_sku_operations():
    """Demonstrate async SKU operations."""
    print("\n🔄 Demonstrating async operations...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get statistics asynchronously
        stats = await client.skus.get_statistics_async()
        print(f"📊 Async - Total SKUs: {stats.total}")
        
        # List SKUs asynchronously
        skus = await client.skus.list_skus_async(limit=5)
        print(f"📝 Async - Listed {len(skus)} SKUs")
        
        # Process multiple SKUs concurrently
        if skus:
            # Get details for first few SKUs concurrently
            tasks = [
                client.skus.get_by_merchant_id_async(sku.merchant_sku_id) 
                for sku in skus[:3]
            ]
            detailed_skus = await asyncio.gather(*tasks, return_exceptions=True)
            
            print("🔍 Detailed SKU info:")
            for result in detailed_skus:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.merchant_sku_id}: {result.name}")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def main():
    """Main example function."""
    print("🚀 MySale API SDK - SKU Management Example")
    print("=" * 50)
    
    # Create a new SKU
    merchant_sku_id = create_new_sku()
    
    if merchant_sku_id:
        # Update various aspects of the SKU
        update_sku_pricing(merchant_sku_id)
        update_sku_inventory(merchant_sku_id)
        upload_sku_images(merchant_sku_id)
        enable_disable_sku(merchant_sku_id)
    
    # List and search operations
    list_and_search_skus()
    
    # Async operations
    asyncio.run(async_sku_operations())
    
    print("\n✨ Example completed!")


if __name__ == "__main__":
    main()
