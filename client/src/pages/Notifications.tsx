import React from 'react';

export const Notifications: React.FC = () => {
  return (
    <div className="h-full overflow-y-auto p-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-4">Notifications</h1>
      <p className="text-slate-600">Welcome to the Civic Flow Notifications.</p>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 md:col-span-3">
             <h3 className="font-semibold text-lg mb-2">History</h3>
             <div className="space-y-4">
                {[...Array(10)].map((_, i) => (
                    <div key={i} className="p-4 bg-gray-50 rounded border border-gray-100">
                        <p className="text-sm text-gray-600">Notification item {i + 1}</p>
                    </div>
                ))}
             </div>
        </div>
      </div>
    </div>
  );
};
