import { http, HttpResponse } from "msw";
import { expect, it, vi } from "vitest";
import { AuthContext } from "@/features/auth/auth-provider";
import { ProfileProvider } from "@/features/profiles/profile-provider";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { API_URL, currentUser } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProviders, screen, userEvent } from "@/tests/test-utils";

const authValue = { user: currentUser, isLoading: false, login: vi.fn(), register: vi.fn(), logout: vi.fn(), refreshSession: vi.fn() };
function SelectedName() { const { selected } = useProfile(); return <p>Selected: {selected?.first_name} {selected?.last_name}</p>; }

it("switches patient context without keeping the previous selected profile visible", async () => {
  server.use(http.get(`${API_URL}/patients`, () => HttpResponse.json([{ id: 10, first_name: "Fictional", last_name: "User", date_of_birth: "1990-01-01" }, { id: 11, first_name: "Shared", last_name: "Example", date_of_birth: "2010-01-01" }])), http.get(`${API_URL}/users/1/family-groups`, () => HttpResponse.json([])));
  const user = userEvent.setup();
  renderWithProviders(<AuthContext.Provider value={authValue}><ProfileProvider><ProfileSelector /><SelectedName /></ProfileProvider></AuthContext.Provider>);
  expect(await screen.findByText("Selected: Fictional User")).toBeVisible();
  await user.selectOptions(screen.getByLabelText("Viewing profile"), "11");
  expect(screen.getByText("Selected: Shared Example")).toBeVisible();
  expect(screen.queryByText("Selected: Fictional User")).not.toBeInTheDocument();
});
