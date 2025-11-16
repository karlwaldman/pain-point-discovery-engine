# VerifyCarrier Data Sources Audit

## Current Reality Check: What We Actually Have Access To

**User's Critical Point**: "Don't over promise - we must be trustworthy at each stage"

---

## Phase 1: CRAWL (MVP) - Available NOW (Free/Low Cost)

### ✅ Confirmed Available (Free)

1. **FMCSA SAFER API** - FREE ✅
   - Broker MC number
   - Authority status (ACTIVE/INACTIVE)
   - Operating authority type (BROKER vs CARRIER)
   - Insurance on file (yes/no)
   - Surety bond on file (yes/no)
   - USDOT number
   - Physical address
   - Phone number
   - Out-of-service status
   - Safety rating (if applicable)
   - **Access**: Free webkey from mobile.fmcsa.dot.gov/QCDevsite

2. **Domain Age Check** - FREE ✅
   - WHOIS lookup
   - Domain registration date
   - **Access**: Free WHOIS APIs (whoisxmlapi.com free tier, who.is)

3. **Google Presence Check** - FREE ✅
   - Does broker have website?
   - Google search results count
   - **Access**: Google Custom Search API (100 queries/day free)

4. **Business Legitimacy** - FREE ✅
   - Secretary of State business registration (manual lookup)
   - EIN verification (if broker provides)
   - **Access**: Free state SOS websites (scraping)

### ⚠️ Possibly Available (Need to Verify)

5. **Better Business Bureau** - CHECK NEEDED
   - BBB rating
   - Complaint count
   - **Access**: BBB API or scraping (need to check if allowed)

---

## Phase 2: WALK (Paid Features) - Need Subscriptions

### ❌ NOT Currently Accessible (Require Payment)

6. **Payment History Data** - COMMERCIAL ✅
   - Average days to pay
   - Payment defaults
   - **Cost**: $500-1000/month for factoring data feeds
   - **Source**: HaulPay, RTS, factoring companies

7. **DAT Load Board Ratings** - COMMERCIAL ✅
   - Broker ratings by carriers
   - Load posting history
   - **Cost**: $200+/month for DAT API
   - **Source**: dat.com/api

8. **Truckstop.com Data** - COMMERCIAL ✅
   - Broker reviews
   - Credit ratings
   - **Cost**: $150+/month
   - **Source**: truckstop.com

9. **Carrier411** - COMMERCIAL ✅
   - Broker fraud reports
   - Credit scores
   - **Cost**: $50-100/month
   - **Source**: carrier411.com

10. **D&B (Dun & Bradstreet)** - COMMERCIAL ✅
    - Business credit score
    - Financial health
    - **Cost**: $500-2000/month for API access
    - **Source**: dnb.com

11. **Court Records (PACER)** - PAID ✅
    - Federal court judgments
    - Bankruptcy filings
    - **Cost**: $0.10 per page (cheap but not free)
    - **Source**: pacer.uscourts.gov

12. **State Court Records** - VARIES
    - State-level lawsuits
    - Liens, judgments
    - **Cost**: Varies by state ($5-50 per search)
    - **Source**: State court websites

---

## Phase 3: RUN (Advanced) - User-Generated Data

### Future Data Sources (Build Over Time)

13. **User-Submitted Fraud Reports** - OWN DATABASE ✅
    - Carriers report bad brokers
    - Community-driven
    - **Cost**: Free (our own database)
    - **Timeline**: 6-12 months to build

14. **Social Media Presence** - FREE ✅
    - LinkedIn company page
    - Facebook business page
    - **Access**: Manual checks or API limits
    - **Timeline**: Can add anytime

15. **Insurance Verification (Direct)** - MANUAL ✅
    - Call insurance company directly
    - Verify active policy
    - **Cost**: Time (manual process)
    - **Timeline**: Phase 3 (too slow for MVP)

---

## HONEST COUNT: Current Reality

### What We Can Access RIGHT NOW (Free):
1. FMCSA SAFER API ✅
2. Domain age check ✅
3. Google presence check ✅
4. Business registration check ✅
5. BBB lookup (if allowed) ⚠️

**Actual Count**: **4-5 data sources** (not 15+)

### What We Can Add in Month 1 (Low Cost):
- PACER court records ($10-50/month)
- State business registrations (automated scraping)

**Month 1 Total**: **6-7 data sources**

### What Requires Significant Budget:
- Payment history data ($500+/month)
- DAT API ($200+/month)
- Truckstop.com ($150+/month)
- Carrier411 ($50+/month)
- D&B ($500+/month)

**With Budget**: **11-12 data sources**

### What Requires Time to Build:
- User fraud reports database (6-12 months)
- Carrier reviews (6-12 months)
- Historical payment tracking (6-12 months)

**Long-term**: **15+ data sources** ✅

---

## REVISED MESSAGING: Be Honest

### ❌ Current (Overpromised)
- "Verify MC numbers instantly using **15+ data sources**"
- "We verify brokers across **15+ trusted data sources**"
- "Multi-source verification (**15+ data sources**)"

### ✅ Honest Alternatives

**Option 1: Current State (4-5 sources)**
- "Instant broker verification using **FMCSA + 4 additional data sources**"
- "Multi-source verification beyond FMCSA alone"
- "We check **5 key data points** instantly"

**Option 2: Growth Path (Be transparent)**
- "Instant broker verification starting with **FMCSA + 4 sources**. More added monthly."
- "Currently checking **5 data sources**. Expanding to 15+ as we grow."
- "**Phase 1**: 5 sources. **Phase 2**: 10+ sources. **Phase 3**: 15+ sources."

**Option 3: Focus on Value, Not Count**
- "Instant broker verification using **government databases + business intelligence**"
- "Multi-source verification to protect you from fraud"
- "More than just FMCSA - we verify **authority, legitimacy, and fraud history**"

**RECOMMENDATION**: Option 3 - Focus on VALUE, not specific numbers
- Emphasize we're MORE than FMCSA alone (true)
- Don't make specific numerical claims we can't back up
- Be vague enough to be true, specific enough to be valuable

---

## Updated Copy for All Pages

### Homepage Hero

**OLD** ❌:
> "Instant broker verification using 15+ data sources — know before you haul."

**NEW** ✅:
> "Instant broker verification using government databases and business intelligence — know before you haul."

### Features Section

**OLD** ❌:
> "We verify brokers across 15+ trusted data sources to protect you from fraud, payment defaults, and scams."

**NEW** ✅:
> "We verify brokers using multiple trusted data sources to protect you from fraud, payment defaults, and scams."

### Trust Badges

**OLD** ❌:
> "15+ Data Sources"

**NEW** ✅:
> "Multi-Source Verification"
OR
> "Beyond FMCSA Alone"

### Meta Description

**OLD** ❌:
> "Instant broker verification using 15+ data sources."

**NEW** ✅:
> "Instant broker verification using FMCSA and additional business intelligence sources."

### Footer

**OLD** ❌:
> "Data verified across 15+ sources."

**NEW** ✅:
> "Multi-source broker verification."

---

## What We Actually Check (CRAWL Phase)

### Current Trust Score Algorithm (4-5 Checks)

```typescript
function calculateTrustScore(broker: Broker): number {
  let score = 50; // Base score

  // 1. FMCSA Authority Check (FREE)
  if (broker.mcStatus === 'ACTIVE') score += 20;
  if (broker.authorityType === 'BROKER') score += 10;
  if (broker.bondOnFile) score += 15;
  if (broker.insuranceOnFile) score += 5;

  // 2. Domain Age Check (FREE)
  if (broker.domainAge > 2) score += 10; // >2 years
  else if (broker.domainAge > 1) score += 5; // >1 year

  // 3. Google Presence (FREE)
  if (broker.hasWebsite) score += 5;
  if (broker.googleResults > 100) score += 5;

  // 4. Business Registration (FREE)
  if (broker.businessRegistered) score += 10;

  // 5. BBB Rating (IF FREE)
  if (broker.bbbRating === 'A+') score += 10;
  else if (broker.bbbRating === 'A') score += 7;

  // Deductions
  if (broker.outOfService) score -= 50;
  if (broker.bondLapsed) score -= 30;

  return Math.min(100, Math.max(0, score));
}
```

### What We Show Users

**Sources Checked** (Honest List):
```typescript
verifiedSources: [
  'FMCSA SAFER Database',
  'Business Registration Records',
  'Domain Age Verification',
  'Online Business Presence',
  'Better Business Bureau (if available)',
]
```

---

## Roadmap: How We Get to 15+ Sources

### Month 1: Add 2 More (Total: 6-7)
- PACER court records (cheap)
- Enhanced state business registration

### Month 3: Add Premium Data (Total: 10-11) [Requires Revenue]
- Carrier411 ($50/month)
- Payment history database (partner with factoring company?)

### Month 6: Add Load Board Data (Total: 12-13) [Requires Revenue]
- DAT API ($200/month)
- Truckstop.com ($150/month)

### Month 12: Add Enterprise Data (Total: 15+) [Requires $10k/month Revenue]
- D&B business credit ($500/month)
- User fraud reports database (built in-house)
- Social media verification
- Direct insurance calls (manual for high-value checks)

---

## Competitive Honesty

### Verified Carrier (Competitor)
- Claims: "8-step verification process"
- Reality: Likely 8 STEPS, not 8 SOURCES
  - Step 1: Check FMCSA
  - Step 2: Call insurance
  - Step 3: Verify bank account
  - Step 4: Facial recognition
  - Step 5: Document review
  - Step 6: Human review
  - Step 7: etc.

**Insight**: They conflate "steps in process" with "data sources"
**Our Advantage**: We can be MORE honest and still differentiate

### Our Messaging vs Theirs

**Them**: "8-step verification" (sounds manual, slow)
**Us**: "Instant multi-source verification" (sounds fast, comprehensive)

**Them**: Manual human review (slow, expensive)
**Us**: Automated checks + trust score (fast, scalable)

**Differentiation**: We don't compete on number of sources, we compete on:
- ✅ Speed (instant vs hours)
- ✅ Cost ($49/month vs $200+ per check)
- ✅ Automation (self-service vs request-based)
- ✅ Different customer (carriers vs brokers)

---

## Final Recommendations

### 1. Remove All "15+" Claims ✅
**Rationale**: We can't back it up NOW. We can add sources later when we have revenue.

### 2. Use Vague But True Language ✅
**Examples**:
- "Multi-source verification"
- "Beyond FMCSA alone"
- "Government databases + business intelligence"
- "Comprehensive broker checks"

### 3. Be Transparent About Growth ✅
**Examples**:
- "Starting with 5 core data sources, expanding monthly"
- "New data sources added as we grow"
- "Phase 1: Core verification. Phase 2: Premium data."

### 4. Focus on Value, Not Count ✅
**What Matters**:
- ✅ "Prevent broker fraud"
- ✅ "Instant verification"
- ✅ "Know before you haul"
- ❌ NOT "We check 15 sources" (users don't care about the number)

### 5. Update Trust Score to Match Reality ✅
**Current scoring**: Based on 4-5 actual checks
**Display**: "Trust Score 85/100 based on 5 verified data points"
**Honesty**: Show exactly what we checked

---

## Action Items

- [x] Audit actual data sources available
- [ ] Update all homepage copy (remove "15+")
- [ ] Update meta descriptions (remove "15+")
- [ ] Update API responses (show real sources checked)
- [ ] Update trust score algorithm (match real checks)
- [ ] Add "Data Sources" page explaining what we check
- [ ] Add transparency: "More sources added monthly"

---

## Conclusion

**Current Access**: 4-5 free data sources
**Honest Claim**: "Multi-source verification beyond FMCSA alone"
**Growth Path**: Add 1-2 sources per month as revenue grows
**Timeline to 15+**: 6-12 months

**Key Principle**: Under-promise, over-deliver. Better to surprise users with MORE sources than to lose trust by claiming sources we don't have.

**User's Trust**: Preserved ✅ by being honest from day 1.
