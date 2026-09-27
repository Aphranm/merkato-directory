import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api';

function CategoryPage() {
  const { buildingId, categoryId } = useParams();
  const [category, setCategory] = useState(null);

  useEffect(() => {
    async function loadCategory() {
      const data = await apiFetch(`/api/categories/${categoryId}`);
      setCategory(data);
    }

    loadCategory();
  }, [categoryId]);

  if (!category) return <div className="container page-space">Loading...</div>;

  return (
    <div className="container page-space">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>›</span>
        <Link to={`/buildings/${buildingId}`}>Building</Link>
        <span>›</span>
        <span>{category.name}</span>
      </nav>

      <section className="panel detail-header">
        {category.image_url && <img src={category.image_url} alt={category.name} loading="lazy" />}
        <div>
          <span className="eyebrow">Category</span>
          <h1>{category.name}</h1>
          <p>{category.description}</p>
        </div>
      </section>

      <section>
        <h2>Rooms / Shops</h2>
        {category.rooms?.length ? (
          <div className="stack-grid">
            {category.rooms.map((room) => (
              <Link key={room.id} to={`/buildings/${buildingId}/categories/${categoryId}/rooms/${room.id}`} className="stack-card">
                {room.image_url && <img src={room.image_url} alt={room.name} loading="lazy" />}
                <div>
                  <strong>{room.name}</strong>
                  <p>Room {room.room_number}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state">No rooms in this category yet.</div>
        )}
      </section>
    </div>
  );
}

export default CategoryPage;
