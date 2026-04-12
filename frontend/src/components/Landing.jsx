import { useState } from 'react';
import { ShieldCheck, BookOpen, ArrowRight, Zap, BarChart3, MessageSquare, Lock, CheckCircle } from 'lucide-react';

export default function Landing({ onNavigate }) {
  const [trackId, setTrackId] = useState('');

  const features = [
    { icon: '🤖', color: '#4f46e5', bg: 'rgba(79,70,229,0.1)', title: 'AI-Powered Triage', desc: 'Five specialized agents classify, prioritize, summarize, route, and analyze sentiment—automatically.' },
    { icon: '⚡', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', title: 'Instant Routing', desc: 'Complaints are routed to the exact department in milliseconds, not days.' },
    { icon: '🔍', color: '#10b981', bg: 'rgba(16,185,129,0.1)', title: 'Live Tracking', desc: 'Track your complaint\'s status in real-time with a full timeline and discussion thread.' },
    { icon: '📊', color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)', title: 'Admin Analytics', desc: 'Comprehensive dashboards give administrators full operational visibility.' },
    { icon: '💬', color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', title: 'Two-Way Chat', desc: 'Students and admins communicate directly within each complaint thread.' },
    { icon: '🔒', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', title: 'Secure & Private', desc: 'Restricted to @iiitranchi.ac.in emails with hashed credentials and PIN-gated admin access.' },
  ];

  return (
    <div>
      {/* ── Hero ────────────────────────────────── */}
      <div className="hero" style={{ padding: '6rem 2rem 2rem' }}>
        <div className="hero-eyebrow">
          <ShieldCheck size={14} />
          IIIT Ranchi — Official Complaint Portal
        </div>
        <h1>
          Campus Grievances,<br />
          <span className="gradient-text">Resolved by AI</span>
        </h1>
        <p>
          Submit, track and resolve campus complaints faster than ever. Our 5-agent AI pipeline classifies every issue and routes it to the right department — instantly.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={() => onNavigate('auth')}>
            <BookOpen size={18} /> Student Login
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('track-public')}>
            <Zap size={18} /> Track a Complaint
          </button>
        </div>
      </div>

      {/* ── Quick Track Bar ──────────────────────── */}
      <div className="page" style={{ paddingTop: 0 }}>
        <div className="glass" style={{ padding: '1.5rem 2rem', display: 'flex', gap: 12, alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Quick Track</p>
            <input
              placeholder="Enter your Tracking ID (e.g. CPS-A3F8E1-2026)"
              value={trackId}
              onChange={e => setTrackId(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && trackId && onNavigate('track-public', trackId)}
              style={{ marginBottom: 0 }}
            />
          </div>
          <button className="btn btn-primary" style={{ marginTop: 22, flexShrink: 0 }} onClick={() => trackId && onNavigate('track-public', trackId)}>
            <ArrowRight size={18} /> Track
          </button>
        </div>

        {/* ── Stats ────────────────────────────── */}
        <div className="stat-strip" style={{ marginTop: '2.5rem' }}>
          {[
            { value: '5-Agent', label: 'AI Pipeline' },
            { value: '< 3s', label: 'Avg. Triage Time' },
            { value: '6 Depts', label: 'Auto-Routed To' },
          ].map((s, i) => (
            <div key={i} className="glass stat-card">
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* ── Features ─────────────────────────── */}
        <div style={{ marginTop: '3rem' }}>
          <h2 className="section-title" style={{ textAlign: 'center' }}>Everything You Need</h2>
          <p className="section-sub" style={{ textAlign: 'center' }}>A complete AI-powered helpdesk platform built for IIIT Ranchi</p>
          <div className="features-grid">
            {features.map((f, i) => (
              <div key={i} className="glass feature-card" style={{ animationDelay: `${i * 0.08}s` }}>
                <div className="feature-icon" style={{ background: f.bg, color: f.color }}>{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── How It Works ─────────────────────── */}
        <div className="glass" style={{ padding: '2.5rem', marginTop: '2rem' }}>
          <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '0.4rem' }}>How It Works</h2>
          <p className="section-sub" style={{ textAlign: 'center' }}>Submit once. Our AI handles the rest.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
            {[
              { step: '01', title: 'Submit Complaint', desc: 'Describe your issue in plain language.' },
              { step: '02', title: 'AI Analysis', desc: '5 agents classify, prioritize, and route automatically.' },
              { step: '03', title: 'Department Notified', desc: 'The right team gets it instantly.' },
              { step: '04', title: 'Track & Resolve', desc: 'Follow progress with live updates.' },
            ].map((s, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{
                  width: 52, height: 52, borderRadius: '50%',
                  background: 'linear-gradient(135deg, #4f46e5, #8b5cf6)',
                  color: 'white', fontFamily: 'Outfit', fontWeight: 800, fontSize: '1rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 12px',
                  boxShadow: '0 4px 12px rgba(79,70,229,0.3)'
                }}>{s.step}</div>
                <h4 style={{ fontFamily: 'Outfit', fontWeight: 700, marginBottom: 6 }}>{s.title}</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── CTA ──────────────────────────────── */}
        <div style={{
          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
          borderRadius: 20, padding: '3rem 2rem', textAlign: 'center', marginTop: '2rem',
          boxShadow: '0 20px 40px rgba(79,70,229,0.25)'
        }}>
          <h2 style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.8rem', color: 'white', marginBottom: 12 }}>
            Got a campus issue?
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '1.5rem' }}>
            Log in with your IIIT Ranchi ID and our AI will handle the rest.
          </p>
          <button className="btn" style={{ background: 'white', color: '#4f46e5', fontWeight: 700 }} onClick={() => onNavigate('auth')}>
            <CheckCircle size={18} /> Submit a Complaint
          </button>
        </div>

        <div style={{ textAlign: 'center', padding: '2rem 0 1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Campus Duvidha Solver · IIIT Ranchi · AI-Powered Complaint Management
        </div>
      </div>
    </div>
  );
}
