import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BriefcaseBusiness, UserRound } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { getEmployee } from "../api/rrhh";

export function EmployeeDetailPage() {
  const employeeId = Number(useParams().id);
  const result = useQuery({ queryKey: ["employee", employeeId], queryFn: () => getEmployee(employeeId), enabled: Number.isInteger(employeeId) && employeeId > 0 });
  if (result.isError) return <p role="alert" className="rounded-xl bg-talca-50 p-5 text-talca-600">{result.error.message}</p>;
  if (!result.data) return <p className="p-10 text-center text-neutral-500">Cargando ficha…</p>;
  const item = result.data;
  return <section className="mx-auto max-w-6xl space-y-7"><div className="flex items-center gap-4"><Button variant="outline" asChild><Link to="/empleados"><ArrowLeft className="size-4"/>Volver</Link></Button><div><p className="text-xs font-black uppercase tracking-[.2em] text-talca-500">Legajo {item.numero_legajo ?? "sin número"}</p><h1 className="text-3xl font-black">{item.nombre_completo || [item.nombre,item.apellido].filter(Boolean).join(" ")}</h1></div></div><div className="grid gap-6 lg:grid-cols-2"><Card icon={UserRound} title="Datos personales" rows={[["DNI",item.numero_documento],["CUIL",item.cuil],["Nacimiento",formatDate(item.fecha_nacimiento)],["Género",item.sexo],["Teléfono",item.telefono],["Correo",item.correo],["Domicilio",item.domicilio],["Provincia",item.provincia],["Código postal",item.codigo_postal],["Licencia de conducir",item.licencia_conducir]]}/><Card icon={BriefcaseBusiness} title="Datos laborales" rows={[["Empresa",item.empresa],["Sector",item.sector],["Puesto",item.puesto],["Fecha de ingreso",formatDate(item.fecha_ingreso)]]}/></div><p className="rounded-xl bg-sky-50 p-4 text-sm text-sky-800">Esta ficha consulta la fuente integrada Empleado2 en modo lectura. La edición permanece separada hasta aprobar la identidad canónica con Empleado.</p></section>;
}
function formatDate(value:string|null){return value?new Date(`${value}T12:00:00`).toLocaleDateString("es-AR"):null;}
function Card({icon:Icon,title,rows}:{icon:typeof UserRound;title:string;rows:[string,string|null][]}){return <article className="overflow-hidden rounded-2xl border bg-white shadow-sm"><header className="flex items-center gap-3 border-b p-5"><Icon className="size-5 text-talca-500"/><h2 className="font-black">{title}</h2></header><dl className="divide-y">{rows.map(([label,value])=><div key={label} className="grid grid-cols-[170px_1fr] gap-4 p-4 text-sm"><dt className="font-semibold text-neutral-500">{label}</dt><dd className="font-medium">{value||"—"}</dd></div>)}</dl></article>}

