import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api';

function BuildingPage() {
  const { buildingId } = useParams();
  const [building, setBuilding] = useState(null);

  useEffect(() => {
    async function loadBuilding() {
      const data = await apiFetch(`/api/buildings/${buildingId}`);
      setBuilding(data);
    }

    loadBuilding();
  }, [buildingId]);

  if (!building) return <div className="container page-space">Loading...</div>;

  return (
    <div className="container page-space">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>›</span>
        <span>{building.name}</span>
      </nav>

      <section className="panel detail-header">
        {building.image_url && <img src={building.image_url} alt={building.name} loading="lazy" />}
        <div>
          <span className="eyebrow">Building</span>
          <h1>{building.name}</h1>
          <p>{building.description}</p>
        </div>
      </section>

      <section>
        <h2>Categories</h2>
        {building.categories?.length ? (
          <div className="stack-grid">
            {building.categories.map((category) => (
              <Link key={category.id} to={`/buildings/${building.id}/categories/${category.id}`} className="stack-card">
                {category.image_url && <img src={category.image_url} alt={category.name} loading="lazy" />}
                <div>
                  <strong>{category.name}</strong>
                  <p>{category.description}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state">No categories in this building yet.</div>
        )}
      </section>
    </div>
  );
}

export default BuildingPage;
