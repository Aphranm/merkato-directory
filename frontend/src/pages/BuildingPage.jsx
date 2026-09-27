import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../api';

function PublicHome() {
  const [buildings, setBuildings] = useState([]);
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await apiFetch('/api/buildings');
        setBuildings(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const visibleBuildings = useMemo(() => {
    if (!query.trim()) return buildings;
    return buildings.filter((building) =>
      building.name.toLowerCase().includes(query.toLowerCase()) ||
      building.description?.toLowerCase().includes(query.toLowerCase()),
    );
  }, [buildings, query]);

  const handleSearch = async () => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const data = await apiFetch(`/api/search?q=${encodeURIComponent(query)}`);
      setSearchResults(data);
    } catch (error) {
      console.error(error);
      setSearchResults([]);
    }
  };

  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="header-inner container">
          <div className="brand-block">
            <span className="brand-mark">M</span>
            <div>
              <strong>Merkato Directory</strong>
              <small>Find shops, services, and businesses</small>
            </div>
          </div>
          <nav className="nav-inline">
            <Link to="/">Home</Link>
            <Link to="/admin/login">Admin</Link>
          </nav>
        </div>
      </header>

      <main className="container">
        <section className="hero panel">
          <div>
            <span className="eyebrow">Marketplace Directory</span>
            <h1>Discover businesses in your building and neighborhood.</h1>
            <p>Search for a shop, product, room, or service and move through the directory from building to business.</p>
            <div className="search-row">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by business, product, room, category, or phone"
                aria-label="Search directory"
              />
              <button onClick={handleSearch}>Search</button>
            </div>
          </div>
          <div className="hero-art">
            <div className="stat-card">
              <strong>{buildings.length}</strong>
              <span>Buildings</span>
            </div>
          </div>
        </section>

        {searchResults.length > 0 && (
          <section className="panel section-block">
            <h2>Search Results</h2>
            <div className="result-grid">
              {searchResults.map((result) => (
                <Link key={result.id} className="result-card" to={`/businesses/${result.id}`}>
                  <div className="result-copy">
                    <strong>{result.business_name}</strong>
                    <span>{result.building?.name} • {result.category?.name}</span>
                    <small>Room {result.room?.room_number || result.room?.name}</small>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="section-block">
          <div className="section-header">
            <h2>Browse Buildings</h2>
          </div>

          {loading ? (
            <p>Loading buildings...</p>
          ) : visibleBuildings.length === 0 ? (
            <div className="empty-state">No buildings match your search.</div>
          ) : (
            <div className="building-grid">
              {visibleBuildings.map((building) => (
                <Link key={building.id} to={`/buildings/${building.id}`} className="building-card">
                  {building.image_url && (
                    <img src={building.image_url} alt={building.name} loading="lazy" />
                  )}
                  <div className="card-body">
                    <h3>{building.name}</h3>
                    <p>{building.description}</p>
                    <span>{building.categories?.length || 0} categories</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default PublicHome;
