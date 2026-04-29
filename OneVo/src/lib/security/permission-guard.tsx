import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/use-auth-store';

interface ProtectedRouteProps {
  permission?: string;
  children: ReactNode;
}

export function ProtectedRoute({ permission, children }: ProtectedRouteProps) {
  const { user, hasPermission } = useAuthStore();
  const location = useLocation();

  if (!user) {
    return (
      <Navigate
        to={`/login?redirect=${encodeURIComponent(location.pathname)}`}
        replace
      />
    );
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/403" replace />;
  }

  return <>{children}</>;
}
