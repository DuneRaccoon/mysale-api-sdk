#!/usr/bin/env python3
"""
Example: Shipping Policies Management with the MySale API SDK

This example demonstrates how to:
1. Retrieve and analyze shipping policies
2. Find policies by criteria
3. Analyze shipping coverage
4. Work with shipping zones and rules
"""

import asyncio
from typing import List

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import ShippingPolicy

# Configuration
API_TOKEN = "your_api_token_here"


def list_all_shipping_policies():
    """Retrieve and display all shipping policies."""
    print("🚢 Retrieving all shipping policies...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get all shipping policies
        policies = client.shipping.list_policies()
        print(f"Found {len(policies)} shipping policies")
        
        if not policies:
            print("No shipping policies configured")
            return []
        
        # Display basic information about each policy
        for i, policy in enumerate(policies, 1):
            print(f"\n{i}. Policy: {policy.name}")
            print(f"   ID: {policy.shipping_policy_id}")
            print(f"   Status: {'✅ Enabled' if policy.enabled else '❌ Disabled'}")
            print(f"   Default: {'🌟 Yes' if policy.is_default else 'No'}")
            print(f"   Shipping Option: {policy.shipping_option}")
            print(f"   Dispatch Locations: {len(policy.dispatch_location_ids)}")
            
            # Display dispatch location IDs
            if policy.dispatch_location_ids:
                print(f"   Location IDs:")
                for loc_id in policy.dispatch_location_ids[:3]:  # Show first 3
                    print(f"     - {loc_id}")
                if len(policy.dispatch_location_ids) > 3:
                    print(f"     ... and {len(policy.dispatch_location_ids) - 3} more")
        
        return policies
        
    except Exception as e:
        print(f"❌ Error retrieving shipping policies: {e}")
        return []


def analyze_shipping_policy_details(policy: ShippingPolicy):
    """Analyze detailed shipping policy configuration."""
    print(f"\n🔍 Analyzing policy: {policy.name}")
    
    # Analyze domestic shipping configuration
    domestic = policy.domestic_shipping
    print(f"   Domestic Shipping Rules: {len(domestic.rules)}")
    
    if domestic.excluded_shipping_zones:
        print(f"   Excluded Zones: {len(domestic.excluded_shipping_zones)}")
        for zone_id in domestic.excluded_shipping_zones[:3]:
            print(f"     - {zone_id}")
    else:
        print("   No excluded shipping zones")
    
    # Analyze shipping rules
    for i, rule in enumerate(domestic.rules, 1):
        print(f"\n   Rule {i}: {rule.type}")
        print(f"     Based on: {rule.rule_based_on}")
        print(f"     Shipping Zones: {len(rule.shipping_zones)}")
        
        # Show first few shipping zones
        for zone_id in rule.shipping_zones[:3]:
            print(f"       - {zone_id}")
        if len(rule.shipping_zones) > 3:
            print(f"       ... and {len(rule.shipping_zones) - 3} more")
        
        # Analyze rule parameters
        print(f"     Parameters: {len(rule.parameters)}")
        for j, param in enumerate(rule.parameters, 1):
            print(f"       Parameter {j}:")
            result = param.result
            
            if param.shipping_price_amount is not None:
                print(f"         Price: ${param.shipping_price_amount}")
            if param.shipping_time_from is not None:
                print(f"         Delivery time: {param.shipping_time_from}-{param.shipping_time_to} business days")
            if param.shipping_price_additional_charge_type:
                print(f"         Additional price charge: {param.shipping_price_additional_charge_type}")
            if param.shipping_cost_additional_charge_type:
                print(f"         Additional cost charge: {param.shipping_cost_additional_charge_type}")


def get_shipping_coverage_analysis():
    """Analyze shipping coverage across all policies."""
    print("\n📊 Analyzing shipping coverage...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get coverage analysis
        coverage = client.shipping.analyze_shipping_coverage()
        
        print("Shipping Coverage Analysis:")
        print(f"   Total Policies: {coverage['total_policies']}")
        print(f"   Enabled Policies: {coverage['enabled_policies']}")
        print(f"   Default Policies: {coverage['default_policies']}")
        print(f"   Unique Dispatch Locations: {coverage['unique_dispatch_locations']}")
        
        # Display shipping options breakdown
        print(f"\n   Shipping Options Breakdown:")
        for option, count in coverage['shipping_options'].items():
            print(f"     - {option}: {count} policies")
        
        # Display dispatch location IDs
        print(f"\n   Dispatch Location IDs:")
        for loc_id in coverage['dispatch_location_ids'][:5]:
            print(f"     - {loc_id}")
        if len(coverage['dispatch_location_ids']) > 5:
            print(f"     ... and {len(coverage['dispatch_location_ids']) - 5} more")
        
        return coverage
        
    except Exception as e:
        print(f"❌ Error analyzing shipping coverage: {e}")
        return None


def find_policies_by_criteria():
    """Find shipping policies based on various criteria."""
    print("\n🔍 Finding policies by criteria...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Find enabled policies
        enabled_policies = client.shipping.get_enabled_policies()
        print(f"✅ Enabled Policies: {len(enabled_policies)}")
        for policy in enabled_policies:
            print(f"   - {policy.name}")
        
        # Find default policies
        default_policies = client.shipping.get_default_policies()
        print(f"\n🌟 Default Policies: {len(default_policies)}")
        for policy in default_policies:
            print(f"   - {policy.name} (Locations: {len(policy.dispatch_location_ids)})")
        
        # Find standard shipping policies
        standard_policies = client.shipping.get_standard_shipping_policies()
        print(f"\n📦 Standard Shipping Policies: {len(standard_policies)}")
        for policy in standard_policies:
            print(f"   - {policy.name}")
        
        # Find policies by name (partial match)
        search_term = "express"
        found_policies = client.shipping.find_policies_by_name(search_term)
        print(f"\n🔎 Policies containing '{search_term}': {len(found_policies)}")
        for policy in found_policies:
            print(f"   - {policy.name}")
        
        # If we have dispatch locations, find policies for specific location
        if enabled_policies and enabled_policies[0].dispatch_location_ids:
            sample_location = str(enabled_policies[0].dispatch_location_ids[0])
            location_policies = client.shipping.get_policies_for_location(sample_location)
            print(f"\n📍 Policies for location {sample_location}: {len(location_policies)}")
            for policy in location_policies:
                print(f"   - {policy.name}")
        
    except Exception as e:
        print(f"❌ Error finding policies: {e}")


def get_specific_policy_details():
    """Get detailed information about a specific shipping policy."""
    print("\n🔍 Getting specific policy details...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # First get all policies to find one to examine
        policies = client.shipping.list_policies()
        
        if not policies:
            print("No policies available to examine")
            return
        
        # Take the first policy for detailed analysis
        sample_policy = policies[0]
        policy_id = str(sample_policy.shipping_policy_id)
        
        # Get the policy by ID
        detailed_policy = client.shipping.get_policy(policy_id)
        
        print(f"Detailed Policy Information:")
        print(f"   Name: {detailed_policy.name}")
        print(f"   ID: {detailed_policy.shipping_policy_id}")
        print(f"   Enabled: {detailed_policy.enabled}")
        print(f"   Default: {detailed_policy.is_default}")
        print(f"   Shipping Option: {detailed_policy.shipping_option}")
        
        # Analyze the policy in detail
        analyze_shipping_policy_details(detailed_policy)
        
    except Exception as e:
        print(f"❌ Error getting policy details: {e}")


def compare_shipping_policies(policies: List[ShippingPolicy]):
    """Compare shipping policies and highlight differences."""
    print("\n⚖️ Comparing shipping policies...")
    
    if len(policies) < 2:
        print("Need at least 2 policies to compare")
        return
    
    print(f"Comparing {len(policies)} policies:")
    
    # Compare basic attributes
    print("\n📋 Basic Comparison:")
    print(f"{'Policy Name':<30} {'Enabled':<8} {'Default':<8} {'Option':<15} {'Locations':<10}")
    print("-" * 80)
    
    for policy in policies:
        enabled = "✅ Yes" if policy.enabled else "❌ No"
        default = "🌟 Yes" if policy.is_default else "No"
        locations = str(len(policy.dispatch_location_ids))
        
        print(f"{policy.name:<30} {enabled:<8} {default:<8} {policy.shipping_option:<15} {locations:<10}")
    
    # Compare shipping rules
    print(f"\n🔧 Rules Comparison:")
    for i, policy in enumerate(policies, 1):
        rules_count = len(policy.domestic_shipping.rules)
        zones_count = sum(len(rule.shipping_zones) for rule in policy.domestic_shipping.rules)
        excluded_zones = len(policy.domestic_shipping.excluded_shipping_zones)
        
        print(f"   Policy {i} ({policy.name}):")
        print(f"     Rules: {rules_count}")
        print(f"     Total shipping zones: {zones_count}")
        print(f"     Excluded zones: {excluded_zones}")
        
        # Analyze rule types
        rule_types = [rule.type for rule in policy.domestic_shipping.rules]
        unique_types = set(rule_types)
        print(f"     Rule types: {', '.join(unique_types)}")


def demonstrate_policy_optimization():
    """Demonstrate how to analyze policies for optimization opportunities."""
    print("\n🎯 Analyzing policies for optimization opportunities...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        policies = client.shipping.list_policies()
        coverage = client.shipping.analyze_shipping_coverage()
        
        if not policies or not coverage:
            print("Unable to analyze - no policies or coverage data")
            return
        
        print("Optimization Analysis:")
        
        # Check for redundant policies
        enabled_count = coverage['enabled_policies']
        total_count = coverage['total_policies']
        disabled_count = total_count - enabled_count
        
        if disabled_count > 0:
            print(f"   ⚠️ Found {disabled_count} disabled policies - consider removing if no longer needed")
        
        # Check for multiple default policies
        default_count = coverage['default_policies']
        if default_count > 1:
            print(f"   ⚠️ Found {default_count} default policies - typically only one should be default")
        elif default_count == 0:
            print(f"   ⚠️ No default policy found - consider setting one as default")
        
        # Analyze dispatch location coverage
        location_count = coverage['unique_dispatch_locations']
        print(f"   📍 Dispatch locations covered: {location_count}")
        
        # Check for overlapping zones (simplified analysis)
        all_zones = set()
        overlapping_zones = set()
        
        for policy in policies:
            if policy.enabled:
                for rule in policy.domestic_shipping.rules:
                    for zone in rule.shipping_zones:
                        if zone in all_zones:
                            overlapping_zones.add(zone)
                        all_zones.add(zone)
        
        if overlapping_zones:
            print(f"   ⚠️ Found {len(overlapping_zones)} shipping zones covered by multiple policies")
            print(f"     This might indicate potential for policy consolidation")
        
        # Analyze shipping options distribution
        options = coverage['shipping_options']
        most_common_option = max(options.items(), key=lambda x: x[1])
        print(f"   📦 Most common shipping option: {most_common_option[0]} ({most_common_option[1]} policies)")
        
        if len(options) > 3:
            print(f"   💡 Consider consolidating shipping options - currently using {len(options)} different options")
        
    except Exception as e:
        print(f"❌ Error analyzing optimization: {e}")


async def async_shipping_operations():
    """Demonstrate async shipping operations."""
    print("\n🔄 Demonstrating async shipping operations...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get policies and analysis concurrently
        tasks = [
            client.shipping.list_policies_async(),
            client.shipping.analyze_shipping_coverage_async(),
            client.shipping.get_enabled_policies_async(),
            client.shipping.get_default_policies_async()
        ]
        
        all_policies, coverage, enabled_policies, default_policies = await asyncio.gather(*tasks)
        
        print(f"📊 Async results:")
        print(f"   All policies: {len(all_policies)}")
        print(f"   Enabled policies: {len(enabled_policies)}")
        print(f"   Default policies: {len(default_policies)}")
        print(f"   Coverage analysis: {coverage['total_policies']} total policies")
        
        # Get detailed info for a few policies concurrently
        if all_policies:
            detail_tasks = [
                client.shipping.get_policy_async(str(policy.shipping_policy_id))
                for policy in all_policies[:3]
            ]
            
            detailed_policies = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            print("\n🔍 Detailed policy info:")
            for result in detailed_policies:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.name}: {len(result.domestic_shipping.rules)} rules")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Shipping Policies Example")
    print("=" * 50)
    
    # List all shipping policies
    policies = list_all_shipping_policies()
    
    if policies:
        # Analyze specific policy details
        if len(policies) > 0:
            analyze_shipping_policy_details(policies[0])
        
        # Compare policies
        compare_shipping_policies(policies[:3])  # Compare first 3 policies
    
    # Get shipping coverage analysis
    get_shipping_coverage_analysis()
    
    # Find policies by criteria
    find_policies_by_criteria()
    
    # Get specific policy details
    get_specific_policy_details()
    
    # Demonstrate optimization analysis
    demonstrate_policy_optimization()
    
    # Demonstrate async operations
    asyncio.run(async_shipping_operations())
    
    print("\n✨ Shipping policies example completed!")


if __name__ == "__main__":
    main()
