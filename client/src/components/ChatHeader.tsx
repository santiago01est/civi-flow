import React from 'react';
import { Search } from 'lucide-react';

export const ChatHeader: React.FC = () => {
  return (
    <header className="bg-white h-16 border-b border-gray-200 flex items-center justify-between px-4 md:px-8 flex-shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-slate-800">Policy Chat</h1>
      </div>
      
      <div className="hidden md:flex items-center relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input 
          type="text" 
          placeholder="Search past conversations..." 
          className="w-full pl-10 pr-4 py-2 rounded-full bg-gray-100 border-transparent focus:bg-white focus:border-teal-500 focus:ring-2 focus:ring-teal-200 transition-all outline-none text-sm"
        />
      </div>
    </header>
  );
};
