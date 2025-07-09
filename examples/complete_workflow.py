#!/usr/bin/env python3
"""
Example: Complete MySale Integration Workflow

This comprehensive example demonstrates a complete workflow using the MySale API SDK:
1. Set up product catalog (taxonomy, products, SKUs)
2. Manage orders and fulfillment
3. Handle returns and customer service
4. Monitor and optimize operations

This example showcases how all components work together in a real-world scenario.
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
    """Complete MySale integration workflow manager."""
    
    def __init__(self, api_token: str):
        self.client = MySaleClient(api_token=api_token)
        self.async_client = MySaleAsyncClient(api_token=api_token)
        self.created_skus = []
        self.created_products = []
        
    async def close_async_client(self):
        """Close the async client."""
        await self.async_client.close()
    
    def setup_product_catalog(self):
        """Set up a complete product catalog with taxonomy, products, and SKUs."""
        print("🏪 Setting up product catalog...")
        
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
        
        # Step 2: Create SKUs for our products
        print("\n2️⃣ Creating product SKUs...")
        
        sku_variants = [
            {"id": "TSHIRT-PREMIUM-BLACK-S", "name": "Premium T-Shirt - Black Small", "size": "S", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-BLACK-M", "name": "Premium T-Shirt - Black Medium", "size": "M", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-BLACK-L", "name": "Premium T-Shirt - Black Large", "size": "L", "color": "Black"},
            {"id": "TSHIRT-PREMIUM-NAVY-S", "name": "Premium T-Shirt - Navy Small", "size": "S", "color": "Navy"},
            {"id": "TSHIRT-PREMIUM-NAVY-M", "name": "Premium T-Shirt - Navy Medium", "size": "M", "color": "Navy"},
            {"id": "TSHIRT-PREMIUM-NAVY-L", "name": "Premium T-Shirt - Navy Large", "size": "L", "color": "Navy"},
        ]
        
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
                
                new_sku = self.client.skus.create_sku(sku_data)
                self.created_skus.append(new_sku.merchant_sku_id)
                print(f"   ✅ Created SKU: {variant['id']}")
                
                # Set pricing
                self._set_sku_pricing(variant["id"])
                
                # Set inventory
                self._set_sku_inventory(variant["id"])
                
                # Enable for sale
                self.client.skus.enable(variant["id"])
                
            except Exception as e:
                print(f"   ❌ Error creating SKU {variant['id']}: {e}")
        
        # Step 3: Create products to group SKUs
        print("\n3️⃣ Creating products...")
        
        # Group by color
        color_groups = {}
        for variant in sku_variants:
            color = variant["color"]
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(variant)
        
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
                
                new_product = self.client.products.create_product(product_data)
                self.created_products.append(new_product.merchant_product_id)
                print(f"   ✅ Created product: {color} T-Shirt ({len(variants)} variants)")
                
            except Exception as e:
                print(f"   ❌ Error creating product for {color}: {e}")
        
        print(f"✅ Catalog setup completed: {len(self.created_skus)} SKUs, {len(self.created_products)} products")
    
    def _set_sku_pricing(self, merchant_sku_id: str):
        """Set pricing for a SKU."""
        try:
            price_data = SKUPrices(
                prices=SKUPrice(
                    cost=PriceValue(currency="AUD", value=Decimal("15.00")),
                    sell=PriceValue(currency="AUD", value=Decimal("29.99")),
                    rrp=PriceValue(currency="AUD", value=Decimal("39.99"))
                )
            )
            self.client.skus.upload_prices(merchant_sku_id, price_data)
        except Exception as e:
            print(f"     ⚠️ Error setting pricing for {merchant_sku_id}: {e}")
    
    def _set_sku_inventory(self, merchant_sku_id: str):
        """Set inventory for a SKU."""
        try:
            inventory_data = SKUInventory(
                inventory=[
                    LocationQuantity(location="Main Warehouse", quantity=100),
                    LocationQuantity(location="Store Front", quantity=25)
                ]
            )
            self.client.skus.upload_inventory(merchant_sku_id, inventory_data)
        except Exception as e:
            print(f"     ⚠️ Error setting inventory for {merchant_sku_id}: {e}")
    
    def process_order_workflow(self):
        """Demonstrate complete order processing workflow."""
        print("\n📦 Processing order workflow...")
        
        # Step 1: Get new orders
        print("\n1️⃣ Retrieving new orders...")
        try:
            new_orders = self.client.orders.list_new_orders(limit=5)
            print(f"   Found {len(new_orders)} new orders")
            
            if not new_orders:
                print("   No new orders to process")
                return
            
            # Process first order as example
            order_summary = new_orders[0]
            order = self.client.orders.get_order(str(order_summary.order_id))
            print(f"   Processing order: {order.customer_order_reference}")
            
        except Exception as e:
            print(f"   ❌ Error retrieving orders: {e}")
            return
        
        # Step 2: Validate and acknowledge order
        print("\n2️⃣ Acknowledging order...")
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
            
            self.client.orders.acknowledge_order(str(order.order_id), acknowledgement)
            print(f"   ✅ Order acknowledged")
            
        except Exception as e:
            print(f"   ❌ Error acknowledging order: {e}")
        
        # Step 3: Check inventory and create shipment
        print("\n3️⃣ Processing fulfillment...")
        try:
            # Check if we have inventory for all items
            can_fulfill = True
            for item in order.order_items:
                try:
                    inventory = self.client.skus.get_inventory(item.merchant_sku_id)
                    total_qty = sum(loc.quantity for loc in inventory.inventory)
                    if total_qty < item.sku_qty:
                        print(f"   ⚠️ Insufficient inventory for {item.merchant_sku_id}: need {item.sku_qty}, have {total_qty}")
                        can_fulfill = False
                except Exception:
                    print(f"   ⚠️ Could not check inventory for {item.merchant_sku_id}")
            
            if can_fulfill:
                # Create shipment
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
                
                shipment_id = self.client.orders.create_shipment(str(order.order_id), shipment_data)
                print(f"   ✅ Shipment created: {shipment_id}")
            else:
                print("   ❌ Cannot fulfill order due to inventory issues")
                
        except Exception as e:
            print(f"   ❌ Error processing fulfillment: {e}")
    
    def handle_returns_workflow(self):
        """Demonstrate returns processing workflow."""
        print("\n🔄 Processing returns workflow...")
        
        # Step 1: Get pending returns
        print("\n1️⃣ Retrieving pending returns...")
        try:
            pending_returns = self.client.returns.list_pending_returns(limit=3)
            print(f"   Found {len(pending_returns)} pending returns")
            
            if not pending_returns:
                print("   No pending returns to process")
                return
            
            # Process first return as example
            return_summary = pending_returns[0]
            return_detail = self.client.returns.get_return(str(return_summary.id))
            print(f"   Processing return: {return_detail.ran}")
            
        except Exception as e:
            print(f"   ❌ Error retrieving returns: {e}")
            return
        
        # Step 2: Update return with tracking info
        print("\n2️⃣ Updating return information...")
        try:
            update_data = ReturnUpdate(
                merchant_return_id=f"RET-{return_detail.ran}",
                notes=f"Return processed for customer {return_detail.customer.name}. "
                      f"Reason: {return_detail.reason_for_return}"
            )
            
            self.client.returns.update_return(str(return_detail.id), update_data)
            print(f"   ✅ Return information updated")
            
        except Exception as e:
            print(f"   ❌ Error updating return: {e}")
        
        # Step 3: Make approval decision (demo only - don't actually process)
        print("\n3️⃣ Making approval decision...")
        try:
            if return_detail.total_amount and return_detail.total_amount.amount < 50:
                print(f"   💰 Low-value return (${return_detail.total_amount.amount}) - would auto-approve")
                # self.client.returns.approve_return(str(return_detail.id))
            else:
                print(f"   🔍 High-value return - would require manual review")
            
            # Create customer communication ticket
            ticket_data = TicketCreate(
                message="Thank you for your return request. We have received your items and are processing your return. "
                       "You will receive an update within 24-48 hours.",
                attachments=[]
            )
            
            # Note: Actual ticket creation commented out for demo
            # self.client.returns.create_ticket_from_return(str(return_detail.id), ticket_data)
            print(f"   ✅ Customer communication prepared")
            
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
        """Demonstrate async operations for high-performance scenarios."""
        print("\n🚀 Demonstrating async operations...")
        
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
            
            # Batch processing simulation
            print("\n2️⃣ Batch processing simulation...")
            
            if not isinstance(new_orders, Exception) and new_orders:
                # Process multiple orders concurrently
                order_detail_tasks = [
                    self.async_client.orders.get_order_async(str(order.order_id))
                    for order in new_orders[:3]
                ]
                
                detailed_orders = await asyncio.gather(*order_detail_tasks, return_exceptions=True)
                
                processed_count = sum(1 for order in detailed_orders if not isinstance(order, Exception))
                print(f"     Processed {processed_count} orders concurrently")
            
            print("   ✅ Async operations completed successfully")
            
        except Exception as e:
            print(f"   ❌ Error in async operations: {e}")


def main():
    """Main workflow demonstration."""
    print("🚀 MySale API SDK - Complete Integration Workflow")
    print("=" * 60)
    
    # Initialize integration
    integration = MySaleIntegration(API_TOKEN)
    
    try:
        # Phase 1: Setup
        print("\n🏗️ PHASE 1: CATALOG SETUP")
        print("-" * 40)
        integration.setup_product_catalog()
        
        # Phase 2: Order Management
        print("\n📦 PHASE 2: ORDER MANAGEMENT")
        print("-" * 40)
        integration.process_order_workflow()
        
        # Phase 3: Returns Management
        print("\n🔄 PHASE 3: RETURNS MANAGEMENT")
        print("-" * 40)
        integration.handle_returns_workflow()
        
        # Phase 4: Operations Monitoring
        print("\n📊 PHASE 4: OPERATIONS MONITORING")
        print("-" * 40)
        integration.monitor_operations()
        
        # Phase 5: Async Operations
        print("\n🚀 PHASE 5: ASYNC OPERATIONS")
        print("-" * 40)
        asyncio.run(integration.async_operations_demo())
        
        print("\n✨ Complete workflow demonstration finished!")
        print("\n💡 Summary:")
        print(f"   - Catalog: {len(integration.created_skus)} SKUs, {len(integration.created_products)} products")
        print("   - Order processing workflow demonstrated")
        print("   - Returns management workflow demonstrated")
        print("   - Operations monitoring completed")
        print("   - Async operations showcased")
        
        print("\n🎯 Next Steps:")
        print("   1. Customize the workflow for your specific business needs")
        print("   2. Implement error handling and retry logic for production")
        print("   3. Add logging and monitoring for operational visibility")
        print("   4. Consider implementing webhooks for real-time notifications")
        print("   5. Set up scheduled tasks for regular data synchronization")
        
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
    
    finally:
        # Cleanup
        asyncio.run(integration.close_async_client())


if __name__ == "__main__":
    main()
