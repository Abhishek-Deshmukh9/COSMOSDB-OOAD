import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import ESIGauge from "../components/ESIGauge";

const API = "http://localhost:8000";

interface PlanetComparison {
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
  eccentricity: number | null;
  insolation_flux: number | null;
  discovery_year: number | null;
  discovery_method: string | null;
  constellation_name: string | null;
  star_temp: number | null;
  star_radius: number | null;
  star_mass: number | null;
  star_luminosity: number | null;
  planet_type?: string;
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

interface PlanetSearchResult {
  planet_id: number;
  planet_name: string;
  system_name: string;
  esi_score: number | null;
}

const CARD_BG = "rgba(255,255,255,0.03)";
const CARD_BORDER = "rgba(255,255,255,0.08)";

export default function ComparePlanets() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [selectedIds, setSelectedIds] = useState<number[]>(() => {
    const raw = searchParams.get("planet_ids") || searchParams.get("ids");
    if (raw) {
      return raw.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n));
    }
    return [1, 2]; // Default to first two planets if available
  });

  const [planets, setPlanets] = useState<PlanetComparison[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search state for adding planets
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PlanetSearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  // Load comparison data whenever selectedIds change
  useEffect(() => {
    if (selectedIds.length === 0) {
      setPlanets([]);
      return;
    }

    setLoading(true);
    setError(null);
    const query = selectedIds.map((id) => `planet_ids=${id}`).join("&");
    fetch(`${API}/api/planets/compare?${query}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Comparison API returned HTTP ${res.status}`);
        return res.json();
      })
      .then((data: PlanetComparison[]) => {
        setPlanets(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });

    // Update query params in URL
    setSearchParams({ planet_ids: selectedIds.join(",") });
  }, [selectedIds]);

  // Handle planet search for adding to comparison
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setSearching(true);
      fetch(`${API}/api/planets?q=${encodeURIComponent(searchQuery)}&limit=8`)
        .then((res) => res.json())
        .then((data) => {
          setSearchResults(data.items || []);
          setSearching(false);
        })
        .catch(() => setSearching(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const addPlanet = (id: number) => {
    if (selectedIds.includes(id)) return;
    if (selectedIds.length >= 4) {
      alert("You can compare a maximum of 4 planets simultaneously.");
      return;
    }
    setSelectedIds([...selectedIds, id]);
    setSearchQuery("");
    setSearchResults([]);
  };

  const removePlanet = (id: number) => {
    setSelectedIds(selectedIds.filter((pId) => pId !== id));
  };

  const getZoneBadge = (zone: string) => {
    switch (zone) {
      case "HABITABLE":
        return <span className="px-2.5 py-1 text-[11px] font-medium rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">Habitable Zone</span>;
      case "TOO_HOT":
        return <span className="px-2.5 py-1 text-[11px] font-medium rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30">Too Hot (Inner Orbit)</span>;
      case "TOO_COLD":
        return <span className="px-2.5 py-1 text-[11px] font-medium rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30">Too Cold (Outer Orbit)</span>;
      default:
        return <span className="px-2.5 py-1 text-[11px] font-medium rounded-full bg-white/10 text-white/50 border border-white/15">Unknown Zone</span>;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white pt-20 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.6)]" />
            <span className="text-[11px] tracking-[0.3em] uppercase text-amber-400/80 font-medium">
              Comparative Planetology
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extralight tracking-tight text-white/95">
            Exoplanet Comparison Matrix
          </h1>
          <p className="text-sm text-white/45 mt-2">
            Side-by-side scientific comparison of Earth Similarity Index, orbital architecture, and physical properties.
          </p>
        </div>

        {/* Search & Selector Toolbar */}
        <div className="rounded-2xl border p-5 relative" style={{ background: CARD_BG, borderColor: CARD_BORDER }}>
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <div className="flex-1 w-full relative">
              <input
                type="text"
                placeholder="Search planets to add to comparison (e.g. Kepler-452 b, Proxima b)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white/[0.05] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-amber-400/60"
              />
              {searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-neutral-900 border border-white/15 rounded-xl shadow-2xl z-50 overflow-hidden divide-y divide-white/5">
                  {searchResults.map((item) => (
                    <div
                      key={item.planet_id}
                      onClick={() => addPlanet(item.planet_id)}
                      className="px-4 py-3 hover:bg-white/10 cursor-pointer flex items-center justify-between transition-colors"
                    >
                      <div>
                        <div className="font-medium text-white/90 text-sm">{item.planet_name}</div>
                        <div className="text-xs text-white/40">{item.system_name}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {item.esi_score !== null && (
                          <span className="text-xs text-amber-400 font-mono">
                            ESI {(item.esi_score * 100).toFixed(0)}%
                          </span>
                        )}
                        <span className="text-xs bg-amber-400/20 text-amber-300 px-2 py-0.5 rounded">
                          + Compare
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Selected Chips */}
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-xs text-white/40 uppercase tracking-wider">Comparing ({planets.length}/4):</span>
              {planets.map((p) => (
                <span
                  key={p.planet_id}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-400/10 text-amber-300 border border-amber-400/30"
                >
                  {p.planet_name}
                  <button
                    onClick={() => removePlanet(p.planet_id)}
                    className="hover:text-white transition-colors cursor-pointer"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="py-20 text-center">
            <div className="w-8 h-8 rounded-full border-2 border-amber-400/40 border-t-amber-400 animate-spin mx-auto mb-3" />
            <p className="text-sm text-white/40 uppercase tracking-widest">Loading comparison vectors…</p>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300 text-sm">
            {error}
          </div>
        )}

        {!loading && planets.length === 0 && (
          <div className="text-center py-20 border border-dashed border-white/10 rounded-2xl">
            <p className="text-white/40 text-base">Select at least 2 planets to view comparison.</p>
          </div>
        )}

        {/* Comparison Grid */}
        {!loading && planets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {planets.map((p) => (
              <div
                key={p.planet_id}
                className="rounded-2xl border p-6 flex flex-col justify-between transition-all duration-300 hover:border-amber-400/40"
                style={{ background: CARD_BG, borderColor: CARD_BORDER }}
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-light text-white tracking-wide">{p.planet_name}</h2>
                      <p className="text-xs text-white/40 tracking-wider uppercase mt-0.5">
                        System: {p.system_name}
                      </p>
                    </div>
                    <button
                      onClick={() => removePlanet(p.planet_id)}
                      className="text-white/30 hover:text-red-400 transition-colors p-1"
                      title="Remove from comparison"
                    >
                      ✕
                    </button>
                  </div>

                  {/* ESI Dial & Classification */}
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5 mb-6">
                    <ESIGauge score={p.esi_score} size={64} />
                    <div>
                      <div className="text-xs uppercase tracking-widest text-white/40">Earth Similarity</div>
                      <div className="text-lg font-light text-amber-400">
                        {p.esi_score !== null ? `${(p.esi_score * 100).toFixed(1)}%` : "N/A"}
                      </div>
                      <div className="text-xs text-white/60 font-mono mt-0.5">
                        {p.planet_type || "Exoplanet"}
                      </div>
                    </div>
                  </div>

                  {/* Habitable Zone Badge */}
                  <div className="mb-6 flex justify-center">
                    {getZoneBadge(p.esi?.zone_status || "UNKNOWN")}
                  </div>

                  {/* Scientific Metrics Table */}
                  <div className="space-y-3 divide-y divide-white/[0.04] text-xs">
                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Radius</span>
                      <span className="text-white/80 font-mono">
                        {p.radius_earth ? `${p.radius_earth.toFixed(2)} R⊕` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Mass</span>
                      <span className="text-white/80 font-mono">
                        {p.mass_earth ? `${p.mass_earth.toFixed(2)} M⊕` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Bulk Density</span>
                      <span className="text-white/80 font-mono">
                        {p.planet_density ? `${p.planet_density.toFixed(2)} g/cm³` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Equilibrium Temp</span>
                      <span className="text-white/80 font-mono">
                        {p.planet_temp ? `${p.planet_temp.toFixed(0)} K (${(p.planet_temp - 273.15).toFixed(0)}°C)` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Semi-Major Axis</span>
                      <span className="text-white/80 font-mono">
                        {p.orbit_radius ? `${p.orbit_radius.toFixed(3)} AU` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Orbital Period</span>
                      <span className="text-white/80 font-mono">
                        {p.orbital_period ? `${p.orbital_period.toFixed(1)} days` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Eccentricity</span>
                      <span className="text-white/80 font-mono">
                        {p.eccentricity !== null && p.eccentricity !== undefined ? p.eccentricity.toFixed(3) : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Insolation Flux</span>
                      <span className="text-white/80 font-mono">
                        {p.insolation_flux ? `${p.insolation_flux.toFixed(2)} S⊕` : "—"}
                      </span>
                    </div>

                    <div className="flex justify-between pt-2">
                      <span className="text-white/40">Discovery</span>
                      <span className="text-white/80 font-mono">
                        {p.discovery_year || "—"} ({p.discovery_method || "Unknown"})
                      </span>
                    </div>
                  </div>
                </div>

                {/* View Details Action */}
                <div className="mt-6 pt-4 border-t border-white/5">
                  <button
                    onClick={() => navigate(`/planet/${p.planet_id}`)}
                    className="w-full py-2 px-3 text-xs uppercase tracking-wider text-amber-400 bg-amber-400/10 hover:bg-amber-400/20 rounded-xl transition-all cursor-pointer text-center"
                  >
                    View System Visualizer →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
