#!/usr/bin/env python3
"""
Example: Returns Management with the MySale API SDK

This example demonstrates how to:
1. Retrieve returns by status
2. Process return approvals/declines using instance methods
3. Handle refunds (full and partial) using instance methods
4. Manage return tickets using instance methods
5. Update return information using instance methods
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
    """Retrieve and process pending returns using enhanced instance methods."""
    print("🔍 Processing pending returns with instance methods...")
    
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
                # Get full return details using collection method
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


def approve_return_instance_method(return_detail):
    """Approve a return using the new instance method."""
    print(f"\n✅ Approving return using instance method: {return_detail.ran}...")
    
    try:
        # Instance method - much cleaner!
        approved_return = return_detail.approve()
        print(f"✅ Return approved using instance method")
        print(f"   New status: {approved_return.status}")
        
        return approved_return
        
    except Exception as e:
        print(f"❌ Error approving return using instance method: {e}")
        return None


def decline_return_with_reason_instance_method(return_detail):
    """Decline a return and add notes using instance methods."""
    print(f"\n❌ Declining return using instance methods: {return_detail.ran}...")
    
    try:
        # First update the return with decline reason using instance method
        update_data = ReturnUpdate(
            notes="Return declined - item shows signs of use beyond return policy limits. "
                  "Customer contacted via email with explanation."
        )
        
        # Instance method
        return_detail.update_return(update_data)
        print("✅ Added decline reason notes using instance method")
        
        # Then decline the return using instance method
        declined_return = return_detail.decline()
        print(f"✅ Return declined using instance method")
        print(f"   New status: {declined_return.status}")
        
        return declined_return
        
    except Exception as e:
        print(f"❌ Error declining return using instance methods: {e}")
        return None


def process_full_refund_instance_method(return_detail):
    """Process a full refund for a return using instance method."""
    print(f"\n💰 Processing full refund using instance method: {return_detail.ran}...")
    
    try:
        # Instance method
        refunded_return = return_detail.full_refund()
        print(f"✅ Full refund processed using instance method")
        print(f"   New status: {refunded_return.status}")
        
        if refunded_return.amount_refunded:
            print(f"   Refunded amount: {refunded_return.amount_refunded.currency} ${refunded_return.amount_refunded.amount}")
        
        return refunded_return
        
    except Exception as e:
        print(f"❌ Error processing full refund using instance method: {e}")
        return None


def process_partial_refund_instance_method(return_detail, refund_amount: Decimal):
    """Process a partial refund for a return using instance method."""
    print(f"\n💰 Processing partial refund using instance method: {return_detail.ran}...")
    
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
        
        # Instance method
        refunded_return = return_detail.partial_refund(partial_refund)
        print(f"✅ Partial refund processed using instance method")
        print(f"   Refunded amount: {currency} ${refund_amount}")
        print(f"   New status: {refunded_return.status}")
        
        return refunded_return
        
    except Exception as e:
        print(f"❌ Error processing partial refund using instance method: {e}")
        return None


def manage_return_tickets_instance_method(return_detail):
    """Manage tickets associated with a return using instance methods."""
    print(f"\n🎫 Managing tickets using instance methods for return {return_detail.ran}...")
    
    try:
        # Get existing tickets using instance method
        tickets = return_detail.get_tickets()
        print(f"Found {len(tickets)} existing tickets")
        
        for ticket in tickets:
            print(f"   - Ticket #{ticket.id}: {ticket.subject}")
            print(f"     Status: {ticket.status}")
            print(f"     Customer: {ticket.customer.name}")
            print(f"     New: {ticket.is_new}")
        
        # Create a new ticket using instance method
        ticket_data = TicketCreate(
            message="Thank you for your return request. We are processing it and will "
                   "update you within 24-48 hours. If you have any questions, please reply to this ticket.",
            attachments=[
                TicketAttachment(url="https://example.com/return-policy.pdf")
            ]
        )
        
        # Instance method
        new_ticket = return_detail.create_ticket(ticket_data)
        print(f"✅ Created new ticket using instance method: #{new_ticket.id}")
        print(f"   Messages: {len(new_ticket.messages)}")
        
        return new_ticket
        
    except Exception as e:
        print(f"❌ Error managing tickets using instance methods: {e}")
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


def update_return_information_instance_method(return_detail):
    """Update return information using instance method."""
    print(f"\n📝 Updating return information using instance method: {return_detail.ran}...")
    
    try:
        # Update return with merchant ID and notes using instance method
        update_data = ReturnUpdate(
            merchant_return_id=f"RET-{return_detail.ran}-2025",
            notes=f"Return processed on {return_detail.ran}. "
                  f"Customer: {return_detail.customer.name}. "
                  f"Original order: {return_detail.customer_order_reference}. "
                  f"Reason: {return_detail.reason_for_return}"
        )
        
        # Instance method
        updated_return = return_detail.update_return(update_data)
        print(f"✅ Return information updated using instance method")
        print(f"   Merchant Return ID: {updated_return.merchant_return_id}")
        print(f"   Notes length: {len(updated_return.notes or '')}")
        
        return updated_return
        
    except Exception as e:
        print(f"❌ Error updating return using instance method: {e}")
        return None


async def async_returns_processing_with_instance_methods():
    """Demonstrate async returns processing using instance methods."""
    print("\n🔄 Demonstrating async returns processing with instance methods...")
    
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
        
        # Process multiple returns concurrently using instance methods
        all_returns = pending + awaiting + received
        if all_returns:
            detail_tasks = [
                client.returns.get_return_async(str(return_item.id))
                for return_item in all_returns[:3]
            ]
            
            detailed_returns = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            print("\n🔍 Processing returns with async instance methods:")
            for result in detailed_returns:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   Return {result.ran}: {result.customer.name} - {result.status}")
                    
                    # Demonstrate async instance methods
                    try:
                        # Update return using async instance method
                        update_data = ReturnUpdate(
                            merchant_return_id=f"ASYNC-{result.ran}",
                            notes=f"Processed asynchronously for {result.customer.name}"
                        )
                        
                        # Async instance method
                        updated_return = await result.update_return_async(update_data)
                        print(f"     ✅ Updated using async instance method")
                        
                        # For low-value returns, approve automatically
                        if result.total_amount and result.total_amount.amount < 25:
                            approved_return = await result.approve_async()
                            print(f"     ✅ Auto-approved low-value return using async instance method")
                        
                    except Exception as e:
                        print(f"     ❌ Error in async instance methods: {e}")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def demonstrate_return_workflow_with_instance_methods(return_detail):
    """Demonstrate a complete return workflow using instance methods."""
    print(f"\n🔄 Demonstrating workflow using instance methods for return {return_detail.ran}...")
    
    try:
        # Step 1: Update return with tracking info using instance method
        updated_return = update_return_information_instance_method(return_detail)
        
        if not updated_return:
            return
        
        # Step 2: Create a ticket for customer communication using instance method
        manage_return_tickets_instance_method(updated_return)
        
        # Step 3: Make a decision based on return amount using instance methods
        if return_detail.total_amount and return_detail.total_amount.amount > 50:
            # For higher value returns, we might want partial refund initially
            print("   High-value return detected - processing partial refund using instance method...")
            # partial_refund_result = process_partial_refund_instance_method(updated_return, Decimal("25.00"))
            print("   (Partial refund commented out for demo)")
        else:
            # For lower value returns, approve and full refund using instance methods
            print("   Standard return - processing approval using instance methods...")
            # approved_return = approve_return_instance_method(updated_return)
            # if approved_return:
            #     process_full_refund_instance_method(approved_return)
            print("   (Approval and refund commented out for demo)")
        
        print("   Workflow demonstration completed using instance methods")
        
    except Exception as e:
        print(f"❌ Error in workflow demonstration: {e}")


def demonstrate_bulk_return_processing():
    """Demonstrate processing multiple returns efficiently."""
    print("\n📋 Demonstrating bulk return processing...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get pending returns
        pending_returns = client.returns.list_pending_returns(limit=10)
        
        if not pending_returns:
            print("No pending returns for bulk processing")
            return
        
        print(f"Processing {len(pending_returns)} returns...")
        
        # Process each return
        processed_count = 0
        approved_count = 0
        updated_count = 0
        
        for return_summary in pending_returns:
            try:
                # Get detailed return instance
                return_detail = client.returns.get_return(str(return_summary.id))
                
                print(f"\nProcessing return {return_detail.ran}:")
                
                # Update with merchant tracking ID using instance method
                update_data = ReturnUpdate(
                    merchant_return_id=f"BULK-{return_detail.ran}",
                    notes=f"Bulk processed return for {return_detail.customer.name}"
                )
                return_detail.update_return(update_data)
                updated_count += 1
                print(f"   ✅ Updated with merchant ID")
                
                # Auto-approve low-value returns using instance method
                if (return_detail.total_amount and 
                    return_detail.total_amount.amount < 30 and 
                    return_detail.reason_for_return in ["damaged", "wrong_item"]):
                    
                    # Instance methods for approval workflow
                    approved_return = return_detail.approve()
                    print(f"   ✅ Auto-approved (${return_detail.total_amount.amount})")
                    
                    # Auto-refund if approved
                    refunded_return = approved_return.full_refund()
                    print(f"   ✅ Auto-refunded")
                    
                    approved_count += 1
                
                processed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing return {return_summary.id}: {e}")
        
        print(f"\n📊 Bulk processing summary:")
        print(f"   Processed: {processed_count}/{len(pending_returns)}")
        print(f"   Updated: {updated_count}")
        print(f"   Auto-approved: {approved_count}")
        
    except Exception as e:
        print(f"❌ Error in bulk processing: {e}")


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Enhanced Returns Management Example")
    print("=" * 60)
    
    # Process pending returns
    returns = process_pending_returns()
    
    if returns:
        # Take the first return for detailed processing
        sample_return = returns[0]
        
        # Demonstrate complete workflow using instance methods (commented out to avoid affecting real data)
        demonstrate_return_workflow_with_instance_methods(sample_return)
        
        # Individual operations using instance methods (commented out to avoid affecting real data)
        # approve_return_instance_method(sample_return)
        # process_partial_refund_instance_method(sample_return, Decimal("15.50"))
        # manage_return_tickets_instance_method(sample_return)
        
        print("\n💡 Individual operations commented out to avoid affecting real data")
    
    # Track returns by status
    track_returns_by_status()
    
    # Demonstrate bulk processing
    # demonstrate_bulk_return_processing()  # Commented out for safety
    print("\n💡 Bulk processing commented out to avoid affecting real data")
    
    # Demonstrate async processing with instance methods
    print("\n" + "="*60)
    print("ASYNC OPERATIONS WITH INSTANCE METHODS")
    print("="*60)
    asyncio.run(async_returns_processing_with_instance_methods())
    
    print("\n✨ Enhanced returns management example completed!")
    print("\n💡 Key improvements:")
    print("   • Instance-based methods: return_detail.approve() instead of client.returns.approve_return(return_id)")
    print("   • Simplified refunds: return_detail.full_refund() instead of client.returns.full_refund_return(return_id)")
    print("   • Direct ticket management: return_detail.create_ticket() instead of client.returns.create_ticket_from_return(return_id)")
    print("   • Cleaner updates: return_detail.update_return() instead of client.returns.update_return(return_id)")
    print("   • More intuitive workflow that follows object-oriented principles")
    print("   • Most operations were demonstrated without making actual changes")


if __name__ == "__main__":
    main()
