import React from 'react';

function StatusAction({ resource, record, onStatusChange }) {
  const archived = record.status === 'archived';
  return (
    <button
      className="admin-secondary"
      type="button"
      onClick={() => onStatusChange(record, archived ? 'active' : 'archived')}
    >
      {archived ? 'Restore' : 'Archive'}
    </button>
  );
}

export function BuildingManagement({ draft, onDraftChange, onSubmit, busy, buildings, onStatusChange, onEdit, onCancelEdit, isEditing, onUploadImage, uploadingBuilding }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">LOCATION STRUCTURE</p><h2>Add a building</h2></div>
      <form className="admin-form admin-form-grid" onSubmit={onSubmit}>
        <label>Building name<input required value={draft.name} onChange={(event) => onDraftChange({ ...draft, name: event.target.value })} /></label>
        <label>Building code<input value={draft.building_code} onChange={(event) => onDraftChange({ ...draft, building_code: event.target.value })} /></label>
        <label>Address<input value={draft.address_text} onChange={(event) => onDraftChange({ ...draft, address_text: event.target.value })} /></label>
        <label>Nearby landmark<input value={draft.landmark} onChange={(event) => onDraftChange({ ...draft, landmark: event.target.value })} /></label>
        <label className="wide-field">Description<textarea rows="3" value={draft.description} onChange={(event) => onDraftChange({ ...draft, description: event.target.value })} /></label>
        <button className="admin-primary" type="submit" disabled={busy || !draft.name.trim()}>{isEditing ? 'Save building' : 'Add building'}</button>
        {isEditing && <button className="admin-back-link" type="button" onClick={onCancelEdit}>Cancel edit</button>}
      </form>
      <div className="admin-record-list">
        {buildings.map((building) => (
          <article key={building.id}>
            <strong>{building.name}</strong>
            <span>{building.address_text || building.building_code || 'Address not listed'} · {building.status}</span>
            {building.image_url && <img className="building-admin-image" src={building.image_url} alt={`${building.name} building`} />}
            <button className="admin-secondary" type="button" onClick={() => onEdit(building)}>Edit</button>
            <StatusAction resource="buildings" record={building} onStatusChange={onStatusChange} />
            <form className="building-photo-upload" onSubmit={(event) => onUploadImage(event, building)}>
              <label>Building photo<input name="file" type="file" accept="image/jpeg,image/png,image/webp" required /></label>
              <button className="admin-secondary" type="submit" disabled={uploadingBuilding === building.id}>{uploadingBuilding === building.id ? 'Uploading…' : 'Upload image'}</button>
            </form>
          </article>
        ))}
      </div>
    </>
  );
}

export function FloorManagement({ draft, onDraftChange, onSubmit, busy, buildings, floors, onStatusChange, onEdit, onCancelEdit, isEditing }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">LOCATION STRUCTURE</p><h2>Add a floor</h2></div>
      <form className="admin-form admin-form-grid" onSubmit={onSubmit}>
        <label>Building<select required value={draft.building_id} onChange={(event) => onDraftChange({ ...draft, building_id: event.target.value })}><option value="">Choose a building</option>{buildings.filter((building) => building.status === 'active').map((building) => <option key={building.id} value={building.id}>{building.name}</option>)}</select></label>
        <label>Floor name<input required value={draft.name} onChange={(event) => onDraftChange({ ...draft, name: event.target.value })} /></label>
        <label>Floor number<input required type="number" step="1" value={draft.floor_number} onChange={(event) => onDraftChange({ ...draft, floor_number: event.target.value })} /></label>
        <label>Description<input value={draft.description} onChange={(event) => onDraftChange({ ...draft, description: event.target.value })} /></label>
        <button className="admin-primary" type="submit" disabled={busy || !draft.building_id || !draft.name.trim() || draft.floor_number === ''}>{isEditing ? 'Save floor' : 'Add floor'}</button>
        {isEditing && <button className="admin-back-link" type="button" onClick={onCancelEdit}>Cancel edit</button>}
      </form>
      <div className="admin-record-list">
        {floors.map((floor) => (
          <article key={floor.id}>
            <strong>{floor.name} <span className="floor-number">({floor.floor_number})</span></strong>
            <span>{buildings.find((building) => building.id === floor.building_id)?.name || 'Building unavailable'} · {floor.status}</span>
            <button className="admin-secondary" type="button" onClick={() => onEdit(floor)}>Edit</button>
            <StatusAction resource="floors" record={floor} onStatusChange={onStatusChange} />
          </article>
        ))}
      </div>
    </>
  );
}

export function CategoryManagement({ draft, onDraftChange, onSubmit, busy, categories, onStatusChange, onEdit, onCancelEdit, isEditing }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">BUSINESS CLASSIFICATION</p><h2>Add a category</h2></div>
      <form className="admin-form admin-form-grid" onSubmit={onSubmit}>
        <label>Category name<input required value={draft.name} onChange={(event) => onDraftChange({ ...draft, name: event.target.value })} /></label>
        <label>Image URL<input type="url" value={draft.image_url} onChange={(event) => onDraftChange({ ...draft, image_url: event.target.value })} /></label>
        <label className="wide-field">Description<input value={draft.description} onChange={(event) => onDraftChange({ ...draft, description: event.target.value })} /></label>
        <button className="admin-primary" type="submit" disabled={busy || !draft.name.trim()}>{isEditing ? 'Save category' : 'Add category'}</button>
        {isEditing && <button className="admin-back-link" type="button" onClick={onCancelEdit}>Cancel edit</button>}
      </form>
      <div className="admin-record-list">
        {categories.map((category) => (
          <article key={category.id}>
            <strong>{category.name}</strong><span>{category.status}</span>
            <button className="admin-secondary" type="button" onClick={() => onEdit(category)}>Edit</button>
            <StatusAction resource="categories" record={category} onStatusChange={onStatusChange} />
          </article>
        ))}
      </div>
    </>
  );
}

export function BusinessManagement({
  draft,
  onDraftChange,
  onBuildingChange,
  onSubmit,
  busy,
  buildings,
  floors,
  categories,
  businesses,
  photos,
  shopFiles,
  setShopFiles,
  uploadingShop,
  onUpload,
  onRemoveImage,
  onStatusChange,
  onEdit,
  onCancelEdit,
  isEditing,
}) {
  const activeCategories = categories.filter((category) => category.status === 'active');

  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">BUSINESS DIRECTORY</p><h2>Add a business</h2></div>
      <form className="admin-form admin-form-grid shop-create-form" onSubmit={onSubmit}>
        <label>Business name<input required value={draft.name} onChange={(event) => onDraftChange({ ...draft, name: event.target.value })} /></label>
        <label>Building<select required value={draft.building_id} onChange={(event) => onBuildingChange(event.target.value)}><option value="">Choose a building</option>{buildings.filter((building) => building.status === 'active').map((building) => <option key={building.id} value={building.id}>{building.name}</option>)}</select></label>
        <label>Floor<select required disabled={!draft.building_id} value={draft.floor_id} onChange={(event) => onDraftChange({ ...draft, floor_id: event.target.value })}><option value="">Choose a floor</option>{floors.map((floor) => <option key={floor.id} value={floor.id}>{floor.name}</option>)}</select></label>
        <label>Categories<select required multiple value={draft.category_ids.map(String)} onChange={(event) => onDraftChange({ ...draft, category_ids: [...event.target.selectedOptions].map((option) => Number(option.value)) })}>{activeCategories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
        <label>Phone<input type="tel" value={draft.phone} onChange={(event) => onDraftChange({ ...draft, phone: event.target.value })} /></label>
        <label>WhatsApp<input type="tel" value={draft.whatsapp} onChange={(event) => onDraftChange({ ...draft, whatsapp: event.target.value })} /></label>
        <label>Email<input type="email" value={draft.email} onChange={(event) => onDraftChange({ ...draft, email: event.target.value })} /></label>
        <label>Website<input type="url" value={draft.website} onChange={(event) => onDraftChange({ ...draft, website: event.target.value })} /></label>
        <label className="wide-field">Short description<input maxLength="220" value={draft.short_description} onChange={(event) => onDraftChange({ ...draft, short_description: event.target.value })} /></label>
        <label className="wide-field">Description<textarea rows="3" value={draft.description} onChange={(event) => onDraftChange({ ...draft, description: event.target.value })} /></label>
        <label className="wide-field image-picker">Business images<input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => setShopFiles(Array.from(event.target.files || []))} /><span>JPEG, PNG, or WebP · up to 5 MB each</span></label>
        <button className="admin-primary" type="submit" disabled={busy || !draft.name.trim() || !draft.floor_id || !draft.category_ids.length}>{busy ? 'Saving business…' : isEditing ? 'Save business' : 'Add business'}</button>
        {isEditing && <button className="admin-back-link" type="button" onClick={onCancelEdit}>Cancel edit</button>}
      </form>

      <div className="admin-section-title shop-list-title"><p className="admin-eyebrow">EXISTING RECORDS</p><h2>Business images</h2></div>
      <div className="shop-admin-list">
        {businesses.map((business) => (
          <article className="shop-admin-row" key={business.id}>
            <div className="shop-admin-heading"><div><h3>{business.name}</h3><p>{business.status} · {business.categories.map((category) => category.name).join(', ') || 'No categories'}</p></div><div className="record-actions"><button className="admin-secondary" type="button" onClick={() => onEdit(business)}>Edit</button><StatusAction resource="businesses" record={business} onStatusChange={onStatusChange} /></div></div>
            <p className="business-location-admin">{business.floor.building_name} · {business.floor.name}</p>
            <div className="shop-photo-grid">
              {(photos[business.id] || []).map((photo) => (
                <figure key={photo.id}>
                  <img src={photo.file_url} alt={photo.alt_text || `${business.name} photo`} />
                  {photo.is_primary && <figcaption>Primary</figcaption>}
                  <button type="button" aria-label={`Remove photo from ${business.name}`} onClick={() => onRemoveImage(business, photo)}>Remove</button>
                </figure>
              ))}
              {!(photos[business.id] || []).length && <p className="no-photos">No photos added yet.</p>}
            </div>
            <form className="shop-photo-upload" onSubmit={(event) => onUpload(event, business)}>
              <label>Add photos<input name="files" type="file" accept="image/jpeg,image/png,image/webp" multiple /></label>
              <button className="admin-secondary" type="submit" disabled={uploadingShop === business.id}>{uploadingShop === business.id ? 'Uploading…' : 'Upload'}</button>
            </form>
          </article>
        ))}
      </div>
    </>
  );
}