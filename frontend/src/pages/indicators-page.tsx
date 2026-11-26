import { useQuery } from "@tanstack/react-query";
import { Activity, CalendarDays, Users, UserX } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState } from "react";
import { getAbsenceIndicators } from "../api/rrhh";

function chartData(labels: string[], values: number[]) { return labels.map((name, index) => ({ name, value: values[index] ?? 0 })); }

export function IndicatorsPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const result = useQuery({ queryKey: ["absence-indicators", now.getFullYear(), month], queryFn: () => getAbsenceIndicators(now.getFullYear(), month) });
  return <section className="mx-auto max-w-7xl space-y-7"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Gestión</p><h1 className="text-3xl font-black">Indicadores</h1><p className="mt-2 text-neutral-500">Información consolidada de Recursos Humanos.</p></div><label className="text-sm font-semibold">Mes<select value={month} onChange={(event) => { setMonth(Number(event.target.value)); }} className="ml-3 rounded-xl border border-neutral-300 bg-white px-4 py-2"><option value={0}>Todo el año</option>{Array.from({ length: 12 }, (_, index) => <option key={index + 1} value={index + 1}>{index + 1}</option>)}</select></label></div>
    {result.isError ? <p role="alert" className="rounded-2xl bg-talca-50 p-5 text-talca-600">{result.error.message}</p> : result.data && <><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[{ label: "Empleados activos", value: result.data.active_employees, icon: Users }, { label: "Con ausencias", value: result.data.absent_employees, icon: UserX }, { label: "Días hábiles", value: result.data.absent_workdays, icon: CalendarDays }, { label: "Tasa de ausentismo", value: result.data.rate.toFixed(2) + "%", icon: Activity }].map(({ label, value, icon: Icon }) => <article key={label} className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><Icon className="mb-4 size-6 text-talca-500"/><p className="text-sm text-neutral-500">{label}</p><p className="text-3xl font-black">{value}</p></article>)}</div><div className="grid gap-5 lg:grid-cols-2"><article className="h-96 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><h2 className="mb-6 font-black">Ausencias por categoría</h2><ResponsiveContainer width="100%" height="85%"><BarChart data={chartData(result.data.categories.labels, result.data.categories.values)}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value" fill="#ed1c24" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></article><article className="h-96 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><h2 className="mb-6 font-black">Tasa por área</h2><ResponsiveContainer width="100%" height="85%"><BarChart data={chartData(result.data.areas.labels, result.data.areas.values)} layout="vertical"><CartesianGrid strokeDasharray="3 3"/><XAxis type="number"/><YAxis dataKey="name" type="category" width={110}/><Tooltip/><Bar dataKey="value" fill="#231f20" radius={[0,6,6,0]}/></BarChart></ResponsiveContainer></article></div></>}
  </section>;
}

