import { useQuery } from "@tanstack/react-query";
import { CalendarDays, ChevronLeft, ChevronRight, Palmtree } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "../components/ui/button";
import { getVacationCalendar, getVacationSummary } from "../api/rrhh";

const months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
const weekdays = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

function monthDays(year: number, month: number): Array<Date | null> {
  const first = new Date(year, month - 1, 1);
  const padding = (first.getDay() + 6) % 7;
  const count = new Date(year, month, 0).getDate();
  return [...Array<Date | null>(padding).fill(null), ...Array.from({ length: count }, (_, index) => new Date(year, month - 1, index + 1))];
}

export function VacationsPage() {
  const today = new Date();
  const [cursor, setCursor] = useState({ year: today.getFullYear(), month: today.getMonth() + 1 });
  const summary = useQuery({ queryKey: ["vacation-summary", cursor.year], queryFn: () => getVacationSummary(cursor.year) });
  const calendar = useQuery({ queryKey: ["vacation-calendar", cursor.year, cursor.month], queryFn: () => getVacationCalendar(cursor.year, cursor.month) });
  const days = useMemo(() => monthDays(cursor.year, cursor.month), [cursor]);
  const move = (delta: number) => { const next = new Date(cursor.year, cursor.month - 1 + delta, 1); setCursor({ year: next.getFullYear(), month: next.getMonth() + 1 }); };
  return (
    <section className="mx-auto max-w-6xl space-y-7">
      <div><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Autogestión</p><h1 className="text-3xl font-black">Mis vacaciones</h1><p className="mt-2 text-neutral-500">Saldo, solicitudes e historial vacacional.</p></div>
      {summary.isError ? <p role="alert" className="rounded-2xl bg-talca-50 p-5 text-talca-600">{summary.error.message}</p> : summary.data && <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[{ label: "Días correspondientes", value: summary.data.entitled_days ?? "—" }, { label: "Saldo actual", value: summary.data.current_balance }, { label: "Días reservados", value: summary.data.reserved_days }, { label: "Disponibles para solicitar", value: summary.data.available_to_request }].map((item) => <article key={item.label} className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><Palmtree className="mb-4 size-6 text-talca-500"/><p className="text-sm text-neutral-500">{item.label}</p><p className="mt-1 text-3xl font-black">{item.value}</p></article>)}
      </div>}
      <article className="rounded-2xl border border-neutral-200 bg-white shadow-sm">
        <header className="flex items-center justify-between border-b border-neutral-200 p-5"><div><h2 className="flex items-center gap-2 font-black"><CalendarDays className="size-5 text-talca-500"/>Calendario</h2><p className="mt-1 text-sm text-neutral-500">{calendar.data?.management_view ? "Vista general de empleados" : "Tus vacaciones registradas"}</p></div><div className="flex items-center gap-2"><Button variant="outline" aria-label="Mes anterior" onClick={() => { move(-1); }}><ChevronLeft className="size-4"/></Button><span className="min-w-32 text-center font-bold">{months[cursor.month - 1]} {cursor.year}</span><Button variant="outline" aria-label="Mes siguiente" onClick={() => { move(1); }}><ChevronRight className="size-4"/></Button></div></header>
        <div className="grid grid-cols-7 border-b border-neutral-200 bg-neutral-50">{weekdays.map((day) => <div key={day} className="p-3 text-center text-xs font-bold uppercase text-neutral-500">{day}</div>)}</div>
        <div className="grid grid-cols-7">{days.map((day, index) => { const iso = day ? day.toLocaleDateString("en-CA") : ""; const events = calendar.data?.events.filter((event) => iso >= event.date_from && iso <= event.date_to) ?? []; return <div key={day?.toISOString() ?? "empty-" + index.toString()} className="min-h-28 border-b border-r border-neutral-100 p-2"><span className="text-sm font-semibold text-neutral-500">{day?.getDate()}</span>{events.slice(0, 3).map((event) => <div key={event.key} title={event.employee_name} className="mt-1 truncate rounded-md bg-sky-100 px-2 py-1 text-xs font-semibold text-sky-800">{event.employee_name}</div>)}</div>; })}</div>
      </article>
    </section>
  );
}

