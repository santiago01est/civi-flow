import React from 'react';

export const Dashboard: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-4">Dashboard</h1>
      <p className="text-slate-600">Welcome to the Civic Flow Dashboard.</p>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="font-semibold text-lg mb-2">Recent Activity</h3>
          <p className="text-gray-500">No recent activity to show.</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="font-semibold text-lg mb-2">System Status</h3>
          <p className="text-green-600 font-medium">All systems operational</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="font-semibold text-lg mb-2">Quick Stats</h3>
          <p className="text-gray-500">Loading statistics...</p>
        </div>
      </div>
    </div>
  );
};
