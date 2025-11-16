# FMCSA Integration TODO

## Critical Issue Discovered

**Problem**: User tested MC 309204 and got wrong company name ("Reliable Freight Brokers LLC" instead of "Reed Transport Services Inc")

**Root Cause**: Using mock data instead of real FMCSA API

**Correct Data for MC 309204**:
- Company: REED TRANSPORT SERVICES INC
- DBA: REED TMS LOGISTICS
- USDOT: 2222662
- MC: 309204
- Type: BROKER
- Status: ACTIVE
- Authority: AUTHORIZED FOR BROKER Property

---

## Immediate Next Steps

### Option 1: Register for Official FMCSA WebKey (RECOMMENDED)

**Steps**:
1. Go to https://mobile.fmcsa.dot.gov/QCDevsite
2. Create developer account using Login.gov
3. Navigate to "My WebKeys"
4. Click "Get a new WebKey"
5. Fill out form (free, instant approval)

**API Endpoint**:
```
GET https://mobile.fmcsa.dot.gov/qc/services/carriers/{mcOrDot}?webKey=YOUR_KEY
```

**Benefits**:
- Official, supported API
- JSON response (easy to parse)
- Free
- Reliable
- Legal (no scraping issues)

**Timeline**: 30 minutes to register + 1 hour to integrate

###Option 2: Scrape Public SAFER Website (INTERIM SOLUTION)

**URL Pattern**:
```
https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=MC_MX&query_string={mcNumber}
```

**Approach**:
- Use cheerio or similar HTML parser
- Extract company name, USDOT, status, authority type
- Parse the HTML table structure

**Challenges**:
- HTML parsing (brittle if they change format)
- Rate limiting concerns
- Potential terms of service issues

**Timeline**: 2-3 hours to implement scraper

### Option 3: Use Third-Party API (PAID)

**Services**:
- SaferWebAPI.com - wraps FMCSA data
- FMCSA DOT Crawler (Apify) - $

**Benefits**:
- Ready to use
- Already parsed
- May have additional data

**Costs**:
- $50-200/month typically

**Timeline**: 1 hour to integrate

---

## Implementation Plan (Recommended: Option 1)

### Step 1: Register for FMCSA WebKey

**Action**: Go to mobile.fmcsa.dot.gov/QCDevsite and register

**What You Need**:
- Login.gov account
- Company/personal details
- Reason for access (business application)

**Expected Result**: WebKey string (e.g., "abc123def456")

### Step 2: Test API Endpoint

**Test Request**:
```bash
curl "https://mobile.fmcsa.dot.gov/qc/services/carriers/309204?webKey=YOUR_KEY"
```

**Expected Response** (JSON):
```json
{
  "content": {
    "carrier": {
      "legalName": "REED TRANSPORT SERVICES INC",
      "dbaName": "REED TMS LOGISTICS",
      "dotNumber": 2222662,
      "mcNumber": "MC-309204",
      "censusType": "BROKER",
      "statusCode": "A",
      "allowedToOperate": "Y",
      ...
    }
  }
}
```

### Step 3: Update API Route

**File**: `app/api/verify/[mc]/route.ts`

**Implementation**:
```typescript
async function fetchFMCSABrokerData(mcNumber: string) {
  const webKey = process.env.FMCSA_WEB_KEY;
  if (!webKey) {
    throw new Error('FMCSA_WEB_KEY not configured');
  }

  const response = await fetch(
    `https://mobile.fmcsa.dot.gov/qc/services/carriers/${mcNumber}?webKey=${webKey}`
  );

  if (!response.ok) {
    throw new Error(`FMCSA API error: ${response.status}`);
  }

  const data = await response.json();
  const carrier = data.content.carrier;

  return {
    found: true,
    name: carrier.legalName,
    dbaName: carrier.dbaName,
    mcNumber: carrier.mcNumber,
    dotNumber: carrier.dotNumber.toString(),
    status: carrier.statusCode === 'A' ? 'ACTIVE' : 'INACTIVE',
    authorityType: carrier.censusType, // BROKER or CARRIER
    insuranceOnFile: carrier.bipdInsuranceOnFile === 'Y',
    bondOnFile: carrier.bondInsuranceOnFile === 'Y',
    physicalAddress: `${carrier.phyStreet}, ${carrier.phyCity}, ${carrier.phyState} ${carrier.phyZipcode}`,
    phone: carrier.telephone,
    lastUpdated: new Date().toISOString(),
  };
}
```

### Step 4: Add Environment Variable

**File**: `.env.local` (create if doesn't exist)
```
FMCSA_WEB_KEY=your_web_key_here
```

**Vercel Setup** (for deployment):
```bash
vercel env add FMCSA_WEB_KEY
# Enter your WebKey when prompted
```

### Step 5: Support Both MC and USDOT Numbers

**Issue**: MC numbers being phased out, USDOT is primary

**Solution**: Accept both MC and USDOT in URL

**API Route Update**:
```typescript
// Current: /api/verify/[mc]/route.ts
// Update to: /api/verify/[identifier]/route.ts

export async function GET(
  request: NextRequest,
  { params }: { params: { identifier: string } }
) {
  const identifier = params.identifier;

  // Determine if it's MC or USDOT (MC numbers are typically 6 digits, USDOT 7)
  const isMC = identifier.length <= 6;
  const queryParam = isMC ? 'MC_MX' : 'USDOT';

  // Call FMCSA API with appropriate parameter
  const data = await fetchFMCSAData(identifier, queryParam);

  ...
}
```

### Step 6: Update Frontend

**Homepage Search Label**:
```typescript
<label htmlFor="mc-number">
  Enter Broker MC or DOT Number
</label>
```

**Placeholder**:
```typescript
<input
  placeholder="MC: 309204 or DOT: 2222662"
  ...
/>
```

---

## MC vs USDOT: What's the Difference?

### MC Number (Motor Carrier)
- Older system
- Format: MC-######
- Being phased out
- Still widely used
- Example: MC-309204

### USDOT Number
- Newer, primary identifier
- Format: #######
- Required for all interstate commerce
- More reliable
- Example: 2222662

### Our Support Strategy
1. Accept both MC and USDOT
2. FMCSA API works with either
3. Display both in results (even if user searched with one)
4. Educate users: "MC 309204 (USDOT: 2222662)"

---

## Data Fields We Can Get from FMCSA API

### Basic Identification
- ✅ Legal name
- ✅ DBA name
- ✅ MC number
- ✅ USDOT number
- ✅ Entity type (BROKER vs CARRIER)

### Contact Information
- ✅ Physical address
- ✅ Mailing address
- ✅ Phone number

### Operating Authority
- ✅ Status (ACTIVE/INACTIVE)
- ✅ Authorized to operate (yes/no)
- ✅ Operating authority (PROPERTY, HOUSEHOLD GOODS, etc.)
- ✅ Out of service date (if any)

### Insurance & Bond
- ✅ Insurance on file (yes/no)
- ✅ Bond on file (yes/no) - required for brokers
- ❌ Insurance policy details (not in free API)
- ❌ Bond amount (not in free API)

### Safety Data
- ✅ Safety rating (if assigned)
- ✅ Crash data (24-month period)
- ✅ Inspection data
- ✅ Out of service violations

### What FMCSA Does NOT Provide
- ❌ Payment history
- ❌ Customer reviews
- ❌ Fraud reports
- ❌ Credit rating
- ❌ BBB rating
- ❌ Court records
- ❌ Bankruptcy filings

**These require additional data sources** (which is why our multi-source approach adds value)

---

## Testing Plan

### Test Cases

1. **Valid Broker MC Number**
   - Input: 309204
   - Expected: REED TRANSPORT SERVICES INC, BROKER, ACTIVE

2. **Valid Broker USDOT Number**
   - Input: 2222662
   - Expected: Same as above

3. **Valid Carrier (Not Broker)**
   - Input: Test with carrier MC
   - Expected: Show warning "This is a CARRIER, not a BROKER"

4. **Invalid MC Number**
   - Input: 999999999
   - Expected: "Broker not found" error

5. **Inactive/Out of Service**
   - Input: Find inactive broker
   - Expected: Show "INACTIVE" status, low trust score

6. **Missing Bond**
   - Input: Broker without bond on file
   - Expected: Show warning, reduced trust score

---

## Trust Score Algorithm Update

**Current (Mock)**:
- Base: 50
- Active: +15
- Broker type: +10
- Insurance: +5
- Bond: +10
- **Max**: 90

**Updated (Real Data)**:
```typescript
function calculateTrustScore(data: FMCSAData): number {
  let score = 50;

  // Operating Status
  if (data.status === 'ACTIVE') score += 15;
  if (data.allowedToOperate === 'Y') score += 10;

  // Authority Type
  if (data.authorityType === 'BROKER') score += 10;
  else score -= 20; // It's a carrier, not broker

  // Insurance & Bond
  if (data.insuranceOnFile) score += 5;
  if (data.bondOnFile) score += 10;
  else score -= 25; // Brokers MUST have bond

  // Safety Record (if available)
  if (data.safetyRating === 'SATISFACTORY') score += 10;
  if (data.crashes24mo === 0) score += 5;

  // Deductions
  if (data.outOfServiceDate) score -= 50;
  if (data.status === 'INACTIVE') score -= 30;

  return Math.min(100, Math.max(0, score));
}
```

---

## Homepage Messaging During Beta

### Option 1: Be Transparent (RECOMMENDED)

**Hero Section**:
```
VerifyCarrier - Verify Freight Brokers

🔧 Early Access Beta

We're building the first platform for carriers to verify brokers.
Real FMCSA integration coming this week.

For now, verify brokers manually at:
safer.fmcsa.dot.gov

Join our waitlist to be notified when we launch!
[Enter Email]
```

### Option 2: Show "Coming Soon"

**Hero Section**:
```
VerifyCarrier - Coming Soon

The first platform built for carriers to verify brokers
before hauling loads.

Launching January 2025

[Join Waitlist] [Verify at FMCSA.gov]
```

### Option 3: Delay Deployment

- Don't deploy until FMCSA API is integrated
- Finish integration first (1-2 hours)
- Launch with real data
- Better first impression

**RECOMMENDED**: Option 3 - Finish integration before deploying

---

## Timeline to Launch

**Current Status**: Mock data showing wrong results

**Path to Launch**:

### Today (2-3 hours):
1. Register for FMCSA WebKey (30 min)
2. Test API endpoint (30 min)
3. Implement integration (1-2 hours)
4. Test with real MC numbers (30 min)

### Tomorrow:
5. Deploy to Vercel
6. Configure custom domain
7. Launch!

---

## Action Items

- [ ] Register for FMCSA WebKey
- [ ] Get WebKey credentials
- [ ] Test API endpoint with curl
- [ ] Implement fetchFMCSABrokerData with real API
- [ ] Add FMCSA_WEB_KEY to .env.local
- [ ] Support both MC and USDOT numbers
- [ ] Update homepage labels (MC or DOT)
- [ ] Test with MC 309204 (should show Reed Transport)
- [ ] Test with invalid MC (should show error)
- [ ] Update trust score algorithm
- [ ] Add Vercel environment variable
- [ ] Deploy to production

---

## Conclusion

**Don't deploy with fake data**. Users will immediately test it (like they just did) and lose trust.

**Better approach**: Spend 2-3 hours integrating real FMCSA API, then launch with accurate data.

**User trust preserved** ✅ by showing real, accurate information from day 1.
