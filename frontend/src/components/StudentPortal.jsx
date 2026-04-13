import { useState, useEffect } from 'react';
import { submitComplaint, getMyComplaints, playSuccessSound } from '../utils/api';
import {
    Send, FileText, CheckCircle2, Search, ExternalLink,
    Sparkles, Clock, AlertCircle, ChevronRight, Loader2,
    BookOpen, Zap, MessageSquare, BarChart2, User
} from 'lucide-react';

const STATUS_META = {
    'Submitted':   { color: '#4f46e5', bg: 'rgba(79,70,229,0.1)',  label: 'Submitted' },
    'In Progress': { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', label: 'In Progress' },
    'Resolved':    { color: '#10b981', bg: 'rgba(16,185,129,0.1)', label: 'Resolved' },
};
const PRIORITY_META = {
    'Low':    { color: '#3b82f6' },
    'Medium': { color: '#f59e0b' },
    'High':   { color: '#f97316' },
    'Urgent': { color: '#ef4444' },
};

const CATEGORY_ICONS = {
    'Infrastructure': '🏗️', 'Academic': '📚', 'Hostel & Mess': '🏠',
    'Anti-Ragging': '🛡️', 'Administration': '📋', 'IT & Network': '💻',
    'Needs Manual Review': '🔍',
};

export default function StudentPortal({ user, onNavigate }) {
    const [tab, setTab] = useState('submit');
    const [desc, setDesc] = useState('');
    const [charCount, setCharCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null); // full API response after submit
    const [complaints, setComplaints] = useState([]);
    const [listLoading, setListLoading] = useState(false);
    const [error, setError] = useState('');

    const username = user.split('@')[0];

    useEffect(() => {
        if (tab === 'list') {
            setListLoading(true);
            getMyComplaints(user)
                .then(res => setComplaints(res.data || []))
                .catch(console.error)
                .finally(() => setListLoading(false));
        }
    }, [tab, user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (desc.trim().length < 20) { setError('Please describe your issue in at least 20 characters.'); return; }
        setError('');
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('email', user);
            formData.append('student_name', username);
            formData.append('description', desc);
            const res = await submitComplaint(formData);
            playSuccessSound();
            setResult(res);
            setDesc('');
            setCharCount(0);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const resolvedCount = complaints.filter(c => c.status === 'Resolved').length;
    const pendingCount  = complaints.filter(c => c.status !== 'Resolved').length;

    return (
        <div className="page animate-in">

            {/* ── Welcome Header ──────────────────────── */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: 16 }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                        <div style={{
                            width: 44, height: 44, borderRadius: 12,
                            background: 'linear-gradient(135deg, #4f46e5, #8b5cf6)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 4px 12px rgba(79,70,229,0.3)'
                        }}>
                            <User size={20} color="white" />
                        </div>
                        <div>
                            <h1 style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.8rem', lineHeight: 1.2 }}>
                                Hey, {username}! 👋
                            </h1>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>{user}</p>
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                {complaints.length > 0 && (
                    <div style={{ display: 'flex', gap: 10 }}>
                        {[
                            { label: 'Total', value: complaints.length, color: '#4f46e5' },
                            { label: 'Resolved', value: resolvedCount, color: '#10b981' },
                            { label: 'Pending', value: pendingCount, color: '#f59e0b' },
                        ].map((s, i) => (
                            <div key={i} className="glass" style={{ padding: '10px 18px', textAlign: 'center', minWidth: 70 }}>
                                <div style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.5rem', color: s.color }}>{s.value}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>{s.label}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ── Tab Bar ─────────────────────────────── */}
            <div className="tab-bar" style={{ marginBottom: '2rem' }}>
                <button className={`tab-btn ${tab === 'submit' ? 'active' : ''}`} onClick={() => { setTab('submit'); setResult(null); }}>
                    <Send size={15} /> New Complaint
                </button>
                <button className={`tab-btn ${tab === 'list' ? 'active' : ''}`} onClick={() => setTab('list')}>
                    <FileText size={15} /> My Complaints {complaints.length > 0 && `(${complaints.length})`}
                </button>
            </div>

            {/* ══════════════════════════════════════════
                TAB: SUBMIT
            ══════════════════════════════════════════ */}
            {tab === 'submit' && !result && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>

                    {/* Main Form */}
                    <div className="glass" style={{ padding: '2rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(79,70,229,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Sparkles size={18} color="#4f46e5" />
                            </div>
                            <div>
                                <h2 style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '1.2rem' }}>Submit a Complaint</h2>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>Our AI will analyze and route it instantly</p>
                            </div>
                        </div>

                        {error && <div className="alert alert-error"><AlertCircle size={15}/> {error}</div>}

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label">Describe your issue</label>
                                <textarea
                                    rows={7}
                                    placeholder="Be specific — mention the location, date, and nature of the problem. For example: 'The internet in Block C Room 214 has been down since Monday morning...'"
                                    value={desc}
                                    onChange={e => { setDesc(e.target.value); setCharCount(e.target.value.length); }}
                                    required
                                    style={{ resize: 'none' }}
                                />
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
                                    <span style={{ fontSize: '0.78rem', color: charCount < 20 ? 'var(--danger)' : 'var(--text-muted)' }}>
                                        {charCount < 20 ? `${20 - charCount} more characters needed` : '✓ Good length'}
                                    </span>
                                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{charCount} chars</span>
                                </div>
                            </div>

                            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                                {loading
                                    ? <><Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }}/> AI is processing your complaint...</>
                                    : <><Send size={18}/> Submit to AI Engine</>
                                }
                            </button>
                        </form>

                        {loading && (
                            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(79,70,229,0.05)', borderRadius: 12, border: '1px solid rgba(79,70,229,0.1)' }}>
                                <p style={{ color: 'var(--primary)', fontWeight: 600, marginBottom: 8, fontSize: '0.9rem' }}>🤖 AI Pipeline Running...</p>
                                {['Classifying category', 'Assessing priority', 'Generating summary', 'Routing to department', 'Analyzing sentiment'].map((step, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--primary)', animation: 'pulse 1.5s ease infinite', animationDelay: `${i*0.2}s` }}/>
                                        {step}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Side Panel */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div className="glass" style={{ padding: '1.5rem' }}>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                                <Zap size={16} color="#f59e0b" /> What happens next?
                            </h3>
                            {[
                                { icon: '🤖', title: 'AI Triage', desc: 'Your complaint is classified into the right category.' },
                                { icon: '⚡', title: 'Priority Set', desc: 'Urgency is assessed automatically.' },
                                { icon: '🏢', title: 'Routed', desc: 'Sent to the exact department responsible.' },
                                { icon: '📡', title: 'Tracked', desc: 'You receive a Tracking ID for live updates.' },
                            ].map((s, i) => (
                                <div key={i} style={{ display: 'flex', gap: 12, marginBottom: 14, alignItems: 'flex-start' }}>
                                    <span style={{ fontSize: '1.2rem', flexShrink: 0 }}>{s.icon}</span>
                                    <div>
                                        <p style={{ fontWeight: 600, fontSize: '0.88rem', marginBottom: 2 }}>{s.title}</p>
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{s.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="glass" style={{ padding: '1.5rem' }}>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.8rem', color: 'var(--text-secondary)' }}>
                                📋 Issue Categories
                            </h3>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                {Object.entries(CATEGORY_ICONS).filter(([k]) => k !== 'Needs Manual Review').map(([cat, icon]) => (
                                    <span key={cat} style={{ background: 'rgba(79,70,229,0.07)', color: 'var(--primary)', padding: '4px 10px', borderRadius: 20, fontSize: '0.75rem', fontWeight: 500 }}>
                                        {icon} {cat}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* ══════════════════════════════════════════
                SUCCESS STATE
            ══════════════════════════════════════════ */}
            {tab === 'submit' && result && (
                <div className="animate-in">
                    {/* Big success card */}
                    <div style={{
                        background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
                        borderRadius: 20, padding: '2.5rem', textAlign: 'center',
                        color: 'white', marginBottom: '1.5rem',
                        boxShadow: '0 20px 40px rgba(16,185,129,0.25)'
                    }}>
                        <CheckCircle2 size={64} style={{ marginBottom: 16, filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))' }} />
                        <h2 style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.8rem', marginBottom: 8 }}>Complaint Submitted!</h2>
                        <p style={{ color: 'rgba(255,255,255,0.85)', marginBottom: 20 }}>Your issue has been analyzed and routed. Save your Tracking ID:</p>
                        <div style={{
                            background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(8px)',
                            borderRadius: 12, padding: '1rem 2rem', display: 'inline-block', marginBottom: 20
                        }}>
                            <div style={{ fontSize: '2.2rem', fontWeight: 900, fontFamily: 'Outfit', letterSpacing: 3 }}>
                                {result.tracking_id}
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <button className="btn" style={{ background: 'white', color: '#059669', fontWeight: 700 }}
                                onClick={() => onNavigate('track-public', result.tracking_id)}>
                                <Search size={18}/> Track Live Status
                            </button>
                            <button className="btn" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.3)' }}
                                onClick={() => setResult(null)}>
                                Submit Another
                            </button>
                        </div>
                    </div>

                    {/* AI Analysis Results */}
                    {result.ai_analysis && (
                        <div>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '1.2rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                                🤖 AI Analysis Results
                            </h3>
                            <div className="card-grid-2" style={{ gap: '1rem' }}>
                                {[
                                    {
                                        icon: '🏷️', label: 'Category',
                                        value: result.ai_analysis.category,
                                        sub: `${Math.round((result.ai_analysis.confidence || 0) * 100)}% confidence`,
                                        color: '#4f46e5'
                                    },
                                    {
                                        icon: '⚡', label: 'Priority',
                                        value: result.ai_analysis.priority,
                                        sub: result.ai_analysis.priority_reason,
                                        color: PRIORITY_META[result.ai_analysis.priority]?.color || '#64748b'
                                    },
                                    {
                                        icon: '🏢', label: 'Routed To',
                                        value: result.ai_analysis.department,
                                        sub: 'Department notified',
                                        color: '#10b981'
                                    },
                                    {
                                        icon: '💭', label: 'Sentiment',
                                        value: result.ai_analysis.sentiment,
                                        sub: result.ai_analysis.flagged ? '⚠ Flagged for urgent attention' : '✓ No flags raised',
                                        color: result.ai_analysis.flagged ? '#ef4444' : '#10b981'
                                    },
                                ].map((item, i) => (
                                    <div key={i} className="glass" style={{ padding: '1.2rem 1.5rem', borderLeft: `4px solid ${item.color}`, display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                                        <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>{item.icon}</span>
                                        <div>
                                            <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>{item.label}</p>
                                            <p style={{ fontFamily: 'Outfit', fontWeight: 700, fontSize: '1.05rem', color: item.color, marginBottom: 3 }}>{item.value}</p>
                                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', lineHeight: 1.4 }}>{item.sub}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* ══════════════════════════════════════════
                TAB: MY COMPLAINTS
            ══════════════════════════════════════════ */}
            {tab === 'list' && (
                <div>
                    {listLoading && (
                        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                            <Loader2 size={32} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 12px', display: 'block' }}/>
                            Loading your complaints...
                        </div>
                    )}

                    {!listLoading && complaints.length === 0 && (
                        <div className="glass empty-state">
                            <BookOpen size={48} style={{ display: 'block', margin: '0 auto 12px', color: 'var(--text-muted)' }} />
                            <p style={{ marginBottom: 16 }}>You haven't submitted any complaints yet.</p>
                            <button className="btn btn-primary" onClick={() => setTab('submit')}>
                                <Send size={16}/> Submit Your First Complaint
                            </button>
                        </div>
                    )}

                    {!listLoading && complaints.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {complaints.map((c) => {
                                const sm = STATUS_META[c.status] || STATUS_META['Submitted'];
                                const pm = PRIORITY_META[c.priority] || { color: '#64748b' };
                                const catIcon = CATEGORY_ICONS[c.category] || '📋';
                                return (
                                    <div key={c.id} className="glass" style={{
                                        padding: '1.5rem 2rem',
                                        borderLeft: `5px solid ${sm.color}`,
                                        display: 'flex', flexDirection: 'column', gap: 12,
                                        cursor: 'pointer',
                                        transition: 'transform 0.2s, box-shadow 0.2s'
                                    }}
                                        onMouseEnter={e => e.currentTarget.style.transform = 'translateX(4px)'}
                                        onMouseLeave={e => e.currentTarget.style.transform = 'translateX(0)'}
                                    >
                                        {/* Top Row */}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                <span style={{ fontSize: '1.4rem' }}>{catIcon}</span>
                                                <div>
                                                    <h3 style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.05rem', color: '#4f46e5' }}>{c.tracking_id}</h3>
                                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                                                        {new Date(c.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                                                    </p>
                                                </div>
                                            </div>
                                            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
                                                <span style={{
                                                    background: sm.bg, color: sm.color,
                                                    padding: '4px 12px', borderRadius: 20,
                                                    fontSize: '0.75rem', fontWeight: 700,
                                                    fontFamily: 'Outfit', textTransform: 'uppercase', letterSpacing: '0.5px'
                                                }}>{sm.label}</span>
                                                {c.priority && (
                                                    <span style={{
                                                        background: `${pm.color}15`, color: pm.color,
                                                        padding: '4px 10px', borderRadius: 20,
                                                        fontSize: '0.72rem', fontWeight: 700, fontFamily: 'Outfit'
                                                    }}>{c.priority}</span>
                                                )}
                                                {c.flagged === 1 && (
                                                    <span style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', padding: '4px 10px', borderRadius: 20, fontSize: '0.72rem', fontWeight: 700 }}>⚠ Flagged</span>
                                                )}
                                            </div>
                                        </div>

                                        {/* Summary */}
                                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.93rem', lineHeight: 1.6 }}>
                                            {c.summary || c.description?.substring(0, 120) + (c.description?.length > 120 ? '...' : '')}
                                        </p>

                                        {/* Footer */}
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div style={{ display: 'flex', gap: 16, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                                                {c.department && <span>🏢 {c.department}</span>}
                                                {c.category && <span>📂 {c.category}</span>}
                                            </div>
                                            <button
                                                className="btn btn-secondary btn-sm"
                                                onClick={() => onNavigate('track-public', c.tracking_id)}
                                            >
                                                View Details <ChevronRight size={14}/>
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
