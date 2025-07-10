#!/usr/bin/env python3
"""
Example: Managing SKUs with the MySale API SDK

This example demonstrates how to:
1. Create a new SKU
2. Update SKU details using instance methods
3. Upload pricing information using instance methods
4. Manage inventory using instance methods
5. Bulk update inventory for multiple SKUs
6. List and search SKUs
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
        return new_sku
    
    except Exception as e:
        print(f"❌ Error creating SKU: {e}")
        return None


def demonstrate_instance_methods(sku):
    """Demonstrate instance-based methods on a SKU."""
    print(f"\n🔧 Demonstrating instance methods for SKU: {sku.merchant_sku_id}")
    
    try:
        # Update pricing using instance method
        print("Updating pricing using instance method...")
        price_data = SKUPrices(
            prices=SKUPrice(
                cost=PriceValue(currency="AUD", value=Decimal("12.50")),
                sell=PriceValue(currency="AUD", value=Decimal("29.99")),
                rrp=PriceValue(currency="AUD", value=Decimal("39.99"))
            )
        )
        
        # Instance method - much cleaner!
        sku.upload_prices(price_data)
        print("✅ Successfully updated pricing using instance method")
        
        # Get updated prices using instance method
        updated_prices = sku.get_prices()
        print(f"   Cost: {updated_prices.prices.cost.currency} {updated_prices.prices.cost.value}")
        print(f"   Sell: {updated_prices.prices.sell.currency} {updated_prices.prices.sell.value}")
        
        # Update inventory using instance method
        print("\nUpdating inventory using instance method...")
        inventory_data = SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=50),
                LocationQuantity(location="Sydney Store", quantity=25),
                LocationQuantity(location="Brisbane Outlet", quantity=15)
            ]
        )
        
        # Instance method
        sku.upload_inventory(inventory_data)
        print("✅ Successfully updated inventory using instance method")
        
        # Get updated inventory using instance method
        updated_inventory = sku.get_inventory()
        total_qty = sum(loc.quantity for loc in updated_inventory.inventory)
        print(f"   Total quantity across all locations: {total_qty}")
        for location in updated_inventory.inventory:
            print(f"   {location.location}: {location.quantity} units")
        
        # Upload images using instance method
        print("\nUploading images using instance method...")
        images_data = SKUImages(
            images=[
                SKUImage(merchant_url="https://example.com/images/tshirt-blue-front.jpg"),
                SKUImage(merchant_url="https://example.com/images/tshirt-blue-back.jpg"),
                SKUImage(merchant_url="https://example.com/images/tshirt-blue-detail.jpg")
            ]
        )
        
        # Instance method
        sku.upload_images(images_data)
        print("✅ Successfully uploaded images using instance method")
        
        # Get images using instance method
        uploaded_images = sku.get_images()
        print(f"   Uploaded {len(uploaded_images.images)} images")
        
        # Enable SKU using instance method
        print("\nEnabling SKU using instance method...")
        sku.enable_sku()
        print("✅ SKU enabled for sale using instance method")
        
        # Update SKU details using instance method
        print("\nUpdating SKU details using instance method...")
        update_data = SKUWrite(
            name="Premium Blue T-Shirt - Medium (Updated)",
            description="High-quality cotton t-shirt in blue color, size medium. "
                       "Perfect for casual wear. Now with improved fabric!",
            brand="Premium Wear Plus"
        )
        
        # Instance method
        updated_sku = sku.update(update_data)
        print(f"✅ Successfully updated SKU using instance method")
        print(f"   New name: {updated_sku.name}")
        print(f"   New brand: {updated_sku.brand}")
        
        return updated_sku
        
    except Exception as e:
        print(f"❌ Error in instance methods: {e}")
        return sku


def demonstrate_bulk_inventory_update():
    """Demonstrate bulk inventory updates."""
    print("\n📦 Demonstrating bulk inventory updates...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Prepare bulk inventory updates
    inventory_updates = {
        "TSHIRT-BLUE-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=100),
                LocationQuantity(location="Sydney Store", quantity=50)
            ]
        ),
        "TSHIRT-RED-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=75),
                LocationQuantity(location="Sydney Store", quantity=25)
            ]
        ),
        "TSHIRT-GREEN-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=60),
                LocationQuantity(location="Sydney Store", quantity=30)
            ]
        )
    }
    
    try:
        # Synchronous bulk update
        print("Performing synchronous bulk inventory update...")
        results = client.skus.bulk_update_inventory(inventory_updates)
        
        print("Bulk update results:")
        for merchant_sku_id, result in results.items():
            if isinstance(result, Exception):
                print(f"   ❌ {merchant_sku_id}: {result}")
            else:
                total_qty = sum(loc.quantity for loc in result.inventory)
                print(f"   ✅ {merchant_sku_id}: {total_qty} total units")
        
    except Exception as e:
        print(f"❌ Error in bulk inventory update: {e}")


async def demonstrate_async_bulk_inventory_update():
    """Demonstrate async bulk inventory updates."""
    print("\n🚀 Demonstrating async bulk inventory updates...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    # Prepare bulk inventory updates
    inventory_updates = {
        "TSHIRT-BLUE-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=120),
                LocationQuantity(location="Sydney Store", quantity=60)
            ]
        ),
        "TSHIRT-RED-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=90),
                LocationQuantity(location="Sydney Store", quantity=40)
            ]
        ),
        "TSHIRT-GREEN-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=80),
                LocationQuantity(location="Sydney Store", quantity=35)
            ]
        ),
        "TSHIRT-BLACK-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=70),
                LocationQuantity(location="Sydney Store", quantity=30)
            ]
        ),
        "TSHIRT-WHITE-M-001": SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=110),
                LocationQuantity(location="Sydney Store", quantity=55)
            ]
        )
    }
    
    try:
        # Asynchronous bulk update with concurrency control
        print("Performing asynchronous bulk inventory update (max 3 concurrent)...")
        results = await client.skus.bulk_update_inventory_async(inventory_updates, max_concurrent=3)
        
        print("Async bulk update results:")
        successful_updates = 0
        failed_updates = 0
        
        for merchant_sku_id, result in results.items():
            if isinstance(result, Exception):
                print(f"   ❌ {merchant_sku_id}: {result}")
                failed_updates += 1
            else:
                total_qty = sum(loc.quantity for loc in result.inventory)
                print(f"   ✅ {merchant_sku_id}: {total_qty} total units")
                successful_updates += 1
        
        print(f"\nSummary: {successful_updates} successful, {failed_updates} failed")
        
    except Exception as e:
        print(f"❌ Error in async bulk inventory update: {e}")
    
    finally:
        await client.close()


async def demonstrate_async_instance_methods():
    """Demonstrate async instance methods."""
    print("\n🔄 Demonstrating async instance methods...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get a SKU instance
        sku = await client.skus.get_by_merchant_id_async("TSHIRT-BLUE-M-001")
        print(f"Retrieved SKU: {sku.merchant_sku_id}")
        
        # Use async instance methods
        print("Updating prices using async instance method...")
        price_data = SKUPrices(
            prices=SKUPrice(
                cost=PriceValue(currency="AUD", value=Decimal("13.00")),
                sell=PriceValue(currency="AUD", value=Decimal("31.99")),
                rrp=PriceValue(currency="AUD", value=Decimal("41.99"))
            )
        )
        
        # Async instance method
        await sku.upload_prices_async(price_data)
        print("✅ Successfully updated pricing using async instance method")
        
        # Get updated prices using async instance method
        updated_prices = await sku.get_prices_async()
        print(f"   New sell price: {updated_prices.prices.sell.currency} {updated_prices.prices.sell.value}")
        
        # Update inventory using async instance method
        print("Updating inventory using async instance method...")
        inventory_data = SKUInventory(
            inventory=[
                LocationQuantity(location="Melbourne Warehouse", quantity=150),
                LocationQuantity(location="Sydney Store", quantity=75)
            ]
        )
        
        # Async instance method
        await sku.upload_inventory_async(inventory_data)
        print("✅ Successfully updated inventory using async instance method")
        
    except Exception as e:
        print(f"❌ Error in async instance methods: {e}")
    
    finally:
        await client.close()


def list_and_search_skus():
    """List SKUs and demonstrate searching/filtering."""
    print("\n📝 Listing and searching SKUs...")
    
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
            
            # Demonstrate getting individual SKU details
            if sku.merchant_sku_id == "TSHIRT-BLUE-M-001":
                try:
                    detailed_sku = client.skus.get_by_merchant_id(sku.merchant_sku_id)
                    print(f"     Brand: {detailed_sku.brand}")
                    print(f"     Weight: {detailed_sku.weight.value}{detailed_sku.weight.unit}")
                except Exception:
                    pass
            
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


def demonstrate_sku_workflow():
    """Demonstrate a complete SKU workflow using both collection and instance methods."""
    print("\n🔄 Demonstrating complete SKU workflow...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Step 1: Create multiple SKUs (collection method)
        print("Step 1: Creating multiple SKU variants...")
        sku_variants = [
            {
                "id": "HOODIE-BLACK-L-001", 
                "name": "Premium Black Hoodie - Large",
                "color": "Black", 
                "size": "Large"
            },
            {
                "id": "HOODIE-GRAY-L-001", 
                "name": "Premium Gray Hoodie - Large",
                "color": "Gray", 
                "size": "Large"
            }
        ]
        
        created_skus = []
        for variant in sku_variants:
            sku_data = SKUCreateWrite(
                merchant_sku_id=variant["id"],
                name=variant["name"],
                description=f"Premium quality hoodie in {variant['color']}, size {variant['size']}.",
                country_of_origin="AU",
                weight=Weight(value=Decimal("0.8"), unit="kg"),
                taxonomy_id=TAXONOMY_ID,
                brand="Premium Wear",
                size=variant["size"]
            )
            
            try:
                sku = client.skus.create_sku(sku_data)
                created_skus.append(sku)
                print(f"   ✅ Created: {sku.merchant_sku_id}")
            except Exception as e:
                print(f"   ❌ Failed to create {variant['id']}: {e}")
        
        # Step 2: Configure each SKU using instance methods
        print("\nStep 2: Configuring SKUs using instance methods...")
        for sku in created_skus:
            print(f"   Configuring {sku.merchant_sku_id}...")
            
            # Set pricing (instance method)
            price_data = SKUPrices(
                prices=SKUPrice(
                    cost=PriceValue(currency="AUD", value=Decimal("25.00")),
                    sell=PriceValue(currency="AUD", value=Decimal("59.99")),
                    rrp=PriceValue(currency="AUD", value=Decimal("79.99"))
                )
            )
            sku.upload_prices(price_data)
            
            # Set inventory (instance method)
            inventory_data = SKUInventory(
                inventory=[
                    LocationQuantity(location="Main Warehouse", quantity=30),
                    LocationQuantity(location="Store", quantity=10)
                ]
            )
            sku.upload_inventory(inventory_data)
            
            # Enable for sale (instance method)
            sku.enable_sku()
            
            print(f"     ✅ Configured and enabled {sku.merchant_sku_id}")
        
        # Step 3: Bulk update inventory for all created SKUs
        print("\nStep 3: Bulk updating inventory...")
        inventory_updates = {}
        for sku in created_skus:
            inventory_updates[sku.merchant_sku_id] = SKUInventory(
                inventory=[
                    LocationQuantity(location="Main Warehouse", quantity=50),
                    LocationQuantity(location="Store", quantity=20)
                ]
            )
        
        bulk_results = client.skus.bulk_update_inventory(inventory_updates)
        successful_bulk = sum(1 for result in bulk_results.values() if not isinstance(result, Exception))
        print(f"   ✅ Bulk updated {successful_bulk}/{len(bulk_results)} SKUs")
        
        print("\n🎉 Complete workflow demonstration finished!")
        
    except Exception as e:
        print(f"❌ Error in workflow demonstration: {e}")


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Enhanced SKU Management Example")
    print("=" * 60)
    
    # Create a new SKU using collection method
    new_sku = create_new_sku()
    
    if new_sku:
        # Demonstrate instance methods on the created SKU
        updated_sku = demonstrate_instance_methods(new_sku)
    
    # Demonstrate bulk operations
    demonstrate_bulk_inventory_update()
    
    # List and search operations
    list_and_search_skus()
    
    # Demonstrate complete workflow
    demonstrate_sku_workflow()
    
    # Async operations
    print("\n" + "="*60)
    print("ASYNC OPERATIONS")
    print("="*60)
    
    asyncio.run(demonstrate_async_bulk_inventory_update())
    asyncio.run(demonstrate_async_instance_methods())
    
    print("\n✨ Enhanced SKU management example completed!")
    print("\n💡 Key improvements:")
    print("   • Instance-based methods: sku.upload_prices() instead of client.skus.upload_prices(sku_id)")
    print("   • Bulk operations: client.skus.bulk_update_inventory() for multiple SKUs")
    print("   • Async bulk operations with concurrency control")
    print("   • Cleaner, more intuitive API")


if __name__ == "__main__":
    main()
