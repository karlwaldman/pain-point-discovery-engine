import { NextRequest, NextResponse } from 'next/server';

// CRAWL MVP Strategy: Provide links to all data sources (aggregation value)
async function generateBrokerVerificationLinks(mcNumber: string) {
  // Instead of fetching data ourselves, we provide direct links to all sources
  // This provides immediate value by saving carriers 15+ minutes of manual searching

  const links = {
    // 1. FMCSA SAFER Database (Primary source)
    fmcsaSafer: {
      name: 'FMCSA SAFER - Official Broker Record',
      url: `https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=MC_MX&query_string=${mcNumber}`,
      description: 'Official government database showing MC/DOT numbers, authority status, insurance, and bond',
      priority: 1,
    },

    // 2. FMCSA SMS (Safety Measurement System) - Alternative to L&I
    fmcsaSMS: {
      name: 'FMCSA SMS - Safety & Compliance',
      url: `https://ai.fmcsa.dot.gov/SMS/Carrier/${mcNumber}/CompleteProfile.aspx`,
      description: 'Safety ratings, violations, inspections, and compliance history',
      priority: 2,
    },

    // 3. Google Search (Company reputation)
    googleSearch: {
      name: 'Google - Company Research',
      url: `https://www.google.com/search?q=MC+${mcNumber}+freight+broker+reviews`,
      description: 'Search for company reviews, complaints, and online presence',
      priority: 3,
    },

    // 4. Better Business Bureau (Note: Will be updated with company name in Phase 2)
    bbbSearch: {
      name: 'Better Business Bureau - Rating & Complaints',
      url: `https://www.bbb.org/search?find_text=freight+broker&find_country=USA`,
      description: 'BBB rating, customer complaints, and business profile (search by company name once loaded from FMCSA)',
      priority: 4,
      note: 'After checking FMCSA, search BBB using the company name',
    },

    // 5. PACER (Federal Court Records)
    pacerSearch: {
      name: 'PACER - Federal Court Records',
      url: `https://pacer.uscourts.gov/`,
      description: 'Search for federal lawsuits, bankruptcies, and judgments ($0.10/page)',
      priority: 5,
      note: 'Requires free PACER account',
    },

    // 6. Carrier411 (Fraud reports)
    carrier411: {
      name: 'Carrier411 - Fraud & Credit Reports',
      url: `https://www.carrier411.com/`,
      description: 'Industry database of broker fraud reports and credit scores',
      priority: 6,
      note: 'Requires subscription ($50-100/month)',
    },

    // 7. DAT Load Board
    datRatings: {
      name: 'DAT - Load Board Ratings',
      url: `https://www.dat.com/`,
      description: 'Broker ratings and reviews from carriers',
      priority: 7,
      note: 'Requires DAT membership',
    },

    // 8. Truckstop.com
    truckstop: {
      name: 'Truckstop.com - Broker Reviews',
      url: `https://www.truckstop.com/`,
      description: 'Carrier reviews and broker credit ratings',
      priority: 8,
      note: 'Requires Truckstop membership',
    },
  };

  return {
    found: true,
    mcNumber: mcNumber,
    searchLinks: links,
    summary: 'Click links below to verify this broker across multiple sources',
    estimatedTimeManual: '15-20 minutes to check all sources manually',
    estimatedTimeWithUs: '30 seconds - all links in one place',
    lastUpdated: new Date().toISOString(),
  };
}

// Calculate trust score based on multiple data sources
function calculateTrustScore(data: any): number {
  let score = 50; // Base score

  // FMCSA broker authority checks
  if (data.status === 'ACTIVE') score += 15;
  if (data.authorityType === 'BROKER') score += 10;
  if (data.insuranceOnFile) score += 5;
  if (data.bondOnFile) score += 10; // Broker surety bond required

  // Additional checks would go here in production:
  // Payment history:
  //   - Days-to-pay average <30 days: +15
  //   - Days-to-pay average 30-45 days: +10
  //   - Days-to-pay average >45 days: +5
  // - No payment defaults: +15
  // - No fraud reports: +15
  // - Years in business >5: +10
  // - BBB rating A+: +10
  // - Positive carrier reviews: +10
  // - Domain age >2 years: +5
  // - Email/phone verified: +5

  // Deductions for red flags:
  // - Payment defaults reported: -40
  // - Fraud reports: -50
  // - Double brokering complaints: -30
  // - Bond lapsed: -25
  // - Bankruptcy filings: -35
  // - Negative carrier reviews: -20

  return Math.min(100, Math.max(0, score));
}

export async function GET(
  request: NextRequest,
  { params }: { params: { mc: string } }
) {
  try {
    const mcNumber = params.mc;

    // Validate MC number
    if (!mcNumber || !/^\d+$/.test(mcNumber)) {
      return NextResponse.json(
        { error: 'Invalid MC number format. Please enter numbers only.' },
        { status: 400 }
      );
    }

    // CRAWL MVP: Generate links to all verification sources
    const verificationData = await generateBrokerVerificationLinks(mcNumber);

    // Return links to all data sources
    return NextResponse.json({
      success: true,
      mcNumber: verificationData.mcNumber,
      message: verificationData.summary,
      valueProp: {
        withoutUs: verificationData.estimatedTimeManual,
        withUs: verificationData.estimatedTimeWithUs,
        timeSaved: '14+ minutes',
      },
      dataSourceLinks: verificationData.searchLinks,
      instructions: [
        '1. Click on each link below to verify the broker',
        '2. Start with FMCSA SAFER (official government database)',
        '3. Check Google for reviews and complaints',
        '4. Look for BBB rating and customer feedback',
        '5. For serious due diligence, check court records and fraud databases',
      ],
      nextPhase: 'We\'re adding automated data fetching soon. For now, we save you time by providing all the links in one place.',
      lastUpdated: verificationData.lastUpdated,
    });

  } catch (error) {
    console.error('Error verifying broker:', error);
    return NextResponse.json(
      { error: 'An error occurred while verifying the broker. Please try again.' },
      { status: 500 }
    );
  }
}
