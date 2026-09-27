import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function BusinessPage() {
  const { businessId } = useParams();
  const [business, setBusiness] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setBusiness(await apiFetch(`/api/businesses/${businessId}`));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [businessId]);

  if (error) return <main className="container"><p>{error}</p></main>;
  if (!business) return <main className="container"><p>Loading...</p></main>;

  return <main className="public-shell">
    <section className="container breadcrumb"><Link to="/">Buildings</Link> / <Link to={`/buildings/${business.room.category.building.id}`}>{business.room.category.building.name}</Link> / <Link to={`/buildings/${business.room.category.building.id}/categories/${business.room.category.id}`}>{business.room.category.name}</Link> / <Link to={`/buildings/${business.room.category.building.id}/categories/${business.room.category.id}/rooms/${business.room.id}`}>{business.room.name}</Link> / <strong>{business.business_name}</strong></section>
    <section className="container detail"><img src={business.image_url || 'https://via.placeholder.com/600'} alt={business.business_name} /><div><h1>{business.business_name}</h1><p>{business.description}</p></div></section>
    <section className="container"><h2>Contact & Info</h2><table className="info-table"><tbody>{business.phone&&<tr><th>Phone</th><td><a href={`tel:${business.phone}`}>{business.phone}</a></td></tr>}{business.alternative_phone&&<tr><th>Alt. Phone</th><td><a href={`tel:${business.alternative_phone}`}>{business.alternative_phone}</a></td></tr>}{business.website&&<tr><th>Website</th><td><a href={business.website} target="_blank" rel="noopener noreferrer">{business.website}</a></td></tr>}{business.instagram&&<tr><th>Instagram</th><td><a href={`https://instagram.com/${business.instagram}`} target="_blank" rel="noopener noreferrer">@{business.instagram}</a></td></tr>}{business.facebook&&<tr><th>Facebook</th><td><a href={`https://facebook.com/${business.facebook}`} target="_blank" rel="noopener noreferrer">{business.facebook}</a></td></tr>}{business.telegram&&<tr><th>Telegram</th><td><a href={`https://t.me/${business.telegram}`}>@{business.telegram}</a></td></tr>}{business.whatsapp&&<tr><th>WhatsApp</th><td><a href={`https://wa.me/${business.whatsapp.replace(/\D/g,'')}`}>{business.whatsapp}</a></td></tr>}{business.opening_hours&&<tr><th>Hours</th><td>{business.opening_hours}</td></tr>}{business.services&&<tr><th>Services</th><td>{business.services}</td></tr>}{business.products&&<tr><th>Products</th><td>{business.products}</td></tr>}{business.notes&&<tr><th>Notes</th><td>{business.notes}</td></tr>}</tbody></table></section>
    {business.gallery_images?.length > 0 && <section className="container"><h2>Gallery</h2><div className="grid">{business.gallery_images.map((img, i) => <img key={i} src={img} alt="Gallery" />)}</div></section>}
  </main>;
}
