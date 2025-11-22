import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { Notifications } from '@/pages/Notifications';
import { PolicyChat } from '@/pages/PolicyChat';
import { Sidebar } from '@/components/Sidebar';
import { NotFoundComponent } from '@/components/404NotFound';

const AppLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div className="absolute left-0 top-0 h-full z-50" onClick={e => e.stopPropagation()}>
            <Sidebar onClose={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <Sidebar className="hidden md:flex" />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">

        {/* Mobile Header Toggle */}
        <div className="md:hidden bg-white h-16 border-b border-gray-200 flex items-center px-4 flex-shrink-0">
          <button className="text-slate-600" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
          <h1 className="text-xl font-bold text-slate-800 ml-4">Civic Flow</h1>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route path="*" element={<NotFoundComponent />} />
            <Route path="/" element={<Navigate to="/policy-chat" replace />} />
            <Route path="/policy-chat" element={<PolicyChat />} />
            <Route path="/notifications" element={<Notifications />} />
          </Routes>
        </div>

      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
};

export default App;