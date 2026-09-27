import { Navigate, Route, Routes } from 'react-router-dom';
import PublicHome from './pages/PublicHome';
import BuildingPage from './pages/BuildingPage';
import CategoryPage from './pages/CategoryPage';
import RoomPage from './pages/RoomPage';
import BusinessPage from './pages/BusinessPage';
import LoginPage from './pages/admin/LoginPage';
import Dashboard from './pages/admin/Dashboard';

function App() {
  return (
    <Routes>
      <Route path="/" element={<PublicHome />} />
      <Route path="/buildings/:buildingId" element={<BuildingPage />} />
      <Route path="/buildings/:buildingId/categories/:categoryId" element={<CategoryPage />} />
      <Route path="/buildings/:buildingId/categories/:categoryId/rooms/:roomId" element={<RoomPage />} />
      <Route path="/businesses/:businessId" element={<BusinessPage />} />
      <Route path="/admin/login" element={<LoginPage />} />
      <Route path="/admin" element={<Dashboard />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
