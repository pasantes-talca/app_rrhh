import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import "./index.css";
import { router } from "./App";

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000 } } });
const root = document.getElementById("root");
if (!root) throw new Error("No se encontró el contenedor principal");
createRoot(root).render(<StrictMode><QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider></StrictMode>);

