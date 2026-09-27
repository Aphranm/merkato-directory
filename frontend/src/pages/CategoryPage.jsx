import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function CategoryPage() {
  const { buildingId, categoryId } = useParams();
  const [category, setCategory] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setCategory(await apiFetch(`/api/categories/${categoryId}`));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [categoryId]);

  if (error) return <main className="container"><p>{error}</p></main>;
  if (!category) return <main className="container"><p>Loading...</p></main>;

  return <main className="public-shell">
    <section className="container breadcrumb"><Link to="/">Buildings</Link> / <Link to={`/buildings/${buildingId}`}>{category.building_name}</Link> / <strong>{category.name}</strong></section>
    <section className="container detail"><img src={category.image_url || 'https://via.placeholder.com/600'} alt={category.name} /><div><h1>{category.name}</h1><p>{category.description}</p></div></section>
    <section className="container"><h2>Rooms & Shops</h2><div className="grid">{category.rooms?.map(r => <div key={r.id} className="card"><img src={r.image_url || 'https://via.placeholder.com/300'} alt={r.name} /><h3>{r.name}</h3><p>{r.description || r.room_number}</p><Link to={`/buildings/${buildingId}/categories/${categoryId}/rooms/${r.id}`}>View →</Link></div>)}</div></section>
  </main>;
}
