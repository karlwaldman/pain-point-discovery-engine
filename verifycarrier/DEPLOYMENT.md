# Vercel Deployment Guide for VerifyCarrier

## Prerequisites

1. Domain registered: `verifycarrier.com`
2. Vercel account created at [vercel.com](https://vercel.com)
3. Git repository (optional but recommended)

## Option 1: Deploy via Vercel CLI (Fastest)

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

Follow the email verification prompt.

### 3. Deploy from Local Directory

Navigate to the verifycarrier directory:

```bash
cd /home/kwaldman/pain-point-discovery-engine/verifycarrier
```

Run deploy command:

```bash
vercel
```

Answer the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? **verifycarrier**
- In which directory is your code located? **./** (current directory)
- Want to override settings? **N**

This creates a preview deployment.

### 4. Deploy to Production

```bash
vercel --prod
```

Your app is now live at `https://verifycarrier.vercel.app`

## Option 2: Deploy via GitHub (Recommended for CI/CD)

### 1. Create GitHub Repository

```bash
cd /home/kwaldman/pain-point-discovery-engine/verifycarrier
git init
git add .
git commit -m "Initial commit: VerifyCarrier with Grade A+ security"
git branch -M main
gh repo create verifycarrier --private --source=. --remote=origin
git push -u origin main
```

### 2. Import to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your `verifycarrier` repository
3. Configure project:
   - Framework Preset: **Next.js**
   - Root Directory: **./verifycarrier** (if monorepo) or **/** (if standalone)
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)
4. Click **Deploy**

## Custom Domain Setup

### 1. Add Domain in Vercel

1. Go to Project Settings > Domains
2. Click "Add Domain"
3. Enter: `verifycarrier.com`
4. Click "Add"

### 2. Configure DNS Records

Vercel will provide DNS records. Add these to your domain registrar:

**For apex domain (verifycarrier.com):**
- Type: `A`
- Name: `@`
- Value: `76.76.21.21`

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Value: `cname.vercel-dns.com`

**SSL Certificate**
- Vercel automatically provisions SSL certificates
- HTTPS will be enabled within minutes

## Environment Variables (Future)

When integrating real APIs, add environment variables:

1. Go to Project Settings > Environment Variables
2. Add variables:
   - `FMCSA_API_KEY`
   - `DATABASE_URL`
   - `EMAIL_API_KEY`
   - etc.

## Security Headers Verification

After deployment, verify Grade A+ security:

1. **SSL Labs**: [ssllabs.com/ssltest](https://www.ssllabs.com/ssltest/analyze.html?d=verifycarrier.com)
2. **SecurityHeaders.com**: [securityheaders.com](https://securityheaders.com/?q=verifycarrier.com)
3. **Mozilla Observatory**: [observatory.mozilla.org](https://observatory.mozilla.org/analyze/verifycarrier.com)

Expected ratings: **A+** across all three.

## Post-Deployment Checklist

- [ ] Verify app loads at production URL
- [ ] Test carrier search functionality
- [ ] Verify security headers (should see A+ ratings)
- [ ] Check mobile responsiveness
- [ ] Test API endpoint: `https://verifycarrier.com/api/verify/123456`
- [ ] Verify SSL certificate is active
- [ ] Test custom domain (verifycarrier.com)
- [ ] Add Google Analytics (optional)
- [ ] Submit sitemap to Google Search Console

## Continuous Deployment

With GitHub integration, every push to `main` triggers automatic deployment:

```bash
git add .
git commit -m "Update carrier verification logic"
git push origin main
```

Vercel automatically:
1. Builds the project
2. Runs production optimizations
3. Deploys to production
4. Updates DNS

## Rollback

If you need to rollback to a previous version:

1. Go to Deployments in Vercel dashboard
2. Find the previous working deployment
3. Click "..." > "Promote to Production"

## Monitoring

Vercel provides:
- **Analytics**: Track page views, unique visitors
- **Real-time logs**: Monitor API calls and errors
- **Performance metrics**: Core Web Vitals

Access in Vercel dashboard under your project.

## Cost

- **Hobby Plan** (Free): 100GB bandwidth/month, unlimited deployments
- **Pro Plan** ($20/month): Custom domains, team features, advanced analytics

Start with Hobby plan, upgrade when needed.

## Support

- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)
- Next.js Docs: [nextjs.org/docs](https://nextjs.org/docs)
- Vercel Support: [vercel.com/support](https://vercel.com/support)

## Quick Commands Reference

```bash
# Deploy preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm [deployment-url]

# Open project in browser
vercel open

# View environment variables
vercel env ls

# Pull environment variables locally
vercel env pull
```

---

**Ready to deploy?** Run `vercel --prod` from the verifycarrier directory!
