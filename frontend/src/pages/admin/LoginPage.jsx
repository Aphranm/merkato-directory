import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api';

function BusinessPage() {
  const { businessId } = useParams();
  const [business, setBusiness] = useState(null);

  useEffect(() => {
    async function loadBusiness() {
      const data = await apiFetch(`/api/businesses/${businessId}`);
      setBusiness(data);
    }

    loadBusiness();
  }, [businessId]);

  if (!business) return <div className="container page-space">Loading...</div>;

  return (
    <div className="container page-space">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>›</span>
        <Link to={`/buildings/${business.room?.category?.building?.id}`}>{business.room?.category?.building?.name}</Link>
        <span>›</span>
        <Link to={`/buildings/${business.room?.category?.building?.id}/categories/${business.room?.category?.id}`}>{business.room?.category?.name}</Link>
        <span>›</span>
        <Link to={`/buildings/${business.room?.category?.building?.id}/categories/${business.room?.category?.id}/rooms/${business.room?.id}`}>{business.room?.name}</Link>
        <span>›</span>
        <span>{business.business_name}</span>
      </nav>

      <section className="panel detail-header">
        {business.image_url && <img src={business.image_url} alt={business.business_name} loading="lazy" />}
        <div>
          <span className="eyebrow">Business</span>
          <h1>{business.business_name}</h1>
          <p>{business.description}</p>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <h2>Contact</h2>
          {business.phone && <p><strong>Phone:</strong> {business.phone}</p>}
          {business.alternative_phone && <p><strong>Alt Phone:</strong> {business.alternative_phone}</p>}
          {business.telegram && <p><strong>Telegram:</strong> {business.telegram}</p>}
          {business.whatsapp && <p><strong>WhatsApp:</strong> {business.whatsapp}</p>}
          {business.facebook && <p><strong>Facebook:</strong> <a href={business.facebook} target="_blank" rel="noreferrer">{business.facebook}</a></p>}
          {business.instagram && <p><strong>Instagram:</strong> <a href={business.instagram} target="_blank" rel="noreferrer">{business.instagram}</a></p>}
          {business.website && <p><strong>Website:</strong> <a href={business.website} target="_blank" rel="noreferrer">{business.website}</a></p>}
        </div>

        <div className="panel">
          <h2>Details</h2>
          {business.opening_hours && <p><strong>Opening hours:</strong> {business.opening_hours}</p>}
          {business.services && <p><strong>Services:</strong> {business.services}</p>}
          {business.products && <p><strong>Products:</strong> {business.products}</p>}
          {business.notes && <p><strong>Notes:</strong> {business.notes}</p>}
        </div>
      </section>
    </div>
  );
}

export default BusinessPage;
