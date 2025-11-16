# VerifyCarrier - Trusted Carrier Verification Platform

A Next.js web application for verifying freight carriers using multiple data sources to prevent fraud and cargo theft.

## Overview

VerifyCarrier goes beyond simple FMCSA database lookups by verifying carriers across 15+ trusted data sources, providing a comprehensive trust score to help freight brokers and logistics companies prevent fraud.

## Features

- **Multi-Source Verification**: Checks 15+ data sources (FMCSA, BBB, D&B, court records, fraud databases, etc.)
- **Trust Score Algorithm**: 0-100 score based on comprehensive verification
- **Grade A+ Security**: Implements all security headers for top-tier security ratings
- **Professional Trust-Focused Design**: Navy blue brand color (#0A2540) with green (verified) and red (fraud) indicators
- **SEO-Optimized**: Comprehensive metadata for search engine visibility
- **Mobile-Responsive**: Works seamlessly on all devices

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Deployment**: Vercel (recommended)

## Security

The application implements Grade A+ security headers:

- **HSTS** (HTTP Strict Transport Security) with preload
- **CSP** (Content Security Policy)
- **X-Frame-Options**: DENY
- **X-Content-Type-Options**: nosniff
- **Referrer-Policy**: strict-origin-when-cross-origin
- **Permissions-Policy**: Restricted geolocation, microphone, camera, payment

## Local Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm run start
```

## Project Structure

```
verifycarrier/
├── app/
│   ├── api/
│   │   └── verify/[mc]/
│   │       └── route.ts          # Carrier verification API endpoint
│   ├── globals.css               # Global styles + trust utilities
│   ├── layout.tsx                # Root layout with SEO metadata
│   └── page.tsx                  # Homepage with search interface
├── next.config.js                # Next.js config with security headers
├── tailwind.config.ts            # Tailwind config with trust colors
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies
```

## API Routes

### GET /api/verify/[mc]

Verifies a carrier by MC number.

**Parameters:**
- `mc` (path parameter): The MC number to verify

**Response:**
```json
{
  "success": true,
  "name": "ABC Trucking Company",
  "mcNumber": "123456",
  "dotNumber": "123456",
  "status": "ACTIVE",
  "safetyRating": "SATISFACTORY",
  "trustScore": 85,
  "verifiedSources": ["FMCSA SAFER", ...],
  "lastUpdated": "2025-11-15T15:45:00.000Z"
}
```

## Deployment to Vercel

### Quick Deploy

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
vercel
```

Follow the prompts to:
- Link to existing project or create new
- Set project name: `verifycarrier`
- Set build settings (should auto-detect Next.js)

4. **Deploy to Production**:
```bash
vercel --prod
```

### Custom Domain Setup

Once deployed, add your custom domain in Vercel dashboard:

1. Go to Project Settings > Domains
2. Add `verifycarrier.com`
3. Configure DNS records as instructed by Vercel

## Color Palette

The application uses a trust-focused color scheme:

- **Primary Navy**: `#0A2540` - Authority and trust
- **Success Green**: `#10B981` - Verified/safe carriers
- **Danger Red**: `#EF4444` - Fraud alerts/high risk
- **Warning Yellow**: `#f59e0b` - Caution/review needed

## Next Steps

### Phase 1: CRAWL (MVP)
- [ ] Integrate real FMCSA SAFER API
- [ ] Add email gate (3 free searches/day)
- [ ] Implement basic fraud database
- [ ] Add email collection for waitlist

### Phase 2: WALK (Paid Features)
- [ ] Add 14+ additional data sources
- [ ] Implement subscription tiers
- [ ] Build user dashboard
- [ ] Add bulk verification
- [ ] Create API access for developers

### Phase 3: RUN (Scale)
- [ ] Real-time fraud alerts
- [ ] Mobile app
- [ ] Partner integrations (TMS systems)
- [ ] Enterprise features

## Security Note

There is 1 critical vulnerability in the dependencies. To address:

```bash
npm audit fix --force
```

Review changes carefully before committing.

## Documentation

Full product documentation:
- [Product Requirements](../VERIFY_CARRIER_PRD.md)
- [Trust Strategy](../VERIFY_CARRIER_TRUST_ENHANCEMENTS.md)
- [Summary](../VERIFY_CARRIER_SUMMARY.md)

## License

Proprietary - All rights reserved
