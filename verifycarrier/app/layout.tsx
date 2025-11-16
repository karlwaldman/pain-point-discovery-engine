import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VerifyCarrier - Verify Freight Brokers | Protect Yourself from Broker Fraud",
  description: "The first platform for carriers to verify brokers before hauling. Instant verification using FMCSA and business intelligence. Prevent fraud, payment defaults, and scams. Built for owner-operators.",
  keywords: "verify freight broker, broker verification, check broker MC number, freight broker fraud, broker scam, payment default, double brokering, carrier protection, owner operator tools, broker legitimacy check, FMCSA broker lookup, freight broker reviews",
  authors: [{ name: "VerifyCarrier" }],
  openGraph: {
    title: "VerifyCarrier - Verify Freight Brokers Before You Haul",
    description: "Protect yourself from broker fraud, payment defaults, and scams. Instant broker verification built for carriers. Know before you haul.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "VerifyCarrier - Verify Freight Brokers Instantly",
    description: "Protect yourself from broker fraud. Built for owner-operators. Multi-source verification. Know before you haul.",
  },
  robots: {
    index: true,
    follow: true,
  },
  verification: {
    // Add Google verification when ready
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Trust signals */}
        <link rel="icon" href="/favicon.ico" />
        <meta name="theme-color" content="#0A2540" />
        {/* Security meta tags */}
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
