import React, { useEffect, useState } from 'react';
import AdminPanel from './AdminPanel';

const PAGE_SIZE = 12;

function readUrlFilters() {
  const params = new URLSearchParams(window.location.search);
  return {
    query: params.get('q') || '',
    buildingId: params.get('building') || '',
    floorId: params.get('floor') || '',
    categoryId: params.get('category') || '',
    page: Math.max(1, Number(params.get('page')) || 1),
  };
}

function writeUrlFilters(filters, replace = false) {
  const params = new URLSearchParams();
  if (filters.query) params.set('q', filters.query);
  if (filters.buildingId) params.set('building', filters.buildingId);
  if (filters.floorId) params.set('floor', filters.floorId);
  if (filters.categoryId) params.set('category', filters.categoryId);
  if (filters.page > 1) params.set('page', String(filters.page));

  const isFiltered = params.size > 0;
  const target = `${isFiltered ? '/search' : '/'}${isFiltered ? `?${params.toString()}` : ''}`;
  window.history[replace ? 'replaceState' : 'pushState']({}, '', target);
}

async function fetchJson(url, signal) {
  const API_BASE = import.meta.env.VITE_API_TARGET || "";
  const response = await fetch(`${API_BASE}${url}`, { signal });
  if (!response.ok) {
    const result = await response.json().catch(() => null);
    throw new Error(typeof result?.detail === 'string' ? result.detail : `Request failed (${response.status})`);
  }
  return response.json();
}

export default function App() {
  const [activeView, setActiveView] = useState('directory');
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('merkato_admin_token') || '');
  const [dataRevision, setDataRevision] = useState(0);
  const [categories, setCategories] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [floorOptions, setFloorOptions] = useState([]);
  const [floorOptionsBuildingId, setFloorOptionsBuildingId] = useState('');
  const [floorLoading, setFloorLoading] = useState(false);
  const [filters, setFilters] = useState(readUrlFilters);
  const [searchInput, setSearchInput] = useState(() => readUrlFilters().query);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      fetchJson('/api/categories', controller.signal),
      fetchJson('/api/buildings', controller.signal),
    ])
      .then(([categoryData, buildingData]) => {
          setCategories(categoryData);
          setBuildings(buildingData);
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError('Directory filters could not be loaded. Check that the API is running.');
        }
      });

    return () => controller.abort();
  }, [dataRevision]);

  useEffect(() => {
    function restoreFromHistory() {
      const next = readUrlFilters();
      setFilters(next);
      setSearchInput(next.query);
    }
    window.addEventListener('popstate', restoreFromHistory);
    return () => window.removeEventListener('popstate', restoreFromHistory);
  }, []);

  function updateFilters(patch, replace = false) {
    const next = { ...filters, ...patch };
    setFilters(next);
    writeUrlFilters(next, replace);
  }

  useEffect(() => {
    const controller = new AbortController();
    if (!filters.buildingId) {
      setFloorOptions([]);
      setFloorOptionsBuildingId('');
      setFloorLoading(false);
      return () => controller.abort();
    }

    setFloorLoading(true);
    fetchJson(`/api/buildings/${filters.buildingId}/floors`, controller.signal)
      .then((options) => {
        setFloorOptions(options);
        setFloorOptionsBuildingId(filters.buildingId);
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setError(requestError.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setFloorLoading(false);
      });
    return () => controller.abort();
  }, [filters.buildingId]);

  useEffect(() => {
    if (
      filters.floorId
      && floorOptionsBuildingId === filters.buildingId
      && !floorLoading
      && !floorOptions.some((floor) => String(floor.id) === filters.floorId)
    ) {
      updateFilters({ floorId: '', page: 1 }, true);
    }
  }, [filters.buildingId, filters.floorId, floorOptionsBuildingId, floorLoading, floorOptions]);

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({ page: String(filters.page), limit: String(PAGE_SIZE) });
    if (filters.query) params.set('q', filters.query);
    if (filters.categoryId) params.set('category_id', filters.categoryId);
    if (filters.buildingId) params.set('building_id', filters.buildingId);
    if (filters.floorId) params.set('floor_id', filters.floorId);

    setLoading(true);
    setError('');
    fetchJson(`/api/search?${params.toString()}`, controller.signal)
      .then((data) => {
        setResults(data.results);
        setTotal(data.total);
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError('Businesses could not be loaded. Check that the API is running, then try again.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [filters, dataRevision]);

  function submitSearch(event) {
    event.preventDefault();
    updateFilters({ query: searchInput.trim(), page: 1 });
  }

  function clearFilters() {
    setSearchInput('');
    updateFilters({ query: '', categoryId: '', buildingId: '', floorId: '', page: 1 });
  }

  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  function saveAdminSession(token) {
    localStorage.setItem('merkato_admin_token', token);
    setAccessToken(token);
  }

  function clearAdminSession() {
    localStorage.removeItem('merkato_admin_token');
    setAccessToken('');
  }

  if (activeView === 'admin') {
    return (
      <AdminPanel
        accessToken={accessToken}
        onAuthenticated={saveAdminSession}
        onSignOut={clearAdminSession}
        onBack={() => setActiveView('directory')}
        onDirectoryChanged={() => setDataRevision((revision) => revision + 1)}
      />
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Merkato Directory home">
          <span className="brand-mark" aria-hidden="true">M</span>
          <span>Merkato <strong>Directory</strong></span>
        </a>
        <nav aria-label="Main navigation">
          <a className="active" href="/">Home</a>
          <button className="nav-admin" type="button" onClick={() => setActiveView('admin')}>Admin</button>
        </nav>
      </header>

      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">ADDIS ABABA · ETHIOPIA</p>
        <h1 id="page-title">Find your way<br />around Merkato.</h1>
        <p className="hero-copy">Discover shops, services, and exactly where to find them.</p>
        <form className="search-box" onSubmit={submitSearch}>
          <label className="search-input-wrap">
            <span className="sr-only">Search businesses</span>
            <span className="search-icon" aria-hidden="true">⌕</span>
            <input
              type="search"
              placeholder="What are you looking for?"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
            />
          </label>
          <button type="submit">Search</button>
        </form>
      </section>

      <section className="directory" aria-labelledby="directory-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow section-eyebrow">THE DIRECTORY</p>
            <h2 id="directory-heading">Businesses in Merkato</h2>
          </div>
          <p className="result-count" aria-live="polite">
            {loading ? 'Loading businesses…' : `${total.toLocaleString()} ${total === 1 ? 'business' : 'businesses'}`}
          </p>
        </div>

        <div className="filter-bar" aria-label="Filter businesses">
          <label>
            <span>Category</span>
            <select
              value={filters.categoryId}
              onChange={(event) => updateFilters({ categoryId: event.target.value, page: 1 })}
            >
              <option value="">All categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Building</span>
            <select
              value={filters.buildingId}
              onChange={(event) => updateFilters({ buildingId: event.target.value, floorId: '', page: 1 })}
            >
              <option value="">All buildings</option>
              {buildings.map((building) => (
                <option key={building.id} value={building.id}>{building.name}</option>
              ))}
            </select>
          </label>
          {filters.buildingId && (
            <label>
              <span>Floor</span>
              <select
                value={filters.floorId}
                disabled={floorLoading || floorOptionsBuildingId !== filters.buildingId}
                onChange={(event) => updateFilters({ floorId: event.target.value, page: 1 })}
              >
                <option value="">{floorLoading ? 'Loading floors…' : 'All floors'}</option>
                {floorOptions.map((floor) => (
                  <option key={floor.id} value={floor.id}>{floor.name}</option>
                ))}
              </select>
            </label>
          )}
          <button className="clear-button" type="button" onClick={clearFilters}>Clear filters</button>
        </div>

        {error && <div className="notice error-notice" role="alert">{error}</div>}

        {!error && !loading && total === 0 && (
          <div className="notice empty-state">
            <span className="empty-mark" aria-hidden="true">⌕</span>
            <h3>No businesses found</h3>
            <p>Try another search or clear your filters.</p>
            <button className="text-button" type="button" onClick={clearFilters}>Clear search and filters</button>
          </div>
        )}

        {loading && <div className="loading-state" role="status">Finding businesses…</div>}

        {!loading && !error && results.length > 0 && (
          <>
            <div className="business-grid">
              {results.map((business) => (
                <article className="business-card" key={business.id}>
                  {business.images?.[0] && (
                    <img
                      className="business-image"
                      src={business.images[0].file_url}
                      alt={business.images[0].alt_text || business.name}
                    />
                  )}
                  <div className="card-topline">
                    <span className="category-label">{business.categories.map((category) => category.name).join(' · ')}</span>
                    {business.verification_status === 'verified' && (
                      <span className="verified-label"><span aria-hidden="true">✓</span> Verified</span>
                    )}
                  </div>
                  <h3>{business.name}</h3>
                  <p className="business-description">
                    {business.short_description || business.description || 'A local business in Merkato.'}
                  </p>
                  <div className="location-list">
                    <p className="location-line">
                      <span aria-hidden="true">⌖</span>
                      <span>{business.floor.building_name} · {business.floor.name}</span>
                    </p>
                  </div>
                  {(business.phone || business.website) && (
                    <div className="card-contact">
                      {business.phone && <a href={`tel:${business.phone}`}>{business.phone}</a>}
                      {business.website && <a href={business.website} target="_blank" rel="noreferrer">Website ↗</a>}
                    </div>
                  )}
                </article>
              ))}
            </div>
            {pageCount > 1 && (
              <div className="pagination" aria-label="Directory pages">
                <button type="button" disabled={filters.page === 1} onClick={() => updateFilters({ page: filters.page - 1 })}>Previous</button>
                <span>Page {filters.page} of {pageCount}</span>
                <button type="button" disabled={filters.page === pageCount} onClick={() => updateFilters({ page: filters.page + 1 })}>Next</button>
              </div>
            )}
          </>
        )}
      </section>

      <footer className="page-footer">
        <span>Merkato Directory</span>
        <span>A clearer way to find your way.</span>
      </footer>
    </main>
  );
}