import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';

const navItems = [
  { to: '/', label: 'Executive Dashboard' },
  // Add more pages here as they're built: Machines, Alerts, Maintenance, ERP...
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        <aside className="w-56 bg-bg1 border-r border-line p-4 flex flex-col gap-1">
          <div className="font-semibold text-t0 mb-4">Smart_Production</div>
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm ${isActive ? 'bg-acc/10 text-acc' : 'text-t1 hover:bg-bg3'}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </aside>
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
