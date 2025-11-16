#!/usr/bin/env python3
"""
Pain Point Discovery Engine - Web Interface

Flask web app to view and analyze collected pain points.
Run with: python app.py
"""

from flask import Flask, render_template, request, jsonify
from backend.models import Opportunity, Tweet, PainAnalysis
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


@app.route('/')
def index():
    """Main dashboard showing top opportunities."""

    # Get filter parameters
    days = int(request.args.get('days', 7))
    min_score = int(request.args.get('min_score', 40))
    source = request.args.get('source', 'all')

    # Get opportunities
    opportunities = Opportunity.get_top_opportunities(
        limit=50,
        min_score=min_score,
        days=days
    )

    # Filter by source if specified
    if source != 'all':
        source_prefixes = {
            'hackernews': '[HN]',
            'stackoverflow': '[SO/',
            'github': '[GH/',
            'reddit': '[REDDIT]',
            'twitter': '[TWITTER]'
        }
        prefix = source_prefixes.get(source, '')
        opportunities = [o for o in opportunities if o['title'].startswith(prefix)]

    # Calculate stats
    total_opps = len(opportunities)
    high_value = len([o for o in opportunities if o['score'] >= 70])
    avg_score = sum(o['score'] for o in opportunities) / total_opps if total_opps > 0 else 0

    # Count by source
    sources = {
        'HackerNews': len([o for o in opportunities if o['title'].startswith('[HN]')]),
        'Stack Overflow': len([o for o in opportunities if '[SO/' in o['title']]),
        'GitHub': len([o for o in opportunities if '[GH/' in o['title']]),
        'Reddit': len([o for o in opportunities if '[REDDIT]' in o['title']]),
        'Twitter': len([o for o in opportunities if '[TWITTER]' in o['title']]),
    }

    return render_template(
        'index.html',
        opportunities=opportunities,
        stats={
            'total': total_opps,
            'high_value': high_value,
            'avg_score': round(avg_score, 1)
        },
        sources=sources,
        filters={
            'days': days,
            'min_score': min_score,
            'source': source
        }
    )


@app.route('/opportunity/<int:opp_id>')
def opportunity_detail(opp_id):
    """View detailed information about an opportunity."""

    # Get opportunity
    opp = Opportunity.get_by_id(opp_id)

    if not opp:
        return "Opportunity not found", 404

    # Get associated tweets/posts
    tweets = Opportunity.get_tweets(opp_id)

    # Get pain analysis for each tweet
    for tweet in tweets:
        pain = PainAnalysis.get_by_tweet(tweet['id'])
        if pain:
            tweet['pain_analysis'] = pain

    return render_template(
        'opportunity.html',
        opportunity=opp,
        tweets=tweets
    )


@app.route('/api/opportunities')
def api_opportunities():
    """API endpoint for opportunities (JSON)."""

    days = int(request.args.get('days', 7))
    min_score = int(request.args.get('min_score', 40))
    limit = int(request.args.get('limit', 50))

    opportunities = Opportunity.get_top_opportunities(
        limit=limit,
        min_score=min_score,
        days=days
    )

    return jsonify(opportunities)


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics (JSON)."""

    days = int(request.args.get('days', 7))

    all_opps = Opportunity.get_top_opportunities(limit=1000, min_score=0, days=days)

    stats = {
        'total_opportunities': len(all_opps),
        'high_value': len([o for o in all_opps if o['score'] >= 70]),
        'medium_value': len([o for o in all_opps if 50 <= o['score'] < 70]),
        'low_value': len([o for o in all_opps if 40 <= o['score'] < 50]),
        'avg_score': sum(o['score'] for o in all_opps) / len(all_opps) if all_opps else 0,
        'sources': {
            'hackernews': len([o for o in all_opps if o['title'].startswith('[HN]')]),
            'stackoverflow': len([o for o in all_opps if '[SO/' in o['title']]),
            'github': len([o for o in all_opps if '[GH/' in o['title']]),
            'reddit': len([o for o in all_opps if '[REDDIT]' in o['title']]),
            'twitter': len([o for o in all_opps if '[TWITTER]' in o['title']]),
        }
    }

    return jsonify(stats)


if __name__ == '__main__':
    # Run in development mode
    # For production, use gunicorn or similar WSGI server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
