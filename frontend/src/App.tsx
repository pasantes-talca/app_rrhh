import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { RutaProtegida } from "./components/RutaProtegida";
import { AppLayout } from "./components/layout/AppLayout";

const DashboardPage=lazy(()=>import("./pages/dashboard-page").then(module=>({default:module.DashboardPage}))); const EmployeesPage=lazy(()=>import("./pages/employees-page").then(module=>({default:module.EmployeesPage}))); const EmployeeDetailPage=lazy(()=>import("./pages/employee-detail-page").then(module=>({default:module.EmployeeDetailPage}))); const LoginPage=lazy(()=>import("./pages/login-page").then(module=>({default:module.LoginPage}))); const VacationsPage=lazy(()=>import("./pages/vacations-page").then(module=>({default:module.VacationsPage}))); const AbsencePage=lazy(()=>import("./pages/absence-page").then(module=>({default:module.AbsencePage}))); const IndicatorsPage=lazy(()=>import("./pages/indicators-page").then(module=>({default:module.IndicatorsPage}))); const NewsPage=lazy(()=>import("./pages/news-page").then(module=>({default:module.NewsPage}))); const SanctionsPage=lazy(()=>import("./pages/sanctions-page").then(module=>({default:module.SanctionsPage}))); const OvertimePage=lazy(()=>import("./pages/overtime-page").then(module=>({default:module.OvertimePage}))); const DocumentsPage=lazy(()=>import("./pages/documents-page").then(module=>({default:module.DocumentsPage}))); const ReceiptsPage=lazy(()=>import("./pages/receipts-page").then(module=>({default:module.ReceiptsPage}))); const ProfilePage=lazy(()=>import("./pages/profile-page").then(module=>({default:module.ProfilePage}))); const AdministrationPage=lazy(()=>import("./pages/administration-page").then(module=>({default:module.AdministrationPage}))); const LicensesPage=lazy(()=>import("./pages/licenses-page").then(module=>({default:module.LicensesPage}))); const OrganizationPage=lazy(()=>import("./pages/organization-page").then(module=>({default:module.OrganizationPage}))); const NotificationsPage=lazy(()=>import("./pages/notifications-page").then(module=>({default:module.NotificationsPage}))); const ImportantDatesPage=lazy(()=>import("./pages/important-dates-page").then(module=>({default:module.ImportantDatesPage})));

const pending=<div className="grid min-h-64 place-items-center text-sm text-neutral-500">Cargando módulo…</div>;
function deferred(element:React.ReactNode){return <Suspense fallback={pending}>{element}</Suspense>}

export const router=createBrowserRouter([
  {path:"/login",element:deferred(<LoginPage/>)},
  {path:"/",element:<RutaProtegida><AppLayout/></RutaProtegida>,children:[
    {index:true,element:deferred(<DashboardPage/>)},
    {path:"estructura",element:deferred(<OrganizationPage/>)},
    {path:"empleados",element:deferred(<EmployeesPage/>)},
    {path:"empleados/:id",element:deferred(<EmployeeDetailPage/>)},
    {path:"vacaciones",element:deferred(<VacationsPage/>)},
    {path:"licencias",element:deferred(<LicensesPage/>)},
    {path:"ausentismo",element:deferred(<AbsencePage/>)},
    {path:"indicadores",element:deferred(<IndicatorsPage/>)},
    {path:"noticias",element:deferred(<NewsPage/>)},
    {path:"fechas-importantes",element:deferred(<ImportantDatesPage/>)},
    {path:"sanciones",element:deferred(<SanctionsPage/>)},
    {path:"horas-extra",element:deferred(<OvertimePage/>)},
    {path:"documentos",element:deferred(<DocumentsPage/>)},
    {path:"recibos",element:deferred(<ReceiptsPage/>)},
    {path:"notificaciones",element:deferred(<NotificationsPage/>)},
    {path:"perfil",element:deferred(<ProfilePage/>)},
    {path:"administracion",element:deferred(<AdministrationPage/>)},
  ]},
]);

