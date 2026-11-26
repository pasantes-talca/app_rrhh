import { z } from "zod";

const healthSchema = z.object({ status: z.literal("ok"), service: z.string(), version: z.string() });
export type Health = z.infer<typeof healthSchema>;

const userSchema = z.object({
  id: z.number(), username: z.string(), display_name: z.string().nullable(), role: z.string(),
  employee_id: z.number().nullable(), employee2_id: z.number().nullable(),
  must_change_password: z.boolean(), permissions: z.array(z.string()),
});
export type SessionUser = z.infer<typeof userSchema>;

const loginSchema = z.object({ user: userSchema, csrf_token: z.string() });
const employeePageSchema = z.object({
  items: z.array(z.object({ id: z.number(), employee_number: z.string().nullable(), display_name: z.string(), company: z.string().nullable(), sector: z.string().nullable(), position: z.string().nullable() })),
  total: z.number(), page: z.number(), page_size: z.number(),
});
export type EmployeePage = z.infer<typeof employeePageSchema>;
const employeeDetailSchema = z.object({ id:z.number(), numero_legajo:z.string().nullable(), numero_documento:z.string().nullable(), nombre:z.string().nullable(), apellido:z.string().nullable(), nombre_completo:z.string().nullable(), empresa:z.string().nullable(), sector:z.string().nullable(), puesto:z.string().nullable(), fecha_ingreso:z.string().nullable(), correo:z.string().nullable(), telefono:z.string().nullable(), fecha_nacimiento:z.string().nullable(), sexo:z.string().nullable(), domicilio:z.string().nullable(), provincia:z.string().nullable(), codigo_postal:z.string().nullable(), cuil:z.string().nullable(), licencia_conducir:z.string().nullable() });
export type EmployeeDetail = z.infer<typeof employeeDetailSchema>;

const vacationSummarySchema = z.object({
  year: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), start_date: z.string().nullable(),
  seniority_months: z.number().nullable(), entitled_days: z.coerce.number().nullable(), used_days: z.coerce.number(),
  reserved_days: z.coerce.number(), current_balance: z.coerce.number(), available_to_request: z.coerce.number(), source: z.string(),
});
export type VacationSummary = z.infer<typeof vacationSummarySchema>;

const vacationCalendarSchema = z.object({
  year: z.number(), month: z.number(), management_view: z.boolean(), people_count: z.number(),
  events: z.array(z.object({ key: z.string(), employee2_id: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), date_from: z.string(), date_to: z.string(), original_date_to: z.string().nullable().optional(), inconsistent_date: z.boolean(), days: z.coerce.number().nullable(), status: z.string(), kind: z.string(), detail: z.string().nullable() })),
});
export type VacationCalendar = z.infer<typeof vacationCalendarSchema>;

const absenceViewSchema = z.object({ id: z.number(), employee_number: z.string(), employee_name: z.string(), area: z.string().nullable(), plant: z.string().nullable(), type_code: z.number(), category: z.string(), description: z.string(), date_from: z.string(), date_to: z.string(), calendar_days: z.number() });
const absencePageSchema = z.object({ items: z.array(absenceViewSchema), total_records: z.number(), total_people: z.number(), total_days: z.number(), page: z.number(), page_size: z.number() });
export type AbsencePage = z.infer<typeof absencePageSchema>;
const seriesSchema = z.object({ labels: z.array(z.string()), values: z.array(z.coerce.number()) });
const absenceIndicatorsSchema = z.object({ date_from: z.string(), date_to: z.string(), active_employees: z.number(), absent_employees: z.number(), absent_workdays: z.number(), rate: z.number(), unjustified_days: z.number(), average_per_absent_employee: z.number(), variation: z.number().nullable(), categories: seriesSchema, people: seriesSchema, areas: seriesSchema, weekdays: seriesSchema, detail: z.array(absenceViewSchema) });
export type AbsenceIndicators = z.infer<typeof absenceIndicatorsSchema>;
const newsSchema = z.object({ id: z.number(), title: z.string(), content: z.string(), has_image: z.boolean(), visible_to_all: z.boolean(), is_important_date: z.boolean(), important_date: z.string().nullable(), company_id: z.number().nullable(), sector_id: z.number().nullable(), published_at: z.string().nullable() });
export type NewsItem = z.infer<typeof newsSchema>;
const sanctionSchema = z.object({ id: z.number(), employee_id: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), kind: z.string(), date: z.string(), date_from: z.string().nullable(), date_to: z.string().nullable(), days: z.coerce.number().nullable(), remaining_days: z.number().nullable(), reason: z.string(), description: z.string().nullable(), observations: z.string().nullable(), state: z.string(), has_file: z.boolean(), original_filename: z.string().nullable(), notified_at: z.string().nullable() });
export type Sanction = z.infer<typeof sanctionSchema>;
const sanctionSummarySchema = z.object({ total: z.number(), drafts: z.number(), notified: z.number(), suspensions: z.number(), items: z.array(sanctionSchema) });
const sanctionEmployeeSchema = z.object({ id: z.number(), display_name: z.string(), employee_number: z.string().nullable() });
export type SanctionEmployee = z.infer<typeof sanctionEmployeeSchema>;
const overtimeSchema = z.object({ id: z.number(), employee_id: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), date: z.string(), time_from: z.string().nullable(), time_to: z.string().nullable(), hours: z.coerce.number().nullable(), reason: z.string().nullable(), state: z.string(), observations: z.string().nullable(), manually_loaded_by_employee: z.boolean(), created_at: z.string() });
export type Overtime = z.infer<typeof overtimeSchema>;
const overtimeSummarySchema = z.object({ items: z.array(overtimeSchema), pending_manual: z.number() });
const documentTypeSchema = z.object({ id: z.number(), name: z.string() });
export type DocumentType = z.infer<typeof documentTypeSchema>;
const documentSchema = z.object({ id: z.number(), employee_id: z.number().nullable(), employee_name: z.string().nullable(), employee_number: z.string().nullable(), type_id: z.number(), type_name: z.string(), name: z.string(), original_filename: z.string().nullable(), visible_to_employee: z.boolean(), observations: z.string().nullable(), state: z.string(), source: z.string(), created_at: z.string() });
export type HrDocument = z.infer<typeof documentSchema>;
const documentFolderSchema = z.object({ employee_id: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), employee_sent: z.number(), shared_by_hr: z.number(), total: z.number(), last_document_at: z.string() });
export type DocumentFolder = z.infer<typeof documentFolderSchema>;
const receiptSchema = z.object({ id: z.number(), employee_id: z.number(), employee_name: z.string(), employee_number: z.string().nullable(), period: z.string(), deadline: z.string().nullable(), state: z.string(), viewed_at: z.string().nullable(), responded_at: z.string().nullable(), response: z.string().nullable(), employee_observation: z.string().nullable(), original_filename: z.string().nullable(), file_hash: z.string(), created_at: z.string() });
export type PayrollReceipt = z.infer<typeof receiptSchema>;
const receiptSummarySchema = z.object({ total: z.number(), pending: z.number(), compliant: z.number(), non_compliant: z.number(), items: z.array(receiptSchema) });
const catalogItemSchema = z.object({ id: z.number(), name: z.string() });
const profileCatalogsSchema = z.object({ companies: z.array(catalogItemSchema), sectors: z.array(catalogItemSchema), positions: z.array(catalogItemSchema), schedules: z.array(catalogItemSchema), supervisors: z.array(catalogItemSchema) });
export type ProfileCatalogs = z.infer<typeof profileCatalogsSchema>;
const profileSchema = z.object({ username: z.string(), display_name: z.string(), email: z.string().nullable(), has_photo: z.boolean(), employee_id: z.number().nullable(), source_employee2: z.boolean(), phone: z.string().nullable(), birth_date: z.string().nullable(), gender: z.string().nullable(), address: z.string().nullable(), province: z.string().nullable(), postal_code: z.string().nullable(), driver_license: z.string().nullable(), document_number: z.string().nullable(), cuil: z.string().nullable(), employee_number: z.string().nullable(), company_id: z.number().nullable(), sector_id: z.number().nullable(), position_id: z.number().nullable(), supervisor_id: z.number().nullable(), schedule_id: z.number().nullable(), workday_hours: z.coerce.number().nullable(), start_date: z.string().nullable(), employee_state: z.string().nullable() });
export type UserProfile = z.infer<typeof profileSchema>;
const adminSummarySchema = z.object({ users: z.number(), active_users: z.number(), operations_30_days: z.number(), unreviewed_errors: z.number(), open_sessions: z.number() });
const adminUserSchema = z.object({ id: z.number(), username: z.string(), display_name: z.string().nullable(), email: z.string().nullable(), employee_id: z.number().nullable(), role_id: z.number(), role: z.string(), active: z.boolean(), protected: z.boolean(), editable: z.boolean(), last_access: z.string().nullable() });
export type AdminUser = z.infer<typeof adminUserSchema>;
const adminRoleSchema = z.object({ id: z.number(), name: z.string() }); export type AdminRole = z.infer<typeof adminRoleSchema>;
const auditSchema = z.object({ id: z.number(), username: z.string().nullable(), module: z.string(), action: z.string(), endpoint: z.string().nullable(), method: z.string().nullable(), detail: z.string().nullable(), ip: z.string().nullable(), http_status: z.number().nullable(), created_at: z.string() });
const activityReportSchema = z.object({ username: z.string().nullable(), module: z.string(), action: z.string(), total: z.number() });
const systemErrorSchema = z.object({ id: z.number(), code: z.number().nullable(), endpoint: z.string().nullable(), method: z.string().nullable(), message: z.string(), ip: z.string().nullable(), reviewed: z.boolean(), review_reason: z.string().nullable(), created_at: z.string() });
const securitySettingsSchema = z.object({ password_min_length: z.number(), session_max_minutes: z.number() }); export type SecuritySettings = z.infer<typeof securitySettingsSchema>;
const sessionSchema = z.object({ id: z.string(), username: z.string(), ip: z.string().nullable(), started_at: z.string(), last_activity: z.string() });
const systemStatusSchema = z.object({ database_version: z.string(), database_latency_ms: z.number(), database_name: z.string(), schema_name: z.string(), python_version: z.string(), environment: z.string(), controls: z.record(z.string(), z.boolean()) });
const leaveTypeSchema = z.object({ id: z.number(), name: z.string(), description: z.string().nullable(), attachment_required: z.boolean() }); export type LeaveType = z.infer<typeof leaveTypeSchema>;
const leaveSchema = z.object({ id: z.number(), employee_id: z.number(), employee_name: z.string(), type_id: z.number(), type_name: z.string(), date_from: z.string(), date_to: z.string(), days: z.coerce.number().nullable(), reason: z.string().nullable(), status: z.string(), supervisor_status: z.string(), hr_observation: z.string().nullable(), supervisor_observation: z.string().nullable(), has_attachment: z.boolean(), created_at: z.string() }); export type Leave = z.infer<typeof leaveSchema>;
const organizationPersonSchema=z.object({title:z.string(),name:z.string()});const organizationTeamSchema=z.object({title:z.string(),members:z.array(z.string())});const organizationSchema=z.object({updated_at:z.string(),leadership:z.array(organizationPersonSchema),areas:z.array(z.object({name:z.string(),color:z.string(),manager:organizationPersonSchema,teams:z.array(organizationTeamSchema)})),total_people:z.number()});export type Organization=z.infer<typeof organizationSchema>;
const notificationSchema=z.object({id:z.number(),title:z.string(),message:z.string(),kind:z.string(),read:z.boolean(),created_at:z.string()});export type NotificationItem=z.infer<typeof notificationSchema>;const checklistSchema=z.object({id:z.number(),description:z.string(),completed:z.boolean(),created_at:z.string(),completed_at:z.string().nullable()});export type ChecklistItem=z.infer<typeof checklistSchema>;const calendarEventSchema=z.object({date:z.string(),title:z.string(),kind:z.string()});const dashboardSchema=z.object({name:z.string(),management:z.boolean(),birthday_today:z.boolean(),counts:z.object({active_employees:z.number().nullable(),pending_licenses:z.number(),pending_overtime:z.number(),received_documents:z.number(),pending_receipts:z.number()}),birthdays:z.array(z.object({employee_name:z.string(),date:z.string(),days:z.number(),age:z.number()})),upcoming_events:z.array(calendarEventSchema),calendar_events:z.array(calendarEventSchema),year:z.number(),month:z.number()});export type DashboardOverview=z.infer<typeof dashboardSchema>;
const importantDateSchema = z.object({ id: z.number(), date: z.string(), description: z.string().nullable() });
export type ImportantDate = z.infer<typeof importantDateSchema>;

let csrfToken = "";

async function request(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  if (init?.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (init?.method && init.method !== "GET" && path !== "/api/v1/auth/login") {
    if (!csrfToken) {
      const csrfResponse = await fetch("/api/v1/auth/csrf", { credentials: "include" });
      if (csrfResponse.ok) csrfToken = z.object({ csrf_token: z.string() }).parse(await csrfResponse.json()).csrf_token;
    }
    if (csrfToken) headers.set("X-CSRF-Token", csrfToken);
  }
  return fetch(path, { ...init, headers, credentials: "include" });
}

export async function getHealth(): Promise<Health> {
  const response = await request("/api/v1/health");
  if (!response.ok) throw new Error("No fue posible consultar el backend");
  return healthSchema.parse(await response.json());
}

export async function login(username: string, password: string): Promise<SessionUser> {
  const response = await request("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
  if (!response.ok) throw new Error("Usuario o contraseña incorrectos");
  const parsed = loginSchema.safeParse(await response.json());
  if (!parsed.success) throw new Error("El servidor devolvió una sesión inválida. Actualizá la página e intentá nuevamente.");
  const result = parsed.data;
  csrfToken = result.csrf_token;
  return result.user;
}

export async function getCurrentUser(): Promise<SessionUser> {
  const response = await request("/api/v1/auth/me");
  if (!response.ok) throw new Error("authentication_required");
  return userSchema.parse(await response.json());
}

export async function logout(): Promise<void> {
  const response = await request("/api/v1/auth/logout", { method: "POST" });
  if (!response.ok) throw new Error("No fue posible cerrar la sesión");
  csrfToken = "";
}

export async function getImportantDates(): Promise<ImportantDate[]> {
  const response = await request("/api/v1/important-dates");
  if (!response.ok) throw new Error("No fue posible cargar las fechas importantes");
  return z.array(importantDateSchema).parse(await response.json());
}

export async function createImportantDate(date: string, description: string): Promise<ImportantDate> {
  const response = await request("/api/v1/important-dates", { method: "POST", body: JSON.stringify({ date, description }) });
  if (!response.ok) throw new Error(response.status === 409 ? "Ya existe una fecha registrada para ese día" : "No fue posible guardar la fecha");
  return importantDateSchema.parse(await response.json());
}

export async function deleteImportantDate(id: number): Promise<void> {
  const response = await request(`/api/v1/important-dates/${String(id)}`, { method: "DELETE" });
  if (!response.ok) throw new Error("No fue posible eliminar la fecha");
}

export async function listEmployees(query = "", page = 1): Promise<EmployeePage> {
  const params = new URLSearchParams({ q: query, page: String(page), page_size: "25" });
  const response = await request("/api/v1/employees?" + params.toString());
  if (!response.ok) throw new Error(response.status === 403 ? "No tenés permiso para consultar empleados" : "No fue posible cargar los empleados");
  return employeePageSchema.parse(await response.json());
}

export async function getEmployee(id: number): Promise<EmployeeDetail> {
  const response = await request(`/api/v1/employees/${String(id)}`);
  if (!response.ok) throw new Error(response.status === 404 ? "Empleado no encontrado" : "No fue posible cargar la ficha");
  return employeeDetailSchema.parse(await response.json());
}

export async function getVacationSummary(year: number): Promise<VacationSummary> {
  const response = await request("/api/v1/vacations/summary?year=" + year.toString());
  if (!response.ok) throw new Error("No fue posible consultar el saldo de vacaciones");
  return vacationSummarySchema.parse(await response.json());
}

export async function getVacationCalendar(year: number, month: number): Promise<VacationCalendar> {
  const params = new URLSearchParams({ year: String(year), month: String(month) });
  const response = await request("/api/v1/vacations/calendar?" + params.toString());
  if (!response.ok) throw new Error("No fue posible consultar el calendario de vacaciones");
  return vacationCalendarSchema.parse(await response.json());
}

export async function getAbsencePage(query = ""): Promise<AbsencePage> {
  const now = new Date();
  const params = new URLSearchParams({ q: query, date_from: now.getFullYear().toString() + "-01-01", date_to: now.getFullYear().toString() + "-12-31" });
  const response = await request("/api/v1/absence?" + params.toString());
  if (!response.ok) throw new Error(response.status === 403 ? "No tenés permiso para consultar ausentismo" : "No fue posible cargar ausentismo");
  return absencePageSchema.parse(await response.json());
}

export async function getAbsenceIndicators(year: number, month: number): Promise<AbsenceIndicators> {
  const params = new URLSearchParams({ year: String(year), month: String(month) });
  const response = await request("/api/v1/indicators/absence?" + params.toString());
  if (!response.ok) throw new Error(response.status === 403 ? "No tenés permiso para consultar indicadores" : "No fue posible cargar indicadores");
  return absenceIndicatorsSchema.parse(await response.json());
}

export async function getNews(): Promise<NewsItem[]> {
  const response = await request("/api/v1/news");
  if (!response.ok) throw new Error("No fue posible cargar las noticias");
  return z.array(newsSchema).parse(await response.json());
}
export async function getFeaturedNews(): Promise<NewsItem[]> { const response=await request("/api/v1/news/featured");if(!response.ok)throw new Error("No fue posible cargar las novedades");return z.array(newsSchema).parse(await response.json()); }

export type NewsInput = { title: string; content: string; visibleToAll: boolean; isImportantDate: boolean; importantDate: string; image?: File };

export async function saveNews(input: NewsInput, id?: number): Promise<NewsItem> {
  const data = new FormData();
  data.set("title", input.title); data.set("content", input.content);
  data.set("visible_to_all", String(input.visibleToAll)); data.set("is_important_date", String(input.isImportantDate));
  if (input.isImportantDate && input.importantDate) data.set("important_date", input.importantDate);
  if (input.image) data.set("image", input.image);
  const path = id ? "/api/v1/news/" + id.toString() : "/api/v1/news";
  const response = await request(path, { method: id ? "PUT" : "POST", body: data });
  if (!response.ok) throw new Error("No fue posible guardar la noticia");
  return newsSchema.parse(await response.json());
}

export async function deleteNews(id: number): Promise<void> {
  const response = await request("/api/v1/news/" + id.toString(), { method: "DELETE" });
  if (!response.ok) throw new Error("No fue posible eliminar la noticia");
}

export async function getActiveSanctions(): Promise<Sanction[]> {
  const response = await request("/api/v1/sanctions/active");
  if (!response.ok) throw new Error("No fue posible cargar las sanciones vigentes");
  return z.array(sanctionSchema).parse(await response.json());
}

export async function getSanctions() {
  const response = await request("/api/v1/sanctions");
  if (!response.ok) throw new Error("No fue posible cargar las sanciones");
  return sanctionSummarySchema.parse(await response.json());
}

export async function getSanctionEmployees(): Promise<SanctionEmployee[]> {
  const response = await request("/api/v1/sanctions/employees");
  if (!response.ok) throw new Error("No fue posible cargar los empleados");
  return z.array(sanctionEmployeeSchema).parse(await response.json());
}

export type SanctionInput = { employeeId: number; kind: string; date: string; dateFrom: string; dateTo: string; days: string; reason: string; description: string; observations: string; state: string; attachment?: File };

export async function saveSanction(input: SanctionInput, id?: number): Promise<Sanction> {
  const data = new FormData();
  data.set("employee_id", String(input.employeeId)); data.set("kind", input.kind); data.set("sanction_date", input.date);
  if (input.kind === "Suspensión") { data.set("date_from", input.dateFrom); data.set("date_to", input.dateTo); data.set("days", input.days); }
  data.set("reason", input.reason); data.set("description", input.description); data.set("observations", input.observations); data.set("state", input.state);
  if (input.attachment) data.set("attachment", input.attachment);
  const response = await request(id ? "/api/v1/sanctions/" + id.toString() : "/api/v1/sanctions", { method: id ? "PUT" : "POST", body: data });
  if (!response.ok) throw new Error("No fue posible guardar la medida disciplinaria");
  return sanctionSchema.parse(await response.json());
}

export async function getOvertime() {
  const response = await request("/api/v1/overtime");
  if (!response.ok) throw new Error("No fue posible cargar las horas extra");
  return overtimeSummarySchema.parse(await response.json());
}

export async function createOvertime(date: string, hours: number, reason: string): Promise<Overtime> {
  const response = await request("/api/v1/overtime", { method: "POST", body: JSON.stringify({ date, hours, reason: reason || null }) });
  if (!response.ok) throw new Error(response.status === 409 ? "Ya enviaste horas extra para esa fecha" : "No fue posible enviar las horas extra");
  return overtimeSchema.parse(await response.json());
}

export async function decideOvertime(id: number, decision: "approve" | "reject", observation = ""): Promise<Overtime> {
  const init: RequestInit = decision === "reject" ? { method: "POST", body: JSON.stringify({ observation: observation || null }) } : { method: "POST" };
  const response = await request("/api/v1/overtime/" + id.toString() + "/" + decision, init);
  if (!response.ok) throw new Error("No fue posible resolver la solicitud");
  return overtimeSchema.parse(await response.json());
}

export async function importOvertime(file: File) {
  const data = new FormData(); data.set("report", file);
  const response = await request("/api/v1/overtime/import", { method: "POST", body: data });
  if (!response.ok) throw new Error("El reporte no tiene el formato esperado");
  return z.object({ created: z.number(), skipped: z.number(), errors: z.array(z.string()) }).parse(await response.json());
}

export async function deleteOvertime(ids: number[]): Promise<void> {
  const response = await request("/api/v1/overtime/delete", { method: "POST", body: JSON.stringify({ ids }) });
  if (!response.ok) throw new Error("No fue posible eliminar los registros");
}

export async function getDocumentTypes(): Promise<DocumentType[]> {
  const response = await request("/api/v1/documents/types");
  if (!response.ok) throw new Error("No fue posible cargar los tipos de documento");
  return z.array(documentTypeSchema).parse(await response.json());
}

export async function getDocuments(employeeId?: number, privateOnly = false): Promise<HrDocument[]> {
  const params = new URLSearchParams();
  if (employeeId) params.set("employee_id", String(employeeId));
  if (privateOnly) params.set("private_only", "true");
  const response = await request("/api/v1/documents?" + params.toString());
  if (!response.ok) throw new Error("No fue posible cargar los documentos");
  return z.array(documentSchema).parse(await response.json());
}

export async function getDocumentFolders(): Promise<DocumentFolder[]> {
  const response = await request("/api/v1/documents/folders");
  if (!response.ok) throw new Error("No fue posible cargar las carpetas por empleado");
  return z.array(documentFolderSchema).parse(await response.json());
}

export type DocumentInput = { typeId: number; name: string; employeeId?: number; visibleToEmployee: boolean; observations: string; attachment: File };
export async function uploadDocument(input: DocumentInput): Promise<HrDocument> {
  const data = new FormData(); data.set("type_id", String(input.typeId)); data.set("name", input.name); data.set("visible_to_employee", String(input.visibleToEmployee)); data.set("observations", input.observations); data.set("attachment", input.attachment);
  if (input.employeeId) data.set("employee_id", String(input.employeeId));
  const response = await request("/api/v1/documents", { method: "POST", body: data });
  if (!response.ok) throw new Error("No fue posible enviar el documento");
  return documentSchema.parse(await response.json());
}

export type DocumentUpdateInput = Omit<DocumentInput, "attachment"> & { attachment?: File };
export async function updateDocument(id: number, input: DocumentUpdateInput): Promise<HrDocument> {
  const data = new FormData(); data.set("type_id", String(input.typeId)); data.set("name", input.name); data.set("visible_to_employee", String(input.visibleToEmployee)); data.set("observations", input.observations);
  if (input.employeeId) data.set("employee_id", String(input.employeeId));
  if (input.attachment) data.set("attachment", input.attachment);
  const response = await request(`/api/v1/documents/items/${String(id)}`, { method: "PUT", body: data });
  if (!response.ok) throw new Error("No fue posible actualizar el documento");
  return documentSchema.parse(await response.json());
}

export async function setDocumentState(id: number, state: "Activo" | "Archivado"): Promise<HrDocument> {
  const response = await request("/api/v1/documents/items/" + id.toString() + "/state?state=" + state, { method: "PATCH" });
  if (!response.ok) throw new Error("No fue posible cambiar el estado");
  return documentSchema.parse(await response.json());
}

export async function getReceipts() {
  const response = await request("/api/v1/documents/receipts/list");
  if (!response.ok) throw new Error("No fue posible cargar los recibos");
  return receiptSummarySchema.parse(await response.json());
}

export type ReceiptInput = { employeeId: number; period: string; deadline: string; observations: string; attachment: File };
export async function publishReceipt(input: ReceiptInput): Promise<PayrollReceipt> {
  const data = new FormData(); data.set("employee_id", String(input.employeeId)); data.set("period", input.period); data.set("observations", input.observations); data.set("attachment", input.attachment); if (input.deadline) data.set("deadline", input.deadline);
  const response = await request("/api/v1/documents/receipts", { method: "POST", body: data });
  if (!response.ok) throw new Error(response.status === 409 ? "Ya existe un recibo para ese empleado y período" : "No fue posible publicar el recibo");
  return receiptSchema.parse(await response.json());
}

export async function respondReceipt(id: number, responseValue: "Conforme" | "Disconforme", observation: string): Promise<PayrollReceipt> {
  const response = await request("/api/v1/documents/receipts/" + id.toString() + "/respond", { method: "POST", body: JSON.stringify({ response: responseValue, observation: observation || null }) });
  if (!response.ok) throw new Error("No fue posible registrar la respuesta");
  return receiptSchema.parse(await response.json());
}

export async function getProfile(): Promise<UserProfile> {
  const response = await request("/api/v1/profile"); if (!response.ok) throw new Error("No fue posible cargar el perfil"); return profileSchema.parse(await response.json());
}

export async function getProfileCatalogs(): Promise<ProfileCatalogs> {
  const response = await request("/api/v1/profile/catalogs"); if (!response.ok) throw new Error("No fue posible cargar las opciones"); return profileCatalogsSchema.parse(await response.json());
}

export async function updateProfile(profile: UserProfile): Promise<UserProfile> {
  const body = { display_name: profile.display_name, email: profile.email, phone: profile.phone, birth_date: profile.birth_date, gender: profile.gender, address: profile.address, province: profile.province, postal_code: profile.postal_code, driver_license: profile.driver_license, document_number: profile.document_number, cuil: profile.cuil, employee_number: profile.employee_number, company_id: profile.company_id, sector_id: profile.sector_id, position_id: profile.position_id, supervisor_id: profile.supervisor_id, schedule_id: profile.schedule_id, workday_hours: profile.workday_hours, start_date: profile.start_date, employee_state: profile.employee_state };
  const response = await request("/api/v1/profile", { method: "PUT", body: JSON.stringify(body) }); if (!response.ok) throw new Error(response.status === 409 ? "Hay un correo, DNI, CUIL o legajo ya utilizado" : "No fue posible guardar el perfil"); return profileSchema.parse(await response.json());
}

export async function uploadProfilePhoto(photo: File): Promise<UserProfile> { const data = new FormData(); data.set("photo", photo); const response = await request("/api/v1/profile/photo", { method: "POST", body: data }); if (!response.ok) throw new Error("No fue posible guardar la foto"); return profileSchema.parse(await response.json()); }
export async function deleteProfilePhoto(): Promise<void> { const response = await request("/api/v1/profile/photo", { method: "DELETE" }); if (!response.ok) throw new Error("No fue posible eliminar la foto"); }
export async function changePassword(currentPassword: string, newPassword: string): Promise<void> { const response = await request("/api/v1/auth/password", { method: "POST", body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }) }); if (!response.ok) throw new Error(response.status === 400 ? "La contraseña actual no es correcta" : "No fue posible cambiar la contraseña"); }

export async function getAdminSummary() { const response = await request("/api/v1/administration/summary"); if (!response.ok) throw new Error("Acceso administrativo requerido"); return adminSummarySchema.parse(await response.json()); }
export async function getAdminUsers() { const response = await request("/api/v1/administration/users"); if (!response.ok) throw new Error("No fue posible cargar usuarios"); return z.array(adminUserSchema).parse(await response.json()); }
export async function getAdminRoles() { const response = await request("/api/v1/administration/roles"); if (!response.ok) throw new Error("No fue posible cargar roles"); return z.array(adminRoleSchema).parse(await response.json()); }
export type AdminUserInput = { username: string; display_name: string; email: string | null; employee_id: number | null; role_id: number; active: boolean; password?: string | null };
export async function saveAdminUser(input: AdminUserInput, id?: number) { const response = await request(id ? `/api/v1/administration/users/${String(id)}` : "/api/v1/administration/users", { method: id ? "PUT" : "POST", body: JSON.stringify(input) }); if (!response.ok) throw new Error(response.status === 403 ? "La cuenta está protegida" : response.status === 409 ? "El usuario ya existe" : "No fue posible guardar la cuenta"); return adminUserSchema.parse(await response.json()); }
export async function resetAdminPassword(id: number, password: string) { const response = await request(`/api/v1/administration/users/${String(id)}/password`, { method: "POST", body: JSON.stringify({ password }) }); if (!response.ok) throw new Error("No fue posible restablecer la contraseña"); }
export async function getUserPermissions(id: number) { const response = await request(`/api/v1/administration/users/${String(id)}/permissions`); if (!response.ok) throw new Error("No fue posible cargar permisos"); return z.array(z.string()).parse(await response.json()); }
export async function saveUserPermissions(id: number, permissions: string[]) { const response = await request(`/api/v1/administration/users/${String(id)}/permissions`, { method: "PUT", body: JSON.stringify({ permissions }) }); if (!response.ok) throw new Error("No fue posible guardar permisos"); }
export async function getAudit() { const response = await request("/api/v1/administration/audit"); if (!response.ok) throw new Error("No fue posible cargar auditoría"); return z.array(auditSchema).parse(await response.json()); }
export async function getActivityReport() { const response = await request("/api/v1/administration/reports/activity"); if (!response.ok) throw new Error("No fue posible cargar el reporte"); return z.array(activityReportSchema).parse(await response.json()); }
export async function getSystemErrors() { const response = await request("/api/v1/administration/errors"); if (!response.ok) throw new Error("No fue posible cargar incidencias"); return z.array(systemErrorSchema).parse(await response.json()); }
export async function reviewSystemError(id: number, reason: string) { const response = await request(`/api/v1/administration/errors/${String(id)}/review`, { method: "POST", body: JSON.stringify({ reason }) }); if (!response.ok) throw new Error("No fue posible marcar la incidencia"); return systemErrorSchema.parse(await response.json()); }
export async function getSecuritySettings() { const response = await request("/api/v1/administration/security"); if (!response.ok) throw new Error("No fue posible cargar seguridad"); return securitySettingsSchema.parse(await response.json()); }
export async function saveSecuritySettings(input: SecuritySettings) { const response = await request("/api/v1/administration/security", { method: "PUT", body: JSON.stringify(input) }); if (!response.ok) throw new Error("No fue posible guardar seguridad"); return securitySettingsSchema.parse(await response.json()); }
export async function getOpenSessions() { const response = await request("/api/v1/administration/sessions"); if (!response.ok) throw new Error("No fue posible cargar sesiones"); return z.array(sessionSchema).parse(await response.json()); }
export async function closeSession(id: string) { const response = await request("/api/v1/administration/sessions/" + id + "/close", { method: "POST" }); if (!response.ok) throw new Error("No fue posible cerrar la sesión"); }
export async function getSystemStatus() { const response = await request("/api/v1/administration/system"); if (!response.ok) throw new Error("No fue posible consultar el sistema"); return systemStatusSchema.parse(await response.json()); }
export async function getLeaveTypes() { const response = await request("/api/v1/licenses/types"); if (!response.ok) throw new Error("No fue posible cargar tipos de licencia"); return z.array(leaveTypeSchema).parse(await response.json()); }
export async function getLeaves() { const response = await request("/api/v1/licenses"); if (!response.ok) throw new Error("No fue posible cargar licencias"); return z.array(leaveSchema).parse(await response.json()); }
export type LeaveInput = { typeId: number; dateFrom: string; dateTo: string; days: number; reason: string; attachment?: File };
export async function createLeave(input: LeaveInput) { const data=new FormData();data.set("type_id",String(input.typeId));data.set("date_from",input.dateFrom);data.set("date_to",input.dateTo);data.set("days",String(input.days));data.set("reason",input.reason);if(input.attachment)data.set("attachment",input.attachment);const response=await request("/api/v1/licenses/upload",{method:"POST",body:data});if(!response.ok)throw new Error("No fue posible enviar la solicitud");return leaveSchema.parse(await response.json()); }
export async function resolveLeave(id:number,stage:"supervisor"|"hr",decision:"Aprobada"|"Rechazada",observation:string){const response=await request(`/api/v1/licenses/${String(id)}/${stage}-resolution`,{method:"POST",body:JSON.stringify({decision,observation:observation||null})});if(!response.ok)throw new Error(response.status===409?"La solicitud todavía no está lista para RR. HH.":"No fue posible resolver la solicitud");return leaveSchema.parse(await response.json());}
export async function getOrganization(q=""){const response=await request("/api/v1/organization?q="+encodeURIComponent(q));if(!response.ok)throw new Error("No fue posible cargar la estructura");return organizationSchema.parse(await response.json());}
export async function getDashboard(year:number,month:number){const response=await request(`/api/v1/dashboard?year=${String(year)}&month=${String(month)}`);if(!response.ok)throw new Error("No fue posible cargar el panel");return dashboardSchema.parse(await response.json());}
export async function getNotifications(){const response=await request("/api/v1/notifications");if(!response.ok)throw new Error("No fue posible cargar notificaciones");return z.array(notificationSchema).parse(await response.json());}
export async function readNotification(id:number){const response=await request(`/api/v1/notifications/${String(id)}/read`,{method:"POST"});if(!response.ok)throw new Error("No fue posible marcar la notificación");}
export async function readAllNotifications(){const response=await request("/api/v1/notifications/read-all",{method:"POST"});if(!response.ok)throw new Error("No fue posible marcar las notificaciones");}
export async function getChecklist(){const response=await request("/api/v1/checklist");if(!response.ok)throw new Error("No fue posible cargar el checklist");return z.array(checklistSchema).parse(await response.json());}
export async function createChecklistTask(description:string){const response=await request("/api/v1/checklist",{method:"POST",body:JSON.stringify({description})});if(!response.ok)throw new Error("No fue posible agregar la tarea");return checklistSchema.parse(await response.json());}
export async function toggleChecklistTask(id:number){const response=await request(`/api/v1/checklist/${String(id)}/toggle`,{method:"POST"});if(!response.ok)throw new Error("No fue posible actualizar la tarea");return checklistSchema.parse(await response.json());}
export async function deleteChecklistTask(id:number){const response=await request(`/api/v1/checklist/${String(id)}`,{method:"DELETE"});if(!response.ok)throw new Error("No fue posible eliminar la tarea");}

