import { useState } from 'react';
import { trackComplaint, postComment } from '../utils/api';
import { Search, Clock, Brain, MessageSquare, FileText, AlertTriangle, CheckCircle2, Download } from 'lucide-react';

const STATUS_COLORS = { 'Submitted': '#4f46e5', 'In Progress': '#f59e0b', 'Resolved': '#10b981' };

export default function Tracking({ initialTrackingId }) {
    const [id, setId] = useState(initialTrackingId || '');
    const [data, setData] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(!!initialTrackingId);
    const [comment, setComment] = useState('');
    const [posting, setPosting] = useState(false);
    const [tab, setTab] = useState('timeline');

    const handleSearch = async (searchId) => {
        const target = searchId || id;
        if (!target.trim()) return;
        setLoading(true);
        setError('');
        setData(null);
        try {
            const res = await trackComplaint(target.trim().toUpperCase());
            setData(res);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Auto-search when initialTrackingId is set
    useState(() => { if (initialTrackingId) handleSearch(initialTrackingId); }, []);

    const handleComment = async (e) => {
        e.preventDefault();
        if (!comment.trim()) return;
        setPosting(true);
        try {
            await postComment(data.problem.id, comment, 'Student');
            setComment('');
            handleSearch(data.problem.tracking_id);
        } catch(err) {
            alert(err.message);
        } finally {
            setPosting(false);
        }
    };

    const generateTranscript = () => {
        if (!data) return;
        const p = data.problem;
        const text = `CAMPUS DUVIDHA SOLVER — OFFICIAL COMPLAINT TRANSCRIPT
======================================================
Tracking ID   : ${p.tracking_id}
Student       : ${p.student_name} (${p.student_email})
Submitted     : ${new Date(p.created_at).toLocaleString()}
Status        : ${p.status}
Department    : ${p.department}
Priority      : ${p.priority}
Category      : ${p.category}
Flagged       : ${p.flagged ? 'YES' : 'NO'}

DESCRIPTION
-----------
${p.description}

AI SUMMARY
----------
${p.summary}

PRIORITY REASON
---------------
${p.priority_reason}

ROUTING REASON
--------------
${p.routing_reason}
======================================================`;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href = url; a.download = `Transcript_${p.tracking_id}.txt`; a.click();
    };

    const stColor = data ? (STATUS_COLORS[data.problem.status] || '#64748b') : '#64748b';

    return (
        <div className="page animate-in">
            <div style={{ marginBottom: '2rem' }}>
                <h1 className="section-title">🔍 Track Your Complaint</h1>
                <p className="section-sub">Enter your Tracking ID to see real-time status, full timeline, and AI analysis.</p>
            </div>

            {/* Search Bar */}
            <div className="glass" style={{ padding: '1.5rem', marginBottom: '2rem', display: 'flex', gap: 12 }}>
                <input
                    placeholder="Enter Tracking ID (e.g. CPS-A3F8E1-2026)"
                    value={id}
                    onChange={e => setId(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSearch()}
                    style={{ marginBottom: 0, flex: 1 }}
                />
                <button className="btn btn-primary" onClick={() => handleSearch()} disabled={loading} style={{ flexShrink: 0 }}>
                    {loading ? <div className="spinner" /> : <><Search size={18} /> Search</>}
                </button>
            </div>

            {error && <div className="alert alert-error"><AlertTriangle size={16} /> {error}</div>}

            {!data && !loading && (
                <div className="glass empty-state">
                    <Search size={48} style={{ display: 'block', margin: '0 auto 16px', color: 'var(--text-muted)' }} />
                    <p>Enter a tracking ID above to view your complaint details, timeline, and AI analysis.</p>
                </div>
            )}

            {data && (
                <div className="animate-in">
                    {/* Header */}
                    <div className="glass" style={{ padding: '2rem', borderLeft: `5px solid ${stColor}`, marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 16 }}>
                            <div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 8 }}>
                                    <h2 style={{ fontFamily: 'Outfit', fontWeight: 900, fontSize: '1.8rem', color: '#4f46e5' }}>{data.problem.tracking_id}</h2>
                                    <span className={`badge badge-${data.problem.status === 'Resolved' ? 'resolved' : data.problem.status === 'In Progress' ? 'progress' : 'submitted'}`}>
                                        {data.problem.status}
                                    </span>
                                    <span className={`badge badge-${data.problem.priority === 'Urgent' ? 'urgent' : 'submitted'}`}>{data.problem.priority}</span>
                                    {data.problem.flagged === 1 && <span className="badge badge-flagged">⚠ Flagged</span>}
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    Submitted by <strong>{data.problem.student_name}</strong> · {new Date(data.problem.created_at).toLocaleString()}
                                </p>
                            </div>
                            <button className="btn btn-ghost btn-sm" onClick={generateTranscript}>
                                <Download size={16} /> Download Transcript
                            </button>
                        </div>
                        <p style={{ fontSize: '1.1rem', color: 'var(--text)', lineHeight: 1.6 }}>{data.problem.summary}</p>
                        <div style={{ marginTop: 16, display: 'flex', gap: 12, flexWrap: 'wrap', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                            <span>📂 {data.problem.category}</span>
                            <span>🏢 {data.problem.department}</span>
                            <span>💭 {data.problem.sentiment}</span>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="tab-bar">
                        {[
                            { key: 'timeline', label: 'Timeline', icon: <Clock size={15}/> },
                            { key: 'analysis', label: 'AI Analysis', icon: <Brain size={15}/> },
                            { key: 'discuss', label: `Discussion (${data.comments.length})`, icon: <MessageSquare size={15}/> },
                            { key: 'original', label: 'Original', icon: <FileText size={15}/> },
                        ].map(t => (
                            <button key={t.key} className={`tab-btn ${tab === t.key ? 'active' : ''}`} onClick={() => setTab(t.key)}>
                                {t.icon} {t.label}
                            </button>
                        ))}
                    </div>

                    {/* Tab: Timeline */}
                    {tab === 'timeline' && (
                        <div className="glass" style={{ padding: '2rem' }}>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, marginBottom: '1.5rem' }}>📜 Status Timeline</h3>
                            {data.timeline.length === 0 ? (
                                <div className="empty-state"><p>No status changes recorded yet.</p></div>
                            ) : (
                                <div className="timeline">
                                    {data.timeline.map((log, i) => (
                                        <div key={i} className="timeline-item">
                                            <div className="timeline-card">
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                        <span style={{ color: 'var(--text-secondary)' }}>{log.old_status || '—'}</span>
                                                        <span style={{ color: '#10b981', fontWeight: 700 }}>→</span>
                                                        <span className={`badge badge-${log.new_status === 'Resolved' ? 'resolved' : log.new_status === 'In Progress' ? 'progress' : 'submitted'}`}>{log.new_status}</span>
                                                    </div>
                                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{new Date(log.changed_at).toLocaleString()}</span>
                                                </div>
                                                <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: 6 }}>Changed by {log.changed_by}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Tab: AI Analysis */}
                    {tab === 'analysis' && (
                        <div className="card-grid-2">
                            {[
                                { label: '🏷 Category', value: data.problem.category, sub: `Confidence: ${Math.round((data.problem.confidence || 0) * 100)}%`, color: '#4f46e5' },
                                { label: '⚡ Priority', value: data.problem.priority, sub: data.problem.priority_reason, color: '#f59e0b' },
                                { label: '🏢 Department', value: data.problem.department, sub: data.problem.routing_reason, color: '#10b981' },
                                { label: '💭 Sentiment', value: data.problem.sentiment, sub: data.problem.flagged ? '⚠ Flagged for immediate attention' : '✓ No flags raised', color: data.problem.flagged ? '#ef4444' : '#10b981' },
                            ].map((item, i) => (
                                <div key={i} className="glass card" style={{ borderLeft: `4px solid ${item.color}` }}>
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, marginBottom: 6 }}>{item.label}</p>
                                    <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'Outfit', color: item.color, marginBottom: 4 }}>{item.value}</p>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.87rem', lineHeight: 1.5 }}>{item.sub}</p>
                                    {item.label.includes('Confidence') && (
                                        <div className="progress-bar"><div className="progress-fill" style={{ width: `${Math.round((data.problem.confidence||0)*100)}%`, background: item.color }} /></div>
                                    )}
                                </div>
                            ))}
                            {data.problem.used_fallback && (
                                <div className="glass card" style={{ gridColumn: '1 / -1', borderLeft: '4px solid #f59e0b' }}>
                                    <p style={{ color: '#d97706', fontWeight: 600 }}>⚠ Fallback Mode Used</p>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: 4 }}>AI agents were unavailable; keyword-based heuristics were used. Set an OpenAI API key for full intelligence.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Tab: Discussion */}
                    {tab === 'discuss' && (
                        <div className="glass" style={{ padding: '2rem' }}>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, marginBottom: '1.5rem' }}>💬 Discussion Thread</h3>
                            {data.comments.length === 0 && (
                                <div className="empty-state" style={{ padding: '2rem' }}><p>No messages yet. Be the first to add a note below.</p></div>
                            )}
                            {data.comments.map((c, i) => (
                                <div key={i} className={`comment comment-${c.posted_by === 'Student' ? 'student' : 'admin'}`}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                        <strong style={{ color: c.posted_by === 'Student' ? '#3b82f6' : '#10b981' }}>{c.posted_by}</strong>
                                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(c.posted_at).toLocaleString()}</span>
                                    </div>
                                    <p style={{ color: 'var(--text)', lineHeight: 1.6 }}>{c.comment}</p>
                                </div>
                            ))}
                            <hr className="divider" />
                            <form onSubmit={handleComment} style={{ display: 'flex', gap: 12, marginTop: '1rem' }}>
                                <input
                                    placeholder="Add a reply or provide extra details..."
                                    value={comment}
                                    onChange={e => setComment(e.target.value)}
                                    style={{ flex: 1, marginBottom: 0 }}
                                    required
                                />
                                <button type="submit" className="btn btn-primary" disabled={posting} style={{ flexShrink: 0 }}>
                                    {posting ? <div className="spinner" /> : 'Post Reply'}
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Tab: Original */}
                    {tab === 'original' && (
                        <div className="glass" style={{ padding: '2rem' }}>
                            <h3 style={{ fontFamily: 'Outfit', fontWeight: 700, marginBottom: '1.5rem' }}>📄 Original Complaint</h3>
                            <div style={{ background: 'rgba(248,250,252,0.8)', border: '1px solid rgba(0,0,0,0.06)', borderRadius: 12, padding: '1.5rem', lineHeight: 1.8, color: 'var(--text)', whiteSpace: 'pre-wrap', fontSize: '0.97rem' }}>
                                {data.problem.description}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
