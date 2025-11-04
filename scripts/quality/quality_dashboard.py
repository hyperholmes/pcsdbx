#!/usr/bin/env python3
"""
Quality Dashboard
Provides comprehensive quality metrics for the supplier database.

Usage:
  python3 scripts/quality/quality_dashboard.py [--html] [--trend]

This tool:
1. Analyzes all JSON listings for quality metrics
2. Tracks enhanced field coverage
3. Identifies missing or incomplete data
4. Provides category-level breakdowns
5. Generates trend data over time (with --trend)
6. Outputs to terminal or HTML (with --html)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import date
from collections import defaultdict
import argparse


def find_all_listings(base_dir: Path = Path("listings")) -> List[Path]:
    """Find all JSON listing files."""
    return list(base_dir.rglob("*.json"))


def analyze_listing(filepath: Path) -> Dict[str, Any]:
    """Analyze a single listing for quality metrics."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Required fields (schema v1.0)
    required_fields = {
        "schema_version", "category_id", "listing_id", 
        "category_path", "url", "status", "date_added"
    }
    
    # Enhanced fields (recommended for quality)
    enhanced_fields = {
        "company_name", "address", "country", "phone", 
        "website", "specializations", "email"
    }
    
    # Strategic fields
    strategic_fields = {
        "tags", "certifications", "product_highlights", 
        "key_benefits", "notes"
    }
    
    # Check field presence
    has_required = all(field in data for field in required_fields)
    present_enhanced = sum(1 for field in enhanced_fields if field in data and data[field])
    present_strategic = sum(1 for field in strategic_fields if field in data and data[field])
    
    # Calculate completeness score (0-100)
    total_fields = len(required_fields) + len(enhanced_fields) + len(strategic_fields)
    present_fields = len(required_fields) + present_enhanced + present_strategic
    completeness_score = (present_fields / total_fields) * 100
    
    # Tag quality
    has_tags = "tags" in data and len(data.get("tags", [])) > 0
    tag_count = len(data.get("tags", []))
    
    # Specializations quality
    has_specializations = "specializations" in data and len(data.get("specializations", [])) > 0
    specialization_count = len(data.get("specializations", []))
    
    return {
        "file": filepath,
        "category_path": data.get("category_path", "Unknown"),
        "company_name": data.get("company_name", "Unknown"),
        "has_schema_version": "schema_version" in data,
        "has_required_fields": has_required,
        "enhanced_field_count": present_enhanced,
        "enhanced_field_total": len(enhanced_fields),
        "strategic_field_count": present_strategic,
        "strategic_field_total": len(strategic_fields),
        "completeness_score": completeness_score,
        "has_tags": has_tags,
        "tag_count": tag_count,
        "has_specializations": has_specializations,
        "specialization_count": specialization_count,
        "has_metadata": "metadata" in data,
        "has_certifications": "certifications" in data and len(data.get("certifications", [])) > 0,
        "date_added": data.get("date_added", "Unknown"),
    }


def generate_dashboard(listings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comprehensive dashboard metrics."""
    total_listings = len(listings_data)
    
    if total_listings == 0:
        return {"error": "No listings found"}
    
    # Overall metrics
    with_schema = sum(1 for d in listings_data if d["has_schema_version"])
    with_metadata = sum(1 for d in listings_data if d["has_metadata"])
    with_tags = sum(1 for d in listings_data if d["has_tags"])
    with_specializations = sum(1 for d in listings_data if d["has_specializations"])
    with_certifications = sum(1 for d in listings_data if d["has_certifications"])
    
    # Enhanced field coverage
    total_enhanced_coverage = sum(d["enhanced_field_count"] for d in listings_data)
    max_enhanced_coverage = sum(d["enhanced_field_total"] for d in listings_data)
    enhanced_coverage_pct = (total_enhanced_coverage / max_enhanced_coverage * 100) if max_enhanced_coverage > 0 else 0
    
    # Strategic field coverage
    total_strategic_coverage = sum(d["strategic_field_count"] for d in listings_data)
    max_strategic_coverage = sum(d["strategic_field_total"] for d in listings_data)
    strategic_coverage_pct = (total_strategic_coverage / max_strategic_coverage * 100) if max_strategic_coverage > 0 else 0
    
    # Average completeness
    avg_completeness = sum(d["completeness_score"] for d in listings_data) / total_listings
    
    # Average tags and specializations
    avg_tags = sum(d["tag_count"] for d in listings_data) / total_listings
    avg_specializations = sum(d["specialization_count"] for d in listings_data) / total_listings
    
    # Category breakdown
    by_category = defaultdict(list)
    for d in listings_data:
        by_category[d["category_path"]].append(d)
    
    category_stats = {}
    for category, items in by_category.items():
        category_stats[category] = {
            "count": len(items),
            "avg_completeness": sum(i["completeness_score"] for i in items) / len(items),
            "with_tags": sum(1 for i in items if i["has_tags"]),
            "avg_tags": sum(i["tag_count"] for i in items) / len(items),
            "with_specializations": sum(1 for i in items if i["has_specializations"]),
        }
    
    # Quality tiers
    excellent = sum(1 for d in listings_data if d["completeness_score"] >= 80)
    good = sum(1 for d in listings_data if 60 <= d["completeness_score"] < 80)
    fair = sum(1 for d in listings_data if 40 <= d["completeness_score"] < 60)
    poor = sum(1 for d in listings_data if d["completeness_score"] < 40)
    
    # Recent additions
    recent_listings = sorted(listings_data, key=lambda x: x["date_added"], reverse=True)[:10]
    
    return {
        "total_listings": total_listings,
        "overall": {
            "schema_version_pct": (with_schema / total_listings * 100),
            "metadata_pct": (with_metadata / total_listings * 100),
            "tags_pct": (with_tags / total_listings * 100),
            "specializations_pct": (with_specializations / total_listings * 100),
            "certifications_pct": (with_certifications / total_listings * 100),
            "enhanced_coverage_pct": enhanced_coverage_pct,
            "strategic_coverage_pct": strategic_coverage_pct,
            "avg_completeness": avg_completeness,
            "avg_tags": avg_tags,
            "avg_specializations": avg_specializations,
        },
        "quality_tiers": {
            "excellent": {"count": excellent, "pct": excellent / total_listings * 100},
            "good": {"count": good, "pct": good / total_listings * 100},
            "fair": {"count": fair, "pct": fair / total_listings * 100},
            "poor": {"count": poor, "pct": poor / total_listings * 100},
        },
        "categories": category_stats,
        "recent_additions": [
            {
                "company": r["company_name"],
                "category": r["category_path"],
                "completeness": round(r["completeness_score"], 1),
                "date": r["date_added"]
            }
            for r in recent_listings
        ]
    }


def print_dashboard(dashboard: Dict[str, Any]):
    """Print dashboard to terminal."""
    print("\n" + "="*80)
    print("PERSONAL CARE SUPPLIERS DATABASE - QUALITY DASHBOARD")
    print("="*80 + "\n")
    
    print(f"Total Listings: {dashboard['total_listings']}\n")
    
    # Overall metrics
    print("="*80)
    print("OVERALL QUALITY METRICS")
    print("="*80)
    overall = dashboard['overall']
    print(f"  Schema Version:          {overall['schema_version_pct']:.1f}%")
    print(f"  Metadata Present:        {overall['metadata_pct']:.1f}%")
    print(f"  Tags Present:            {overall['tags_pct']:.1f}%")
    print(f"  Specializations Present: {overall['specializations_pct']:.1f}%")
    print(f"  Certifications Present:  {overall['certifications_pct']:.1f}%")
    print(f"\n  Enhanced Field Coverage:   {overall['enhanced_coverage_pct']:.1f}%")
    print(f"  Strategic Field Coverage:  {overall['strategic_coverage_pct']:.1f}%")
    print(f"\n  Average Completeness Score: {overall['avg_completeness']:.1f}/100")
    print(f"  Average Tags per Listing:   {overall['avg_tags']:.1f}")
    print(f"  Average Specializations:    {overall['avg_specializations']:.1f}")
    
    # Quality tiers
    print("\n" + "="*80)
    print("QUALITY DISTRIBUTION")
    print("="*80)
    tiers = dashboard['quality_tiers']
    print(f"  Excellent (80-100): {tiers['excellent']['count']:3d} listings ({tiers['excellent']['pct']:5.1f}%)")
    print(f"  Good (60-79):       {tiers['good']['count']:3d} listings ({tiers['good']['pct']:5.1f}%)")
    print(f"  Fair (40-59):       {tiers['fair']['count']:3d} listings ({tiers['fair']['pct']:5.1f}%)")
    print(f"  Poor (<40):         {tiers['poor']['count']:3d} listings ({tiers['poor']['pct']:5.1f}%)")
    
    # Category breakdown
    print("\n" + "="*80)
    print("CATEGORY BREAKDOWN")
    print("="*80)
    categories = sorted(dashboard['categories'].items(), key=lambda x: x[1]['count'], reverse=True)
    for category, stats in categories[:15]:  # Top 15 categories
        print(f"\n  {category}")
        print(f"    Listings: {stats['count']}")
        print(f"    Avg Completeness: {stats['avg_completeness']:.1f}/100")
        print(f"    With Tags: {stats['with_tags']} ({stats['with_tags']/stats['count']*100:.0f}%)")
        print(f"    Avg Tags: {stats['avg_tags']:.1f}")
        print(f"    With Specializations: {stats['with_specializations']} ({stats['with_specializations']/stats['count']*100:.0f}%)")
    
    if len(categories) > 15:
        print(f"\n  ... and {len(categories) - 15} more categories")
    
    # Recent additions
    print("\n" + "="*80)
    print("RECENT ADDITIONS (Last 10)")
    print("="*80)
    for i, listing in enumerate(dashboard['recent_additions'], 1):
        print(f"  {i:2d}. {listing['company']:<40s} | {listing['category']:<35s} | {listing['completeness']:5.1f}% | {listing['date']}")
    
    print("\n" + "="*80 + "\n")


def save_trend_data(dashboard: Dict[str, Any], trend_file: Path = Path("quality_trends.json")):
    """Save trend data for tracking over time."""
    trend_entry = {
        "date": str(date.today()),
        "total_listings": dashboard["total_listings"],
        "avg_completeness": dashboard["overall"]["avg_completeness"],
        "enhanced_coverage_pct": dashboard["overall"]["enhanced_coverage_pct"],
        "strategic_coverage_pct": dashboard["overall"]["strategic_coverage_pct"],
        "tags_pct": dashboard["overall"]["tags_pct"],
    }
    
    # Load existing trends
    trends = []
    if trend_file.exists():
        with open(trend_file, 'r') as f:
            trends = json.load(f)
    
    # Append new entry
    trends.append(trend_entry)
    
    # Save updated trends
    with open(trend_file, 'w') as f:
        json.dump(trends, f, indent=2)
    
    print(f"Trend data saved to: {trend_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate quality dashboard for supplier database"
    )
    parser.add_argument("--html", action="store_true",
                       help="Generate HTML output (not yet implemented)")
    parser.add_argument("--trend", action="store_true",
                       help="Save trend data for tracking over time")
    parser.add_argument("--listings-dir", type=str, default="listings",
                       help="Directory containing listings (default: listings)")
    
    args = parser.parse_args()
    
    listings_dir = Path(args.listings_dir)
    
    # Find all listings
    print("Scanning for listings...")
    listing_files = find_all_listings(listings_dir)
    print(f"Found {len(listing_files)} listings\n")
    
    if not listing_files:
        print("No listings found!")
        return
    
    # Analyze each listing
    print("Analyzing listings...")
    listings_data = [analyze_listing(f) for f in listing_files]
    
    # Generate dashboard
    print("Generating dashboard...")
    dashboard = generate_dashboard(listings_data)
    
    # Display dashboard
    print_dashboard(dashboard)
    
    # Save trend data if requested
    if args.trend:
        save_trend_data(dashboard)
    
    if args.html:
        print("\nHTML output not yet implemented. Coming soon!")


if __name__ == "__main__":
    main()
