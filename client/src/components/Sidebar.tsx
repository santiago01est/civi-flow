import React from 'react';
import { 
  LayoutDashboard, 
  Gavel, 
  MessageSquareText, 
  FileText, 
  Users, 
  Settings, 
  LogOut, 
  User 
} from 'lucide-react';
import { NavItem } from '@/types';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, id: 'dashboard' },
  { label: 'Policy Chat', icon: MessageSquareText, id: 'policy-chat' },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="hidden md:flex flex-col w-64 bg-slate-900 text-gray-300 h-full flex-shrink-0">
      {/* Logo Area */}
      <div className="p-6 flex items-center gap-3 text-white mb-6">
        <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center">
          <span className="font-bold text-lg">C</span>
        </div>
        <span className="text-xl font-semibold tracking-tight">Civic Flow</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium transition-colors duration-200 rounded-md ${
                isActive 
                  ? 'bg-teal-600/20 text-teal-400 border-l-4 border-teal-500' 
                  : 'hover:bg-slate-800 hover:text-white border-l-4 border-transparent'
              }`}
            >
              <Icon size={20} />
              {item.label}
            </button>
          );
        })}
      </nav>

    </div>
  );
};