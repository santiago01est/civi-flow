import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { PolicyChat } from './pages/PolicyChat';
import { Menu, X } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('policy-chat');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'policy-chat':
        return <PolicyChat />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile Sidebar Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div className="absolute left-0 top-0 h-full z-50" onClick={e => e.stopPropagation()}>
             <Sidebar activeTab={activeTab} setActiveTab={(tab) => { setActiveTab(tab); setMobileMenuOpen(false); }} />
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

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
            {renderContent()}
        </div>

      </div>
    </div>
  );
};

export default App;