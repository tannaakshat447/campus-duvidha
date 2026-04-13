import { useState, useEffect } from 'react';
import { getAdminComplaints, updateStatus, getAnalytics, postComment, trackComplaint } from '../utils/api';
import {
    LayoutDashboard, PieChart, Users, ShieldAlert, CheckCircle2,
    Clock, Search, MessageSquare, Brain, ArrowUpRight,
    Filter, RefreshCw, ChevronDown, ChevronUp, AlertCircle,
    Building2, Activity, Tag, Flag
} from 'lucide-react';

const PRIORITY_META = {
    'Urgent': { color: '#ef4444', label: 'Urgent' },
    'High':   { color: '#f97316', label: 'High' },
    'Medium': { color: '#f59e0b', label: 'Medium' },
    'Low':    { color: '#3b82f6', label: 'Low' },
};

const STATUS_META = {
    'Submitted':   { color: '#4f46e5', bg: 'rgba(79,70,229,0.1)' },
    'In Progress': { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)' },
    'Resolved':    { color: '#10b981', bg: 'rgba(16,185,129,0.1)' },
};

export default function AdminDash() {
    const [tab, setTab] = useState('tickets');
    const [complaints, setComplaints] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedTicket, setExpandedTicket] = useState(null);
    const [ticketDetails, setTicketDetails] = useState(null);
    const [commentText, setCommentText] = useState({});
    const [postingComment, setPostingComment] = useState(null);

    useEffect(() => {
        loadData();
    }, [tab]);

    const loadData = async () => {
        setLoading(true);
        try {
            if (tab === 'tickets') {
                const res = await getAdminComplaints();
                setComplaints(res.data || []);
            } else {
                const res = await getAnalytics();
                setStats(res);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleExpandTicket = async (id, tracking_id) => {
        if (expandedTicket === id) {
            setExpandedTicket(null);
            setTicketDetails(null);
            return;
        }
        setExpandedTicket(id);
        try {
            const res = await trackComplaint(tracking_id);
            setTicketDetails(res);
        } catch (err) {
            console.error(err);
        }
    };

    const handleStatusUpdate = async (id, tracking_id, newStatus) => {
        try {
            await updateStatus(id, newStatus, tracking_id);
            loadData();
        } catch(err) { alert(err) }
    };

    const handleComment = async (id, tracking_id) => {
        if (!commentText[id]) return;
        setPostingComment(id);
        try {
            await postComment(id, commentText[id], 'Admin');
            setCommentText({ ...commentText, [id]: '' });
            // Refresh details if expanded
            if (expandedTicket === id) {
                const res = await trackComplaint(tracking_id);
                setTicketDetails(res);
            }
            alert("Official reply posted");
        } catch (err) {
            alert(err);
        } finally {
            setPostingComment(null);
        }
    };

    const filteredComplaints = complaints.filter(c => {
        const matchesFilter = filter === 'All' || c.department === filter || c.status === filter;
        const matchesSearch = c.tracking_id.toLowerCase().includes(searchTerm.toLowerCase()) || 
                             c.student_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             c.summary.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <div className="page animate-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1 className="section-title">Admin Command Center</h1>
                    <p className="section-sub">Manage complaints, monitor AI agents, and analyze platform performance.</p>
                </div>
                <button className="btn btn-ghost" onClick={loadData} disabled={loading}>
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                </button>
            </div>

            <div className="tab-bar" style={{ marginBottom: '2rem' }}>
                <button className={`tab-btn ${tab === 'tickets' ? 'active' : ''}`} onClick={() => setTab('tickets')}>
                    <LayoutDashboard size={15} /> Global Tickets
                </button>
                <button className={`tab-btn ${tab === 'analytics' ? 'active' : ''}`} onClick={() => setTab('analytics')}>
                    <PieChart size={15} /> Platform Insights
                </button>
            </div>

            {/* ══════════════════════════════════════════
                TAB: TICKETS
            ══════════════════════════════════════════ */}
            {tab === 'tickets' && (
                <div>
                    {/* Filters & Search */}
                    <div className="glass" style={{ padding: '1.2rem', marginBottom: '1.5rem', display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                        <div style={{ position: 'relative', flex: 1, minWidth: '250px' }}>
                            <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input 
                                placeholder="Search by ID, Email, or Summary..." 
                                style={{ paddingLeft: 38, marginBottom: 0 }}
                                value={searchTerm}
                                onChange={e => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <Filter size={16} style={{ color: 'var(--text-muted)' }} />
                            <select 
                                style={{ marginBottom: 0, width: '200px' }}
                                value={filter}
                                onChange={e => setFilter(e.target.value)}
                            >
                                <option value="All">All Entities</option>
                                <optgroup label="Status">
                                    <option value="Submitted">Submitted</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="Resolved">Resolved</option>
                                </optgroup>
                                <optgroup label="Department">
                                    <option value="Maintenance & Infrastructure Dept.">Maintenance & Infrastructure</option>
                                    <option value="Academic Affairs Office">Academic Affairs</option>
                                    <option value="Hostel Warden & Mess Committee">Hostel & Mess</option>
                                    <option value="Anti-Ragging Cell">Anti-Ragging Cell</option>
                                    <option value="Registrar / Admin Office">Registrar / Admin Office</option>
                                    <option value="IT Services & Network Dept.">IT & Network</option>
                                    <option value="Dean of Student Welfare">Manual Review (Dean)</option>
                                </optgroup>
                            </select>
                        </div>
                    </div>

                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '4rem' }}>
                            <div className="spinner spinner-dark" style={{ margin: '0 auto 1rem', width: 40, height: 40 }} />
                            <p style={{ color: 'var(--text-secondary)' }}>Syncing with AI Command Center...</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {filteredComplaints.length === 0 ? (
                                <div className="glass empty-state">
                                    <Search size={48} />
                                    <p>No complaints found matching your filters.</p>
                                </div>
                            ) : (
                                filteredComplaints.map(c => (
                                    <div key={c.id} className="glass" style={{ 
                                        padding: '1.2rem 1.8rem', 
                                        borderLeft: c.flagged ? '6px solid var(--danger)' : `6px solid ${STATUS_META[c.status]?.color || '#4f46e5'}`,
                                        transition: 'all 0.25s ease'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 6 }}>
                                                    <h3 style={{ fontFamily: 'Outfit', fontWeight: 900, fontSize: '1.1rem', color: '#4f46e5' }}>{c.tracking_id}</h3>
                                                    {c.flagged === 1 && <span className="badge badge-flagged" style={{ verticalAlign: 'middle' }}><ShieldAlert size={12} /> Flagged</span>}
                                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>• {new Date(c.created_at).toLocaleString()}</span>
                                                </div>
                                                <div style={{ display: 'flex', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4 }}>
                                                        <Users size={14} /> {c.student_email}
                                                    </span>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 4 }}>
                                                        <Building2 size={14} /> {c.department}
                                                    </span>
                                                </div>
                                            </div>
                                            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                                                <select 
                                                    style={{ marginBottom: 0, width: '140px', fontSize: '0.85rem', padding: '8px 12px' }}
                                                    value={c.status}
                                                    onChange={(e) => handleStatusUpdate(c.id, c.tracking_id, e.target.value)}
                                                >
                                                    <option value="Submitted">Submitted</option>
                                                    <option value="In Progress">In Progress</option>
                                                    <option value="Resolved">Resolved</option>
                                                </select>
                                                <button 
                                                    className="btn btn-ghost btn-sm"
                                                    onClick={() => handleExpandTicket(c.id, c.tracking_id)}
                                                    style={{ padding: '8px' }}
                                                >
                                                    {expandedTicket === c.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                                                </button>
                                            </div>
                                        </div>

                                        <p style={{ color: 'var(--text)', fontSize: '1rem', fontWeight: 500, marginBottom: 12 }}>{c.summary}</p>

                                        {/* Expanded Section */}
                                        {expandedTicket === c.id && (
                                            <div className="animate-in" style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(0,0,0,0.06)' }}>
                                                {!ticketDetails ? (
                                                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                                                        <div className="spinner spinner-dark" style={{ margin: '0 auto' }} />
                                                    </div>
                                                ) : (
                                                    <div>
                                                        {/* Discussion Threads */}
                                                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1rem' }}>
                                                                <MessageSquare size={18} color="var(--success)" />
                                                                <h4 style={{ fontFamily: 'Outfit', fontWeight: 700 }}>Discussion Threads</h4>
                                                            </div>
                                                            <div style={{ flex: 1, maxHeight: '200px', overflowY: 'auto', marginBottom: '1rem', paddingRight: '8px' }}>
                                                                {ticketDetails.comments && ticketDetails.comments.map((cm, i) => (
                                                                    <div key={i} className={`comment comment-${cm.posted_by === 'Student' ? 'student' : 'admin'}`} style={{ padding: '8px 12px', marginBottom: 8, fontSize: '0.88rem' }}>
                                                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                                                                            <strong>{cm.posted_by}</strong>
                                                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(cm.posted_at).toLocaleTimeString()}</span>
                                                                        </div>
                                                                        <p>{cm.comment}</p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                            <div style={{ display: 'flex', gap: 10 }}>
                                                                <input 
                                                                    style={{ marginBottom: 0, flex: 1, fontSize: '0.88rem' }}
                                                                    placeholder="Type official reply..."
                                                                    value={commentText[c.id] || ''}
                                                                    onChange={e => setCommentText({ ...commentText, [c.id]: e.target.value })}
                                                                />
                                                                <button 
                                                                    className="btn btn-primary" 
                                                                    onClick={() => handleComment(c.id, c.tracking_id)}
                                                                    disabled={postingComment === c.id}
                                                                >
                                                                    {postingComment === c.id ? <div className="spinner" /> : 'Send'}
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* ══════════════════════════════════════════
                TAB: ANALYTICS
            ══════════════════════════════════════════ */}
            {tab === 'analytics' && (
                <div>
                    {!stats ? (
                        <div style={{ textAlign: 'center', padding: '4rem' }}>
                            <div className="spinner spinner-dark" />
                        </div>
                    ) : (
                        <div className="animate-in">
                            <div className="card-grid-3" style={{ marginBottom: '2rem' }}>
                                {[
                                    { label: 'Total Tickets', value: stats.stats.total, icon: <Activity />, color: '#4f46e5' },
                                    { label: 'System Resolved', value: stats.stats.resolved, icon: <CheckCircle2 />, color: '#10b981' },
                                    { label: 'Operational Load', value: `${Math.round((stats.stats.total - stats.stats.resolved) / (stats.stats.total || 1) * 100)}%`, icon: <AlertCircle />, color: '#f59e0b' }
                                ].map((m, i) => (
                                    <div key={i} className="glass stat-card">
                                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 12 }}>
                                            <div style={{ background: `${m.color}15`, color: m.color, padding: 10, borderRadius: 12 }}>
                                                {m.icon}
                                            </div>
                                        </div>
                                        <div className="stat-value" style={{ fontSize: '2.5rem' }}>{m.value}</div>
                                        <div className="stat-label">{m.label}</div>
                                    </div>
                                ))}
                            </div>

                            <div className="card-grid-2">
                                {/* Department Breakdown */}
                                <div className="glass" style={{ padding: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                                        <Building2 size={20} color="var(--primary)" />
                                        <h3 style={{ fontFamily: 'Outfit', fontWeight: 800 }}>Department Workload</h3>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                                        {stats.departments.filter(d => d.department).map((d, i) => {
                                            const pct = Math.round((d.total / (stats.stats.total || 1)) * 100);
                                            const resPct = Math.round((d.resolved / (d.total || 1)) * 100);
                                            return (
                                                <div key={i}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: '0.9rem' }}>
                                                        <span style={{ fontWeight: 600 }}>{d.department}</span>
                                                        <span style={{ color: 'var(--text-secondary)' }}>{d.total} Cases ({resPct}% Resolved)</span>
                                                    </div>
                                                    <div className="progress-bar" style={{ height: 10 }}>
                                                        <div className="progress-fill" style={{ width: `${resPct}%`, background: '#10b981' }} />
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* AI Categories */}
                                <div className="glass" style={{ padding: '2rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.5rem' }}>
                                        <Tag size={20} color="var(--accent)" />
                                        <h3 style={{ fontFamily: 'Outfit', fontWeight: 800 }}>Issue Distribution</h3>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        {stats.categories.filter(c => c.category).map((c, i) => (
                                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'rgba(255,255,255,0.4)', borderRadius: 12 }}>
                                                <div style={{ width: 12, height: 12, borderRadius: '50%', background: `hsl(${i * 60}, 70%, 50%)` }} />
                                                <span style={{ flex: 1, fontSize: '0.92rem' }}>{c.category}</span>
                                                <span className="badge badge-submitted" style={{ minWidth: 40, textAlign: 'center' }}>{c.count}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
