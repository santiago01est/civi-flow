import React from 'react';

export const NotFoundComponent: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-slate-600 bg-gray-50">
      <h1 className="text-6xl font-bold mb-4 text-teal-600">404</h1>
      <p className="text-2xl font-semibold mb-2">Page Not Found</p>
      <p className="text-gray-500">The page you are looking for doesn't exist or has been moved.</p>
    </div>
  );
};
