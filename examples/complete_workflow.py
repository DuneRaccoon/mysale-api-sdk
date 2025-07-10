#!/usr/bin/env python3
"""
Example: Complete MySale Integration Workflow with Enhanced Instance Methods

This comprehensive example demonstrates a complete workflow using the MySale API SDK:
1. Set up product catalog (taxonomy, products, SKUs) using collection and instance methods
2. Manage orders and fulfillment using instance methods
3. Handle returns and customer service using instance methods
4. Monitor and optimize operations

This example showcases how all components work together in a real-world scenario
using the enhanced instance-based API for cleaner, more intuitive code.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4, UUID

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import *

# Configuration
API_TOKEN = "your_api_token_here"


class MySaleIntegration:
    """Complete MySale integration workflow manager with enhanced instance methods."""
    
    def __init__(self, api_token: str):
        self.client = MySaleClient(api_token=api_token)
        self.async_client = MySaleAsyncClient(api_token=api_token)
        self.created_skus = []
        self.created_products = []
        
    async def close_async_client(self):
        """Close the async client."""
        await self.async_client.close()
    
    def setup_product_catalog(self):
        """Set up a complete product catalog using enhanced instance methods."""
        print("🏪 Setting up product catalog with enhanced instance methods...")
        
        # Step 1: Explore taxonomy to find suitable categories
        print("\n1️⃣ Finding suitable product categories...")
        
        # Find categories for clothing items
        clothing_categories = self.client.taxonomy.search_branches("clothing")
        if clothing_categories:
            selected_category = clothing_categories[0]
            print(f"   Selected category: {selected_category.name}")
            print(f"   Category ID: {selected_category.branch_id}")
            taxonomy_id = selected_category.branch_id
        else:
            print("   ❌ No clothing categories found, using placeholder")
            taxonomy_id = uuid4()  # Placeholder
        
        # Step 2: Create SKUs for our products using collection methods
        print("\n2️⃣ Creating product SKUs using collection methods...")
        
        sku_variants = [
            {"id": "TSHIRT-PREMIUM-BLACK-S", "name": "Premium T-Shirt - Black Small", "size": "S", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-BLACK-M", "name": "Premium T-Shirt - Black Medium", "size": "M", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-BLACK-L", "name": "Premium T-Shirt - Black Large", "size": "L", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-NAVY-S", "name": "Premium T-Shirt - Navy Small", "size": "S", "color": "Navy"},
            {"id": "TSHIRT-PREMIUM-NAVY-M", "name": "Premium T-Shirt - Navy Medium", "size": "M", "color": "Navy"},
            {"id": "TSHIRT-PREMIUM-NAVY-L", "name": "Premium T-Shirt - Navy Large", "size": "L", "color": "Navy"},
        ]
        
        created_sku_instances = []
        
        for variant in sku_variants:
            try:
                sku_data = SKUCreateWrite(
                    merchant_sku_id=variant["id"],
                    name=variant["name"],
                    description=f"Premium quality cotton t-shirt in {variant['color']}, size {variant['size']}. "
                               f"Comfortable fit, pre-shrunk fabric, machine washable.",
                    country_of_origin="AU",
                    weight=Weight(value=Decimal("0.25"), unit="kg"),
                    volume=Volume(
                        height=Decimal("30"),
                        width=Decimal("40"),
                        length=Decimal("2"),
                        unit="cm"
                    ),
                    taxonomy_id=taxonomy_id,
                    brand="Premium Wear",
                    size=variant["size"]
                )
                
                # Collection method for creation
                new_sku = self.client.skus.create_sku(sku_data)
                created_sku_instances.append(new_sku)
                self.created_skus.append(new_sku.merchant_sku_id)
                print(f"   ✅ Created SKU: {variant['id']}")
                
                # Now use instance methods for configuration
                self._configure_sku_using_instance_methods(new_sku)
                
            except Exception as e:
                print(f"   ❌ Error creating SKU {variant['id']}: {e}")
        
        # Step 3: Create products to group SKUs using collection and instance methods
        print("\n3️⃣ Creating products using collection and instance methods...")
        
        # Group by color
        color_groups = {}
        for variant in sku_variants:
            color = variant["color"]
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(variant)
        
        created_product_instances = []
        
        for color, variants in color_groups.items():
            try:
                product_data = ProductCreateWrite(
                    merchant_product_id=f"TSHIRT-PREMIUM-{color.upper()}",
                    name=f"Premium T-Shirt - {color}",
                    description=f"""
                    <h2>Premium {color} T-Shirt</h2>
                    <p>Our premium {color.lower()} t-shirt combines comfort with style.</p>
                    <ul>
                        <li>100% premium cotton fabric</li>
                        <li>Pre-shrunk for lasting fit</li>
                        <li>Available in Small, Medium, and Large</li>
                        <li>Machine washable</li>
                        <li>Comfortable crew neck design</li>
                    </ul>
                    """,
                    skus=[ProductSKU(merchant_sku_id=v["id"]) for v in variants]
                )
                
                # Collection method for creation
                new_product = self.client.products.create_product(product_data)
                created_product_instances.append(new_product)
                self.created_products.append(new_product.merchant_product_id)
                print(f"   ✅ Created product: {color} T-Shirt ({len(variants)} variants)")
                
                # Enhance product description using instance method
                self._enhance_product_using_instance_methods(new_product, color)
                
            except Exception as e:
                print(f"   ❌ Error creating product for {color}: {e}")
        
        print(f"✅ Catalog setup completed: {len(self.created_skus)} SKUs, {len(self.created_products)} products")
        print("   Used enhanced instance methods for SKU and product configuration!")
    
    def _configure_sku_using_instance_methods(self, sku):
        """Configure a SKU using instance methods."""
        try:
            # Set pricing using instance method
            price_data = SKUPrices(
                prices=SKUPrice(
                    cost=PriceValue(currency="AUD", value=Decimal("15.00")),
                    sell=PriceValue(currency="AUD", value=Decimal("29.99")),
                    rrp=PriceValue(currency="AUD", value=Decimal("39.99"))
                )
            )
            sku.upload_prices(price_data)  # Instance method!
            
            # Set inventory using instance method
            inventory_data = SKUInventory(
                inventory=[
                    LocationQuantity(location="Main Warehouse", quantity=100),
                    LocationQuantity(location="Store Front", quantity=25)
                ]
            )
            sku.upload_inventory(inventory_data)  # Instance method!
            
            # Enable for sale using instance method
            sku.enable_sku()  # Instance method!
            
        except Exception as e:
            print(f"     ⚠️ Error configuring SKU {sku.merchant_sku_id} using instance methods: {e}")
    
    def _enhance_product_using_instance_methods(self, product, color):
        """Enhance a product using instance methods."""
        try:
            # Update product with enhanced description using instance method
            enhanced_description = product.description + f"""
            
            <h3>Style Guide for {color}:</h3>
            <p>This {color.lower()} t-shirt pairs perfectly with:</p>
            <ul>
                <li>Casual jeans for everyday wear</li>
                <li>Dress pants for smart-casual looks</li>
                <li>Shorts for summer comfort</li>
                <li>Layering under jackets and cardigans</li>
            </ul>
            
            <h3>Care Instructions:</h3>
            <p>Machine wash cold, tumble dry low, iron inside out if needed.</p>
            """
            
            update_data = ProductWrite(description=enhanced_description)
            product.update(update_data)  # Instance method!
            
            print(f"     ✅ Enhanced {color} product description using instance method")
            
        except Exception as e:
            print(f"     ⚠️ Error enhancing product {product.merchant_product_id}: {e}")
    
    def process_order_workflow(self):
        """Demonstrate complete order processing workflow using instance methods."""
        print("\n📦 Processing order workflow with instance methods...")
        
        # Step 1: Get new orders using collection method
        print("\n1️⃣ Retrieving new orders...")
        try:
            new_orders = self.client.orders.list_new_orders(limit=5)
            print(f"   Found {len(new_orders)} new orders")
            
            if not new_orders:
                print("   No new orders to process")
                return
            
            # Process first order as example
            order_summary = new_orders[0]
            order = self.client.orders.get_order(str(order_summary.order_id))  # Collection method
            print(f"   Processing order: {order.customer_order_reference}")
            
        except Exception as e:
            print(f"   ❌ Error retrieving orders: {e}")
            return
        
        # Step 2: Acknowledge order using instance method
        print("\n2️⃣ Acknowledging order using instance method...")
        try:
            acknowledgement = OrderAcknowledgement(
                merchant_order_id=f"INT-{order.customer_order_reference}-{datetime.now().strftime('%Y%m%d')}",
                order_items=[
                    AcknowledgementOrderItem(
                        order_item_id=item.order_item_id,
                        merchant_order_item_id=f"ITEM-{i+1}"
                    )
                    for i, item in enumerate(order.order_items)
                ]
            )
            
            # Instance method - cleaner API!
            order.acknowledge(acknowledgement)
            print(f"   ✅ Order acknowledged using instance method")
            
        except Exception as e:
            print(f"   ❌ Error acknowledging order using instance method: {e}")
        
        # Step 3: Check inventory and create shipment using instance methods
        print("\n3️⃣ Processing fulfillment using instance methods...")
        try:
            # Check if we have inventory for all items using instance methods
            can_fulfill = True
            for item in order.order_items:
                try:
                    # Get SKU instance and check inventory using instance method
                    sku = self.client.skus.get_by_merchant_id(item.merchant_sku_id)
                    inventory = sku.get_inventory()  # Instance method!
                    total_qty = sum(loc.quantity for loc in inventory.inventory)
                    if total_qty < item.sku_qty:
                        print(f"   ⚠️ Insufficient inventory for {item.merchant_sku_id}: need {item.sku_qty}, have {total_qty}")
                        can_fulfill = False
                except Exception:
                    print(f"   ⚠️ Could not check inventory for {item.merchant_sku_id}")
            
            if can_fulfill:
                # Create shipment using instance method
                shipment_data = ShipmentCreate(
                    merchant_shipment_id=f"SHIP-{order.customer_order_reference}",
                    tracking_number=f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    carrier="Australia Post",
                    carrier_shipment_method="Express Post",
                    dispatch_date=datetime.now(),
                    expected_delivery_date=datetime.now() + timedelta(days=2),
                    shipment_items=[
                        ShipmentItem(
                            merchant_sku_id=item.merchant_sku_id,
                            sku_id=item.sku_id,
                            sku_qty=item.sku_qty
                        )
                        for item in order.order_items
                    ]
                )
                
                # Instance method - cleaner API!
                shipment_id = order.create_shipment(shipment_data)
                print(f"   ✅ Shipment created using instance method: {shipment_id}")
            else:
                print("   ❌ Cannot fulfill order due to inventory issues")
                
        except Exception as e:
            print(f"   ❌ Error processing fulfillment: {e}")
    
    def handle_returns_workflow(self):
        """Demonstrate returns processing workflow using instance methods."""
        print("\n🔄 Processing returns workflow with instance methods...")
        
        # Step 1: Get pending returns using collection method
        print("\n1️⃣ Retrieving pending returns...")
        try:
            pending_returns = self.client.returns.list_pending_returns(limit=3)
            print(f"   Found {len(pending_returns)} pending returns")
            
            if not pending_returns:
                print("   No pending returns to process")
                return
            
            # Process first return as example
            return_summary = pending_returns[0]
            return_detail = self.client.returns.get_return(str(return_summary.id))  # Collection method
            print(f"   Processing return: {return_detail.ran}")
            
        except Exception as e:
            print(f"   ❌ Error retrieving returns: {e}")
            return
        
        # Step 2: Update return using instance method
        print("\n2️⃣ Updating return information using instance method...")
        try:
            update_data = ReturnUpdate(
                merchant_return_id=f"RET-{return_detail.ran}",
                notes=f"Return processed for customer {return_detail.customer.name}. "
                      f"Reason: {return_detail.reason_for_return}"
            )
            
            # Instance method - cleaner API!
            return_detail.update_return(update_data)
            print(f"   ✅ Return information updated using instance method")
            
        except Exception as e:
            print(f"   ❌ Error updating return using instance method: {e}")
        
        # Step 3: Make approval decision using instance methods (demo only)
        print("\n3️⃣ Making approval decision using instance methods...")
        try:
            if return_detail.total_amount and return_detail.total_amount.amount < 50:
                print(f"   💰 Low-value return (${return_detail.total_amount.amount}) - would auto-approve using instance method")
                # return_detail.approve()  # Instance method!
            else:
                print(f"   🔍 High-value return - would require manual review")
            
            # Create customer communication ticket using instance method
            ticket_data = TicketCreate(
                message="Thank you for your return request. We have received your items and are processing your return. "
                       "You will receive an update within 24-48 hours.",
                attachments=[]
            )
            
            # Note: Actual ticket creation commented out for demo
            # return_detail.create_ticket(ticket_data)  # Instance method!
            print(f"   ✅ Customer communication prepared (instance method available)")
            
        except Exception as e:
            print(f"   ❌ Error processing return decision: {e}")
    
    def monitor_operations(self):
        """Monitor and analyze operations."""
        print("\n📊 Monitoring operations...")
        
        # Step 1: SKU performance analysis
        print("\n1️⃣ Analyzing SKU performance...")
        try:
            sku_stats = self.client.skus.get_statistics()
            print(f"   Total SKUs: {sku_stats.total}")
            print(f"   Archived SKUs: {sku_stats.archived}")
            print(f"   Active SKUs: {sku_stats.total - (sku_stats.archived or 0)}")
            
        except Exception as e:
            print(f"   ❌ Error getting SKU stats: {e}")
        
        # Step 2: Order status overview
        print("\n2️⃣ Order status overview...")
        try:
            order_counts = {}
            statuses = [
                ("new", self.client.orders.list_new_orders),
                ("acknowledged", self.client.orders.list_acknowledged_orders),
                ("inprogress", self.client.orders.list_inprogress_orders),
                ("completed", self.client.orders.list_completed_orders)
            ]
            
            for status_name, list_method in statuses:
                try:
                    orders = list_method(limit=100)
                    order_counts[status_name] = len(orders)
                except Exception:
                    order_counts[status_name] = 0
            
            print(f"   Order pipeline:")
            for status, count in order_counts.items():
                print(f"     {status.title()}: {count}")
            
            total_active = sum(order_counts[s] for s in ["new", "acknowledged", "inprogress"])
            print(f"   Total active orders: {total_active}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing orders: {e}")
        
        # Step 3: Returns analysis
        print("\n3️⃣ Returns analysis...")
        try:
            return_counts = {}
            return_statuses = [
                ("pending", self.client.returns.list_pending_returns),
                ("awaiting", self.client.returns.list_awaiting_returns),
                ("received", self.client.returns.list_received_returns),
                ("closed", self.client.returns.list_closed_returns)
            ]
            
            for status_name, list_method in return_statuses:
                try:
                    returns = list_method(limit=100)
                    return_counts[status_name] = len(returns)
                except Exception:
                    return_counts[status_name] = 0
            
            print(f"   Returns pipeline:")
            for status, count in return_counts.items():
                print(f"     {status.title()}: {count}")
            
            total_active_returns = sum(return_counts[s] for s in ["pending", "awaiting", "received"])
            print(f"   Total active returns: {total_active_returns}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing returns: {e}")
        
        # Step 4: Shipping policy analysis
        print("\n4️⃣ Shipping configuration...")
        try:
            coverage = self.client.shipping.analyze_shipping_coverage()
            print(f"   Total shipping policies: {coverage['total_policies']}")
            print(f"   Enabled policies: {coverage['enabled_policies']}")
            print(f"   Dispatch locations: {coverage['unique_dispatch_locations']}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing shipping: {e}")
    
    async def async_operations_demo(self):
        """Demonstrate async operations with instance methods for high-performance scenarios."""
        print("\n🚀 Demonstrating async operations with instance methods...")
        
        try:
            # Concurrent data retrieval
            print("\n1️⃣ Concurrent data retrieval...")
            
            tasks = [
                self.async_client.skus.get_statistics_async(),
                self.async_client.orders.list_new_orders_async(limit=10),
                self.async_client.returns.list_pending_returns_async(limit=10),
                self.async_client.shipping.analyze_shipping_coverage_async()
            ]
            
            sku_stats, new_orders, pending_returns, shipping_coverage = await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"   Results retrieved concurrently:")
            if not isinstance(sku_stats, Exception):
                print(f"     SKU stats: {sku_stats.total} total SKUs")
            if not isinstance(new_orders, Exception):
                print(f"     New orders: {len(new_orders)}")
            if not isinstance(pending_returns, Exception):
                print(f"     Pending returns: {len(pending_returns)}")
            if not isinstance(shipping_coverage, Exception):
                print(f"     Shipping policies: {shipping_coverage['total_policies']}")
            
            # Batch processing simulation using async instance methods
            print("\n2️⃣ Batch processing with async instance methods...")
            
            if not isinstance(new_orders, Exception) and new_orders:
                # Process multiple orders concurrently using async instance methods
                order_detail_tasks = [
                    self.async_client.orders.get_order_async(str(order.order_id))
                    for order in new_orders[:3]
                ]
                
                detailed_orders = await asyncio.gather(*order_detail_tasks, return_exceptions=True)
                
                processed_count = sum(1 for order in detailed_orders if not isinstance(order, Exception))
                print(f"     Processed {processed_count} orders concurrently")
                
                # Demonstrate async instance methods on orders
                for order in detailed_orders:
                    if not isinstance(order, Exception):
                        try:
                            # Get shipments using async instance method
                            shipments = await order.get_shipments_async()
                            print(f"     Order {order.customer_order_reference}: {len(shipments.shipments)} shipments (async instance method)")
                        except Exception as e:
                            print(f"     Could not get shipments for order {order.customer_order_reference}: {e}")
            
            # Demonstrate async instance methods with SKUs
            print("\n3️⃣ SKU operations with async instance methods...")
            
            if self.created_skus:
                try:
                    # Get a few SKU instances and use async instance methods
                    sku_tasks = [
                        self.async_client.skus.get_by_merchant_id_async(sku_id)
                        for sku_id in self.created_skus[:3]
                    ]
                    
                    sku_instances = await asyncio.gather(*sku_tasks, return_exceptions=True)
                    
                    for sku in sku_instances:
                        if not isinstance(sku, Exception):
                            try:
                                # Get inventory using async instance method
                                inventory = await sku.get_inventory_async()
                                total_qty = sum(loc.quantity for loc in inventory.inventory)
                                print(f"     SKU {sku.merchant_sku_id}: {total_qty} total units (async instance method)")
                            except Exception as e:
                                print(f"     Could not get inventory for SKU {sku.merchant_sku_id}: {e}")
                
                except Exception as e:
                    print(f"     Error in SKU async operations: {e}")
            
            # Demonstrate async instance methods with products
            print("\n4️⃣ Product operations with async instance methods...")
            
            if self.created_products:
                try:
                    # Get a product instance and use async instance methods
                    product = await self.async_client.products.get_by_merchant_id_async(self.created_products[0])
                    
                    # Get images using async instance method
                    try:
                        images = await product.get_images_async()
                        print(f"     Product {product.merchant_product_id}: {len(images.images)} images (async instance method)")
                    except Exception as e:
                        print(f"     Could not get images for product {product.merchant_product_id}: {e}")
                    
                    # Update product using async instance method
                    update_data = ProductWrite(
                        description=product.description + "\n<p><em>Updated with async instance method!</em></p>"
                    )
                    
                    updated_product = await product.update_async(update_data)
                    print(f"     ✅ Updated product {updated_product.merchant_product_id} using async instance method")
                
                except Exception as e:
                    print(f"     Error in product async operations: {e}")
            
            print("   ✅ Async operations with instance methods completed successfully")
            
        except Exception as e:
            print(f"   ❌ Error in async operations: {e}")


def main():
    """Main workflow demonstration with enhanced instance methods."""
    print("🚀 MySale API SDK - Complete Integration Workflow with Enhanced Instance Methods")
    print("=" * 80)
    
    # Initialize integration
    integration = MySaleIntegration(API_TOKEN)
    
    try:
        # Phase 1: Setup with enhanced methods
        print("\n🏗️ PHASE 1: CATALOG SETUP WITH ENHANCED METHODS")
        print("-" * 50)
        integration.setup_product_catalog()
        
        # Phase 2: Order Management with instance methods
        print("\n📦 PHASE 2: ORDER MANAGEMENT WITH INSTANCE METHODS")
        print("-" * 50)
        integration.process_order_workflow()
        
        # Phase 3: Returns Management with instance methods
        print("\n🔄 PHASE 3: RETURNS MANAGEMENT WITH INSTANCE METHODS")
        print("-" * 50)
        integration.handle_returns_workflow()
        
        # Phase 4: Operations Monitoring
        print("\n📊 PHASE 4: OPERATIONS MONITORING")
        print("-" * 40)
        integration.monitor_operations()
        
        # Phase 5: Async Operations with instance methods
        print("\n🚀 PHASE 5: ASYNC OPERATIONS WITH INSTANCE METHODS")
        print("-" * 50)
        asyncio.run(integration.async_operations_demo())
        
        print("\n✨ Complete workflow demonstration with enhanced instance methods finished!")
        print("\n💡 Summary of Enhanced Features Used:")
        print(f"   - Catalog: {len(integration.created_skus)} SKUs, {len(integration.created_products)} products")
        print("   - SKU configuration using instance methods: sku.upload_prices(), sku.upload_inventory(), sku.enable_sku()")
        print("   - Product enhancement using instance methods: product.update()")
        print("   - Order processing using instance methods: order.acknowledge(), order.create_shipment()")
        print("   - Returns management using instance methods: return.update_return(), return.create_ticket()")
        print("   - Async instance methods for high-performance operations")
        
        print("\n🎯 Key Benefits of Enhanced Instance Methods:")
        print("   1. Cleaner, more intuitive API design")
        print("   2. Reduced error-prone code (no need to pass IDs repeatedly)")
        print("   3. Object-oriented approach follows Python best practices")
        print("   4. Better IDE support with autocomplete and type hints")
        print("   5. Async instance methods for high-performance scenarios")
        print("   6. Maintained collection methods for initial creation and listing")
        
        print("\n🔮 Next Steps for Production:")
        print("   1. Implement comprehensive error handling and retry logic")
        print("   2. Add structured logging for operational visibility")
        print("   3. Set up monitoring and alerting for API operations")
        print("   4. Consider implementing webhooks for real-time notifications")
        print("   5. Use async instance methods for high-throughput scenarios")
        print("   6. Implement bulk operations for efficiency at scale")
        
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
    
    finally:
        # Cleanup
        asyncio.run(integration.close_async_client())


if __name__ == "__main__":
    main()
