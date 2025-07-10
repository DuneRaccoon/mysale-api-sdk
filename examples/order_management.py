#!/usr/bin/env python3
"""
Example: Order Management with the MySale API SDK

This example demonstrates how to:
1. Retrieve and process new orders
2. Acknowledge orders using instance methods
3. Create shipments using instance methods
4. Handle cancellations using instance methods
5. Track order lifecycle
"""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models.order import (
    OrderAcknowledgement, AcknowledgementOrderItem,
    ShipmentCreate, ShipmentItem,
    CancellationCreate, CancelledItem
)

# Configuration
API_TOKEN = "your_api_token_here"


def process_new_orders():
    """Retrieve and process new orders using enhanced instance methods."""
    print("🔍 Processing new orders with instance methods...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get new orders that need processing
        new_orders = client.orders.list_new_orders(limit=50)
        print(f"Found {len(new_orders)} new orders")
        
        if not new_orders:
            print("No new orders to process")
            return []
        
        processed_orders = []
        
        for order_summary in new_orders[:5]:  # Process first 5 orders
            try:
                # Get full order details using collection method
                order = client.orders.get_order(str(order_summary.order_id))
                
                print(f"\n📦 Order {order.customer_order_reference}:")
                print(f"   Order ID: {order.order_id}")
                print(f"   Status: {order.order_status}")
                print(f"   Date: {order.order_date}")
                print(f"   Customer: {order.recipient.name}")
                print(f"   Email: {order.recipient.email}")
                print(f"   Items: {len(order.order_items)}")
                
                # Display order items
                total_value = 0
                for item in order.order_items:
                    item_total = item.item_sell_price.amount * item.sku_qty
                    total_value += item_total
                    print(f"     - {item.merchant_sku_id}: {item.sku_qty} × ${item.item_sell_price.amount} = ${item_total}")
                
                print(f"   Total Value: ${total_value}")
                print(f"   Shipping: {order.order_shipping_price.currency} ${order.order_shipping_price.amount}")
                
                # Display shipping address
                addr = order.recipient.address
                print(f"   Ship to: {addr.address_line}, {addr.city}, {addr.state} {addr.postcode}")
                
                processed_orders.append(order)
                
            except Exception as e:
                print(f"❌ Error processing order {order_summary.order_id}: {e}")
        
        return processed_orders
        
    except Exception as e:
        print(f"❌ Error retrieving new orders: {e}")
        return []


def acknowledge_order_instance_method(order):
    """Acknowledge an order using the new instance method."""
    print(f"\n✅ Acknowledging order using instance method: {order.customer_order_reference}...")
    
    try:
        # Create acknowledgement with internal order ID
        internal_order_id = f"INT-{order.customer_order_reference}-{datetime.now().strftime('%Y%m%d')}"
        
        acknowledgement = OrderAcknowledgement(
            merchant_order_id=internal_order_id,
            order_items=[
                AcknowledgementOrderItem(
                    order_item_id=item.order_item_id,
                    merchant_order_item_id=f"{internal_order_id}-{i+1}"
                )
                for i, item in enumerate(order.order_items)
            ]
        )
        
        # Instance method - much cleaner!
        order.acknowledge(acknowledgement)
        print(f"✅ Order acknowledged using instance method with internal ID: {internal_order_id}")
        
        return internal_order_id
        
    except Exception as e:
        print(f"❌ Error acknowledging order using instance method: {e}")
        return None


def create_shipment_instance_method(order, internal_order_id):
    """Create a shipment for an order using the new instance method."""
    print(f"\n📦 Creating shipment using instance method for order {order.customer_order_reference}...")
    
    try:
        # Create shipment data
        shipment_id = f"SHIP-{internal_order_id}-001"
        tracking_number = f"TR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        shipment = ShipmentCreate(
            merchant_shipment_id=shipment_id,
            tracking_number=tracking_number,
            carrier="Australia Post",
            carrier_shipment_method="Express Post",
            delivery_option="standard",
            dispatch_date=datetime.now(),
            expected_delivery_date=datetime.now() + timedelta(days=3),
            shipment_items=[
                ShipmentItem(
                    merchant_shipment_item_id=f"{shipment_id}-{i+1}",
                    merchant_sku_id=item.merchant_sku_id,
                    sku_id=item.sku_id,
                    sku_qty=item.sku_qty
                )
                for i, item in enumerate(order.order_items)
            ]
        )
        
        # Instance method - cleaner API!
        created_shipment_id = order.create_shipment(shipment)
        print(f"✅ Shipment created using instance method with ID: {created_shipment_id}")
        print(f"   Tracking number: {tracking_number}")
        print(f"   Expected delivery: {shipment.expected_delivery_date.strftime('%Y-%m-%d')}")
        
        return created_shipment_id, tracking_number
        
    except Exception as e:
        print(f"❌ Error creating shipment using instance method: {e}")
        return None, None


def handle_partial_cancellation_instance_method(order):
    """Demonstrate handling a partial order cancellation using instance method."""
    print(f"\n❌ Creating partial cancellation using instance method for order {order.customer_order_reference}...")
    
    try:
        # Cancel the first item (or part of it) due to no stock
        if order.order_items:
            first_item = order.order_items[0]
            cancel_qty = min(1, first_item.sku_qty)  # Cancel 1 unit or the full quantity
            
            cancellation = CancellationCreate(
                cancelled_items=[
                    CancelledItem(
                        merchant_cancel_item_id=f"CANCEL-{order.customer_order_reference}-1",
                        merchant_sku_id=first_item.merchant_sku_id,
                        sku_id=first_item.sku_id,
                        sku_qty=cancel_qty,
                        cancellation_reason="no_stock"
                    )
                ]
            )
            
            # Instance method!
            cancellation_id = order.create_cancellation(cancellation)
            print(f"✅ Partial cancellation created using instance method with ID: {cancellation_id}")
            print(f"   Cancelled: {cancel_qty} × {first_item.merchant_sku_id} (No stock)")
            
            return cancellation_id
        
    except Exception as e:
        print(f"❌ Error creating cancellation using instance method: {e}")
        return None


def get_order_details_with_shipments_instance_method(order):
    """Get comprehensive order details using instance methods."""
    print(f"\n🔍 Getting detailed information using instance methods for order {order.customer_order_reference}...")
    
    try:
        print(f"Order {order.customer_order_reference} ({order.order_status}):")
        
        # Get shipments using instance method
        try:
            shipments = order.get_shipments()
            print(f"   Shipments: {len(shipments.shipments)}")
            
            for shipment in shipments.shipments:
                print(f"     - {shipment.merchant_shipment_id}")
                print(f"       Tracking: {shipment.tracking_number}")
                print(f"       Carrier: {shipment.carrier} ({shipment.carrier_shipment_method})")
                print(f"       Items: {len(shipment.shipment_items)}")
                
        except Exception as e:
            print(f"   No shipments found: {e}")
        
        # Get cancellations using instance method
        try:
            cancellations = order.get_cancellations()
            print(f"   Cancellations: {len(cancellations.cancellations)}")
            
            for cancellation in cancellations.cancellations:
                print(f"     - Cancellation ID: {cancellation.cancellation_id}")
                for item in cancellation.cancelled_items:
                    print(f"       {item.merchant_sku_id}: {item.sku_qty} ({item.cancellation_reason})")
                    
        except Exception as e:
            print(f"   No cancellations found: {e}")
            
    except Exception as e:
        print(f"❌ Error getting order details using instance methods: {e}")


def track_order_status():
    """Track orders across different statuses."""
    print("\n📊 Tracking orders by status...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        statuses = [
            ("new", client.orders.list_new_orders),
            ("acknowledged", client.orders.list_acknowledged_orders),
            ("inprogress", client.orders.list_inprogress_orders),
            ("completed", client.orders.list_completed_orders)
        ]
        
        for status_name, list_method in statuses:
            orders = list_method(limit=10)
            print(f"   {status_name.title()}: {len(orders)} orders")
            
            # Show a few examples
            for order in orders[:3]:
                merchant_id = order.merchant_order_id or "No internal ID"
                print(f"     - {order.order_id} ({merchant_id})")
        
        # Get incomplete orders (new + acknowledged + inprogress)
        incomplete = client.orders.list_incomplete_orders(limit=50)
        print(f"\n   Total incomplete orders: {len(incomplete)}")
        
    except Exception as e:
        print(f"❌ Error tracking order status: {e}")


async def async_order_processing_with_instance_methods():
    """Demonstrate async order processing using instance methods."""
    print("\n🔄 Demonstrating async order processing with instance methods...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get orders from multiple statuses concurrently
        tasks = [
            client.orders.list_new_orders_async(limit=5),
            client.orders.list_acknowledged_orders_async(limit=5),
            client.orders.list_inprogress_orders_async(limit=5)
        ]
        
        new_orders, ack_orders, progress_orders = await asyncio.gather(*tasks)
        
        print(f"📊 Async results:")
        print(f"   New orders: {len(new_orders)}")
        print(f"   Acknowledged orders: {len(ack_orders)}")
        print(f"   In-progress orders: {len(progress_orders)}")
        
        # Process multiple orders concurrently using instance methods
        if new_orders:
            order_detail_tasks = [
                client.orders.get_order_async(str(order.order_id))
                for order in new_orders[:3]
            ]
            
            detailed_orders = await asyncio.gather(*order_detail_tasks, return_exceptions=True)
            
            print("\n🔍 Processing orders with async instance methods:")
            for result in detailed_orders:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   Order {result.customer_order_reference}: {len(result.order_items)} items")
                    
                    # Demonstrate async instance method
                    try:
                        acknowledgement = OrderAcknowledgement(
                            merchant_order_id=f"ASYNC-{result.customer_order_reference}",
                            order_items=[]
                        )
                        
                        # Async instance method
                        await result.acknowledge_async(acknowledgement)
                        print(f"     ✅ Acknowledged using async instance method")
                        
                        # Create shipment using async instance method
                        shipment = ShipmentCreate(
                            merchant_shipment_id=f"ASYNC-SHIP-{result.customer_order_reference}",
                            tracking_number=f"ASYNC{datetime.now().strftime('%H%M%S')}",
                            carrier="Fast Delivery",
                            shipment_items=[
                                ShipmentItem(
                                    merchant_sku_id=item.merchant_sku_id,
                                    sku_id=item.sku_id,
                                    sku_qty=item.sku_qty
                                )
                                for item in result.order_items
                            ]
                        )
                        
                        # Async instance method
                        shipment_id = await result.create_shipment_async(shipment)
                        print(f"     ✅ Created shipment using async instance method: {shipment_id}")
                        
                    except Exception as e:
                        print(f"     ❌ Error in async instance methods: {e}")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def demonstrate_order_workflow_with_instance_methods():
    """Demonstrate a complete order workflow using instance methods."""
    print("\n🔄 Demonstrating complete order workflow with instance methods...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Step 1: Get new orders
        print("Step 1: Retrieving new orders...")
        new_orders = client.orders.list_new_orders(limit=3)
        
        if not new_orders:
            print("No new orders to process")
            return
        
        # Step 2: Process each order using instance methods
        for order_summary in new_orders:
            try:
                # Get full order instance
                order = client.orders.get_order(str(order_summary.order_id))
                print(f"\nProcessing order: {order.customer_order_reference}")
                
                # Acknowledge using instance method
                acknowledgement = OrderAcknowledgement(
                    merchant_order_id=f"WORKFLOW-{order.customer_order_reference}",
                    order_items=[
                        AcknowledgementOrderItem(
                            order_item_id=item.order_item_id,
                            merchant_order_item_id=f"ITEM-{i+1}"
                        )
                        for i, item in enumerate(order.order_items)
                    ]
                )
                
                # Instance method
                order.acknowledge(acknowledgement)
                print(f"   ✅ Acknowledged")
                
                # Create shipment using instance method
                shipment = ShipmentCreate(
                    merchant_shipment_id=f"WORKFLOW-SHIP-{order.customer_order_reference}",
                    tracking_number=f"WF{datetime.now().strftime('%H%M%S')}",
                    carrier="Standard Shipping",
                    shipment_items=[
                        ShipmentItem(
                            merchant_sku_id=item.merchant_sku_id,
                            sku_id=item.sku_id,
                            sku_qty=item.sku_qty
                        )
                        for item in order.order_items
                    ]
                )
                
                # Instance method
                shipment_id = order.create_shipment(shipment)
                print(f"   ✅ Created shipment: {shipment_id}")
                
                # Get shipments to verify using instance method
                shipments = order.get_shipments()
                print(f"   📦 Order now has {len(shipments.shipments)} shipments")
                
            except Exception as e:
                print(f"   ❌ Error processing order {order_summary.order_id}: {e}")
        
        print("\n🎉 Workflow demonstration completed!")
        
    except Exception as e:
        print(f"❌ Error in workflow demonstration: {e}")


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Enhanced Order Management Example")
    print("=" * 60)
    
    # Process new orders
    orders = process_new_orders()
    
    if orders:
        # Take the first order for detailed processing
        sample_order = orders[0]
        
        # Acknowledge the order using instance method
        internal_id = acknowledge_order_instance_method(sample_order)
        
        if internal_id:
            # Create shipment using instance method
            shipment_id, tracking = create_shipment_instance_method(sample_order, internal_id)
            
            # Demonstrate partial cancellation using instance method (commented out to avoid affecting real orders)
            # handle_partial_cancellation_instance_method(sample_order)
            
            # Get detailed order information using instance methods
            get_order_details_with_shipments_instance_method(sample_order)
    
    # Track order statuses
    track_order_status()
    
    # Demonstrate complete workflow
    demonstrate_order_workflow_with_instance_methods()
    
    # Demonstrate async processing with instance methods
    print("\n" + "="*60)
    print("ASYNC OPERATIONS WITH INSTANCE METHODS")
    print("="*60)
    asyncio.run(async_order_processing_with_instance_methods())
    
    print("\n✨ Enhanced order management example completed!")
    print("\n💡 Key improvements:")
    print("   • Instance-based methods: order.acknowledge() instead of client.orders.acknowledge_order(order_id)")
    print("   • Cleaner shipment creation: order.create_shipment() instead of client.orders.create_shipment(order_id)")
    print("   • Simplified cancellations: order.create_cancellation() instead of client.orders.create_cancellation(order_id)")
    print("   • Direct access to related data: order.get_shipments() instead of client.orders.get_shipments(order_id)")
    print("   • More intuitive API that follows object-oriented principles")


if __name__ == "__main__":
    main()
