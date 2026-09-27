import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiFetch } from '../api';

function RoomPage() {
  const { buildingId, categoryId, roomId } = useParams();
  const [room, setRoom] = useState(null);

  useEffect(() => {
    async function loadRoom() {
      const data = await apiFetch(`/api/rooms/${roomId}`);
      setRoom(data);
    }

    loadRoom();
  }, [roomId]);

  if (!room) return <div className="container page-space">Loading...</div>;

  return (
    <div className="container page-space">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>›</span>
        <Link to={`/buildings/${buildingId}`}>Building</Link>
        <span>›</span>
        <Link to={`/buildings/${buildingId}/categories/${categoryId}`}>Category</Link>
        <span>›</span>
        <span>{room.name}</span>
      </nav>

      <section className="panel detail-header">
        {room.image_url && <img src={room.image_url} alt={room.name} loading="lazy" />}
        <div>
          <span className="eyebrow">Room / Shop</span>
          <h1>{room.name}</h1>
          <p>{room.description}</p>
        </div>
      </section>

      {room.business ? (
        <section className="panel business-card">
          <h2>{room.business.business_name}</h2>
          <p>{room.business.description}</p>
          <div className="business-meta">
            {room.business.phone && <p>Phone: {room.business.phone}</p>}
            {room.business.website && <p>Website: <a href={room.business.website} target="_blank" rel="noreferrer">{room.business.website}</a></p>}
            {room.business.whatsapp && <p>WhatsApp: {room.business.whatsapp}</p>}
            {room.business.instagram && <p>Instagram: {room.business.instagram}</p>}
          </div>
          <Link className="primary-button" to={`/businesses/${room.business.id}`}>Open Business</Link>
        </section>
      ) : (
        <div className="empty-state">No business information available for this room yet.</div>
      )}
    </div>
  );
}

export default RoomPage;
