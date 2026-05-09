export default function ResultCard({ result }) {
  const { prediction, is_phishing, confidence, risk_score, url, top_reasons } = result;

  const accent = is_phishing ? 'var(--red)' : 'var(--green)';
  const accentPale = is_phishing ? 'var(--red-pale)' : 'var(--green-pale)';
  const accentMuted = is_phishing ? 'var(--red-muted)' : 'var(--green-muted)';

  const barColor = risk_score > 70 ? 'var(--red-dim)' : risk_score > 40 ? 'var(--amber)' : 'var(--green-dim)';

  return (
    <div className="card animate-in" style={{ padding: '1.5rem', borderColor: is_phishing ? 'var(--red-muted)' : 'var(--green-muted)' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <span className={`tag ${is_phishing ? 'tag-phishing' : 'tag-safe'}`}>
              {is_phishing ? '⚠ phishing detected' : '✓ legitimate'}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--text-muted)' }}>
              {(confidence * 100).toFixed(1)}% confidence
            </span>
          </div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--text-muted)', wordBreak: 'break-all' }}>
            {url.length > 60 ? url.slice(0, 60) + '…' : url}
          </p>
        </div>

        {/* Risk score circle */}
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          border: `2px solid ${accent}`,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: accentPale, flexShrink: 0, marginLeft: 16,
        }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 500, color: accent, lineHeight: 1 }}>
            {risk_score}
          </span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: accent, opacity: 0.7, letterSpacing: '0.05em' }}>RISK</span>
        </div>
      </div>

      {/* Risk bar */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.08em' }}>RISK SCORE</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-muted)' }}>0 — 100</span>
        </div>
        <div style={{ height: 6, background: 'var(--bg)', borderRadius: 3, overflow: 'hidden', border: '1px solid var(--border)' }}>
          <div style={{
            height: '100%', width: `${risk_score}%`,
            background: barColor, borderRadius: 3,
            transition: 'width 0.6s ease',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--green-dim)' }}>SAFE</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--amber)' }}>SUSPICIOUS</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--red-dim)' }}>PHISHING</span>
        </div>
      </div>

      {/* Reasons */}
      {top_reasons.length > 0 && (
        <div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.08em', marginBottom: 8 }}>
            {is_phishing ? 'THREAT INDICATORS' : 'TRUST SIGNALS'}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {top_reasons.map((reason, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '8px 12px',
                background: accentPale,
                borderRadius: 'var(--radius)',
                border: `1px solid ${accentMuted}`,
              }}>
                <span style={{ color: accent, fontFamily: 'var(--mono)', fontSize: 12, flexShrink: 0 }}>
                  {is_phishing ? '!' : '✓'}
                </span>
                <span style={{ fontSize: 13, color: 'var(--text)' }}>{reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
