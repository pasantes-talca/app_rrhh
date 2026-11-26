import { useQuery } from "@tanstack/react-query";
import { Search, Users } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { listEmployees } from "../api/rrhh";

export function EmployeesPage() {
  const [query,setQuery]=useState("");
  const employees=useQuery({queryKey:["employees",query],queryFn:()=>listEmployees(query),placeholderData:(previous)=>previous});
  return <section className="mx-auto max-w-6xl"><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Equipo</p><h1 className="text-3xl font-black">Directorio de empleados</h1><div className="mt-8 rounded-2xl border bg-white shadow-sm"><div className="flex items-center gap-3 border-b p-5"><Search className="size-4 text-neutral-400"/><input value={query} onChange={(event)=>{setQuery(event.target.value);}} placeholder="Buscar por nombre o legajo" className="w-full outline-none"/></div>{employees.isError?<p role="alert" className="p-8 text-center text-talca-600">{employees.error.message}</p>:employees.isPending?<p className="p-8 text-center text-neutral-500">Cargando empleados…</p>:<div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-neutral-50 text-xs uppercase text-neutral-500"><tr><th className="p-4">Legajo</th><th className="p-4">Nombre</th><th className="p-4">Empresa</th><th className="p-4">Sector</th><th className="p-4">Puesto</th></tr></thead><tbody>{employees.data.items.map(employee=><tr key={employee.id} className="border-t"><td className="p-4 font-semibold">{employee.employee_number??"—"}</td><td className="p-4 font-bold"><Link className="hover:text-talca-600 hover:underline" to={`/empleados/${String(employee.id)}`}>{employee.display_name}</Link></td><td className="p-4">{employee.company??"—"}</td><td className="p-4">{employee.sector??"—"}</td><td className="p-4">{employee.position??"—"}</td></tr>)}</tbody></table>{employees.data.items.length===0&&<div className="grid place-items-center p-12 text-neutral-500"><Users className="mb-3 size-8"/>Sin resultados</div>}</div>}</div></section>;
}

