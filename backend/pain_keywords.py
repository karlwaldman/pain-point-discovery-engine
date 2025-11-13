"""
Pain Expression Keywords and Patterns

This module contains all the pain keywords and search patterns
we use to find business opportunities on social media.

Based on CRAWL plan: 50+ pain expression patterns
"""

# Frustration Expressions (exact phrases for Twitter search)
FRUSTRATION_PHRASES = [
    "why is there no",
    "I can't believe there's no",
    "still no solution for",
    "how is there not a",
    "someone needs to build",
    "I wish someone would make",
    "there should be a tool for",
    "frustrated with",
    "hate dealing with",
    "sick of",
]

# Solution Seeking Phrases
SOLUTION_SEEKING_PHRASES = [
    "does anyone know a tool for",
    "looking for a way to",
    "is there a service that",
    "anyone have a solution for",
    "recommendations for",
    "what do you use for",
    "how do you handle",
    "what's the best way to",
    "struggling with",
    "need help with",
]

# Workaround Mentions
WORKAROUND_PHRASES = [
    "my janky solution is",
    "I'm duct-taping together",
    "currently using 3 tools for",
    "built a spreadsheet to",
    "manual process for",
    "hacky way to",
    "cobbled together",
]

# Time Investment Signals
TIME_INVESTMENT_PHRASES = [
    "spent hours trying to",
    "wasted all day",
    "takes me forever to",
    "so much time on",
    "always spending time",
    "hours every week",
    "daily struggle with",
]

# Budget Signals
BUDGET_PHRASES = [
    "paying $ for",
    "our team uses",
    "tried",
    "switching from",
    "looking for alternative to",
    "cheaper than",
    "too expensive",
]

# Urgency Markers
URGENCY_PHRASES = [
    "need this ASAP",
    "urgent need for",
    "immediately need",
    "this week I need",
    "deadline coming up",
]

# Frequency Indicators
FREQUENCY_PHRASES = [
    "every single time",
    "daily struggle",
    "always having to",
    "constantly dealing with",
    "this keeps happening",
    "happens all the time",
]

# Impact Statements
IMPACT_PHRASES = [
    "losing customers because",
    "costing us",
    "blocking our team",
    "can't scale until",
    "biggest pain point",
    "critical issue",
]

# Negative Product Experiences
NEGATIVE_PRODUCT_PHRASES = [
    "doesn't do what I need",
    "missing feature",
    "can't believe it doesn't",
    "why can't it",
    "should be able to",
]

# All search queries for Twitter (combine keywords for better results)
TWITTER_SEARCH_QUERIES = [
    # High-intent frustration + solution seeking
    "why is there no tool",
    "there should be a way to",
    "does anyone know how to",
    "looking for a tool that",

    # Budget signals (strong buying intent)
    "paying for * but",
    "expensive for what",
    "$99 and still",
    "cheaper alternative to",

    # Time wasting signals
    "wasted hours on",
    "spent all day trying",
    "takes forever to",

    # Workarounds (clear pain point)
    "manual process for",
    "spreadsheet to manage",
    "duct tape solution",

    # Specific pain points (testing a few domains)
    "invoicing pain",
    "scheduling nightmare",
    "database frustration",
    "API monitoring expensive",

    # General SaaS/tool pain
    "SaaS tool missing",
    "software doesn't",
    "app should have",

    # Founder/entrepreneur pain
    "as a founder struggling",
    "startup pain point",
    "indie hacker problem",

    # Work process pain
    "workflow broken",
    "process inefficient",
    "system doesn't work",
]

# Reddit-specific subreddits to monitor
REDDIT_SUBREDDITS = [
    # Entrepreneurship
    'entrepreneur',
    'startups',
    'SaaS',
    'indiehackers',
    'Entrepreneur',
    'smallbusiness',

    # Work/Productivity
    'productivity',
    'freelance',
    'digital_nomad',
    'remotework',

    # Tech/Development
    'webdev',
    'programming',
    'sysadmin',
    'devops',

    # Specific pain aggregation
    'mildlyinfuriating',
    'assholedesign',
    'crappydesign',

    # Ask communities (good for pain discovery)
    'AskReddit',  # Filter for business/work questions
]

# Reddit search queries
REDDIT_SEARCH_QUERIES = [
    "why is there no tool",
    "does anyone know how to",
    "what do you use for",
    "looking for software",
    "frustrated with",
    "pain point",
    "biggest problem",
]

# Twitter API v2 query operators
def build_twitter_query(keywords: list, exclude_retweets: bool = True) -> str:
    """
    Build Twitter API v2 query with proper operators.

    Example:
        ("why is there no" OR "there should be") -is:retweet lang:en
    """
    query_parts = []

    # Add keywords with OR operator
    if len(keywords) > 1:
        keyword_query = "(" + " OR ".join([f'"{k}"' for k in keywords]) + ")"
    else:
        keyword_query = f'"{keywords[0]}"'

    query_parts.append(keyword_query)

    # Exclude retweets (they're not original pain points)
    if exclude_retweets:
        query_parts.append("-is:retweet")

    # English only
    query_parts.append("lang:en")

    return " ".join(query_parts)


# Example queries
if __name__ == "__main__":
    print("Twitter Search Queries:")
    print("=" * 60)

    # Test a few queries
    test_queries = [
        ["why is there no", "there should be"],
        ["wasted hours", "spent all day"],
        ["paying for", "too expensive"],
    ]

    for keywords in test_queries:
        query = build_twitter_query(keywords)
        print(f"\nKeywords: {keywords}")
        print(f"Query: {query}")

    print("\n\nReddit Subreddits:")
    print("=" * 60)
    print(f"Monitoring {len(REDDIT_SUBREDDITS)} subreddits:")
    for sub in REDDIT_SUBREDDITS:
        print(f"  r/{sub}")

    print(f"\n\nTotal search patterns: {len(TWITTER_SEARCH_QUERIES)}")
