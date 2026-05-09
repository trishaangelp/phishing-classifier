import { useState } from 'react';

export default function URLInput({ onSubmit, loading }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) onSubmit(url.trim());
  };

  const examples = [
    'https://www.google.com',
    'http://paypa1-secure.xyz/login',
    'http://192.168.1.1/update-account',
  ];

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 10 }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <span style={{
            position: 'absolute', left: 14, top: '50%',
            transform: 'translateY(-50%)',
            fontFamily: 'var(--mono)', fontSize: 13,
            color: 'var(--green-dim)', userSelect: 'none',
          }}>$</span>
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="enter url to analyze..."
            style={{
              width: '100%',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-active)',
              borderRadius: 'var(--radius)',
              padding: '12px 14px 12px 28px',
              fontFamily: 'var(--mono)',
              fontSize: 13,
              color: 'var(--text)',
              outline: 'none',
              letterSpacing: '0.02em',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--green-dim)'}
            onBlur={e => e.target.style.borderColor = 'var(--border-active)'}
            autoComplete="off"
            spellCheck="false"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading || !url.trim()}>
          {loading ? (
            <span style={{ animation: 'pulse-green 1s infinite' }}>analyzing...</span>
          ) : 'analyze →'}
        </button>
      </form>

      <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--text-dim)' }}>try:</span>
        {examples.map(ex => (
          <button
            key={ex}
            onClick={() => { setUrl(ex); onSubmit(ex); }}
            style={{
              background: 'none',
              border: '1px solid var(--border)',
              borderRadius: 3,
              padding: '3px 10px',
              fontFamily: 'var(--mono)',
              fontSize: 11,
              color: 'var(--text-muted)',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.target.style.borderColor = 'var(--text-muted)'; e.target.style.color = 'var(--text)'; }}
            onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--text-muted)'; }}
          >
            {ex.length > 38 ? ex.slice(0, 38) + '…' : ex}
          </button>
        ))}
      </div>
    </div>
  );
}
