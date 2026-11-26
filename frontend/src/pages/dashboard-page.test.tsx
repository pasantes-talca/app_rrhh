import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { DashboardPage } from "./dashboard-page";

test("muestra la identidad del nuevo portal", () => {
  render(<MemoryRouter><QueryClientProvider client={new QueryClient()}><DashboardPage /></QueryClientProvider></MemoryRouter>);
  expect(screen.getByText("Talca Personas")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: /Hola,/ })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Licencias pendientes/ })).toHaveAttribute("href", "/licencias");
});

