:root {
  --bg: #f5f7fb;
  --panel: #ffffff;
  --panel-alt: #eef3ff;
  --text: #162033;
  --muted: #5d677a;
  --card-border: #dfe7f7;
  --primary: #0f6fff;
  --primary-dark: #0a4fc4;
  --accent: #f59e0b;
  --success: #1e9d65;
  --shadow: 0 10px 30px rgba(14, 28, 52, 0.08);
  --radius: 18px;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: Inter, "Segoe UI", sans-serif;
  background: linear-gradient(180deg, #f8fafc 0%, #eef5ff 100%);
  color: var(--text);
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  display: block;
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  cursor: pointer;
}

.container {
  width: min(1120px, calc(100% - 24px));
  margin: 0 auto;
}

.page-shell,
.admin-shell {
  min-height: 100vh;
}

.topbar,
.admin-topbar {
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--card-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-inner,
.admin-topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), #6ea8ff);
  color: white;
  font-weight: 700;
}

.brand-block strong {
  display: block;
}

.brand-block small {
  color: var(--muted);
}

.nav-inline,
.admin-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-inline a,
.admin-actions a,
.admin-actions button {
  color: var(--text);
  font-weight: 600;
}

.admin-actions button {
  border: 1px solid var(--card-border);
  background: #fff;
  border-radius: 12px;
  padding: 8px 14px;
}

.hero {
  display: grid;
  grid-template-columns: 1.4fr 0.6fr;
  gap: 24px;
  align-items: center;
  padding: 28px;
  margin-top: 24px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.eyebrow {
  display: inline-block;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 12px;
}

.hero h1 {
  font-size: clamp(2rem, 4vw, 3.2rem);
  margin: 0 0 10px;
  line-height: 1.1;
}

.hero p {
  color: var(--muted);
  max-width: 60ch;
}

.search-row {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.search-row input,
.admin-form input,
.admin-form textarea,
.admin-form select {
  width: 100%;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid var(--card-border);
  background: #fafcff;
}

.search-row button,
.primary-button {
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  padding: 14px 20px;
  font-weight: 700;
  min-height: 48px;
}

.hero-art {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 220px;
  background: linear-gradient(135deg, #edf4ff, #dfeeff);
  border-radius: var(--radius);
  border: 1px solid var(--card-border);
}

.stat-card {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: var(--primary);
  background: rgba(15, 111, 255, 0.08);
  text-align: center;
}

.stat-card strong {
  display: block;
  font-size: 2.4rem;
}

.section-block {
  margin-top: 30px;
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.result-grid,
.building-grid,
.stack-grid,
.detail-grid {
  display: grid;
  gap: 16px;
}

.result-grid,
.building-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.stack-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.result-card,
.building-card,
.stack-card {
  display: block;
  overflow: hidden;
  border: 1px solid var(--card-border);
  background: white;
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.result-card {
  padding: 18px;
}

.building-card img,
.stack-card img,
.detail-header img {
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.card-body,
.stack-card > div {
  padding: 16px;
}

.building-card h3,
.stack-card strong,
.business-card h2 {
  margin: 0 0 10px;
}

.result-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.building-card p,
.stack-card p,
.business-card p,
.empty-state,
.admin-section p {
  color: var(--muted);
  margin: 0;
}

.empty-state {
  background: #f7f9ff;
  border: 1px dashed var(--card-border);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.page-space {
  padding: 30px 0 60px;
}

.breadcrumb {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  color: var(--muted);
  margin-bottom: 18px;
}

.detail-header {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
  padding: 0;
  overflow: hidden;
}

.detail-header > div {
  padding: 22px;
}

.detail-header h1 {
  margin: 0 0 12px;
  font-size: clamp(2rem, 5vw, 3rem);
}

.detail-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  margin-top: 24px;
}

.panel.business-card,
.panel.admin-section {
  padding: 20px;
}

.business-meta {
  display: grid;
  gap: 8px;
  margin: 18px 0;
}

.auth-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.auth-card {
  width: min(480px, 100%);
  background: white;
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 28px;
}

.auth-card h1 {
  margin-top: 0;
}

.auth-card label,
.admin-form label {
  display: block;
  margin-bottom: 14px;
  color: var(--muted);
  font-weight: 600;
}

.auth-card input,
.admin-form input,
.admin-form textarea,
.admin-form select {
  margin-top: 8px;
}

.form-error {
  background: rgba(220, 38, 38, 0.08);
  color: #b42318;
  padding: 10px 12px;
  border-radius: 10px;
  margin-bottom: 12px;
}

.admin-grid {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 24px;
  padding: 24px 0 60px;
}

.admin-sidebar {
  padding: 20px;
  height: fit-content;
}

.admin-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
  color: var(--muted);
  font-weight: 600;
}

.admin-main {
  display: grid;
  gap: 20px;
}

.admin-form {
  display: grid;
  gap: 12px;
}

.preview-image {
  max-height: 160px;
  object-fit: cover;
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--card-border);
}

.tree-list {
  display: grid;
  gap: 16px;
}

.tree-node {
  border: 1px solid var(--card-border);
  padding: 12px 14px;
  border-radius: 12px;
  background: #fafcff;
}

.tree-indent {
  margin-left: 16px;
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.tree-indent.inner {
  margin-top: 8px;
}

@media (max-width: 860px) {
  .hero,
  .detail-header,
  .admin-grid {
    grid-template-columns: 1fr;
  }

  .header-inner,
  .admin-topbar-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 12px 0;
    gap: 8px;
  }

  .nav-inline,
  .admin-actions {
    width: 100%;
    justify-content: space-between;
  }

  .search-row {
    flex-direction: column;
  }

  .search-row button,
  .primary-button {
    width: 100%;
  }
}
