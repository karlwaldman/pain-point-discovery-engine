"""
Pain Detection Module

This module analyzes text to detect pain signals:
- Frustration level (0-10)
- Budget signals (0-50)
- Product/competitor mentions
- Pain keywords
"""

import re
from typing import Dict, List, Tuple


# Pain Expression Patterns (from CRAWL plan)
FRUSTRATION_KEYWORDS = [
    'hate', 'hating', 'frustrated', 'frustrating', 'annoying', 'annoyed',
    'sick of', 'fed up', 'terrible', 'horrible', 'awful', 'worst',
    'ridiculous', 'stupid', 'broken', 'sucks', 'garbage'
]

SOLUTION_SEEKING_PHRASES = [
    'why is there no', 'how is there not', 'why isn\'t there',
    'i wish someone would build', 'there should be',
    'does anyone know', 'looking for a tool', 'is there a service',
    'need a way to', 'how do you', 'what do you use for'
]

BUDGET_KEYWORDS = [
    'paying', 'pay', 'paid', 'spend', 'spent', 'spending',
    'cost', 'costs', 'expensive', 'cheap', 'price', 'pricing',
    'subscription', 'monthly', 'annually', 'per month', 'per year',
    '$', '€', '£', 'dollar'
]

# Known paid tools/services (partial list)
KNOWN_PAID_TOOLS = [
    'airtable', 'notion', 'asana', 'trello', 'jira', 'monday',
    'salesforce', 'hubspot', 'intercom', 'zendesk',
    'stripe', 'chargebee', 'paddle', 'recurly',
    'freshbooks', 'quickbooks', 'xero', 'wave',
    'mailchimp', 'convertkit', 'sendgrid', 'postmark',
    'figma', 'sketch', 'invision', 'adobe', 'canva',
    'zoom', 'slack', 'teams', 'discord'
]

TIME_INVESTMENT_PHRASES = [
    'spent hours', 'wasted', 'takes forever', 'so much time',
    'always spending', 'every day', 'daily struggle', 'constantly'
]


def count_frustration_keywords(text: str) -> int:
    """Count frustration keywords in text."""
    text_lower = text.lower()
    count = 0

    for keyword in FRUSTRATION_KEYWORDS:
        if keyword in text_lower:
            count += 1

    return count


def count_exclamation_marks(text: str) -> int:
    """Count exclamation marks."""
    return text.count('!')


def calculate_caps_ratio(text: str) -> float:
    """Calculate ratio of capital letters (excluding spaces/punctuation)."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0

    caps = [c for c in letters if c.isupper()]
    return len(caps) / len(letters)


def detect_solution_seeking(text: str) -> bool:
    """Check if text contains solution-seeking language."""
    text_lower = text.lower()

    for phrase in SOLUTION_SEEKING_PHRASES:
        if phrase in text_lower:
            return True

    return False


def extract_dollar_amounts(text: str) -> List[str]:
    """Extract dollar amounts from text."""
    # Pattern: $10, $99/mo, $1,000, etc.
    pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:/mo|/month|/yr|/year)?'
    return re.findall(pattern, text)


def count_budget_keywords(text: str) -> int:
    """Count budget-related keywords."""
    text_lower = text.lower()
    count = 0

    for keyword in BUDGET_KEYWORDS:
        if keyword in text_lower:
            count += 1

    return count


def detect_paid_tools(text: str) -> List[str]:
    """Detect mentions of known paid tools."""
    text_lower = text.lower()
    mentioned = []

    for tool in KNOWN_PAID_TOOLS:
        if tool in text_lower:
            mentioned.append(tool)

    return mentioned


def extract_products_mentioned(text: str) -> List[str]:
    """Extract product/company names from text."""
    products = []

    # Detect @ mentions (often products/companies)
    mentions = re.findall(r'@(\w+)', text)
    products.extend(mentions)

    # Detect known paid tools
    tools = detect_paid_tools(text)
    products.extend(tools)

    # Detect capitalized words that might be products (naive approach)
    # Skip common words
    skip_words = {'I', 'Why', 'How', 'What', 'When', 'There', 'This', 'That'}
    caps_words = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', text)
    for word in caps_words:
        if word not in skip_words and len(word) > 2:
            products.append(word)

    # Remove duplicates while preserving order
    seen = set()
    unique_products = []
    for p in products:
        p_lower = p.lower()
        if p_lower not in seen:
            seen.add(p_lower)
            unique_products.append(p)

    return unique_products


def detect_time_investment(text: str) -> bool:
    """Check if text mentions time investment."""
    text_lower = text.lower()

    for phrase in TIME_INVESTMENT_PHRASES:
        if phrase in text_lower:
            return True

    return False


def calculate_frustration_score(text: str) -> int:
    """
    Calculate frustration score (0-10).

    Factors:
    - Frustration keywords
    - Exclamation marks
    - Caps ratio
    - Solution seeking language
    """
    score = 0

    # Frustration keywords (max 6 points)
    keyword_count = count_frustration_keywords(text)
    score += min(6, keyword_count * 2)

    # Exclamation marks (max 2 points)
    exclamations = count_exclamation_marks(text)
    score += min(2, exclamations)

    # Caps ratio (max 2 points)
    caps_ratio = calculate_caps_ratio(text)
    if caps_ratio > 0.3:  # More than 30% caps
        score += 2
    elif caps_ratio > 0.15:  # More than 15% caps
        score += 1

    return min(10, score)


def calculate_budget_signal_score(text: str) -> int:
    """
    Calculate budget signal score (0-50).

    Strong signals of willingness to pay:
    - Mentions dollar amounts (20 points)
    - Mentions paid tools (20 points)
    - Budget-related keywords (10 points)
    """
    score = 0

    # Dollar amounts (strong signal)
    dollar_amounts = extract_dollar_amounts(text)
    if dollar_amounts:
        score += 20

    # Mentions paid tools (strong signal)
    paid_tools = detect_paid_tools(text)
    if paid_tools:
        score += 20

    # Budget keywords
    budget_keyword_count = count_budget_keywords(text)
    score += min(10, budget_keyword_count * 5)

    return min(50, score)


def extract_pain_keywords(text: str) -> List[str]:
    """Extract matched pain keywords from text."""
    keywords = []
    text_lower = text.lower()

    # Frustration keywords
    for keyword in FRUSTRATION_KEYWORDS:
        if keyword in text_lower:
            keywords.append(keyword)

    # Solution seeking phrases
    for phrase in SOLUTION_SEEKING_PHRASES:
        if phrase in text_lower:
            keywords.append(phrase)

    # Time investment
    for phrase in TIME_INVESTMENT_PHRASES:
        if phrase in text_lower:
            keywords.append(phrase)

    return keywords


def analyze_pain(text: str) -> Dict:
    """
    Main pain analysis function.

    Returns dictionary with:
    - frustration_score: 0-10
    - budget_signal_score: 0-50
    - products_mentioned: list of product names
    - pain_keywords: list of matched keywords
    - has_solution_seeking: boolean
    - has_time_investment: boolean
    """

    return {
        'frustration_score': calculate_frustration_score(text),
        'budget_signal_score': calculate_budget_signal_score(text),
        'products_mentioned': extract_products_mentioned(text),
        'pain_keywords': extract_pain_keywords(text),
        'has_solution_seeking': detect_solution_seeking(text),
        'has_time_investment': detect_time_investment(text),
        'dollar_amounts': extract_dollar_amounts(text)
    }


# Testing
if __name__ == "__main__":
    # Test with sample tweet
    sample_tweet = """I'm paying $99/mo for Airtable and it STILL doesn't do what I need!
    Why is there no simple database for small teams???"""

    print("Analyzing tweet:")
    print(f"  {sample_tweet}")
    print()

    analysis = analyze_pain(sample_tweet)

    print("Results:")
    print(f"  Frustration Score: {analysis['frustration_score']}/10")
    print(f"  Budget Signal: {analysis['budget_signal_score']}/50")
    print(f"  Products Mentioned: {analysis['products_mentioned']}")
    print(f"  Pain Keywords: {analysis['pain_keywords']}")
    print(f"  Dollar Amounts: {analysis['dollar_amounts']}")
    print(f"  Solution Seeking: {analysis['has_solution_seeking']}")
    print(f"  Time Investment: {analysis['has_time_investment']}")
