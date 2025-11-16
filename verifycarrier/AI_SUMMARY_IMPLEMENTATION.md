# AI-Powered Broker Intelligence Report - Implementation Plan

## Vision: Transform from "Link Aggregator" to "AI Intelligence Platform"

**Current (CRAWL)**: Show 8 verification links → saves 14 minutes
**Next (WALK)**: AI-generated comprehensive report → saves 30+ minutes
**Future (RUN)**: Real-time monitoring + alerts → continuous protection

---

## User's Brilliant Idea

> "Can we get a PACER account? And then summarize it all in a nicely formatted document with trustworthy branding and ask for an email. Perhaps we use Claude API to create a nice document summarized with accurate data. Also we should use Perplexity or Gemini for full company deep research and include in summary."

### Why This is Genius

✅ **Higher perceived value** - AI report worth way more than links
✅ **Email lead magnet** - "Enter email to get full AI report"
✅ **Differentiation** - No competitor does AI-powered broker intelligence
✅ **Upsell path** - Free: 1 report/week, Paid: Unlimited reports
✅ **Trust building** - Beautiful branded PDF shows professionalism
✅ **Viral potential** - Carriers share reports with each other

---

## Implementation Phases

### Phase 1: Fix Broken Links (DONE ✅)
- ✅ Fixed FMCSA L&I link (now uses SMS portal)
- ✅ Updated BBB link (instructions to search by name)
- ⏳ Test all 8 links work

### Phase 2: Data Scraping (1-2 days)
**Goal**: Extract data from FMCSA SAFER automatically

**Approach**:
```typescript
async function scrapeFMCSAData(mcNumber: string) {
  const url = `https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=MC_MX&query_string=${mcNumber}`;

  const response = await fetch(url);
  const html = await response.text();

  // Parse HTML to extract:
  const data = {
    companyName: extractCompanyName(html),
    dbaName: extractDBAName(html),
    mcNumber: mcNumber,
    dotNumber: extractDOTNumber(html),
    physicalAddress: extractAddress(html),
    phone: extractPhone(html),
    status: extractStatus(html),
    authorityType: extractAuthorityType(html), // BROKER vs CARRIER
    insuranceOnFile: extractInsurance(html),
    bondOnFile: extractBond(html),
    outOfService: extractOOS(html),
  };

  return data;
}
```

**Libraries**:
- cheerio (HTML parsing)
- OR puppeteer (if JavaScript rendering needed)
- OR just use FMCSA official API (need WebKey)

**Timeline**: 2-3 hours to implement scraper

### Phase 3: Google Deep Research with Perplexity (1 day)

**Perplexity API** (https://docs.perplexity.ai/)
```typescript
async function researchBrokerWithPerplexity(companyName: string, mcNumber: string) {
  const prompt = `Research the freight broker "${companyName}" (MC ${mcNumber}). Provide:
1. Company overview and history
2. Online reputation and reviews
3. Any fraud complaints or scam reports
4. Payment history reputation among carriers
5. Social media presence and activity
6. News articles or press mentions
7. Red flags or concerns
8. Positive indicators of legitimacy

Be thorough and cite sources.`;

  const response = await fetch('https://api.perplexity.ai/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.PERPLEXITY_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-sonar-large-128k-online',
      messages: [{
        role: 'user',
        content: prompt,
      }],
    }),
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

**Cost**: ~$0.001 per request (very cheap)
**Value**: Deep internet research no human could do in 15 minutes

**Alternative**: Google Gemini with Grounding
```typescript
// Gemini 2.0 Flash with Google Search grounding
const model = genAI.getGenerativeModel({
  model: "gemini-2.0-flash-exp",
  tools: [{ googleSearch: {} }],
});
```

### Phase 4: Claude API Summary (1 day)

**Claude API** (Sonnet 4 for analysis)
```typescript
async function generateBrokerReport(rawData: {
  fmcsaData: any,
  perplexityResearch: string,
  googleSearchSummary: string,
}) {
  const prompt = `You are an expert freight broker analyst. Create a comprehensive broker verification report.

**Data Sources:**
1. FMCSA Official Data:
${JSON.stringify(rawData.fmcsaData, null, 2)}

2. Deep Internet Research:
${rawData.perplexityResearch}

3. Additional Findings:
${rawData.googleSearchSummary}

**Create a professional broker intelligence report with:**

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Overall recommendation (VERIFIED SAFE / CAUTION / HIGH RISK)
   - Key findings
   - Trust score (0-100)

2. COMPANY PROFILE
   - Legal name, DBA, location
   - MC/DOT numbers
   - Years in business
   - Operating authority status

3. COMPLIANCE & SAFETY
   - FMCSA authority status
   - Insurance and bond on file
   - Safety rating
   - Out of service status
   - Recent violations

4. REPUTATION ANALYSIS
   - Online reviews summary
   - Fraud reports or complaints
   - Payment history reputation
   - Social media presence

5. RED FLAGS (if any)
   - List any concerning findings
   - Risk assessment

6. POSITIVE INDICATORS
   - List strengths and trust signals

7. VERIFICATION CHECKLIST
   - ✅ Items verified
   - ⚠️ Items needing attention
   - ❌ Red flags

8. RECOMMENDATION
   - Should carrier work with this broker?
   - What precautions to take?
   - Next steps for due diligence

Format as professional markdown with clear sections, bullet points, and emojis for visual clarity.`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4000,
    messages: [{
      role: 'user',
      content: prompt,
    }],
  });

  return response.content[0].text;
}
```

**Cost**: ~$0.015 per report (1.5 cents)
**Value**: Professional analyst-quality report

### Phase 5: Beautiful PDF Generation (1 day)

**Libraries**:
- react-pdf/renderer OR
- puppeteer (HTML to PDF) OR
- jsPDF

**Design**:
```typescript
import { Document, Page, Text, View, StyleSheet, PDFDownloadLink } from '@react-pdf/renderer';

const BrokerReport = ({ data }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* Header with VerifyCarrier branding */}
      <View style={styles.header}>
        <Text style={styles.logo}>VerifyCarrier</Text>
        <Text style={styles.subtitle}>AI-Powered Broker Intelligence Report</Text>
        <Text style={styles.date}>{new Date().toLocaleDateString()}</Text>
      </View>

      {/* Trust Score Badge */}
      <View style={styles.trustBadge}>
        <Text style={styles.trustScore}>{data.trustScore}/100</Text>
        <Text style={styles.trustLabel}>{data.recommendation}</Text>
      </View>

      {/* Executive Summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Executive Summary</Text>
        <Text style={styles.body}>{data.executiveSummary}</Text>
      </View>

      {/* Company Profile */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Company Profile</Text>
        <Text style={styles.body}>
          {data.companyName}\n
          MC: {data.mcNumber} | DOT: {data.dotNumber}\n
          {data.address}\n
          {data.phone}
        </Text>
      </View>

      {/* ... rest of report sections ... */}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Generated by VerifyCarrier.com | Grade A+ Security | Multi-Source Verification
        </Text>
        <Text style={styles.disclaimer}>
          This report is for informational purposes only. Always conduct your own due diligence.
        </Text>
      </View>
    </Page>
  </Document>
);
```

**Branding Elements**:
- VerifyCarrier logo
- Navy blue (#0A2540) header
- Green trust score for good brokers
- Red warnings for high-risk
- Professional typography
- Watermark: "Powered by AI"

### Phase 6: Email Gate (1 day)

**Flow**:
```
User enters MC number
  ↓
Show loading: "Researching broker across 8+ sources..."
  ↓
Progress indicators:
- ✅ Fetching FMCSA data...
- ✅ Researching online reputation...
- ✅ Analyzing compliance history...
- ✅ Generating AI summary...
  ↓
"Report ready! Enter your email to download:"
  ↓
[Email input] [Get Report]
  ↓
1. Send report via email
2. Save email to database
3. Show download link on page
```

**Email Content**:
```html
Subject: Your Broker Intelligence Report - MC 309204

Hi,

Your AI-powered broker intelligence report for MC 309204 (Reed Transport Services Inc) is ready!

🎯 Trust Score: 85/100 - VERIFIED SAFE

Key Findings:
✅ Active FMCSA authority
✅ Insurance and bond on file
✅ Positive carrier reviews
⚠️ Limited online presence

Download your full report:
[Download PDF Report]

Want unlimited broker reports?
Upgrade to VerifyCarrier Pro for $49/month
[Start Free Trial]

---
VerifyCarrier - Protecting carriers from broker fraud
Grade A+ Security | Multi-Source Verification
```

**Database Schema**:
```sql
CREATE TABLE email_subscribers (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  mc_number VARCHAR(20),
  report_generated_at TIMESTAMP DEFAULT NOW(),
  ip_address VARCHAR(45),
  user_agent TEXT,
  converted_to_paid BOOLEAN DEFAULT FALSE
);
```

---

## PACER Account Setup

### What is PACER?

**PACER** (Public Access to Court Electronic Records)
- Federal court records database
- Bankruptcies, lawsuits, judgments
- $0.10 per page (max $3 per document)
- Free account registration

### How to Get PACER Account

**Step 1: Register**
- Go to: https://pacer.uscourts.gov/
- Click "Register for an Account"
- Fill out form (free, no credit card needed)
- Verify email

**Step 2: Link Credit Card**
- Add payment method
- Only charged for documents you view
- Quarterly bills (only if you use it)
- Free if under $30/quarter

**Step 3: Search for Broker**
```
1. Login to PACER
2. Select "Case Locator" (searches all courts)
3. Search by:
   - Party name: "Reed Transport Services Inc"
   - Nature of suit: Bankruptcy, Contract, Fraud
4. View case details ($0.10/page)
```

### Cost Analysis

**Typical search**:
- Case search: Free
- View case summary: $0.30 (3 pages)
- Download judgment: $1.00 (10 pages)
- **Total per broker**: $1-2

**For VerifyCarrier**:
- Monthly searches: ~100 brokers
- Monthly cost: $100-200
- **Include in Pro plan** ($49/month x 200 users = $9,800/month revenue)
- PACER cost: 1-2% of revenue ✅ Profitable

### Automate PACER Searches

**Can we scrape PACER?**
- ❌ Against TOS for automated scraping
- ✅ OK for manual searches
- ✅ OK for API integration (if available)

**Solution for MVP**:
1. Manual PACER checks for Pro users only
2. Batch searches (once per week)
3. Cache results for 30 days
4. Include in premium $49/month tier

---

## Complete Data Flow

### Input
```
MC Number: 309204
```

### Step 1: Scrape FMCSA SAFER
```javascript
const fmcsaData = await scrapeFMCSAData('309204');
// Returns: {
//   companyName: 'Reed Transport Services Inc',
//   mcNumber: '309204',
//   dotNumber: '2222662',
//   status: 'ACTIVE',
//   ...
// }
```

### Step 2: Deep Research with Perplexity
```javascript
const research = await researchBrokerWithPerplexity(
  'Reed Transport Services Inc',
  '309204'
);
// Returns: Comprehensive internet research with citations
```

### Step 3: Generate Report with Claude
```javascript
const report = await generateBrokerReport({
  fmcsaData,
  perplexityResearch: research,
  googleSearchSummary: '', // Optional: scrape Google results
});
// Returns: Markdown formatted professional report
```

### Step 4: Create PDF
```javascript
const pdf = await generatePDF(report, fmcsaData);
// Returns: Beautiful branded PDF
```

### Step 5: Email Gate
```javascript
await sendReportEmail(userEmail, pdf, fmcsaData.mcNumber);
await saveEmailSubscriber(userEmail, fmcsaData.mcNumber);
```

### Output
```
✉️ Email sent to user with:
- PDF attachment (Broker_Intelligence_Report_MC309204.pdf)
- Summary in email body
- Call-to-action for Pro plan
```

---

## Pricing Strategy

### Free Tier
- **1 report per week** (email gate)
- AI-powered summary
- PDF download
- All 8 data source links

### Pro Tier - $49/month
- **Unlimited reports**
- PACER court record checks (manual, weekly batches)
- Chrome extension (verify from load boards)
- Email alerts (if broker status changes)
- Report history dashboard
- Priority support

### Enterprise Tier - $199/month
- Everything in Pro
- API access
- Bulk verification (upload CSV)
- Custom integrations (TMS systems)
- Dedicated account manager

---

## Technical Stack

### APIs Needed

1. **Anthropic Claude API** ✅
   - Already have access
   - Cost: ~$0.015/report
   - Model: claude-sonnet-4

2. **Perplexity API** ⏳
   - Sign up: https://www.perplexity.ai/settings/api
   - Cost: ~$0.001/request
   - Model: llama-3.1-sonar-large-128k-online

3. **FMCSA SAFER** (scraping or WebKey)
   - Option A: Register for WebKey (free)
   - Option B: Scrape public site (legal gray area)
   - **Recommended**: Get WebKey

4. **Email Service** (Resend or SendGrid)
   - Resend: 3,000 emails/month free
   - SendGrid: 100 emails/day free
   - **Recommended**: Resend (better DX)

### Database

**Supabase** (PostgreSQL + Auth)
```sql
-- Email subscribers
CREATE TABLE subscribers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  reports_generated INT DEFAULT 1,
  last_report_at TIMESTAMP DEFAULT NOW(),
  is_pro BOOLEAN DEFAULT FALSE
);

-- Reports generated
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  mc_number VARCHAR(20) NOT NULL,
  subscriber_id UUID REFERENCES subscribers(id),
  report_data JSONB NOT NULL,
  pdf_url TEXT,
  generated_at TIMESTAMP DEFAULT NOW()
);

-- Rate limiting
CREATE TABLE rate_limits (
  subscriber_id UUID REFERENCES subscribers(id),
  last_report_at TIMESTAMP,
  reports_this_week INT DEFAULT 0,
  PRIMARY KEY (subscriber_id)
);
```

---

## Implementation Timeline

### Week 1: Core Data Scraping
- Day 1-2: FMCSA scraper OR WebKey integration
- Day 3: Test data extraction accuracy
- Day 4: Add Perplexity API integration
- Day 5: Test deep research quality

### Week 2: AI Report Generation
- Day 1-2: Claude API integration
- Day 3: Report template design
- Day 4: Test report quality with real brokers
- Day 5: Iterate on prompt engineering

### Week 3: Email Gate + PDF
- Day 1-2: Email capture flow
- Day 3: PDF generation
- Day 4: Email delivery (Resend)
- Day 5: Database setup (Supabase)

### Week 4: Polish + Launch
- Day 1-2: UI/UX improvements
- Day 3: Testing with real users
- Day 4: Deploy to production
- Day 5: Launch + marketing

**Total: 1 month to full AI-powered reports**

---

## MVP (Next 48 Hours)

### Saturday (Tomorrow)
1. ✅ Fix broken links (DONE)
2. ⏳ Get FMCSA WebKey (30 min)
3. ⏳ Scrape basic FMCSA data (2-3 hours)
4. ⏳ Test data accuracy with MC 309204

### Sunday
5. ⏳ Sign up for Perplexity API
6. ⏳ Test Perplexity research for one broker
7. ⏳ Create simple text report (no PDF yet)
8. ⏳ Add email gate

**Goal**: By Sunday night, users can:
- Enter MC number
- Get AI-generated text summary (no PDF yet)
- Email gate working
- Basic report shows FMCSA data + Perplexity research

---

## Cost Analysis

### Per Report Cost

| Service | Cost | Purpose |
|---------|------|---------|
| Perplexity API | $0.001 | Deep internet research |
| Claude API | $0.015 | AI report generation |
| FMCSA API | $0.000 | Free (WebKey) |
| Email (Resend) | $0.001 | PDF delivery |
| **Total** | **$0.017** | **~2 cents per report** |

### Revenue Model

**Free Tier** (1 report/week):
- Users: 1,000 free users
- Reports: 1,000/week = 4,000/month
- Cost: 4,000 × $0.017 = $68/month
- Revenue: $0 (lead generation)

**Pro Tier** ($49/month):
- Users: 200 paying
- Revenue: $9,800/month
- Reports: ~20 per user = 4,000/month
- Cost: 4,000 × $0.017 = $68/month
- **Margin**: $9,732/month (99.3%) ✅

**Conclusion**: Even with AI reports, margins are incredible!

---

## Security & Privacy

### Data Handling
- ✅ No storage of FMCSA data (always fresh)
- ✅ Cache Perplexity research for 7 days
- ✅ Encrypt email addresses
- ✅ GDPR compliant (delete on request)
- ✅ No selling of email lists

### Rate Limiting
- Free: 1 report per week per email
- Pro: Unlimited (but fair use: ~100/month)
- IP-based: Max 3 requests per day (unauthenticated)

---

## Next Steps

1. **Deploy current version** (link aggregation)
2. **Get FMCSA WebKey** (30 minutes)
3. **Sign up for Perplexity API** (10 minutes)
4. **Build Phase 2** (AI reports) over next 2-4 weeks
5. **Launch Pro tier** when reports are ready

**Question for you**: Should we:
- A) Deploy link aggregation NOW, add AI reports in 2 weeks?
- B) Wait 2-3 days, deploy with basic AI reports?
- C) Full 1-month build, launch with perfect AI reports?

My recommendation: **Option A** - Deploy now, iterate quickly based on user feedback.
