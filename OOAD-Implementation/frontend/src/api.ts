const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface Planet {
  planet_id: number;
  planet_name: string;
  system_id: number;
  system_name: string;
  radius_earth: number | null;
  mass_earth: number | null;
  planet_density: number | null;
  planet_temp: number | null;
  orbit_radius: number | null;
  orbital_period: number | null;
  discovery_year: number | null;
  discovery_method: string | null;
  constellation_name: string | null;
  esi_score: number | null;
  esi: {
    interior: number | null;
    surface: number | null;
    base: number | null;
    score: number | null;
    zone_status: string;
    hz_inner: number | null;
    hz_outer: number | null;
  };
}

export interface SystemSummary {
  system_id: number;
  system_name: string;
  distance_ly: number | null;
  constellation_name: string | null;
  num_planets: number;
}

export interface Star {
  star_id: number;
  star_name: string;
  spectral_type: string | null;
  star_temp: number | null;
  star_radius: number | null;
  star_mass: number | null;
}

export interface Page<T> {
  [key: string]: T[] | number;
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AnalyticsSummary {
  planet_count: number;
  system_count: number;
  average_esi: number | null;
  scored_planet_count: number;
  top_discovery_method: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => undefined) as { detail?: string } | undefined;
    throw new Error(body?.detail ?? `Request failed (${response.status}).`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function queryString(values: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  return search.toString();
}

export const api = {
  systems: (q: string) => request<Page<SystemSummary>>(`/api/systems?${queryString({ q, limit: 30 })}`),
  system: (id: number) => request<SystemSummary & { stars: Star[]; planets: Planet[] }>(`/api/systems/${id}`),
  planets: (q: string, method: string, sortBy: string) =>
    request<Page<Planet>>(`/api/planets?${queryString({ q, method, sort_by: sortBy, limit: 50 })}`),
  planet: (id: number) => request<Planet>(`/api/planets/${id}`),
  compare: (ids: number[]) =>
    request<Planet[]>(`/api/planets/compare?${ids.map((id) => `planet_ids=${id}`).join("&")}`),
  analytics: () => request<AnalyticsSummary>("/api/analytics/summary"),
  constellations: () => request<{ constellation_name: string; system_count: number }[]>("/api/constellations"),
  discoveryMethods: () => request<string[]>("/api/discovery-methods"),
};
