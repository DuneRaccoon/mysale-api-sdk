#!/usr/bin/env python3
"""
Example: Returns Management with the MySale API SDK

This example demonstrates how to:
1. Retrieve returns by status
2. Process return approvals/declines
3. Handle refunds (full and partial)
4. Manage return tickets
5. Update return information
"""

import asyncio
from decimal import Decimal

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import (
    ReturnUpdate, PartialRefund, Price,
    TicketCreate, TicketAttachment
)

# Configuration
API_TOKEN = "your_api_token_here"


def process_pending_returns():
    """Retrieve and process pending returns."""
    print("🔍 Processing pending returns...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get pending returns
        pending_returns = client.returns.list_pending_returns(limit=20)
        print(f"Found {len(pending_returns)} pending returns")
        
        if not pending_returns:
            print("No pending returns to process")
            return []
        
        processed_returns = []
        
        for return_summary in pending_returns[:5]:  # Process first 5 returns
            try:
                # Get full return details
                return_detail = client.returns.get_return(str(return_summary.id))
                
                print(f"\n📋 Return {return_detail.ran}:")
                print(f"   Return ID: {return_detail.id}")
                print(f"   Status: {return_detail.status}")
                print(f"   Customer: {return_detail.customer.name} ({return_detail.customer.email})")
                print(f"   Order Reference: {return_detail.customer_order_reference}")
                print(f"   Reason: {return_detail.reason_for_return}")
                
                # Display return amounts
                if return_detail.total_amount:
                    print(f"   Total Amount: {return_detail.total_amount.currency} ${return_detail.total_amount.amount}")
                if return_detail.amount_to_refund:
                    print(f"   To Refund: {return_detail.amount_to_refund.currency} ${return_detail.amount_to_refund.amount}")
                if return_detail.amount_refunded:
                    print(f"   Already Refunded: {return_detail.amount_refunded.currency} ${return_detail.amount_refunded.amount}")
                
                # Display returned items
                if return_detail.items:
                    print(f"   Items ({len(return_detail.items)}):")
                    for item in return_detail.items:
                        print(f"     - {item.merchant_sku_id}: {item.sku_qty} × ${item.item_sell_price.amount}")
                
                # Display attachments
                if return_detail.attachments:
                    print(f"   Attachments: {len(return_detail.attachments)}")
                    for attachment in return_detail.attachments:
                        print(f"     - {attachment.title}: {attachment.type}")
                
                processed_returns.append(return_detail)
                
            except Exception as e:
                print(f"❌ Error processing return {return_summary.id}: {e}")
        
        return processed_returns
        
    except Exception as e:
        print(f"❌ Error retrieving pending returns: {e}")
        return []


def approve_return(return_detail):
    """Approve a return."""
    print(f"\n✅ Approving return {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Approve the return
        approved_return = client.returns.approve_return(str(return_detail.id))
        print(f"✅ Return approved successfully")
        print(f"   New status: {approved_return.status}")
        
        return approved_return
        
    except Exception as e:
        print(f"❌ Error approving return: {e}")
        return None


def decline_return_with_reason(return_detail):
    """Decline a return and add notes."""
    print(f"\n❌ Declining return {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # First update the return with decline reason
        update_data = ReturnUpdate(
            notes="Return declined - item shows signs of use beyond return policy limits. "
                  "Customer contacted via email with explanation."
        )
        
        client.returns.update_return(str(return_detail.id), update_data)
        print("✅ Added decline reason notes")
        
        # Then decline the return
        declined_return = client.returns.decline_return(str(return_detail.id))
        print(f"✅ Return declined successfully")
        print(f"   New status: {declined_return.status}")
        
        return declined_return
        
    except Exception as e:
        print(f"❌ Error declining return: {e}")
        return None


def process_full_refund(return_detail):
    """Process a full refund for a return."""
    print(f"\n💰 Processing full refund for return {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Process full refund
        refunded_return = client.returns.full_refund_return(str(return_detail.id))
        print(f"✅ Full refund processed successfully")
        print(f"   New status: {refunded_return.status}")
        
        if refunded_return.amount_refunded:
            print(f"   Refunded amount: {refunded_return.amount_refunded.currency} ${refunded_return.amount_refunded.amount}")
        
        return refunded_return
        
    except Exception as e:
        print(f"❌ Error processing full refund: {e}")
        return None


def process_partial_refund(return_detail, refund_amount: Decimal):
    """Process a partial refund for a return."""
    print(f"\n💰 Processing partial refund for return {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Determine currency from return details
        currency = "AUD"
        if return_detail.total_amount:
            currency = return_detail.total_amount.currency
        
        # Create partial refund data
        partial_refund = PartialRefund(
            amount_to_refund=Price(
                currency=currency,
                amount=refund_amount
            )
        )
        
        # Process partial refund
        refunded_return = client.returns.partial_refund_return(str(return_detail.id), partial_refund)
        print(f"✅ Partial refund processed successfully")
        print(f"   Refunded amount: {currency} ${refund_amount}")
        print(f"   New status: {refunded_return.status}")
        
        return refunded_return
        
    except Exception as e:
        print(f"❌ Error processing partial refund: {e}")
        return None


def manage_return_tickets(return_detail):
    """Manage tickets associated with a return."""
    print(f"\n🎫 Managing tickets for return {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get existing tickets
        tickets = client.returns.get_return_tickets(str(return_detail.id))
        print(f"Found {len(tickets)} existing tickets")
        
        for ticket in tickets:
            print(f"   - Ticket #{ticket.id}: {ticket.subject}")
            print(f"     Status: {ticket.status}")
            print(f"     Customer: {ticket.customer.name}")
            print(f"     New: {ticket.is_new}")
        
        # Create a new ticket
        ticket_data = TicketCreate(
            message="Thank you for your return request. We are processing it and will "
                   "update you within 24-48 hours. If you have any questions, please reply to this ticket.",
            attachments=[
                TicketAttachment(url="https://example.com/return-policy.pdf")
            ]
        )
        
        new_ticket = client.returns.create_ticket_from_return(str(return_detail.id), ticket_data)
        print(f"✅ Created new ticket #{new_ticket.id}")
        print(f"   Subject: {new_ticket.subject if hasattr(new_ticket, 'subject') else 'Return Follow-up'}")
        print(f"   Messages: {len(new_ticket.messages)}")
        
        return new_ticket
        
    except Exception as e:
        print(f"❌ Error managing tickets: {e}")
        return None


def track_returns_by_status():
    """Track returns across different statuses."""
    print("\n📊 Tracking returns by status...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        statuses = [
            ("pending", client.returns.list_pending_returns),
            ("awaiting", client.returns.list_awaiting_returns),
            ("received", client.returns.list_received_returns),
            ("closed", client.returns.list_closed_returns),
            ("declined", client.returns.list_declined_returns)
        ]
        
        total_returns = 0
        
        for status_name, list_method in statuses:
            returns = list_method(limit=100)
            total_returns += len(returns)
            print(f"   {status_name.title()}: {len(returns)} returns")
            
            # Show a few examples
            for return_item in returns[:3]:
                merchant_id = return_item.merchant_return_id or "No merchant ID"
                print(f"     - {return_item.ran} ({merchant_id})")
        
        print(f"\n   Total returns: {total_returns}")
        
    except Exception as e:
        print(f"❌ Error tracking returns: {e}")


def update_return_information(return_detail):
    """Update return information with merchant tracking and notes."""
    print(f"\n📝 Updating return information for {return_detail.ran}...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Update return with merchant ID and notes
        update_data = ReturnUpdate(
            merchant_return_id=f"RET-{return_detail.ran}-2025",
            notes=f"Return processed on {return_detail.ran}. "
                  f"Customer: {return_detail.customer.name}. "
                  f"Original order: {return_detail.customer_order_reference}. "
                  f"Reason: {return_detail.reason_for_return}"
        )
        
        updated_return = client.returns.update_return(str(return_detail.id), update_data)
        print(f"✅ Return information updated")
        print(f"   Merchant Return ID: {updated_return.merchant_return_id}")
        print(f"   Notes length: {len(updated_return.notes or '')}")
        
        return updated_return
        
    except Exception as e:
        print(f"❌ Error updating return: {e}")
        return None


async def async_returns_processing():
    """Demonstrate async returns processing for high-volume scenarios."""
    print("\n🔄 Demonstrating async returns processing...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get returns from multiple statuses concurrently
        tasks = [
            client.returns.list_pending_returns_async(limit=5),
            client.returns.list_awaiting_returns_async(limit=5),
            client.returns.list_received_returns_async(limit=5)
        ]
        
        pending, awaiting, received = await asyncio.gather(*tasks)
        
        print(f"📊 Async results:")
        print(f"   Pending returns: {len(pending)}")
        print(f"   Awaiting returns: {len(awaiting)}")
        print(f"   Received returns: {len(received)}")
        
        # Process multiple returns concurrently
        all_returns = pending + awaiting + received
        if all_returns:
            detail_tasks = [
                client.returns.get_return_async(str(return_item.id))
                for return_item in all_returns[:3]
            ]
            
            detailed_returns = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            print("\n🔍 Detailed return info:")
            for result in detailed_returns:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.ran}: {result.customer.name} - {result.status}")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def demonstrate_return_workflow(return_detail):
    """Demonstrate a complete return workflow."""
    print(f"\n🔄 Demonstrating workflow for return {return_detail.ran}...")
    
    # Step 1: Update return with tracking info
    updated_return = update_return_information(return_detail)
    
    if not updated_return:
        return
    
    # Step 2: Create a ticket for customer communication
    manage_return_tickets(updated_return)
    
    # Step 3: Make a decision based on return amount
    if return_detail.total_amount and return_detail.total_amount.amount > 50:
        # For higher value returns, we might want partial refund initially
        print("   High-value return detected - considering partial refund...")
        # process_partial_refund(updated_return, Decimal("25.00"))
    else:
        # For lower value returns, approve and full refund
        print("   Standard return - processing approval...")
        # approved_return = approve_return(updated_return)
        # if approved_return:
        #     process_full_refund(approved_return)
    
    print("   Workflow demonstration completed (no actual changes made)")


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Returns Management Example")
    print("=" * 50)
    
    # Process pending returns
    returns = process_pending_returns()
    
    if returns:
        # Take the first return for detailed processing
        sample_return = returns[0]
        
        # Demonstrate complete workflow (commented out to avoid affecting real data)
        demonstrate_return_workflow(sample_return)
        
        # Individual operations (commented out to avoid affecting real data)
        # approve_return(sample_return)
        # process_partial_refund(sample_return, Decimal("15.50"))
        # manage_return_tickets(sample_return)
    
    # Track returns by status
    track_returns_by_status()
    
    # Demonstrate async processing
    asyncio.run(async_returns_processing())
    
    print("\n✨ Returns management example completed!")
    print("\n💡 Note: Most operations were demonstrated without making actual changes.")
    print("   Uncomment the processing calls to perform real operations.")


if __name__ == "__main__":
    main()
