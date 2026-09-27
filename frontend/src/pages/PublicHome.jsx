import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function PublicHome() {
  const navigate = useNavigate();
  const [buildings, setBuildings] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setBuildings(await apiFetch('/api/buildings'));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  return <main className="public-shell">
    <header className="hero"><div className="container"><h1>Merkato Directory</h1><p>Discover shops and businesses</p><Link to="/admin/login" className="admin-link">Admin</Link></div></header>
    {error && <div className="container error-notice">{error}</div>}
    <section className="container"><div className="grid">{buildings.map(b => <div key={b.id} className="card"><img src={b.image_url || 'https://via.placeholder.com/300'} alt={b.name} /><h3>{b.name}</h3><p>{b.description}</p><Link to={`/buildings/${b.id}`}>View →</Link></div>)}</div></section>
  </main>;
}
