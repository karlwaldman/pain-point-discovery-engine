#!/usr/bin/env python3
"""
GitHub Issues Pain Point Collection

Uses GitHub REST API (free, no auth for public repos) to find:
- Feature requests in popular DevOps tools
- Product gaps and missing features
- Community pain points and complaints

Excellent for competitive analysis and identifying product opportunities!
"""

import os
import sys
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Tweet, PainAnalysis, Opportunity
from backend.pain_detector import analyze_pain
from backend.scoring import calculate_opportunity_score


def search_github_issues(repo, label=None, keyword=None, state='open'):
    """
    Search GitHub issues using REST API.

    API Docs: https://docs.github.com/en/rest/issues
    Free, no auth required (60 req/hour)
    With auth: 5000 req/hour
    """
    url = f'https://api.github.com/repos/{repo}/issues'

    params = {
        'state': state,
        'sort': 'reactions',  # Most reactions = most pain
        'direction': 'desc',
        'per_page': 20,
    }

    # Add label filter if provided
    if label:
        params['labels'] = label

    # Add keyword search (GitHub doesn't support this directly in issues API)
    # We'll filter client-side

    try:
        # Check for GitHub token (optional, increases rate limit)
        github_token = os.getenv('GITHUB_TOKEN')
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            issues = response.json()

            # Filter by keyword if provided
            if keyword:
                filtered = []
                for issue in issues:
                    title = issue.get('title', '').lower()
                    body = issue.get('body', '') or ''
                    body_lower = body.lower()

                    if keyword.lower() in title or keyword.lower() in body_lower:
                        filtered.append(issue)
                return filtered
            else:
                return issues

        elif response.status_code == 403:
            # Rate limit exceeded
            print(f"  ⚠ Rate limit exceeded (60/hour without auth)")
            return []

        else:
            print(f"  ✗ API error: {response.status_code}")
            return []

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def process_github_issue(issue, repo):
    """Process a GitHub issue for pain signals."""

    # Get issue details
    title = issue.get('title', '')
    body = issue.get('body', '') or ''
    full_text = f"{title}\n\n{body[:800]}"  # Limit body

    if not full_text or len(full_text) < 20:
        return False, 0

    # Check if already exists (use GitHub issue ID)
    issue_id = str(issue.get('id', ''))
    if Tweet.exists(f"GH_{issue_id}"):
        return False, 0

    # Analyze pain
    pain_analysis = analyze_pain(full_text)

    # Create engagement data from GitHub metrics
    reactions = issue.get('reactions', {})
    total_reactions = (
        reactions.get('total_count', 0) or
        reactions.get('+1', 0) + reactions.get('-1', 0) +
        reactions.get('laugh', 0) + reactions.get('hooray', 0) +
        reactions.get('confused', 0) + reactions.get('heart', 0) +
        reactions.get('rocket', 0) + reactions.get('eyes', 0)
    )

    comments = issue.get('comments', 0)

    # High reactions = widespread pain, many comments = active discussion
    tweet_data = {
        'likes': total_reactions * 3,  # Reactions indicate strong agreement
        'retweets': comments // 2,
        'replies': comments
    }

    # Calculate opportunity score
    opp_score = calculate_opportunity_score(tweet_data, pain_analysis)

    # Boost for feature requests
    labels = [label.get('name', '') for label in issue.get('labels', [])]
    if any(label in ['feature-request', 'enhancement', 'improvement'] for label in labels):
        opp_score += 10  # Feature request = clear product gap

    # Boost for open issues (still unresolved)
    if issue.get('state') == 'open':
        opp_score += 5

    opp_score = min(100, opp_score)

    # Only store if meets threshold
    min_score = int(os.getenv('MIN_OPPORTUNITY_SCORE', 40))
    if opp_score < min_score:
        return False, opp_score

    # Store
    try:
        tweet_id = Tweet.create(
            tweet_id=f"GH_{issue_id}",
            text=full_text[:1000],
            created_at=issue.get('created_at', datetime.now().isoformat()),
            author_username=issue.get('user', {}).get('login', 'unknown'),
            author_followers=0,  # GitHub doesn't provide follower count in issue API
            likes=total_reactions * 3,
            retweets=comments // 2,
            replies=comments
        )

        # Pain analysis
        PainAnalysis.create(
            tweet_id=tweet_id,
            frustration_score=pain_analysis['frustration_score'],
            budget_signal_score=pain_analysis['budget_signal_score'],
            products_mentioned=pain_analysis['products_mentioned'],
            pain_keywords=pain_analysis['pain_keywords']
        )

        # Create opportunity
        repo_short = repo.split('/')[-1]  # e.g., "kubernetes" from "kubernetes/kubernetes"
        opportunity_id = Opportunity.create(
            title=f"[GH/{repo_short}] {title[:100]}",
            description=f"{full_text[:400]}\n\nLink: {issue.get('html_url', '')}",
            score=opp_score,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat()
        )

        Opportunity.add_tweet(opportunity_id, tweet_id)

        return True, opp_score

    except Exception as e:
        print(f"    ✗ Error storing: {e}")
        return False, 0


def collect_from_github():
    """Main GitHub collection function."""

    print("=" * 60)
    print("GITHUB ISSUES PAIN POINT COLLECTION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    load_dotenv()

    # Import search parameters from pain_keywords
    from backend.pain_keywords import GITHUB_REPOSITORIES, GITHUB_LABELS, GITHUB_KEYWORDS

    total_found = 0
    total_stored = 0
    total_high_value = 0

    # Strategy: Search top repos with feature-request label
    # Limit to avoid rate limits (60 req/hour without auth)
    selected_repos = GITHUB_REPOSITORIES[:5]  # Top 5 repos
    selected_label = GITHUB_LABELS[0]  # 'feature-request'

    print(f"Searching {len(selected_repos)} repositories for '{selected_label}' issues...")
    print()

    search_count = 0

    for repo in selected_repos:
        search_count += 1
        print(f"[{search_count}/{len(selected_repos)}] Repository: {repo}")

        issues = search_github_issues(repo, label=selected_label)
        total_found += len(issues)

        print(f"  Found: {len(issues)} feature requests")

        stored_this_repo = 0
        high_value_this_repo = 0

        for issue in issues:
            stored, score = process_github_issue(issue, repo)

            if stored:
                stored_this_repo += 1
                total_stored += 1

                if score >= 70:
                    high_value_this_repo += 1
                    total_high_value += 1

                    title = issue.get('title', '')[:50]
                    print(f"    ⭐ High-value: \"{title}...\" (Score: {score})")

        print(f"  Stored: {stored_this_repo} issues")
        if high_value_this_repo > 0:
            print(f"  🔥 High-value: {high_value_this_repo}")
        print()

        time.sleep(1)  # Rate limiting

    # Summary
    print("=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Repositories searched: {search_count}")
    print(f"Issues found: {total_found}")
    print(f"Issues stored: {total_stored}")
    print(f"High-value: {total_high_value} (score >= 70)")
    print()

    # Show top opportunities
    opps = Opportunity.get_top_opportunities(limit=5, min_score=40, days=1)

    gh_opps = [o for o in opps if o['title'].startswith('[GH/')]

    if gh_opps:
        print("🔥 TOP 5 GITHUB OPPORTUNITIES:")
        print("-" * 60)
        for i, opp in enumerate(gh_opps[:5], 1):
            # Extract title after [GH/repo]
            title_parts = opp['title'].split('] ', 1)
            title = title_parts[1] if len(title_parts) > 1 else opp['title']
            print(f"{i}. [{opp['score']}/100] {title[:60]}...")

    print("=" * 60)


if __name__ == "__main__":
    try:
        collect_from_github()
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Collection failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
