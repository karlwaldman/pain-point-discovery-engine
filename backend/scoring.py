"""
Opportunity Scoring Module

Calculate 0-100 scores for opportunities based on:
- Engagement (0-20 points)
- Frustration (0-30 points)
- Budget signals (0-50 points)
"""

from typing import Dict


def calculate_engagement_score(likes: int, retweets: int, replies: int = 0) -> int:
    """
    Calculate engagement score (0-20 points).

    Formula: (likes + (retweets * 2)) / 10
    Cap at 20 points.
    """
    engagement = likes + (retweets * 2)
    score = engagement / 10

    return min(20, int(score))


def calculate_frustration_score_from_analysis(pain_analysis: Dict) -> int:
    """
    Calculate frustration score (0-30 points) from pain analysis.

    Factors:
    - Base frustration score from detector (0-10) × 2.5
    - Solution seeking bonus (+5)
    - Time investment bonus (+5)
    """
    score = pain_analysis['frustration_score'] * 2.5

    # Bonus for solution seeking (indicates active problem)
    if pain_analysis.get('has_solution_seeking'):
        score += 5

    # Bonus for time investment (indicates chronic pain)
    if pain_analysis.get('has_time_investment'):
        score += 5

    return min(30, int(score))


def calculate_opportunity_score(tweet_data: Dict, pain_analysis: Dict) -> int:
    """
    Calculate total opportunity score (0-100).

    Components:
    - Engagement: 0-20 points
    - Frustration: 0-30 points
    - Budget signals: 0-50 points

    Total: 0-100 points

    Thresholds:
    - 80+: Excellent opportunity
    - 60-79: Good opportunity
    - 40-59: Worth investigating
    - <40: Low signal
    """

    # Engagement score (0-20)
    engagement_score = calculate_engagement_score(
        tweet_data.get('likes', 0),
        tweet_data.get('retweets', 0),
        tweet_data.get('replies', 0)
    )

    # Frustration score (0-30)
    frustration_score = calculate_frustration_score_from_analysis(pain_analysis)

    # Budget signal score (0-50)
    budget_score = pain_analysis.get('budget_signal_score', 0)

    # Total score
    total = engagement_score + frustration_score + budget_score

    return min(100, int(total))


def get_score_rating(score: int) -> str:
    """Get text rating for score."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Worth Investigating"
    else:
        return "Low Signal"


def get_score_color(score: int) -> str:
    """Get color code for score (for UI)."""
    if score >= 80:
        return "success"  # Green
    elif score >= 60:
        return "warning"  # Yellow/Orange
    elif score >= 40:
        return "info"  # Blue
    else:
        return "secondary"  # Gray


def calculate_score_breakdown(tweet_data: Dict, pain_analysis: Dict) -> Dict:
    """
    Calculate score with detailed breakdown.

    Returns:
    {
        'total': 73,
        'rating': 'Good',
        'color': 'warning',
        'breakdown': {
            'engagement': 6,
            'frustration': 22,
            'budget': 45
        },
        'factors': {
            'likes': 45,
            'retweets': 12,
            'frustration_keywords': 3,
            'has_dollar_amount': True,
            'mentions_paid_tool': True
        }
    }
    """

    # Calculate component scores
    engagement_score = calculate_engagement_score(
        tweet_data.get('likes', 0),
        tweet_data.get('retweets', 0),
        tweet_data.get('replies', 0)
    )

    frustration_score = calculate_frustration_score_from_analysis(pain_analysis)
    budget_score = pain_analysis.get('budget_signal_score', 0)

    total_score = engagement_score + frustration_score + budget_score

    return {
        'total': min(100, total_score),
        'rating': get_score_rating(total_score),
        'color': get_score_color(total_score),
        'breakdown': {
            'engagement': engagement_score,
            'frustration': frustration_score,
            'budget': budget_score
        },
        'factors': {
            'likes': tweet_data.get('likes', 0),
            'retweets': tweet_data.get('retweets', 0),
            'replies': tweet_data.get('replies', 0),
            'frustration_level': pain_analysis['frustration_score'],
            'has_solution_seeking': pain_analysis.get('has_solution_seeking', False),
            'has_time_investment': pain_analysis.get('has_time_investment', False),
            'has_dollar_amount': len(pain_analysis.get('dollar_amounts', [])) > 0,
            'mentions_paid_tool': len(pain_analysis.get('products_mentioned', [])) > 0,
            'pain_keywords_count': len(pain_analysis.get('pain_keywords', []))
        }
    }


# Testing
if __name__ == "__main__":
    # Test with sample data
    from pain_detector import analyze_pain

    sample_tweet_text = """I'm paying $99/mo for Airtable and it STILL doesn't do what I need!
    Why is there no simple database for small teams???"""

    tweet_data = {
        'likes': 45,
        'retweets': 12,
        'replies': 8
    }

    print("Sample Tweet:")
    print(f"  {sample_tweet_text}")
    print(f"  Likes: {tweet_data['likes']}, Retweets: {tweet_data['retweets']}")
    print()

    # Analyze pain
    pain_analysis = analyze_pain(sample_tweet_text)

    # Calculate score
    score_breakdown = calculate_score_breakdown(tweet_data, pain_analysis)

    print("Opportunity Score Breakdown:")
    print(f"  Total Score: {score_breakdown['total']}/100")
    print(f"  Rating: {score_breakdown['rating']}")
    print()
    print("Component Scores:")
    print(f"  Engagement: {score_breakdown['breakdown']['engagement']}/20")
    print(f"  Frustration: {score_breakdown['breakdown']['frustration']}/30")
    print(f"  Budget Signal: {score_breakdown['breakdown']['budget']}/50")
    print()
    print("Factors:")
    for key, value in score_breakdown['factors'].items():
        print(f"  {key}: {value}")
