#!/usr/bin/env python3
"""
Example: Taxonomy Navigation with the MySale API SDK

This example demonstrates how to:
1. Navigate the MySale taxonomy structure
2. Search for categories
3. Build category hierarchies
4. Find suitable categories for products
"""

import asyncio
from typing import List, Dict

from mysale_api import MySaleClient, MySaleAsyncClient
from mysale_api.models import TaxonomyBranch

# Configuration
API_TOKEN = "your_api_token_here"


def explore_root_categories():
    """Explore the root level categories in MySale taxonomy."""
    print("🌳 Exploring root categories...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get all root categories (categories with no parent)
        root_branches = client.taxonomy.get_root_branches()
        print(f"Found {len(root_branches)} root categories")
        
        if not root_branches:
            print("No root categories found")
            return []
        
        # Display root categories
        for i, branch in enumerate(root_branches, 1):
            print(f"\n{i}. {branch.name}")
            print(f"   ID: {branch.branch_id}")
            print(f"   Level: {branch.level}")
            print(f"   Keywords: {', '.join(branch.keywords) if branch.keywords else 'None'}")
            print(f"   Main Category: {'Yes' if branch.is_main_category else 'No'}")
        
        return root_branches
        
    except Exception as e:
        print(f"❌ Error exploring root categories: {e}")
        return []


def navigate_category_tree(parent_branch_id: str, max_depth: int = 3, current_depth: int = 0):
    """Navigate down the category tree from a given parent."""
    if current_depth >= max_depth:
        return
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get child branches of the parent
        child_branches = client.taxonomy.get_child_branches(parent_branch_id)
        
        if not child_branches:
            return
        
        indent = "  " * current_depth
        print(f"{indent}📁 Child categories ({len(child_branches)}):")
        
        for child in child_branches:
            print(f"{indent}  - {child.name} (Level {child.level})")
            if child.keywords:
                print(f"{indent}    Keywords: {', '.join(child.keywords[:3])}{'...' if len(child.keywords) > 3 else ''}")
            
            # Recursively navigate deeper (limit to avoid too much output)
            if current_depth < 2:  # Only go 2 levels deep for demo
                navigate_category_tree(str(child.branch_id), max_depth, current_depth + 1)
        
    except Exception as e:
        print(f"❌ Error navigating category tree: {e}")


def search_categories_by_keyword():
    """Search for categories using keywords."""
    print("\n🔍 Searching categories by keywords...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Common search terms for e-commerce
    search_terms = ["clothing", "electronics", "home", "beauty", "sports", "books"]
    
    for term in search_terms:
        try:
            print(f"\n🔎 Searching for: '{term}'")
            results = client.taxonomy.search_branches(term)
            
            if results:
                print(f"   Found {len(results)} categories:")
                for result in results[:5]:  # Show first 5 results
                    print(f"     - {result.name} (Level {result.level})")
                    if result.keywords:
                        matching_keywords = [kw for kw in result.keywords if term.lower() in kw.lower()]
                        if matching_keywords:
                            print(f"       Matching keywords: {', '.join(matching_keywords)}")
                
                if len(results) > 5:
                    print(f"     ... and {len(results) - 5} more")
            else:
                print(f"   No categories found for '{term}'")
                
        except Exception as e:
            print(f"❌ Error searching for '{term}': {e}")


def build_category_hierarchy(branch_id: str):
    """Build and display the complete hierarchy for a category."""
    print(f"\n🏗️ Building hierarchy for category: {branch_id}")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get the complete hierarchy from root to this branch
        hierarchy = client.taxonomy.get_branch_hierarchy(branch_id)
        
        if not hierarchy:
            print("No hierarchy found")
            return
        
        print(f"Category hierarchy ({len(hierarchy)} levels):")
        
        for i, branch in enumerate(hierarchy):
            indent = "  " * i
            arrow = "└─ " if i == len(hierarchy) - 1 else "├─ "
            print(f"{indent}{arrow}{branch.name}")
            print(f"{indent}   ID: {branch.branch_id}")
            print(f"{indent}   Level: {branch.level}")
            
            if branch.keywords:
                print(f"{indent}   Keywords: {', '.join(branch.keywords[:3])}{'...' if len(branch.keywords) > 3 else ''}")
        
        return hierarchy
        
    except Exception as e:
        print(f"❌ Error building hierarchy: {e}")
        return []


def find_suitable_categories_for_product():
    """Find suitable categories for different types of products."""
    print("\n🎯 Finding suitable categories for products...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    # Sample products to categorize
    sample_products = [
        {"name": "Men's Cotton T-Shirt", "keywords": ["clothing", "men", "shirt", "cotton", "apparel"]},
        {"name": "Smartphone Case", "keywords": ["electronics", "phone", "case", "accessory", "mobile"]},
        {"name": "Coffee Maker", "keywords": ["kitchen", "appliance", "coffee", "home", "brewing"]},
        {"name": "Running Shoes", "keywords": ["shoes", "sports", "running", "footwear", "athletic"]},
        {"name": "Skincare Cream", "keywords": ["beauty", "skincare", "cosmetics", "cream", "health"]}
    ]
    
    for product in sample_products:
        print(f"\n📦 Product: {product['name']}")
        print(f"   Looking for categories matching: {', '.join(product['keywords'])}")
        
        suitable_categories = []
        
        # Search for categories using each keyword
        for keyword in product['keywords']:
            try:
                results = client.taxonomy.search_branches(keyword)
                for result in results:
                    # Score the category based on keyword matches
                    score = 0
                    matching_keywords = []
                    
                    for product_keyword in product['keywords']:
                        if any(product_keyword.lower() in branch_keyword.lower() 
                               for branch_keyword in result.keywords):
                            score += 1
                            matching_keywords.extend([
                                kw for kw in result.keywords 
                                if product_keyword.lower() in kw.lower()
                            ])
                    
                    if score > 0:
                        suitable_categories.append({
                            'branch': result,
                            'score': score,
                            'matching_keywords': list(set(matching_keywords))
                        })
                        
            except Exception as e:
                print(f"     Error searching for '{keyword}': {e}")
        
        # Sort by score and remove duplicates
        seen_ids = set()
        unique_categories = []
        for cat in sorted(suitable_categories, key=lambda x: x['score'], reverse=True):
            if cat['branch'].branch_id not in seen_ids:
                unique_categories.append(cat)
                seen_ids.add(cat['branch'].branch_id)
        
        # Display top suggestions
        if unique_categories:
            print(f"   📋 Top category suggestions:")
            for i, cat in enumerate(unique_categories[:3], 1):
                branch = cat['branch']
                print(f"     {i}. {branch.name} (Level {branch.level})")
                print(f"        Score: {cat['score']}/5")
                print(f"        Matching: {', '.join(cat['matching_keywords'][:3])}")
                print(f"        ID: {branch.branch_id}")
        else:
            print(f"   ❌ No suitable categories found")


def get_category_statistics():
    """Get statistics about the taxonomy structure."""
    print("\n📊 Analyzing taxonomy statistics...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Get all branch IDs
        all_branches = client.taxonomy.list_branches(limit=1000)  # Get a large number
        print(f"Total branches in taxonomy: {len(all_branches)}")
        
        if not all_branches:
            print("No branches found")
            return
        
        # Sample some branches to analyze structure
        sample_size = min(50, len(all_branches))
        print(f"Analyzing sample of {sample_size} branches...")
        
        levels = {}
        has_keywords_count = 0
        total_keywords = 0
        main_categories = 0
        
        for branch_id in all_branches[:sample_size]:
            try:
                branch = client.taxonomy.get_branch(branch_id)
                
                # Count by level
                levels[branch.level] = levels.get(branch.level, 0) + 1
                
                # Count keywords
                if branch.keywords:
                    has_keywords_count += 1
                    total_keywords += len(branch.keywords)
                
                # Count main categories
                if branch.is_main_category:
                    main_categories += 1
                    
            except Exception as e:
                print(f"     Error analyzing branch {branch_id}: {e}")
        
        # Display statistics
        print(f"\n📈 Taxonomy Structure Analysis (sample of {sample_size}):")
        print(f"   Branches with keywords: {has_keywords_count}/{sample_size} ({has_keywords_count/sample_size*100:.1f}%)")
        print(f"   Average keywords per branch: {total_keywords/sample_size:.1f}")
        print(f"   Main categories: {main_categories}")
        
        print(f"\n📏 Level Distribution:")
        for level in sorted(levels.keys()):
            count = levels[level]
            percentage = count / sample_size * 100
            print(f"     Level {level}: {count} branches ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error analyzing taxonomy: {e}")


def demonstrate_category_navigation_patterns():
    """Demonstrate common category navigation patterns."""
    print("\n🧭 Demonstrating navigation patterns...")
    
    client = MySaleClient(api_token=API_TOKEN)
    
    try:
        # Pattern 1: Top-down exploration
        print("1. 📁 Top-down exploration pattern:")
        root_branches = client.taxonomy.get_root_branches()
        
        if root_branches:
            sample_root = root_branches[0]
            print(f"   Starting from root: {sample_root.name}")
            
            # Get immediate children
            children = client.taxonomy.get_child_branches(str(sample_root.branch_id))
            print(f"   Direct children: {len(children)}")
            
            if children:
                for child in children[:3]:
                    print(f"     - {child.name}")
                    # Get grandchildren
                    grandchildren = client.taxonomy.get_child_branches(str(child.branch_id))
                    if grandchildren:
                        print(f"       └─ Has {len(grandchildren)} subcategories")
        
        # Pattern 2: Bottom-up hierarchy building
        print("\n2. 🔼 Bottom-up hierarchy building:")
        if root_branches:
            # Take a category and build its full hierarchy
            sample_branch = root_branches[0]
            hierarchy = client.taxonomy.get_branch_hierarchy(str(sample_branch.branch_id))
            print(f"   Full path to {sample_branch.name}:")
            for i, branch in enumerate(hierarchy):
                print(f"     {'  ' * i}└─ {branch.name}")
        
        # Pattern 3: Keyword-based discovery
        print("\n3. 🔍 Keyword-based discovery pattern:")
        keywords_to_try = ["clothing", "electronics", "home"]
        
        for keyword in keywords_to_try:
            try:
                results = client.taxonomy.search_branches(keyword)
                if results:
                    print(f"   '{keyword}' → {len(results)} categories found")
                    # Show a sample hierarchy for the first result
                    first_result = results[0]
                    hierarchy = client.taxonomy.get_branch_hierarchy(str(first_result.branch_id))
                    if len(hierarchy) > 1:
                        print(f"     Example path: {' > '.join(h.name for h in hierarchy)}")
                break  # Just show one example
            except Exception:
                continue
        
    except Exception as e:
        print(f"❌ Error demonstrating patterns: {e}")


async def async_taxonomy_operations():
    """Demonstrate async taxonomy operations."""
    print("\n🔄 Demonstrating async taxonomy operations...")
    
    client = MySaleAsyncClient(api_token=API_TOKEN)
    
    try:
        # Get multiple taxonomy data concurrently
        tasks = [
            client.taxonomy.get_root_branches_async(),
            client.taxonomy.list_branches_async(limit=20),
            client.taxonomy.search_branches_async("clothing"),
            client.taxonomy.search_branches_async("electronics")
        ]
        
        root_branches, all_branches, clothing_results, electronics_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"📊 Async results:")
        if not isinstance(root_branches, Exception):
            print(f"   Root branches: {len(root_branches)}")
        if not isinstance(all_branches, Exception):
            print(f"   All branches (sample): {len(all_branches)}")
        if not isinstance(clothing_results, Exception):
            print(f"   Clothing categories: {len(clothing_results)}")
        if not isinstance(electronics_results, Exception):
            print(f"   Electronics categories: {len(electronics_results)}")
        
        # Get detailed info for some branches concurrently
        if not isinstance(root_branches, Exception) and root_branches:
            detail_tasks = [
                client.taxonomy.get_branch_async(str(branch.branch_id))
                for branch in root_branches[:3]
            ]
            
            detailed_branches = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            print("\n🔍 Detailed branch info:")
            for result in detailed_branches:
                if isinstance(result, Exception):
                    print(f"   Error: {result}")
                else:
                    print(f"   {result.name}: Level {result.level}, {len(result.keywords)} keywords")
    
    except Exception as e:
        print(f"❌ Async error: {e}")
    
    finally:
        await client.close()


def main():
    """Main example function."""
    print("🚀 MySale API SDK - Taxonomy Navigation Example")
    print("=" * 50)
    
    # Explore root categories
    root_branches = explore_root_categories()
    
    if root_branches:
        # Navigate category tree from first root
        print(f"\n🌳 Navigating from root category: {root_branches[0].name}")
        navigate_category_tree(str(root_branches[0].branch_id))
        
        # Build hierarchy for a category
        build_category_hierarchy(str(root_branches[0].branch_id))
    
    # Search categories by keywords
    search_categories_by_keyword()
    
    # Find suitable categories for products
    find_suitable_categories_for_product()
    
    # Get taxonomy statistics
    get_category_statistics()
    
    # Demonstrate navigation patterns
    demonstrate_category_navigation_patterns()
    
    # Demonstrate async operations
    asyncio.run(async_taxonomy_operations())
    
    print("\n✨ Taxonomy navigation example completed!")


if __name__ == "__main__":
    main()
