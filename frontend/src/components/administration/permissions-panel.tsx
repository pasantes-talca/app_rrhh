import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { useState } from "react";
import { getUserPermissions, saveUserPermissions, type AdminUser } from "../../api/rrhh";
import { Button } from "../ui/button";

const modules = ["dashboard", "empleados", "licencias", "horas_extra", "sanciones", "noticias", "documentos", "estructura", "notificaciones", "ausentismo", "vacaciones", "indicadores"];
const actions = ["consultar", "crear", "editar", "anular", "exportar", "configurar"];

export function PermissionsPanel({ user }: { user: AdminUser }) {
  const client = useQueryClient();
  const result = useQuery({ queryKey: ["admin-permissions", user.id], queryFn: () => getUserPermissions(user.id) });
  const [selected, setSelected] = useState<string[] | null>(null);
  const effective = selected ?? result.data ?? [];
  const save = useMutation({ mutationFn: () => saveUserPermissions(user.id, effective), onSuccess: () => { setSelected(null); void client.invalidateQueries({ queryKey: ["admin-permissions", user.id] }); } });
  const toggle = (value: string) => { setSelected(effective.includes(value) ? effective.filter((item) => item !== value) : [...effective, value]); };
  return <div className="mt-5"><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr><th className="p-2 text-left">Módulo</th>{actions.map((action) => <th key={action} className="p-2 capitalize">{action}</th>)}</tr></thead><tbody>{modules.map((module) => <tr key={module} className="border-t"><th className="p-2 text-left capitalize">{module.replaceAll("_", " ")}</th>{actions.map((action) => { const value = `${module}:${action}`; return <td key={value} className="p-2 text-center"><input type="checkbox" aria-label={value} checked={effective.includes(value)} onChange={() => { toggle(value); }}/></td>; })}</tr>)}</tbody></table></div><Button className="mt-4" disabled={save.isPending || result.isLoading} onClick={() => { save.mutate(); }}><Save className="size-4"/>Guardar permisos</Button></div>;
}

