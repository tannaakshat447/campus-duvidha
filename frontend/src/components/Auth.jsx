import { useState } from 'react';
import { login, register, adminLogin, playSuccessSound } from '../utils/api';
import { LogIn, UserPlus, Shield, ShieldCheck, Mail, Lock, ArrowLeft } from 'lucide-react';

export default function Auth({ onLogin, onBack }) {
    const [mode, setMode] = useState('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            if (mode === 'login') {
                const res = await login(email, password);
                playSuccessSound();
                onLogin(res.user, 'student');
            } else if (mode === 'register') {
                await register(email, password);
                playSuccessSound();
                setMode('login');
                setError('');
                alert("Account created! Please log in.");
            } else {
                await adminLogin(pin);
                playSuccessSound();
                onLogin('admin', 'admin');
            }
        } catch(err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page animate-in" style={{ maxWidth: 480, paddingTop: '3rem' }}>
            <button className="btn btn-ghost btn-sm" style={{ marginBottom: '1.5rem' }} onClick={onBack}>
                <ArrowLeft size={16} /> Back to Home
            </button>

            <div className="glass" style={{ padding: '2.5rem' }}>
                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{
                        width: 64, height: 64, borderRadius: 18,
                        background: 'linear-gradient(135deg, #4f46e5, #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        margin: '0 auto 12px',
                        boxShadow: '0 8px 24px rgba(79,70,229,0.3)'
                    }}>
                        <ShieldCheck size={30} color="white" />
                    </div>
                    <h1 style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.6rem', marginBottom: 4 }}>
                        {mode === 'login' ? 'Welcome Back' : mode === 'register' ? 'Create Account' : 'Admin Access'}
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        {mode === 'admin' ? 'Restricted to administrators only' : 'IIIT Ranchi Student Portal'}
                    </p>
                </div>

                {/* Role Toggle */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: '1.5rem', padding: 6, background: 'rgba(0,0,0,0.04)', borderRadius: 12 }}>
                    <button
                        className={`btn ${mode !== 'admin' ? 'btn-primary' : 'btn-ghost'}`}
                        style={{ borderRadius: 8 }}
                        onClick={() => { setMode('login'); setError(''); }}
                    ><UserPlus size={16}/> Student</button>
                    <button
                        className={`btn ${mode === 'admin' ? 'btn-primary' : 'btn-ghost'}`}
                        style={{ borderRadius: 8 }}
                        onClick={() => { setMode('admin'); setError(''); }}
                    ><Shield size={16}/> Admin</button>
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <form onSubmit={handleSubmit}>
                    {mode !== 'admin' ? (
                        <>
                            <div className="form-group">
                                <label className="form-label"><Mail size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />College Email</label>
                                <input type="email" placeholder="yourname@iiitranchi.ac.in" value={email} onChange={e => setEmail(e.target.value)} required />
                            </div>
                            <div className="form-group">
                                <label className="form-label"><Lock size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Password</label>
                                <input type="password" placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} required />
                            </div>
                        </>
                    ) : (
                        <div className="form-group">
                            <label className="form-label"><Shield size={13} style={{ verticalAlign: 'middle', marginRight: 4 }} />Admin PIN</label>
                            <input type="password" placeholder="Enter PIN" value={pin} onChange={e => setPin(e.target.value)} required />
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary btn-full" style={{ marginTop: 8 }} disabled={loading}>
                        {loading ? <div className="spinner" /> :
                            mode === 'login' ? <><LogIn size={18}/> Log In</> :
                            mode === 'register' ? <><UserPlus size={18}/> Create Account</> :
                            <><Shield size={18}/> Verify & Enter</>}
                    </button>
                </form>

                {mode !== 'admin' && (
                    <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                        {mode === 'login' ? (
                            <>Don't have an account?{' '}
                                <a href="#" style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}
                                    onClick={e => { e.preventDefault(); setMode('register'); setError(''); }}>Create one</a>
                            </>
                        ) : (
                            <>Already registered?{' '}
                                <a href="#" style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}
                                    onClick={e => { e.preventDefault(); setMode('login'); setError(''); }}>Log in</a>
                            </>
                        )}
                    </div>
                )}
            </div>


        </div>
    );
}
