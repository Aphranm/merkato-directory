import React, { useEffect, useState } from 'react';
import './admin.css';
import { BuildingManagement, BusinessManagement, CategoryManagement, FloorManagement } from './admin/EntityForms';
import { AuditPanel, ReportsPanel, UsersPanel, VerificationPanel } from './admin/OperationsPanels';

const sections = [
  ['overview', 'Overview'],
  ['buildings', 'Buildings'],
  ['floors', 'Floors'],
  ['categories', 'Categories'],
  ['businesses', 'Businesses'],
  ['reports', 'Reports'],
  ['verification', 'Verification'],
  ['users', 'Users'],
  ['audit', 'Audit logs'],
];

async function apiRequest(url, { token, method = 'GET', body, signal } = {}) {
  const API_BASE = import.meta.env.VITE_API_TARGET || "";
  const headers = {};
  let requestBody = body;
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${url}`, { method, headers, body: requestBody, signal });
  if (!response.ok) {
    const result = await response.json().catch(() => null);
    const detail = result?.detail;
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function slugify(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function emptyPhotos(businesses) {
  return Object.fromEntries(businesses.map((business) => [business.id, []]));
}

export default function AdminPanel({ accessToken, onAuthenticated, onSignOut, onBack, onDirectoryChanged }) {
  const [section, setSection] = useState('overview');
  const [editing, setEditing] = useState(null);
  const [user, setUser] = useState(null);
  const [sessionLoading, setSessionLoading] = useState(Boolean(accessToken));
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [passwordPanelOpen, setPasswordPanelOpen] = useState(false);
  const [passwordDraft, setPasswordDraft] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [passwordError, setPasswordError] = useState('');
  const [emailPanelOpen, setEmailPanelOpen] = useState(false);
  const [emailDraft, setEmailDraft] = useState({ current_password: '', new_email: '' });
  const [emailError, setEmailError] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [buildings, setBuildings] = useState([]);
  const [floors, setFloors] = useState([]);
  const [shopFloors, setShopFloors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [reports, setReports] = useState([]);
  const [verifications, setVerifications] = useState([]);
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [photos, setPhotos] = useState({});
  const [buildingDraft, setBuildingDraft] = useState({ name: '', building_code: '', address_text: '', landmark: '', description: '', image_url: '' });
  const [floorDraft, setFloorDraft] = useState({ building_id: '', floor_number: '', name: '', description: '' });
  const [categoryDraft, setCategoryDraft] = useState({ name: '', image_url: '', description: '' });
  const [shopDraft, setShopDraft] = useState({
    name: '', short_description: '', description: '', phone: '', whatsapp: '', email: '', website: '',
    category_ids: [], building_id: '', floor_id: '',
  });
  const [shopFiles, setShopFiles] = useState([]);
  const [uploadingShop, setUploadingShop] = useState(null);
  const [uploadingBuilding, setUploadingBuilding] = useState(null);

  async function refreshWorkspace(token = accessToken) {
    const [buildingData, floorData, categoryData, businessData, reportData, verificationData, userData, auditData] = await Promise.all([
      apiRequest('/api/admin/buildings', { token }),
      apiRequest('/api/admin/floors', { token }),
      apiRequest('/api/admin/categories', { token }),
      apiRequest('/api/admin/businesses', { token }),
      apiRequest('/api/admin/reports', { token }),
      apiRequest('/api/admin/verifications', { token }),
      apiRequest('/api/users', { token }),
      apiRequest('/api/audit', { token }),
    ]);
    setBuildings(buildingData);
    setFloors(floorData);
    setCategories(categoryData);
    setBusinesses(businessData);
    setReports(reportData);
    setVerifications(verificationData);
    setUsers(userData);
    setAuditLogs(auditData);
    setPhotos(emptyPhotos(businessData));

    const photoEntries = await Promise.all(businessData.map(async (business) => [
      business.id,
      await apiRequest(`/api/businesses/${business.id}/images`, { token }),
    ]));
    setPhotos(Object.fromEntries(photoEntries));
  }

  useEffect(() => {
    if (!accessToken) {
      setSessionLoading(false);
      setUser(null);
      return undefined;
    }

    const controller = new AbortController();
    setSessionLoading(true);
    apiRequest('/api/auth/me', { token: accessToken, signal: controller.signal })
      .then(async (profile) => {
        if (!['admin', 'super_admin'].includes(profile.role)) {
          throw new Error('This account does not have admin access.');
        }
        setUser(profile);
        await refreshWorkspace(accessToken);
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          if (requestError.message.includes('admin access')) setLoginError(requestError.message);
          else onSignOut();
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setSessionLoading(false);
      });
    return () => controller.abort();
  }, [accessToken]);

  async function handleLogin(event) {
    event.preventDefault();
    setBusy(true);
    setLoginError('');
    try {
      const result = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: { email, password },
      });
      if (!['admin', 'super_admin'].includes(result.user.role)) {
        throw new Error('This account does not have admin access.');
      }
      setUser(result.user);
      onAuthenticated(result.access_token);
    } catch (requestError) {
      setLoginError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function handlePasswordChange(event) {
    event.preventDefault();
    setPasswordError('');
    setMessage('');
    if (passwordDraft.new_password !== passwordDraft.confirm_password) {
      setPasswordError('The new passwords do not match.');
      return;
    }

    setBusy(true);
    try {
      const result = await apiRequest('/api/auth/change-password', {
        token: accessToken,
        method: 'POST',
        body: {
          current_password: passwordDraft.current_password,
          new_password: passwordDraft.new_password,
        },
      });
      setMessage(result.message);
      setPasswordDraft({ current_password: '', new_password: '', confirm_password: '' });
      setPasswordPanelOpen(false);
    } catch (requestError) {
      setPasswordError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleEmailChange(event) {
    event.preventDefault();
    setEmailError('');
    setMessage('');
    setBusy(true);
    try {
      const result = await apiRequest('/api/auth/change-email', {
        token: accessToken,
        method: 'POST',
        body: emailDraft,
      });
      setUser((current) => ({ ...current, email: result.email }));
      setMessage(result.message);
      setEmailDraft({ current_password: '', new_email: '' });
      setEmailPanelOpen(false);
    } catch (requestError) {
      setEmailError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function saveEntity(event, endpoint, body, successMessage, method = 'POST') {
    event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');
    try {
      await apiRequest(endpoint, { token: accessToken, method, body });
      setMessage(successMessage);
      await refreshWorkspace();
      onDirectoryChanged();
      return true;
    } catch (requestError) {
      setError(requestError.message);
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function createBuilding(event) {
    const isEditing = editing?.resource === 'buildings';
    const body = {
      ...buildingDraft,
      slug: slugify(buildingDraft.name),
      status: 'active',
    };
    const endpoint = isEditing ? `/api/admin/buildings/${editing.id}` : '/api/admin/buildings';
    if (await saveEntity(event, endpoint, body, isEditing ? 'Building updated.' : 'Building added.', isEditing ? 'PATCH' : 'POST')) {
      setBuildingDraft({ name: '', building_code: '', address_text: '', landmark: '', description: '', image_url: '' });
      setEditing(null);
    }
  }

  async function createFloor(event) {
    const isEditing = editing?.resource === 'floors';
    const body = {
      building_id: Number(floorDraft.building_id),
      floor_number: Number(floorDraft.floor_number),
      name: floorDraft.name.trim(),
      description: floorDraft.description || null,
      status: 'active',
    };
    const endpoint = isEditing ? `/api/admin/floors/${editing.id}` : '/api/admin/floors';
    if (await saveEntity(event, endpoint, body, isEditing ? 'Floor updated.' : 'Floor added to building.', isEditing ? 'PATCH' : 'POST')) {
      setFloorDraft({ building_id: floorDraft.building_id, floor_number: '', name: '', description: '' });
      setEditing(null);
    }
  }

  async function createCategory(event) {
    const isEditing = editing?.resource === 'categories';
    const body = {
      ...categoryDraft,
      slug: slugify(categoryDraft.name),
      status: 'active',
    };
    const endpoint = isEditing ? `/api/admin/categories/${editing.id}` : '/api/admin/categories';
    if (await saveEntity(event, endpoint, body, isEditing ? 'Category updated.' : 'Category added.', isEditing ? 'PATCH' : 'POST')) {
      setCategoryDraft({ name: '', image_url: '', description: '' });
      setEditing(null);
    }
  }

  async function loadShopFloors(buildingId) {
    setShopFloors([]);
    if (!buildingId) return;
    try {
      setShopFloors(await apiRequest(`/api/buildings/${buildingId}/floors`));
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  function editRecord(resource, record) {
    setEditing({ resource, id: record.id });
    setSection(resource);
    setError('');
    setMessage('');
    if (resource === 'buildings') {
      setBuildingDraft({
        name: record.name,
        building_code: record.building_code || '',
        address_text: record.address_text || '',
        landmark: record.landmark || '',
        description: record.description || '',
        image_url: record.image_url || '',
      });
    } else if (resource === 'floors') {
      setFloorDraft({
        building_id: String(record.building_id),
        floor_number: String(record.floor_number),
        name: record.name,
        description: record.description || '',
      });
    } else if (resource === 'categories') {
      setCategoryDraft({ name: record.name, image_url: record.image_url || '', description: record.description || '' });
    } else if (resource === 'businesses') {
      const buildingId = String(record.floor.building_id);
      setShopDraft({
        name: record.name,
        short_description: record.short_description || '',
        description: record.description || '',
        phone: record.phone || '',
        whatsapp: record.whatsapp || '',
        email: record.email || '',
        website: record.website || '',
        category_ids: record.categories.filter((category) => category.status === 'active').map((category) => category.id),
        building_id: buildingId,
        floor_id: String(record.floor_id),
      });
      loadShopFloors(buildingId);
    }
  }

  function cancelEdit() {
    setEditing(null);
    setBuildingDraft({ name: '', building_code: '', address_text: '', landmark: '', description: '', image_url: '' });
    setFloorDraft({ building_id: '', floor_number: '', name: '', description: '' });
    setCategoryDraft({ name: '', image_url: '', description: '' });
    setShopDraft({ name: '', short_description: '', description: '', phone: '', whatsapp: '', email: '', website: '', category_ids: [], building_id: '', floor_id: '' });
    setShopFloors([]);
  }

  async function changeRecordStatus(resource, record, nextStatus) {
    setError('');
    setMessage('');
    try {
      if (nextStatus === 'archived') {
        await apiRequest(`/api/admin/${resource}/${record.id}`, { token: accessToken, method: 'DELETE' });
      } else {
        await apiRequest(`/api/admin/${resource}/${record.id}`, {
          token: accessToken,
          method: 'PATCH',
          body: { status: nextStatus },
        });
      }
      setMessage(`${resource.slice(0, -1)} ${nextStatus === 'archived' ? 'archived' : 'restored'}.`);
      await refreshWorkspace();
      onDirectoryChanged();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function uploadBuildingImage(event, building) {
    event.preventDefault();
    const form = event.currentTarget;
    const file = new FormData(form).get('file');
    if (!(file instanceof File)) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('alt_text', `${building.name} building image`);
    setUploadingBuilding(building.id);
    setError('');
    setMessage('');
    try {
      await apiRequest(`/api/buildings/${building.id}/image`, {
        token: accessToken,
        method: 'POST',
        body: formData,
      });
      form.reset();
      setMessage(`Photo added to ${building.name}.`);
      await refreshWorkspace();
      onDirectoryChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUploadingBuilding(null);
    }
  }

  async function updateQueueRecord(resource, recordId, body) {
    setError('');
    setMessage('');
    try {
      await apiRequest(`/api/admin/${resource}/${recordId}`, {
        token: accessToken,
        method: 'PATCH',
        body,
      });
      setMessage(`${resource === 'reports' ? 'Report' : 'Verification'} updated.`);
      await refreshWorkspace();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function createShop(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setMessage('');
    try {
      const isEditing = editing?.resource === 'businesses';
      const endpoint = isEditing ? `/api/admin/businesses/${editing.id}` : '/api/admin/businesses';
      const result = await apiRequest(endpoint, {
        token: accessToken,
        method: isEditing ? 'PATCH' : 'POST',
        body: {
          name: shopDraft.name.trim(),
          slug: slugify(shopDraft.name),
          short_description: shopDraft.short_description || null,
          description: shopDraft.description || null,
          phone: shopDraft.phone || null,
          email: shopDraft.email || null,
          category_ids: shopDraft.category_ids.map(Number),
          floor_id: Number(shopDraft.floor_id),
          status: 'active',
          verification_status: 'unverified',
        },
      });

      let imageError = '';
      for (const file of isEditing ? [] : shopFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('alt_text', `${shopDraft.name} photo`);
        try {
          await apiRequest(`/api/businesses/${result.id}/images`, {
            token: accessToken,
            method: 'POST',
            body: formData,
          });
        } catch (requestError) {
          imageError = requestError.message;
          break;
        }
      }

      setMessage(imageError ? `Business saved, but an image could not be uploaded: ${imageError}` : isEditing ? 'Business updated.' : 'Business added to the selected floor.');
      setShopDraft({ ...shopDraft, name: '', short_description: '', description: '', phone: '', whatsapp: '', email: '', website: '' });
      setShopFiles([]);
      setEditing(null);
      await refreshWorkspace();
      onDirectoryChanged();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  async function uploadMoreImages(event, business) {
    event.preventDefault();
    const form = event.currentTarget;
    const files = Array.from(new FormData(form).getAll('files'));
    if (!files.length) return;
    setUploadingShop(business.id);
    setError('');
    setMessage('');
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('alt_text', `${business.name} photo`);
        await apiRequest(`/api/businesses/${business.id}/images`, {
          token: accessToken,
          method: 'POST',
          body: formData,
        });
      }
      const updatedPhotos = await apiRequest(`/api/businesses/${business.id}/images`, { token: accessToken });
      setPhotos((current) => ({ ...current, [business.id]: updatedPhotos }));
      setMessage(`Photos added to ${business.name}.`);
      onDirectoryChanged();
      form.reset();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUploadingShop(null);
    }
  }

  async function removeImage(business, image) {
    setError('');
    setMessage('');
    try {
      await apiRequest(`/api/businesses/${business.id}/images/${image.id}`, {
        token: accessToken,
        method: 'DELETE',
      });
      const updatedPhotos = await apiRequest(`/api/businesses/${business.id}/images`, { token: accessToken });
      setPhotos((current) => ({ ...current, [business.id]: updatedPhotos }));
      setMessage('Photo removed.');
      onDirectoryChanged();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  if (sessionLoading) {
    return <main className="app-shell admin-shell"><div className="loading-state">Checking admin access…</div></main>;
  }

  if (!user) {
    return (
      <main className="app-shell admin-shell">
        <header className="topbar">
          <a className="brand" href="/" onClick={(event) => { event.preventDefault(); onBack(); }}>
            <span className="brand-mark" aria-hidden="true">M</span><span>Merkato <strong>Directory</strong></span>
          </a>
          <button className="admin-back-link" type="button" onClick={onBack}>Back to directory</button>
        </header>
        <section className="admin-login">
          <p className="admin-eyebrow">ADMINISTRATION</p>
          <h1>Sign in to manage Merkato.</h1>
          <p className="admin-subtitle">Use an administrator account to manage locations, shops, categories, and photos.</p>
          <form className="admin-form" onSubmit={handleLogin}>
            <label>Email<input required type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>Password<input required type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} /></label>
            {loginError && <p className="admin-error" role="alert">{loginError}</p>}
            <button className="admin-primary" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell admin-shell">
      <header className="topbar">
        <a className="brand" href="/" onClick={(event) => { event.preventDefault(); onBack(); }}>
          <span className="brand-mark" aria-hidden="true">M</span><span>Merkato <strong>Directory</strong></span>
        </a>
        <div className="admin-user">
          <span>{user.name}</span>
          <button type="button" onClick={() => { setPasswordPanelOpen((open) => !open); setPasswordError(''); }}>Change password</button>
          <button type="button" onClick={() => { setEmailDraft({ current_password: '', new_email: user.email }); setEmailPanelOpen((open) => !open); setEmailError(''); }}>Change email</button>
          <button type="button" onClick={onSignOut}>Sign out</button>
        </div>
      </header>

      <div className="admin-heading">
        <div><p className="admin-eyebrow">DIRECTORY OPERATIONS</p><h1>Admin workspace</h1></div>
        <button className="admin-back-link" type="button" onClick={onBack}>Public directory</button>
      </div>

      {passwordPanelOpen && (
        <section className="password-panel" aria-labelledby="password-heading">
          <div className="password-panel-heading">
            <div><p className="admin-eyebrow">ACCOUNT SECURITY</p><h2 id="password-heading">Change password</h2></div>
            <button className="admin-back-link" type="button" onClick={() => setPasswordPanelOpen(false)}>Close</button>
          </div>
          <form className="password-form" onSubmit={handlePasswordChange}>
            <label>Current password<input required type="password" autoComplete="current-password" value={passwordDraft.current_password} onChange={(event) => setPasswordDraft({ ...passwordDraft, current_password: event.target.value })} /></label>
            <label>New password<input required type="password" minLength="8" maxLength="128" autoComplete="new-password" value={passwordDraft.new_password} onChange={(event) => setPasswordDraft({ ...passwordDraft, new_password: event.target.value })} /><span>Use at least 8 characters.</span></label>
            <label>Confirm new password<input required type="password" minLength="8" maxLength="128" autoComplete="new-password" value={passwordDraft.confirm_password} onChange={(event) => setPasswordDraft({ ...passwordDraft, confirm_password: event.target.value })} /></label>
            {passwordError && <p className="admin-error" role="alert">{passwordError}</p>}
            <div className="password-actions"><button className="admin-primary" type="submit" disabled={busy}>{busy ? 'Updating…' : 'Update password'}</button><button className="admin-back-link" type="button" onClick={() => setPasswordPanelOpen(false)}>Cancel</button></div>
          </form>
        </section>
      )}

      {emailPanelOpen && (
        <section className="password-panel" aria-labelledby="email-heading">
          <div className="password-panel-heading">
            <div><p className="admin-eyebrow">ACCOUNT DETAILS</p><h2 id="email-heading">Change email</h2></div>
            <button className="admin-back-link" type="button" onClick={() => setEmailPanelOpen(false)}>Close</button>
          </div>
          <form className="password-form email-form" onSubmit={handleEmailChange}>
            <label>Current password<input required type="password" autoComplete="current-password" value={emailDraft.current_password} onChange={(event) => setEmailDraft({ ...emailDraft, current_password: event.target.value })} /></label>
            <label>New email address<input required type="email" autoComplete="email" value={emailDraft.new_email} onChange={(event) => setEmailDraft({ ...emailDraft, new_email: event.target.value })} /></label>
            {emailError && <p className="admin-error" role="alert">{emailError}</p>}
            <div className="password-actions"><button className="admin-primary" type="submit" disabled={busy}>{busy ? 'Updating…' : 'Update email'}</button><button className="admin-back-link" type="button" onClick={() => setEmailPanelOpen(false)}>Cancel</button></div>
          </form>
        </section>
      )}

      <div className="admin-layout">
        <aside className="admin-sidebar" aria-label="Admin sections">
          {sections.map(([key, label]) => (
            <button key={key} className={section === key ? 'selected' : ''} type="button" onClick={() => { setSection(key); setError(''); setMessage(''); }}>
              {label}
            </button>
          ))}
        </aside>

        <section className="admin-content">
          {message && <div className="admin-notice success" role="status">{message}</div>}
          {error && <div className="admin-notice failure" role="alert">{error}</div>}

          {section === 'overview' && (
            <>
              <div className="admin-section-title"><p className="admin-eyebrow">AT A GLANCE</p><h2>Directory records</h2></div>
              <div className="admin-metrics">
                <div><span>Buildings</span><strong>{buildings.length}</strong></div>
                <div><span>Floors</span><strong>{floors.length}</strong></div>
                <div><span>Categories</span><strong>{categories.length}</strong></div>
                <div><span>Shops</span><strong>{businesses.length}</strong></div>
              </div>
              <div className="admin-section-title"><p className="admin-eyebrow">RELATIONAL MODEL</p><h2>Building → Floor → Business ↔ Category</h2></div>
              <p className="admin-copy">Each business belongs to one floor; its building is derived from that floor. Categories are managed independently and linked through the category relationship.</p>
            </>
          )}

          {section === 'buildings' && (
            <BuildingManagement draft={buildingDraft} onDraftChange={setBuildingDraft} onSubmit={createBuilding} busy={busy} buildings={buildings} uploadingBuilding={uploadingBuilding} onUploadImage={uploadBuildingImage} isEditing={editing?.resource === 'buildings'} onCancelEdit={cancelEdit} onEdit={(record) => editRecord('buildings', record)} onStatusChange={(record, status) => changeRecordStatus('buildings', record, status)} />
          )}

          {section === 'floors' && (
            <FloorManagement draft={floorDraft} onDraftChange={setFloorDraft} onSubmit={createFloor} busy={busy} buildings={buildings} floors={floors} isEditing={editing?.resource === 'floors'} onCancelEdit={cancelEdit} onEdit={(record) => editRecord('floors', record)} onStatusChange={(record, status) => changeRecordStatus('floors', record, status)} />
          )}

          {section === 'categories' && (
            <CategoryManagement draft={categoryDraft} onDraftChange={setCategoryDraft} onSubmit={createCategory} busy={busy} categories={categories} isEditing={editing?.resource === 'categories'} onCancelEdit={cancelEdit} onEdit={(record) => editRecord('categories', record)} onStatusChange={(record, status) => changeRecordStatus('categories', record, status)} />
          )}

          {section === 'businesses' && (
            <BusinessManagement
              draft={shopDraft}
              onDraftChange={setShopDraft}
              onBuildingChange={(buildingId) => {
                setShopDraft({ ...shopDraft, building_id: buildingId, floor_id: '' });
                loadShopFloors(buildingId);
              }}
              onSubmit={createShop}
              busy={busy}
              buildings={buildings}
              floors={shopFloors}
              categories={categories}
              businesses={businesses}
              photos={photos}
              shopFiles={shopFiles}
              setShopFiles={setShopFiles}
              uploadingShop={uploadingShop}
              onUpload={uploadMoreImages}
              onRemoveImage={removeImage}
              onStatusChange={(record, status) => changeRecordStatus('businesses', record, status)}
              isEditing={editing?.resource === 'businesses'}
              onCancelEdit={cancelEdit}
              onEdit={(record) => editRecord('businesses', record)}
            />
          )}

          {section === 'reports' && (
            <ReportsPanel
              reports={reports}
              businesses={businesses}
              onUpdate={(id, body) => updateQueueRecord('reports', id, body)}
            />
          )}
          {section === 'verification' && (
            <VerificationPanel
              verifications={verifications}
              businesses={businesses}
              onUpdate={(id, body) => updateQueueRecord('verifications', id, body)}
            />
          )}
          {section === 'users' && <UsersPanel users={users} />}
          {section === 'audit' && <AuditPanel auditLogs={auditLogs} users={users} />}
        </section>
      </div>
    </main>
  );
}