import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../../api';
import '../../styles.css';

export default function RoomPage() {
  const { buildingId, categoryId, roomId } = useParams();
  const [room, setRoom] = useState(null);
  const [business, setBusiness] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setRoom(await apiFetch(`/api/rooms/${roomId}`));
        setBusiness(await apiFetch(`/api/rooms/${roomId}/business`).catch(() => null));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, [roomId]);

  if (error) return <main className="container"><p>{error}</p></main>;
  if (!room) return <main className="container"><p>Loading...</p></main>;

  return <main className="public-shell">
    <section className="container breadcrumb"><Link to="/">Buildings</Link> / <Link to={`/buildings/${buildingId}`}>{room.building_name}</Link> / <Link to={`/buildings/${buildingId}/categories/${categoryId}`}>{room.category_name}</Link> / <strong>{room.name}</strong></section>
    <section className="container detail"><img src={room.image_url || 'https://via.placeholder.com/600'} alt={room.name} /><div><h1>{room.name}</h1><p>Room {room.room_number}</p><p>{room.description}</p></div></section>
    {business && <section className="container"><h2>{business.business_name}</h2><p>{business.description}</p><table className="info-table"><tbody>{business.phone&&<tr><th>Phone</th><td><a href={`tel:${business.phone}`}>{business.phone}</a></td></tr>}{business.website&&<tr><th>Website</th><td><a href={business.website} target="_blank" rel="noopener noreferrer">{business.website}</a></td></tr>}{business.instagram&&<tr><th>Instagram</th><td><a href={`https://instagram.com/${business.instagram}`} target="_blank" rel="noopener noreferrer">@{business.instagram}</a></td></tr>}{business.facebook&&<tr><th>Facebook</th><td><a href={`https://facebook.com/${business.facebook}`} target="_blank" rel="noopener noreferrer">{business.facebook}</a></td></tr>}{business.whatsapp&&<tr><th>WhatsApp</th><td><a href={`https://wa.me/${business.whatsapp.replace(/\D/g,'')}`}>{business.whatsapp}</a></td></tr>}{business.opening_hours&&<tr><th>Hours</th><td>{business.opening_hours}</td></tr>}{business.services&&<tr><th>Services</th><td>{business.services}</td></tr>}{business.products&&<tr><th>Products</th><td>{business.products}</td></tr>}</tbody></table></section>}
  </main>;
}
