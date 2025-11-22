import React from 'react';
import { Plus } from 'lucide-react';

export const FloatingActionMenu: React.FC = () => {
  return (
    <button className="absolute bottom-28 right-8 w-14 h-14 bg-teal-500 hover:bg-teal-600 text-white rounded-full shadow-lg flex items-center justify-center transition-transform hover:scale-105 group z-20">
      <Plus size={28} />
      {/* Tooltip */}
      <div className="absolute right-full mr-3 bg-slate-800 text-white text-xs font-medium px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
        Quick Actions & Support
      </div>
    </button>
  );
};
