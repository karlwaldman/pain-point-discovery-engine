'use client';

import { useState, useEffect, useRef } from 'react';

interface Broker {
  mc: string;
  name: string;
  city: string;
  state: string;
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [mcNumber, setMcNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [brokers, setBrokers] = useState<Broker[]>([]);
  const [filteredBrokers, setFilteredBrokers] = useState<Broker[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Load brokers data on mount
  useEffect(() => {
    fetch('/brokers.json')
      .then(res => res.json())
      .then(data => setBrokers(data))
      .catch(err => console.error('Failed to load brokers:', err));
  }, []);

  // Filter brokers as user types
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setFilteredBrokers([]);
      setShowSuggestions(false);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = brokers.filter(broker =>
      broker.mc.includes(query) ||
      broker.name.toLowerCase().includes(query) ||
      broker.city.toLowerCase().includes(query) ||
      broker.state.toLowerCase().includes(query)
    ).slice(0, 10); // Limit to 10 suggestions

    setFilteredBrokers(filtered);
    setShowSuggestions(filtered.length > 0);
    setSelectedIndex(-1);
  }, [searchQuery, brokers]);

  const handleSelectBroker = (broker: Broker) => {
    setSearchQuery(broker.name);
    setMcNumber(broker.mc);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev =>
        prev < filteredBrokers.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSelectBroker(filteredBrokers[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    const mcToVerify = mcNumber || searchQuery.replace(/\D/g, '');
    if (!mcToVerify.trim()) return;

    setLoading(true);
    setResult(null);
    setShowSuggestions(false);

    try {
      const response = await fetch(`/api/verify/${mcToVerify}`);
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: 'Failed to verify carrier. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <div className="trust-gradient text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="flex justify-center items-center gap-2 mb-6">
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <h1 className="text-5xl font-bold">VerifyCarrier</h1>
            </div>
            <p className="text-xl mb-4 text-blue-100">
              Protect Yourself from Freight Broker Fraud
            </p>
            <p className="text-lg mb-8 text-blue-200 max-w-3xl mx-auto">
              The first platform built for carriers to verify brokers before hauling a load. Instant broker verification using <strong>government databases and business intelligence</strong> — know before you haul.
            </p>

            {/* Trust Badges */}
            <div className="flex flex-wrap justify-center gap-6 mb-12">
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
                <svg className="w-5 h-5 text-success-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">Grade A+ Security</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
                <svg className="w-5 h-5 text-success-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">Multi-Source Verification</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
                <svg className="w-5 h-5 text-success-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">Built for Carriers</span>
              </div>
            </div>

            {/* Search Form */}
            <form onSubmit={handleVerify} className="max-w-2xl mx-auto">
              <div className="bg-white rounded-lg shadow-2xl p-6">
                <label htmlFor="broker-search" className="block text-left text-sm font-medium text-gray-700 mb-2">
                  Search by Company Name or MC Number
                </label>
                <div className="flex gap-3">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      id="broker-search"
                      value={searchQuery}
                      onChange={(e) => {
                        setSearchQuery(e.target.value);
                        setMcNumber('');
                      }}
                      onKeyDown={handleKeyDown}
                      onFocus={() => filteredBrokers.length > 0 && setShowSuggestions(true)}
                      placeholder="e.g., C.H. Robinson or 139867"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent text-gray-900 text-lg"
                      disabled={loading}
                      autoComplete="off"
                    />

                    {/* Autocomplete Dropdown */}
                    {showSuggestions && filteredBrokers.length > 0 && (
                      <div
                        ref={suggestionsRef}
                        className="absolute z-50 w-full mt-2 bg-white border border-gray-300 rounded-lg shadow-xl max-h-80 overflow-y-auto"
                      >
                        {filteredBrokers.map((broker, index) => (
                          <div
                            key={broker.mc}
                            onClick={() => handleSelectBroker(broker)}
                            className={`px-4 py-3 cursor-pointer border-b border-gray-100 hover:bg-primary-50 transition-colors ${
                              index === selectedIndex ? 'bg-primary-50' : ''
                            }`}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="font-semibold text-gray-900">{broker.name}</div>
                                <div className="text-sm text-gray-600 mt-1">
                                  {broker.city}, {broker.state}
                                </div>
                              </div>
                              <div className="ml-4 text-sm font-medium text-primary-700">
                                MC {broker.mc}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    type="submit"
                    disabled={loading || (!mcNumber.trim() && !searchQuery.trim())}
                    className="px-8 py-3 bg-success-600 text-white rounded-lg font-semibold hover:bg-success-700 focus:outline-none focus:ring-2 focus:ring-success-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
                  >
                    {loading ? 'Verifying...' : 'Verify Broker'}
                  </button>
                </div>
                {mcNumber && (
                  <p className="text-sm text-primary-700 mt-2 text-left font-medium">
                    ✓ Selected: MC {mcNumber}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-2 text-left">
                  Free instant verification • No credit card required • 3 checks per day
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {result.error ? (
            <div className="bg-danger-50 border-l-4 border-danger-500 p-6 rounded-lg">
              <div className="flex items-center gap-3">
                <svg className="w-6 h-6 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-danger-800 font-medium">{result.error}</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Header */}
              <div className="bg-white shadow-xl rounded-lg p-8 border border-gray-200">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">Verification Links for MC {result.mcNumber}</h2>
                    <p className="text-lg text-gray-600 mb-4">{result.message}</p>
                    {result.valueProp && (
                      <div className="bg-success-50 border-l-4 border-success-500 p-4 rounded">
                        <p className="text-success-800 font-medium">
                          ⏱️ Time Saved: {result.valueProp.timeSaved}
                        </p>
                        <p className="text-sm text-success-700 mt-1">
                          Without us: {result.valueProp.withoutUs} • With us: {result.valueProp.withUs}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Instructions */}
              {result.instructions && (
                <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-primary-900 mb-3">How to Verify This Broker:</h3>
                  <ol className="space-y-2 text-primary-800">
                    {result.instructions.map((instruction: string, idx: number) => (
                      <li key={idx} className="text-sm">{instruction}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Data Source Links */}
              {result.dataSourceLinks && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(result.dataSourceLinks).map(([key, source]: [string, any]) => (
                    <a
                      key={key}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-white border-2 border-gray-200 rounded-lg p-6 hover:border-primary-600 hover:shadow-lg transition-all group"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-700 rounded-full text-sm font-bold">
                            {source.priority}
                          </span>
                          <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">
                            {source.name}
                          </h3>
                        </div>
                        <svg className="w-5 h-5 text-gray-400 group-hover:text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{source.description}</p>
                      {source.note && (
                        <p className="text-xs text-warning-700 bg-warning-50 px-2 py-1 rounded inline-block">
                          ℹ️ {source.note}
                        </p>
                      )}
                    </a>
                  ))}
                </div>
              )}

              {/* Coming Soon Notice */}
              {result.nextPhase && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-primary-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Coming Soon: Automated Verification</h3>
                      <p className="text-sm text-gray-600">{result.nextPhase}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Beyond FMCSA: Multi-Source Broker Verification
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We don't just check one database. We verify brokers using <strong>multiple trusted data sources</strong> to protect you from fraud, payment defaults, and scams.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Government Databases</h3>
            <p className="text-gray-600">FMCSA SAFER, USDOT, court records, safety ratings, insurance verification, and more.</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-success-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment History</h3>
            <p className="text-gray-600">Days-to-pay averages, payment default reports, factoring data, credit ratings, bankruptcy filings.</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-danger-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Fraud Protection</h3>
            <p className="text-gray-600">Broker fraud database, identity theft alerts, double brokering detection, scam reports from carriers.</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-50 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Don't Haul for a Broker You Haven't Verified
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of owner-operators and small fleets protecting themselves from broker fraud, payment defaults, and scams.
          </p>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="px-8 py-4 bg-primary-950 text-white rounded-lg font-semibold hover:bg-primary-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors text-lg"
          >
            Verify a Broker Now
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-primary-950 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-blue-200 mb-4 md:mb-0">
              © 2025 VerifyCarrier. Protecting carriers from broker fraud. Grade A+ security. Multi-source verification.
            </p>
            <div className="flex gap-6 text-sm text-blue-200">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
