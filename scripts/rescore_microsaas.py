#!/usr/bin/env python3
"""
Re-score all opportunities with MicroSaaS criteria

Filters for:
- SEO-driven acquisition (searchable problems)
- Self-service potential (no sales team)
- Extreme pain points
- Recurring revenue potential
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Opportunity, Tweet, PainAnalysis
from backend.microsaas_scoring import calculate_microsaas_score, get_microsaas_breakdown


def rescore_all_opportunities():
    """Re-score all opportunities with MicroSaaS criteria."""

    print("=" * 70)
    print("RE-SCORING OPPORTUNITIES FOR MICROSAAS")
    print("=" * 70)
    print()
    print("Criteria:")
    print("  ✓ SEO-driven acquisition (no sales team)")
    print("  ✓ Self-service product (no marketing team)")
    print("  ✓ Extreme pain points")
    print("  ✓ Recurring revenue potential")
    print()

    # Get all opportunities
    all_opps = Opportunity.get_top_opportunities(limit=1000, min_score=0, days=365)

    print(f"Found {len(all_opps)} opportunities to re-score...")
    print()

    rescored = []

    for opp in all_opps:
        # Get associated tweets/posts
        tweets = Opportunity.get_tweets(opp['id'])

        if not tweets:
            continue

        # Get pain analysis for first tweet (primary source)
        tweet = tweets[0]
        pain = PainAnalysis.get_by_tweet(tweet['id'])

        if not pain:
            continue

        # Calculate MicroSaaS score
        microsaas_score = calculate_microsaas_score(opp, pain)
        breakdown = get_microsaas_breakdown(opp, pain)

        # Update opportunity score in database
        from backend.models import get_db_path, get_db_connection

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE opportunities
                SET score = ?
                WHERE id = ?
            ''', (microsaas_score, opp['id']))
            conn.commit()

        rescored.append({
            'id': opp['id'],
            'title': opp['title'],
            'old_score': opp['score'],
            'new_score': microsaas_score,
            'breakdown': breakdown
        })

    print(f"✅ Re-scored {len(rescored)} opportunities")
    print()

    # Show biggest changes
    rescored_sorted = sorted(rescored, key=lambda x: x['new_score'], reverse=True)

    print("=" * 70)
    print("TOP 10 MICROSAAS OPPORTUNITIES (NEW SCORES)")
    print("=" * 70)
    print()

    for i, opp in enumerate(rescored_sorted[:10], 1):
        change = opp['new_score'] - opp['old_score']
        change_str = f"+{change}" if change >= 0 else str(change)

        source = opp['title'].split(']')[0].strip('[')
        title = opp['title'][opp['title'].find(']')+1:].strip()

        print(f"{i:2}. [{opp['new_score']:3}/100] (was {opp['old_score']:3}, {change_str:>4})")
        print(f"    {source:15} {title[:48]}")
        print(f"    SEO: {opp['breakdown']['seo_potential']}/25 | "
              f"Self-Service: {opp['breakdown']['self_service']}/25 | "
              f"Pain: {opp['breakdown']['pain_intensity']}/30 | "
              f"Recurring: {opp['breakdown']['recurring']}/20")
        print()

    # Show biggest gainers
    print("=" * 70)
    print("BIGGEST MICROSAAS WINNERS (Score Increased Most)")
    print("=" * 70)
    print()

    gainers = sorted(rescored, key=lambda x: x['new_score'] - x['old_score'], reverse=True)

    for i, opp in enumerate(gainers[:5], 1):
        change = opp['new_score'] - opp['old_score']
        if change <= 0:
            continue

        title = opp['title'][opp['title'].find(']')+1:].strip()
        print(f"{i}. +{change} points: {title[:55]}")

    print()

    # Show biggest losers
    print("=" * 70)
    print("MICROSAAS MISMATCHES (Score Decreased Most)")
    print("=" * 70)
    print()

    losers = sorted(rescored, key=lambda x: x['new_score'] - x['old_score'])

    for i, opp in enumerate(losers[:5], 1):
        change = opp['new_score'] - opp['old_score']
        if change >= 0:
            continue

        title = opp['title'][opp['title'].find(']')+1:].strip()
        print(f"{i}. {change} points: {title[:55]}")
        print(f"   (Likely requires sales team or not SEO-friendly)")

    print()
    print("=" * 70)
    print()
    print("✅ Re-scoring complete!")
    print("🔄 Flask app will auto-reload with new scores")
    print("🌐 View at: http://localhost:5000")
    print()


if __name__ == "__main__":
    try:
        rescore_all_opportunities()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
