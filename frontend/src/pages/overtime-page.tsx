import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Clock3, Download, Plus, Upload, X } from "lucide-react";
import { useState } from "react";
import { Button } from "../components/ui/button";
import { createOvertime, decideOvertime, getCurrentUser, getOvertime, importOvertime } from "../api/rrhh";

export function OvertimePage() {
  const client = useQueryClient();
  const session = useQuery({ queryKey: ["session"], queryFn: getCurrentUser, retry: false });
  const result = useQuery({ queryKey: ["overtime"], queryFn: getOvertime });
  const canManage = session.data ? ["administrador", "recursos_humanos"].includes(session.data.role) : false;
  const [manualOpen, setManualOpen] = useState(false);
  const [date, setDate] = useState(new Date().toLocaleDateString("en-CA"));
  const [hours, setHours] = useState("1");
  const [reason, setReason] = useState("");
  const [importMessage, setImportMessage] = useState("");
  const refresh = () => client.invalidateQueries({ queryKey: ["overtime"] });
  const create = useMutation({ mutationFn: () => createOvertime(date, Number(hours), reason), onSuccess: () => { void refresh(); setManualOpen(false); setReason(""); } });
  const decide = useMutation({ mutationFn: ({ id, action, observation }: { id: number; action: "approve" | "reject"; observation?: string }) => decideOvertime(id, action, observation), onSuccess: () => { void refresh(); } });
  const upload = useMutation({ mutationFn: importOvertime, onSuccess: (data) => { setImportMessage(data.created.toString() + " registros creados, " + data.skipped.toString() + " omitidos."); void refresh(); } });
  return (
    <section className="mx-auto max-w-7xl space-y-7">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div><p className="mb-2 text-xs font-black uppercase tracking-[.2em] text-talca-500">Jornada laboral</p><h1 className="text-3xl font-black">Horas extra</h1><p className="mt-2 text-neutral-500">{canManage ? "Revisión, importación y liquidación." : "Tus registros y solicitudes."}</p></div>
        <div className="flex flex-wrap gap-2">{canManage ? <><label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-talca-500 px-4 py-2.5 text-sm font-semibold text-white"><Upload className="size-4"/>Importar Voetime<input type="file" accept=".csv,.xls,.xlsx,.html,.htm" className="sr-only" onChange={(event) => { const file = event.target.files?.[0]; if (file) upload.mutate(file); }}/></label><Button variant="outline" asChild><a href="/api/v1/overtime/export"><Download className="size-4"/>Exportar Excel</a></Button></> : <Button onClick={() => { setManualOpen(true); }}><Plus className="size-4"/>Cargar horas</Button>}</div>
      </div>
      {importMessage && <p className="rounded-xl bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">{importMessage}</p>}
      {manualOpen && <article className="rounded-2xl border border-neutral-200 bg-white p-6 shadow-sm">
        <header className="mb-5 flex justify-between"><h2 className="font-black">Informar horas extra</h2><Button variant="ghost" onClick={() => { setManualOpen(false); }}><X className="size-4"/></Button></header>
        <form className="grid gap-4 md:grid-cols-3" onSubmit={(event) => { event.preventDefault(); create.mutate(); }}>
          <label className="text-sm font-semibold">Fecha<input type="date" max={new Date().toLocaleDateString("en-CA")} required value={date} onChange={(event) => { setDate(event.target.value); }} className="mt-2 h-11 w-full rounded-xl border border-neutral-300 px-3"/></label>
          <label className="text-sm font-semibold">Cantidad de horas<input type="number" min="0.25" max="16" step="0.25" required value={hours} onChange={(event) => { setHours(event.target.value); }} className="mt-2 h-11 w-full rounded-xl border border-neutral-300 px-3"/></label>
          <label className="text-sm font-semibold">Motivo<input maxLength={500} value={reason} onChange={(event) => { setReason(event.target.value); }} className="mt-2 h-11 w-full rounded-xl border border-neutral-300 px-3"/></label>
          <Button disabled={create.isPending} className="md:col-span-3">Enviar a Recursos Humanos</Button>
        </form>
      </article>}
      {canManage && result.data && <article className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm"><Clock3 className="mb-3 size-6 text-talca-500"/><p className="text-sm text-neutral-500">Solicitudes manuales pendientes</p><p className="text-3xl font-black">{result.data.pending_manual}</p></article>}
      <article className="overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm">
        {result.isError ? <p role="alert" className="p-8 text-talca-600">{result.error.message}</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-neutral-50 text-xs uppercase text-neutral-500"><tr><th className="p-4">Empleado</th><th className="p-4">Fecha</th><th className="p-4">Horas</th><th className="p-4">Estado</th>{canManage && <th className="p-4">Acciones</th>}</tr></thead><tbody>
          {result.data?.items.map((item) => <tr key={item.id} className="border-t border-neutral-100"><td className="p-4"><strong>{item.employee_name}</strong><small className="block text-neutral-500">{item.reason}</small></td><td className="p-4">{item.date}</td><td className="p-4 font-black">{item.hours ?? 0}</td><td className="p-4"><span className="rounded-full bg-neutral-100 px-3 py-1 text-xs font-bold">{item.state}</span></td>{canManage && <td className="p-4">{item.state === "Pendiente" && <div className="flex gap-2"><Button variant="outline" onClick={() => { decide.mutate({ id: item.id, action: "approve" }); }}><Check className="size-4"/></Button><Button variant="ghost" onClick={() => { const observation = window.prompt("Observación del rechazo") ?? ""; decide.mutate({ id: item.id, action: "reject", observation }); }}><X className="size-4"/></Button></div>}</td>}</tr>)}
        </tbody></table></div>}
      </article>
    </section>
  );
}

