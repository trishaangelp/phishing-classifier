import { useState } from 'react';
import api from './api/axios';
import URLInput from './components/URLInput';
import ResultCard from './components/ResultCard';
import FeatureBreakdown from './components/FeatureBreakdown';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);

  const classify = async (url) => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.post('/classify', { url });
      setResult(res.data);
      setHistory(h => [res.data, ...h].slice(0, 5));
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to connect to API. Is the server running?';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 740, margin: '0 auto', padding: '2.5rem 1.5rem' }}>

      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <div style={{
            width: 10, height: 10, borderRadius: '50%',
            background: 'var(--green)', boxShadow: '0 0 8px var(--green)',
            animation: 'pulse-green 2s infinite',
          }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-dim)', letterSpacing: '0.1em' }}>
            PHISHING CLASSIFIER v1.0 — MODEL ONLINE
          </span>
        </div>
        <h1 style={{
          fontFamily: 'var(--mono)', fontSize: '1.8rem',
          fontWeight: 400, color: 'var(--text)', letterSpacing: '-0.01em',
        }}>
          <span style={{ color: 'var(--green)' }}>{'>'}</span> url threat analyzer
        </h1>
        <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 13 }}>
          XGBoost · SHAP explainability · 15 phishing indicators
        </p>
      </div>

      {/* Input */}
      <div style={{ marginBottom: '1.5rem' }}>
        <URLInput onSubmit={classify} loading={loading} />
      </div>

      {/* Error */}
      {error && (
        <div className="card animate-in" style={{
          padding: '1rem 1.25rem', marginBottom: '1.5rem',
          borderColor: 'var(--red-muted)', background: 'var(--red-pale)',
        }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--red)' }}>
            error: {error}
          </span>
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          <ResultCard result={result} />
          <FeatureBreakdown features={result.features} />
        </div>
      )}

      {/* History */}
      {history.length > 1 && (
        <div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.08em', marginBottom: 10 }}>
            RECENT SCANS
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {history.slice(1).map((h, i) => (
              <div
                key={i}
                className="card"
                onClick={() => setResult(h)}
                style={{
                  padding: '10px 14px', cursor: 'pointer',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  transition: 'border-color 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-active)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {h.url.length > 55 ? h.url.slice(0, 55) + '…' : h.url}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0, marginLeft: 12 }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                    {h.risk_score}/100
                  </span>
                  <span className={`tag ${h.is_phishing ? 'tag-phishing' : 'tag-safe'}`} style={{ fontSize: 10 }}>
                    {h.is_phishing ? 'phishing' : 'safe'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
        <p style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-dim)', lineHeight: 1.7 }}>
          trained on UCI phishing dataset · ~96% accuracy · not a replacement for professional security tools
        </p>
      </div>
    </div>
  );
}
