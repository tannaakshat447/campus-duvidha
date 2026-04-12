const BASE_URL = '/api';

export const playSuccessSound = () => {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function playNote(freq, startTime, duration) {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, startTime);
            gain.gain.setValueAtTime(0, startTime);
            gain.gain.linearRampToValueAtTime(0.15, startTime + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
            osc.start(startTime);
            osc.stop(startTime + duration);
        }
        const now = ctx.currentTime;
        playNote(783.99, now, 0.4); // G5 
        playNote(1046.50, now + 0.15, 0.6); // C6 
    } catch(e) {
        console.log("Audio not supported");
    }
};

export const apiCall = async (endpoint, options = {}) => {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Server error');
    return data;
};

// Auth
export const login = (email, password) => apiCall('/auth/login', { method: 'POST', body: JSON.stringify({email, password}) });
export const register = (email, password) => apiCall('/auth/register', { method: 'POST', body: JSON.stringify({email, password}) });
export const adminLogin = (pin) => apiCall('/auth/admin_login', { method: 'POST', body: JSON.stringify({pin}) });

// Complaints
export const getMyComplaints = (email) => apiCall(`/complaints/me?email=${email}`);
export const trackComplaint = (id) => apiCall(`/tracking/${id}`);
export const postComment = (id, text, sender) => apiCall(`/tracking/${id}/comment`, { method: 'POST', body: JSON.stringify({text, sender}) });
export const submitComplaint = async (formData) => {
    const res = await fetch(`${BASE_URL}/complaints/submit`, {
        method: 'POST',
        body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Submission failed');
    return data;
};

// Admin
export const getAdminComplaints = () => apiCall('/admin/complaints');
export const updateStatus = (id, status, tracking_id) => apiCall(`/admin/complaints/${id}/status`, { method: 'POST', body: JSON.stringify({status, tracking_id}) });
export const getAnalytics = () => apiCall('/admin/analytics');
