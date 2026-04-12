import { useState, useEffect } from 'react';
import Landing from './components/Landing';
import Auth from './components/Auth';
import StudentPortal from './components/StudentPortal';
import Tracking from './components/Tracking';
import AdminDash from './components/AdminDash';
import { ShieldCheck, LogOut, Search, LayoutDashboard, User } from 'lucide-react';

function App() {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [view, setView] = useState('landing');
  const [activeTracking, setActiveTracking] = useState(null);

  const handleLogin = (identifier, userRole) => {
    setUser(identifier);
    setRole(userRole);
    setView(userRole === 'admin' ? 'admin' : 'portal');
  };

  const handleLogout = () => {
    setUser(null); setRole(null); setView('landing'); setActiveTracking(null);
  };

  const navigateTo = (newView, payload = null) => {
    if (newView === 'track-public' || newView === 'tracking') {
      setActiveTracking(payload || null);
      setView('track-public');
    } else {
      setView(newView);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      {/* ── Navbar ─────────────────────────────── */}
      <nav className="navbar">
        <div className="nav-brand" onClick={() => navigateTo('landing')}>
          <ShieldCheck size={24} />
          Campus Duvidha
        </div>

        <div className="nav-links">
          {/* Track is always visible */}
          <button
            className={`nav-btn nav-btn-ghost ${view === 'track-public' ? 'active' : ''}`}
            onClick={() => navigateTo('track-public')}
          >
            <Search size={15} style={{ verticalAlign: 'middle', marginRight: 4 }} />
            Track Complaint
          </button>

          {!user ? (
            <>
              <button className="nav-btn nav-btn-ghost" onClick={() => navigateTo('auth')}>Log In</button>
              <button className="nav-btn nav-btn-primary" onClick={() => navigateTo('auth')}>Get Started</button>
            </>
          ) : (
            <>
              {role === 'student' && (
                <button
                  className={`nav-btn nav-btn-ghost ${view === 'portal' ? 'active' : ''}`}
                  onClick={() => navigateTo('portal')}
                >
                  <User size={15} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                  My Portal
                </button>
              )}
              {role === 'admin' && (
                <button
                  className={`nav-btn nav-btn-ghost ${view === 'admin' ? 'active' : ''}`}
                  onClick={() => navigateTo('admin')}
                >
                  <LayoutDashboard size={15} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                  Admin
                </button>
              )}
              <div className="nav-badge">
                {role === 'admin' ? '🛡 Admin' : `👤 ${user.split('@')[0]}`}
              </div>
              <button className="nav-btn nav-btn-ghost" onClick={handleLogout} title="Log out">
                <LogOut size={15} />
              </button>
            </>
          )}
        </div>
      </nav>

      {/* ── Views ──────────────────────────────── */}
      {view === 'landing' && <Landing onNavigate={navigateTo} />}
      {view === 'auth' && <Auth onLogin={handleLogin} onBack={() => navigateTo('landing')} />}
      {view === 'portal' && <StudentPortal user={user} onNavigate={navigateTo} />}
      {view === 'track-public' && <Tracking initialTrackingId={activeTracking} key={activeTracking} />}
      {view === 'admin' && <AdminDash />}
    </div>
  );
}

export default App;
