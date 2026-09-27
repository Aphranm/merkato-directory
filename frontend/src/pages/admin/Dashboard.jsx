import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiFetch, apiUpload } from '../../api';
import '../../styles.css';

const blank = { name: '', description: '', image_url: '', sort_order: 0, is_published: true };
const blankRoom = { room_number: '', name: '', description: '', image_url: '', sort_order: 0, is_published: true };
const blankBusiness = { business_name: '', description: '', phone: '', alternative_phone: '', telegram: '', whatsapp: '', facebook: '', instagram: '', website: '', opening_hours: '', services: '', products: '', notes: '', image_url: '', is_published: true };

export default function Dashboard() {
  const navigate = useNavigate();
  const [buildings, setBuildings] = useState([]); const [error, setError] = useState(''); const [notice, setNotice] = useState('');
  const [building, setBuilding] = useState(blank); const [category, setCategory] = useState({...blank, building_id: ''});
  const [room, setRoom] = useState({...blankRoom, category_id: ''}); const [business, setBusiness] = useState({...blankBusiness, room_id: ''});

  async function load() { try { setBuildings(await apiFetch('/api/buildings')); } catch (e) { if (e.message.includes('authenticated')) navigate('/admin/login'); else setError(e.message); } }
  useEffect(() => { if (!localStorage.getItem('merkato_token')) navigate('/admin/login'); else load(); }, [navigate]);
  function fail(e) { setError(e.message); setNotice(''); }
  async function upload(e, setter) { const file = e.target.files?.[0]; if (!file) return; try { const result = await apiUpload(file); setter(v => ({...v, image_url: result.url})); } catch (err) { fail(err); } }
  async function save(label, path, payload, reset) { try { setError(''); await apiFetch(path, {method:'POST', body: JSON.stringify(payload)}); reset(); setNotice(`${label} saved`); await load(); } catch (e) { fail(e); } }
  const categories = buildings.flatMap(b => (b.categories || []).map(c => ({...c, building_name: b.name})));
  const rooms = categories.flatMap(c => (c.rooms || []).map(r => ({...r, category_name: c.name, building_name: c.building_name})));
  const logout = () => { localStorage.removeItem('merkato_token'); navigate('/admin/login'); };
  return <div className="admin-shell"><header className="admin-topbar"><div className="container admin-topbar-inner"><h2>Merkato Admin</h2><div className="admin-actions"><Link to="/">Public site</Link><button onClick={logout}>Logout</button></div></div></header>
    <main className="container admin-grid"><aside className="admin-sidebar panel"><h3>Directory</h3><p>Build the hierarchy in order.</p><ul><li>Buildings</li><li>Categories</li><li>Rooms / Shops</li><li>Businesses</li></ul></aside>
    <div className="admin-main">{error && <div className="form-error">{error}</div>}{notice && <div className="notice">{notice}</div>}
      <Form title="Add building" onSubmit={e => {e.preventDefault(); save('Building','/api/buildings',building,()=>setBuilding(blank));}}>
        <input required placeholder="Building name" value={building.name} onChange={e=>setBuilding({...building,name:e.target.value})}/><textarea placeholder="Description" value={building.description} onChange={e=>setBuilding({...building,description:e.target.value})}/><ImageField onChange={e=>upload(e,setBuilding)} preview={building.image_url}/><button className="primary-button">Save building</button>
      </Form>
      <Form title="Add category" onSubmit={e => {e.preventDefault(); save('Category',`/api/buildings/${category.building_id}/categories`,category,()=>setCategory({...blank,building_id:''}));}}>
        <select required value={category.building_id} onChange={e=>setCategory({...category,building_id:e.target.value})}><option value="">Select building</option>{buildings.map(b=><option key={b.id} value={b.id}>{b.name}</option>)}</select><input required placeholder="Category name" value={category.name} onChange={e=>setCategory({...category,name:e.target.value})}/><textarea placeholder="Description" value={category.description} onChange={e=>setCategory({...category,description:e.target.value})}/><ImageField onChange={e=>upload(e,setCategory)} preview={category.image_url}/><button className="primary-button">Save category</button>
      </Form>
      <Form title="Add room / shop" onSubmit={e => {e.preventDefault(); save('Room',`/api/categories/${room.category_id}/rooms`,room,()=>setRoom({...blankRoom,category_id:''}));}}>
        <select required value={room.category_id} onChange={e=>setRoom({...room,category_id:e.target.value})}><option value="">Select category</option>{categories.map(c=><option key={c.id} value={c.id}>{c.building_name} / {c.name}</option>)}</select><input required placeholder="Room number" value={room.room_number} onChange={e=>setRoom({...room,room_number:e.target.value})}/><input required placeholder="Shop name" value={room.name} onChange={e=>setRoom({...room,name:e.target.value})}/><textarea placeholder="Description" value={room.description} onChange={e=>setRoom({...room,description:e.target.value})}/><ImageField onChange={e=>upload(e,setRoom)} preview={room.image_url}/><button className="primary-button">Save room</button>
      </Form>
      <Form title="Add business" onSubmit={e => {e.preventDefault(); save('Business',`/api/rooms/${business.room_id}/business`,business,()=>setBusiness({...blankBusiness,room_id:''}));}}>
        <select required value={business.room_id} onChange={e=>setBusiness({...business,room_id:e.target.value})}><option value="">Select room</option>{rooms.map(r=><option key={r.id} value={r.id}>{r.building_name} / {r.category_name} / {r.name}</option>)}</select><input required placeholder="Business name" value={business.business_name} onChange={e=>setBusiness({...business,business_name:e.target.value})}/><textarea placeholder="Description" value={business.description} onChange={e=>setBusiness({...business,description:e.target.value})}/>{['phone','alternative_phone','whatsapp','telegram','website','instagram','facebook','opening_hours','services','products','notes'].map(key=><input key={key} placeholder={key.replaceAll('_',' ')} value={business[key]} onChange={e=>setBusiness({...business,[key]:e.target.value})}/>)}<ImageField onChange={e=>upload(e,setBusiness)} preview={business.image_url}/><button className="primary-button">Save business</button>
      </Form>
      <section className="panel admin-section"><h3>Current directory</h3>{buildings.map(b=><div className="tree-node" key={b.id}><strong>{b.name}</strong>{(b.categories||[]).map(c=><div className="tree-indent" key={c.id}>• {c.name}</div>)}</div>)}</section>
    </div></main></div>;
}
function Form({title,onSubmit,children}) { return <section className="panel admin-section"><h3>{title}</h3><form className="admin-form" onSubmit={onSubmit}>{children}</form></section>; }
function ImageField({onChange,preview}) { return <label>Image<input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={onChange}/>{preview&&<img className="preview-image" src={preview} alt="Selected preview"/>}</label>; }
