import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button } from "../components/ui/button";
import { createImportantDate, deleteImportantDate, getCurrentUser, getImportantDates } from "../api/rrhh";

export function ImportantDatesPage() {
  const client = useQueryClient();
  const session = useQuery({ queryKey: ["session"], queryFn: getCurrentUser, retry: false });
  const dates = useQuery({ queryKey: ["important-dates"], queryFn: getImportantDates });
  const [date, setDate] = useState("");
  const [description, setDescription] = useState("");
  const canManage = ["administrador", "recursos_humanos"].includes(session.data?.role ?? "");
  const refresh = () => client.invalidateQueries({ queryKey: ["important-dates"] });
  const create = useMutation({ mutationFn: () => createImportantDate(date, description), onSuccess: () => { setDate(""); setDescription(""); void refresh(); } });
  const remove = useMutation({ mutationFn: deleteImportantDate, onSuccess: () => { void refresh(); } });

  return <section className="mx-auto max-w-5xl space-y-7"><div><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Calendario corporativo</p><h1 className="text-3xl font-black">Fechas importantes</h1><p className="mt-2 text-neutral-500">Feriados y días destacados visibles en el calendario de todos los usuarios.</p></div>
    {canManage && <form className="grid gap-4 rounded-2xl border bg-white p-5 shadow-sm sm:grid-cols-[180px_1fr_auto] sm:items-end" onSubmit={(event) => { event.preventDefault(); create.mutate(); }}><label className="text-sm font-semibold">Fecha<input type="date" required value={date} onChange={(event) => { setDate(event.target.value); }} className="mt-2 h-11 w-full rounded-xl border px-3"/></label><label className="text-sm font-semibold">Descripción<input required maxLength={200} value={description} onChange={(event) => { setDescription(event.target.value); }} className="mt-2 h-11 w-full rounded-xl border px-3" placeholder="Ej.: Día de la Independencia"/></label><Button disabled={create.isPending}><Plus className="size-4"/>Agregar</Button>{create.isError && <p role="alert" className="text-sm text-talca-600 sm:col-span-3">{create.error.message}</p>}</form>}
    <article className="overflow-hidden rounded-2xl border bg-white shadow-sm">{dates.isError && <p role="alert" className="p-6 text-talca-600">{dates.error.message}</p>}{dates.data?.length === 0 && <p className="p-10 text-center text-neutral-500">No hay fechas registradas.</p>}{dates.data?.map((item) => <div key={item.id} className="flex items-center gap-4 border-b p-5 last:border-0"><span className="grid size-11 place-items-center rounded-xl bg-talca-50 text-talca-600"><CalendarDays className="size-5"/></span><div className="flex-1"><strong>{item.description || "Fecha importante"}</strong><small className="block text-neutral-500">{new Date(`${item.date}T12:00:00`).toLocaleDateString("es-AR", { dateStyle: "long" })}</small></div>{canManage && <Button variant="ghost" aria-label="Eliminar fecha" onClick={() => { if (window.confirm("¿Eliminar esta fecha importante?")) remove.mutate(item.id); }}><Trash2 className="size-4"/></Button>}</div>)}</article>
  </section>;
}

