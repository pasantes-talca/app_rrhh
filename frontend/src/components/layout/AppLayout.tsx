import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Bell, Building2, CalendarDays, CalendarX2, Clock3, FileText, LayoutDashboard, LogOut, Megaphone, Moon, ReceiptText, Settings, ShieldAlert, Sun, UserRound, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { cn } from "../../lib/utils";
import { getCurrentUser, getNotifications, logout } from "../../api/rrhh";

const links = [
  { to: "/", label: "Inicio", icon: LayoutDashboard },
  { to: "/estructura", label: "Estructura", icon: Building2 },
  { to: "/empleados", label: "Empleados", icon: Users, roles: ["administrador", "recursos_humanos"] },
  { to: "/vacaciones", label: "Mis vacaciones", icon: CalendarDays, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/licencias", label: "Licencias", icon: CalendarDays, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/ausentismo", label: "Ausentismo", icon: CalendarX2, roles: ["administrador", "recursos_humanos", "gerencia"] },
  { to: "/indicadores", label: "Indicadores", icon: Activity, roles: ["administrador", "gerencia"] },
  { to: "/noticias", label: "Noticias", icon: Megaphone },
  { to: "/fechas-importantes", label: "Fechas importantes", icon: CalendarDays },
  { to: "/sanciones", label: "Sanciones", icon: ShieldAlert, roles: ["recursos_humanos"] },
  { to: "/horas-extra", label: "Horas extra", icon: Clock3, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/documentos", label: "Documentos", icon: FileText, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/recibos", label: "Recibos", icon: ReceiptText, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/notificaciones", label: "Notificaciones", icon: Bell },
  { to: "/perfil", label: "Mi perfil", icon: UserRound, roles: ["empleado", "supervisor", "recursos_humanos", "gerencia"] },
  { to: "/administracion", label: "Administración", icon: Settings, roles: ["administrador"] },
];

export function AppLayout() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const session = useQuery({ queryKey: ["session"], queryFn: getCurrentUser, retry: false });
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: getNotifications, refetchInterval: 60_000 });
  const unread = notifications.data?.filter((item) => !item.read).length ?? 0;
  const closeSession = useMutation({ mutationFn: logout, onSuccess: () => { queryClient.clear(); void navigate("/login", { replace: true }); } });
  const visibleLinks = links.filter((link) => !link.roles || link.roles.includes(session.data?.role ?? ""));
  const [darkMode, setDarkMode] = useState(() => {
    const stored = window.localStorage.getItem("talca-theme");
    return stored ? stored === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    window.localStorage.setItem("talca-theme", darkMode ? "dark" : "light");
    return () => { document.documentElement.classList.remove("dark"); };
  }, [darkMode]);

  return <div className="min-h-screen bg-[#f7f4f2] lg:grid lg:grid-cols-[260px_1fr]">
    <aside className="border-b border-neutral-200 bg-white px-5 py-5 lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col lg:border-b-0 lg:border-r">
      <div className="mb-8 flex items-center gap-3"><img src="/logo-talca.png" alt="Talca" className="h-12 w-20 object-contain"/><div><p className="text-xs font-semibold text-neutral-500">Personas</p><p className="text-[10px] text-neutral-400">Siempre con vos</p></div></div>
      <nav className="flex gap-2 overflow-x-auto lg:max-h-[calc(100vh-9rem)] lg:flex-col lg:overflow-y-auto">
        {visibleLinks.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => cn("flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold", isActive ? "bg-talca-500 text-white" : "text-neutral-600 hover:bg-neutral-100")}><Icon className="size-4 shrink-0" />{label}{to === "/notificaciones" && unread > 0 && <span className="ml-auto rounded-full bg-talca-600 px-2 py-0.5 text-[10px] text-white">{unread}</span>}</NavLink>)}
      </nav>
      <div className="mt-auto hidden border-t border-neutral-200 pt-4 lg:block">
        {session.data?.role !== "administrador" && <NavLink to="/perfil" className="mb-2 flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold text-neutral-600 hover:bg-neutral-100"><UserRound className="size-4"/>Mi perfil</NavLink>}
        <button type="button" onClick={() => { closeSession.mutate(); }} className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold text-neutral-600 hover:bg-neutral-100"><LogOut className="size-4"/>Cerrar sesión</button>
      </div>
    </aside>
    <div><header className="flex h-20 items-center justify-between border-b border-neutral-200 bg-white px-6 lg:px-10"><div className="flex items-center gap-2 text-sm text-neutral-500"><Building2 className="size-4" /> Portal interno de RR. HH.</div><div className="flex items-center gap-3"><button type="button" onClick={() => { setDarkMode((current) => !current); }} className="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-semibold text-neutral-600 hover:bg-neutral-50" aria-label={darkMode ? "Activar modo claro" : "Activar modo oscuro"} aria-pressed={darkMode}>{darkMode ? <Sun className="size-5"/> : <Moon className="size-5"/>}<span className="hidden xl:inline">{darkMode ? "Modo claro" : "Modo oscuro"}</span></button><NavLink to="/notificaciones" aria-label={`Notificaciones: ${String(unread)} sin leer`} className="relative rounded-xl border p-2 text-neutral-600 hover:bg-neutral-50"><Bell className="size-5"/>{unread > 0 && <span className="absolute -right-2 -top-2 grid min-w-5 place-items-center rounded-full bg-talca-500 px-1 text-[10px] font-bold text-white">{unread}</span>}</NavLink><div className="hidden text-right sm:block"><strong className="block text-sm">{session.data?.display_name ?? session.data?.username}</strong><small className="capitalize text-neutral-500">{session.data?.role.replace("_", " ")}</small></div><button type="button" onClick={() => { closeSession.mutate(); }} disabled={closeSession.isPending} className="rounded-xl border p-2 text-neutral-600 hover:bg-neutral-50" aria-label="Cerrar sesión"><LogOut className="size-5"/></button></div></header><main className="p-6 lg:p-10"><Outlet /></main></div>
  </div>;
}

