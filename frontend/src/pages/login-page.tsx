import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LockKeyhole, Moon, Sun, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { login } from "../api/rrhh";

const schema = z.object({ username: z.string().min(1, "Ingresá tu usuario"), password: z.string().min(1, "Ingresá tu contraseña") });
type LoginValues = z.infer<typeof schema>;

function initialDarkMode() {
  const stored = localStorage.getItem("talca-theme");
  return stored ? stored === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [dark, setDark] = useState(initialDarkMode);
  const form = useForm<LoginValues>({ resolver: zodResolver(schema), defaultValues: { username: "", password: "" } });
  const mutation = useMutation({
    mutationFn: (values: LoginValues) => login(values.username, values.password),
    onSuccess: (user) => { queryClient.setQueryData(["session"], user); void navigate("/"); },
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("talca-theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <main className="talca-login-shell">
      <div className="talca-login-bubbles" aria-hidden="true">
        {Array.from({ length: 9 }, (_, index) => <i key={index} />)}
      </div>

      <div className="talca-login-brand">
        <img src="/logo-talca.png" alt="Talca" />
        <span>Personas · Siempre con vos</span>
      </div>

      <button className="talca-theme-button" type="button" onClick={() => { setDark((value) => !value); }} aria-label={dark ? "Activar modo claro" : "Activar modo oscuro"}>
        {dark ? <Sun /> : <Moon />}<span>{dark ? "Modo claro" : "Modo oscuro"}</span>
      </button>

      <section className="talca-login-card">
        <div className="talca-login-heading">
          <span>Portal de personas</span>
          <h1>Bienvenido</h1>
          <p>Ingresá tus datos para acceder al sistema.</p>
        </div>
        <form onSubmit={(event) => { void form.handleSubmit((values) => { mutation.mutate(values); })(event); }}>
          <label>Usuario</label>
          <div className="talca-login-input"><UserRound /><input autoFocus autoComplete="username" placeholder="Tu usuario" {...form.register("username")} /></div>
          <small>{form.formState.errors.username?.message}</small>

          <label>Contraseña</label>
          <div className="talca-login-input"><LockKeyhole /><input type="password" autoComplete="current-password" placeholder="Tu contraseña" {...form.register("password")} /></div>
          <small>{form.formState.errors.password?.message}</small>

          {mutation.isError && <p className="talca-login-error" role="alert">{mutation.error.message}</p>}
          <button className="talca-login-submit" disabled={mutation.isPending}>{mutation.isPending ? "Ingresando…" : "Ingresar"}</button>
        </form>
      </section>
      <p className="talca-login-footer">Portal interno de Recursos Humanos</p>
    </main>
  );
}
