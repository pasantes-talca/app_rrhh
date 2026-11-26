import { useQuery } from "@tanstack/react-query";
import { CalendarX2, Search, UserRoundX } from "lucide-react";
import { useState } from "react";
import { getAbsencePage } from "../api/rrhh";

export function AbsencePage() {
  const [query, setQuery] = useState("");
  const result = useQuery({ queryKey: ["absence", query], queryFn: () => getAbsencePage(query), placeholderData: (previous) => previous });
  return <section className="mx-auto max-w-6xl space-y-7"><div><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Control</p><h1 className="text-3xl font-black">Ausentismo</h1><p className="mt-2 text-neutral-500">Registros consolidados del período actual.</p></div>
    {result.data && <div className="grid gap-4 sm:grid-cols-3">{[{ label: "Registros", value: result.data.total_records, icon: CalendarX2 }, { label: "Personas", value: result.data.total_people, icon: UserRoundX }, { label: "Días calendario", value: result.data.total_days, icon: CalendarX2 }].map(({ label, value, icon: Icon }) => <article key={label} className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><Icon className="mb-4 size-6 text-talca-500"/><p className="text-sm text-neutral-500">{label}</p><p className="text-3xl font-black">{value}</p></article>)}</div>}
    <article className="rounded-2xl border border-neutral-200 bg-white shadow-sm"><div className="flex items-center gap-3 border-b border-neutral-200 p-5"><Search className="size-4 text-neutral-400"/><input value={query} onChange={(event) => { setQuery(event.target.value); }} placeholder="Buscar persona o legajo" className="w-full outline-none"/></div>{result.isError ? <p role="alert" className="p-8 text-talca-600">{result.error.message}</p> : result.isPending ? <p className="p-8 text-neutral-500">Cargando…</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-neutral-50 text-xs uppercase text-neutral-500"><tr><th className="p-4">Empleado</th><th className="p-4">Categoría</th><th className="p-4">Desde</th><th className="p-4">Hasta</th><th className="p-4">Días</th></tr></thead><tbody>{result.data.items.map((item) => <tr key={item.id} className="border-t border-neutral-100"><td className="p-4"><strong>{item.employee_name}</strong><small className="block text-neutral-500">Legajo {item.employee_number}</small></td><td className="p-4">{item.category}</td><td className="p-4">{item.date_from}</td><td className="p-4">{item.date_to}</td><td className="p-4 font-bold">{item.calendar_days}</td></tr>)}</tbody></table></div>}</article>
  </section>;
}

