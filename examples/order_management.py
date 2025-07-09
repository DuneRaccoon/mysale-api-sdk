#!/usr/bin/env python3
"""
Example: Order Management with the MySale API SDK

This example demonstrates how to:
1. Retrieve and process new orders
2. Acknowledge orders
3. Create shipments
4. Handle cancellations
5. Track order lifecycle
"""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import (
    OrderAcknowledgement, AcknowledgementOrderItem,
    ShipmentCreate, ShipmentItem,
    CancellationCreate, CancelledItem
)

# Configuration
API_TOKEN = "your_api_token_here"


def process_new_orders():
    """Retrieve and process new orders."""
    print("🔍 Processing new orders...")
    
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
                # Get full order details
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


def acknowledge_order(order):
    """Acknowledge an order and assign internal order ID."""
    print(f"\n✅ Acknowledging order {order.customer_order_reference}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
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
        
        client.orders.acknowledge_order(str(order.order_id), acknowledgement)
        print(f"✅ Order acknowledged with internal ID: {internal_order_id}")
        
        return internal_order_id
        
    except Exception as e:
        print(f"❌ Error acknowledging order: {e}")
        return None


def create_shipment_for_order(order, internal_order_id):
    """Create a shipment for an order."""
    print(f"\n📦 Creating shipment for order {order.customer_order_reference}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
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
        
        # Create the shipment
        created_shipment_id = client.orders.create_shipment(str(order.order_id), shipment)
        print(f"✅ Shipment created with ID: {created_shipment_id}")
        print(f"   Tracking number: {tracking_number}")
        print(f"   Expected delivery: {shipment.expected_delivery_date.strftime('%Y-%m-%d')}")
        
        return created_shipment_id, tracking_number
        
    except Exception as e:
        print(f"❌ Error creating shipment: {e}")
        return None, None


def handle_partial_cancellation(order):
    """Demonstrate handling a partial order cancellation."""
    print(f"\n❌ Creating partial cancellation for order {order.customer_order_reference}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
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
            
            cancellation_id = client.orders.create_cancellation(str(order.order_id), cancellation)
            print(f"✅ Partial cancellation created with ID: {cancellation_id}")
            print(f"   Cancelled: {cancel_qty} × {first_item.merchant_sku_id} (No stock)")
            
            return cancellation_id
        
    except Exception as e:
        print(f"❌ Error creating cancellation: {e}")
        return None


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


def get_order_details_with_shipments(order_id: str):
    """Get comprehensive order details including shipments and cancellations."""
    print(f"\n🔍 Getting detailed information for order {order_id}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get order details
        order = client.orders.get_order(order_id)
        print(f"Order {order.customer_order_reference} ({order.order_status}):")
        
        # Get shipments
        try:
            shipments = client.orders.get_shipments(order_id)
            print(f"   Shipments: {len(shipments.shipments)}")
            
            for shipment in shipments.shipments:
                print(f"     - {shipment.merchant_shipment_id}")
                print(f"       Tracking: {shipment.tracking_number}")
                print(f"       Carrier: {shipment.carrier} ({shipment.carrier_shipment_method})")
                print(f"       Items: {len(shipment.shipment_items)}")
                
        except Exception as e:
            print(f"   No shipments found: {e}")
        
        # Get cancellations
        try:
            cancellations = client.orders.get_cancellations(order_id)
            print(f"   Cancellations: {len(cancellations.cancellations)}")
            
            for cancellation in cancellations.cancellations:
                print(f"     - Cancellation ID: {cancellation.cancellation_id}")
                for item in cancellation.cancelled_items:
                    print(f"       {item.merchant_sku_id}: {item.sku_qty} ({item.cancellation_reason})")
                    
        except Exception as e:
            print(f"   No cancellations found: {e}")
            
    except Exception as e:
        print(f"❌ Error getting order details: {e}")


async def async_order_processing():
    """Demonstrate async order processing for high-volume scenarios."""
    print("\n🔄 Demonstrating async order processing...")
    
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
        
        # Process multiple orders concurrently
        if new_orders:
            order_detail_tasks = [
                client.orders.get_order_async(str(order.order_id))
                for order in new_orders[:3]
            ]
            
            detailed_orders = await asyncio.gather(*order_detail_tasks, return_exceptions=True)
            
            print("\n🔍 Detailed order info:")
            for result in detailed_orders:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.customer_order_reference}: {len(result.order_items)} items")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Order Management Example")
    print("=" * 50)
    
    # Process new orders
    orders = process_new_orders()
    
    if orders:
        # Take the first order for detailed processing
        sample_order = orders[0]
        
        # Acknowledge the order
        internal_id = acknowledge_order(sample_order)
        
        if internal_id:
            # Create shipment
            shipment_id, tracking = create_shipment_for_order(sample_order, internal_id)
            
            # Demonstrate partial cancellation (commented out to avoid affecting real orders)
            # handle_partial_cancellation(sample_order)
            
            # Get detailed order information
            get_order_details_with_shipments(str(sample_order.order_id))
    
    # Track order statuses
    track_order_status()
    
    # Demonstrate async processing
    asyncio.run(async_order_processing())
    
    print("\n✨ Order management example completed!")


if __name__ == "__main__":
    main()
