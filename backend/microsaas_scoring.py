"""
MicroSaaS Opportunity Scoring

Scores opportunities based on MicroSaaS viability:
- SEO-driven acquisition (no sales team)
- Self-service product (no marketing team)
- Extreme pain points
- Good customer satisfaction potential

MicroSaaS sweet spot:
- Clear search intent
- Obvious value proposition
- Recurring problem
- SMB/mid-market (not enterprise)
- Can explain in one sentence
"""


def calculate_seo_potential(title: str, description: str, keywords: str) -> int:
    """
    Calculate SEO potential (0-25 points).

    High SEO potential = people actively searching for solutions
    """
    score = 0

    title_lower = title.lower()
    desc_lower = description.lower()

    # Handle keywords as string or list
    if isinstance(keywords, list):
        kw_lower = ' '.join(keywords).lower()
    elif keywords:
        kw_lower = keywords.lower()
    else:
        kw_lower = ""

    combined_text = f"{title_lower} {desc_lower} {kw_lower}"

    # High-intent search phrases (people looking for solutions)
    high_intent_phrases = [
        'how to prevent',
        'best tool for',
        'software for',
        'platform for',
        'solution for',
        'alternative to',
        'prevention',
        'automation',
        'tracking',
        'monitoring',
        'detection',
        'verification',
        'management',
    ]

    for phrase in high_intent_phrases:
        if phrase in combined_text:
            score += 3

    # Clear problem statement (good for SEO)
    problem_indicators = [
        'theft', 'fraud', 'loss', 'missing', 'stolen',
        'slow', 'manual', 'inefficient', 'expensive',
        'complicated', 'difficult', 'frustrating'
    ]

    for indicator in problem_indicators:
        if indicator in combined_text:
            score += 2

    # Bonus for B2B keywords (good search volume, less competitive than B2C)
    b2b_keywords = ['freight', 'cargo', 'compliance', 'verification', 'reporting', 'api']
    for kw in b2b_keywords:
        if kw in combined_text:
            score += 3

    return min(25, score)


def calculate_self_service_potential(title: str, description: str) -> int:
    """
    Calculate self-service potential (0-25 points).

    Can this be sold without sales team?
    """
    score = 0

    desc_lower = description.lower()
    title_lower = title.lower()

    # Positive indicators (self-service friendly)
    self_service_indicators = [
        ('api', 5),           # APIs are self-service
        ('dashboard', 5),     # Dashboards are self-serve
        ('automated', 5),     # Automation = less human touch
        ('real-time', 4),     # Real-time products sell themselves
        ('instant', 4),       # Instant value = self-serve
        ('platform', 3),      # Platforms can be self-serve
        ('saas', 4),          # SaaS keyword
        ('subscription', 4),  # Recurring revenue
    ]

    for indicator, points in self_service_indicators:
        if indicator in desc_lower or indicator in title_lower:
            score += points

    # Negative indicators (requires sales team)
    sales_required = [
        ('enterprise', -8),   # Enterprise needs sales
        ('custom', -5),       # Customization needs sales
        ('integration', -3),  # Complex integrations need help
        ('consulting', -8),   # Consulting = not self-serve
        ('implementation', -5),
    ]

    for indicator, points in sales_required:
        if indicator in desc_lower or indicator in title_lower:
            score += points

    # Market size indicators
    # MicroSaaS sweet spot: SMB/mid-market, not enterprise
    if 'small business' in desc_lower or 'smb' in desc_lower:
        score += 5

    if 'enterprise' in desc_lower and 'only' in desc_lower:
        score -= 10  # Enterprise-only is bad for MicroSaaS

    return max(0, min(25, score))


def calculate_pain_intensity(frustration_score: int, budget_score: int, keywords: str) -> int:
    """
    Calculate pain intensity (0-30 points).

    MicroSaaS needs EXTREME pain to justify self-service purchase.
    """
    score = 0

    # Frustration score (0-10) → scale to 15 points
    score += min(15, frustration_score * 1.5)

    # Budget score (0-10) → scale to 10 points
    score += min(10, budget_score)

    # Extreme pain keywords
    if keywords:
        # Handle keywords as string or list
        if isinstance(keywords, list):
            kw_lower = ' '.join(keywords).lower()
        else:
            kw_lower = keywords.lower()

        extreme_pain = [
            'existential', 'crisis', 'emergency', 'urgent',
            'losing money', 'losing customers', 'costing',
            'theft', 'fraud', 'stolen', 'breach'
        ]

        for pain_kw in extreme_pain:
            if pain_kw in kw_lower:
                score += 2

    return min(30, score)


def calculate_recurring_potential(description: str) -> int:
    """
    Calculate recurring problem potential (0-20 points).

    MicroSaaS needs recurring problems for MRR.
    """
    score = 0

    desc_lower = description.lower()

    # Recurring problem indicators
    recurring_indicators = [
        ('daily', 5),
        ('every', 4),
        ('ongoing', 4),
        ('continuous', 4),
        ('monitoring', 5),
        ('tracking', 5),
        ('real-time', 5),
        ('subscription', 5),
        ('monthly', 4),
        ('recurring', 5),
    ]

    for indicator, points in recurring_indicators:
        if indicator in desc_lower:
            score += points

    # One-time problem (bad for MicroSaaS)
    if 'one-time' in desc_lower or 'once' in desc_lower:
        score -= 5

    return max(0, min(20, score))


def calculate_microsaas_score(opportunity_data: dict, pain_analysis: dict) -> int:
    """
    Calculate MicroSaaS viability score (0-100).

    Breakdown:
    - SEO Potential: 0-25 points
    - Self-Service Potential: 0-25 points
    - Pain Intensity: 0-30 points
    - Recurring Potential: 0-20 points

    Total: 100 points
    """

    title = opportunity_data.get('title', '')
    description = opportunity_data.get('description', '')

    frustration_score = pain_analysis.get('frustration_score', 0)
    budget_score = pain_analysis.get('budget_signal_score', 0)
    keywords = pain_analysis.get('pain_keywords', '')

    # Calculate components
    seo_score = calculate_seo_potential(title, description, keywords)
    self_service_score = calculate_self_service_potential(title, description)
    pain_score = calculate_pain_intensity(frustration_score, budget_score, keywords)
    recurring_score = calculate_recurring_potential(description)

    total_score = seo_score + self_service_score + pain_score + recurring_score

    return min(100, total_score)


def get_microsaas_breakdown(opportunity_data: dict, pain_analysis: dict) -> dict:
    """
    Get detailed scoring breakdown for debugging.
    """

    title = opportunity_data.get('title', '')
    description = opportunity_data.get('description', '')
    frustration_score = pain_analysis.get('frustration_score', 0)
    budget_score = pain_analysis.get('budget_signal_score', 0)
    keywords = pain_analysis.get('pain_keywords', '')

    return {
        'seo_potential': calculate_seo_potential(title, description, keywords),
        'self_service': calculate_self_service_potential(title, description),
        'pain_intensity': calculate_pain_intensity(frustration_score, budget_score, keywords),
        'recurring': calculate_recurring_potential(description),
        'total': calculate_microsaas_score(opportunity_data, pain_analysis)
    }
