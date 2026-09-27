import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function BuildingPage() {
  const { buildingId } = useParams();
  const [building, setBuilding] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setBuilding(await apiFetch(`/api/buildings/${buildingId}`));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [buildingId]);

  if (error) return <main className="container"><p>{error}</p></main>;
  if (!building) return <main className="container"><p>Loading...</p></main>;

  return <main className="public-shell">
    <section className="container breadcrumb"><Link to="/">Buildings</Link> / <strong>{building.name}</strong></section>
    <section className="container detail"><img src={building.image_url || 'https://via.placeholder.com/600'} alt={building.name} /><div><h1>{building.name}</h1><p>{building.description}</p></div></section>
    <section className="container"><h2>Categories</h2><div className="grid">{building.categories?.map(c => <div key={c.id} className="card"><img src={c.image_url || 'https://via.placeholder.com/300'} alt={c.name} /><h3>{c.name}</h3><p>{c.description}</p><Link to={`/buildings/${buildingId}/categories/${c.id}`}>View →</Link></div>)}</div></section>
  </main>;
}
