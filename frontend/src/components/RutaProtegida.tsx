import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { getCurrentUser } from "../api/rrhh";

export function RutaProtegida({ children }: { children: React.ReactNode }) {
  const session = useQuery({ queryKey: ["session"], queryFn: getCurrentUser, retry: false });
  if (session.isPending) return <div className="grid min-h-screen place-items-center bg-[#f7f4f2] text-sm text-neutral-500">Cargando sesión…</div>;
  if (session.isError) return <Navigate to="/login" replace />;
  return children;
}


