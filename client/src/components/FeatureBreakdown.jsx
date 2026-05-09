const FEATURE_LABELS = {
  url_length:        { label: 'URL length', unit: 'chars', threshold: 75, higher_is_bad: true },
  domain_length:     { label: 'Domain length', unit: 'chars', threshold: 20, higher_is_bad: true },
  num_dots:          { label: 'Dots in URL', unit: '', threshold: 4, higher_is_bad: true },
  num_hyphens:       { label: 'Hyphens in domain', unit: '', threshold: 1, higher_is_bad: true },
  num_subdomains:    { label: 'Subdomain count', unit: '', threshold: 2, higher_is_bad: true },
  has_ip:            { label: 'IP address as domain', unit: '', bool: true, flag_if_true: true },
  has_at:            { label: '@ symbol in URL', unit: '', bool: true, flag_if_true: true },
  has_https:         { label: 'HTTPS', unit: '', bool: true, flag_if_true: false },
  is_shortener:      { label: 'URL shortener', unit: '', bool: true, flag_if_true: true },
  suspicious_tld:    { label: 'Suspicious TLD', unit: '', bool: true, flag_if_true: true },
  has_brand_keyword: { label: 'Brand in domain', unit: '', bool: true, flag_if_true: true },
  path_depth:        { label: 'Path depth', unit: '', threshold: 4, higher_is_bad: true },
  has_query:         { label: 'Query string', unit: '', bool: true, flag_if_true: false },
  num_special_chars: { label: 'Special characters', unit: '', threshold: 3, higher_is_bad: true },
  has_double_slash:  { label: 'Double slash in path', unit: '', bool: true, flag_if_true: true },
};

export default function FeatureBreakdown({ features }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <button
        onClick={() => setExpanded(e => !e)}
        style={{
          width: '100%', display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', padding: '1rem 1.25rem',
          background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)',
        }}
      >
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, letterSpacing: '0.08em' }}>
          FEATURE BREAKDOWN ({Object.keys(features).length} features)
        </span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--text-dim)' }}>
          {expanded ? '[ collapse ]' : '[ expand ]'}
        </span>
      </button>

      {expanded && (
        <div style={{ borderTop: '1px solid var(--border)', padding: '0 1.25rem 1.25rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
            <thead>
              <tr>
                {['Feature', 'Value', 'Status'].map(h => (
                  <th key={h} style={{
                    textAlign: 'left', padding: '4px 8px',
                    fontFamily: 'var(--mono)', fontSize: 10,
                    color: 'var(--text-dim)', letterSpacing: '0.08em',
                    borderBottom: '1px solid var(--border)',
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(features).map(([key, value]) => {
                const meta = FEATURE_LABELS[key];
                if (!meta) return null;

                let status = 'neutral';
                if (meta.bool) {
                  if (meta.flag_if_true && value) status = 'bad';
                  else if (!meta.flag_if_true && value) status = 'good';
                  else if (!meta.flag_if_true && !value) status = 'bad';
                } else if (meta.higher_is_bad) {
                  status = value > meta.threshold ? 'bad' : 'good';
                }

                const statusColor = status === 'bad' ? 'var(--red)' : status === 'good' ? 'var(--green)' : 'var(--text-muted)';
                const statusText = status === 'bad' ? '!' : status === 'good' ? '✓' : '–';

                const displayVal = meta.bool
                  ? (value ? 'yes' : 'no')
                  : `${value}${meta.unit ? ' ' + meta.unit : ''}`;

                return (
                  <tr key={key} style={{ borderBottom: '1px solid rgba(30,42,30,0.5)' }}>
                    <td style={{ padding: '7px 8px', fontSize: 12, color: 'var(--text-muted)' }}>{meta.label}</td>
                    <td style={{ padding: '7px 8px', fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--text)' }}>{displayVal}</td>
                    <td style={{ padding: '7px 8px', fontFamily: 'var(--mono)', fontSize: 12, color: statusColor }}>{statusText}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import { useState } from 'react';
