import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  async function submit(event) {
    event.preventDefault(); setError('');
    try {
      const result = await apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify(form) });
      localStorage.setItem('merkato_token', result.access_token);
      navigate('/admin');
    } catch (err) { setError(err.message); }
  }
  return <main className="auth-shell"><form className="auth-card" onSubmit={submit}>
    <h1>Admin Login</h1><p>Manage the Merkato directory.</p>
    <label>Username<input required value={form.username} onChange={e => setForm({...form, username: e.target.value})} /></label>
    <label>Password<input required type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} /></label>
    {error && <p className="form-error">{error}</p>}<button className="primary-button">Sign in</button>
  </form></main>;
}
