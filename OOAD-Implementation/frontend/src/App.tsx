import { useEffect, useMemo, useState } from "react";
import { api, type AnalyticsSummary, type Planet, type Star, type SystemSummary } from "./api";

type View = "systems" | "planets" | "compare" | "analytics";

const format = (value: number | null | undefined, digits = 2) =>
  value == null ? "—" : value.toLocaleString(undefined, { maximumFractionDigits: digits });

export default function App() {
  const [view, setView] = useState<View>("systems");
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("");
  const [methods, setMethods] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState("name");
  const [systems, setSystems] = useState<SystemSummary[]>([]);
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [selectedSystem, setSelectedSystem] = useState<(SystemSummary & { stars: Star[]; planets: Planet[] }) | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<Planet | null>(null);
  const [comparison, setComparison] = useState<Planet[]>([]);
  const [compared, setCompared] = useState<Planet[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    void api.discoveryMethods().then((items) => {
      if (active) setMethods(items);
    }).catch((reason: unknown) => {
      if (active) setError(reason instanceof Error ? reason.message : "Discovery filters could not be loaded.");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    setError("");
    setLoading(true);
    const load = async () => {
      try {
        if (view === "systems") {
          const result = await api.systems(query);
          if (active) setSystems(result.systems as SystemSummary[]);
        } else if (view === "planets") {
          const result = await api.planets(query, method, sortBy);
          if (active) setPlanets(result.planets as Planet[]);
        } else if (view === "analytics") {
          const result = await api.analytics();
          if (active) setAnalytics(result);
        }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "The catalog could not be loaded.");
      } finally {
        if (active) setLoading(false);
      }
    };
    void load();
    return () => { active = false; };
  }, [view, query, method, sortBy]);

  const compareIds = useMemo(() => new Set(comparison.map((planet) => planet.planet_id)), [comparison]);

  async function openSystem(system: SystemSummary) {
    setError("");
    setLoading(true);
    try {
      setSelectedSystem(await api.system(system.system_id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "System details could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  async function openPlanet(planet: Planet) {
    setError("");
    setLoading(true);
    try {
      setSelectedPlanet(await api.planet(planet.planet_id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Planet details could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  function toggleComparison(planet: Planet) {
    setComparison((selected) => {
      if (selected.some((entry) => entry.planet_id === planet.planet_id)) {
        return selected.filter((entry) => entry.planet_id !== planet.planet_id);
      }
      if (selected.length >= 4) return selected;
      return [...selected, planet];
    });
  }

  async function runComparison() {
    setError("");
    try {
      setCompared(await api.compare(comparison.map((planet) => planet.planet_id)));
      setView("compare");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The comparison could not be loaded.");
    }
  }

  const visiblePlanets = view === "systems" && selectedSystem ? selectedSystem.planets : planets;

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#" onClick={() => { setView("systems"); setSelectedSystem(null); }}>
          <span className="brand-mark">C</span>
          <span>COSMODB<span className="brand-sub"> / EXOPLANET ATLAS</span></span>
        </a>
        <nav aria-label="Primary navigation">
          {(["systems", "planets", "compare", "analytics"] as View[]).map((item) => (
            <button key={item} className={view === item ? "nav-link active" : "nav-link"} onClick={() => {
              setView(item);
              if (item !== "systems") setSelectedSystem(null);
            }}>{item}</button>
          ))}
        </nav>
        <div className="live"><span /> CATALOG ONLINE</div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">A FIELD GUIDE TO OTHER WORLDS</p>
          <h1>Somewhere, a new<br /><em>world is waiting.</em></h1>
          <p className="hero-text">Explore the systems beyond our own. Browse confirmed exoplanets, inspect their host stars, and compare the worlds we have found.</p>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <span className="orbit orbit-one" /><span className="orbit orbit-two" />
          <span className="planet-dot" /><span className="star-core" />
        </div>
        <div className="hero-caption"><span>01</span> / THE SEARCH CONTINUES</div>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <div>
            <p className="eyebrow">CATALOG / {view.toUpperCase()}</p>
            <h2>{view === "systems" ? selectedSystem?.system_name ?? "Star systems" :
              view === "planets" ? "Known planets" : view === "compare" ? "Worlds side by side" : "A wider view"}</h2>
          </div>
          {view !== "analytics" && view !== "compare" && !selectedSystem && (
            <form className="search" onSubmit={(event) => { event.preventDefault(); setQuery(search.trim()); }}>
              <span aria-hidden="true">⌕</span>
              <input aria-label="Search catalog" placeholder={view === "systems" ? "Search star systems" : "Search planets or hosts"} value={search} onChange={(event) => setSearch(event.target.value)} />
              {view === "planets" && <>
                <select aria-label="Filter by discovery method" value={method} onChange={(event) => setMethod(event.target.value)}>
                  <option value="">All methods</option>{methods.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <select aria-label="Sort planets" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
                  <option value="name">Name</option><option value="esi">ESI score</option><option value="mass">Mass</option><option value="radius">Radius</option>
                </select>
              </>}
              <button type="submit">Search</button>
            </form>
          )}
          {view === "planets" && (
            <div className="compare-action">
              <span>{comparison.length}/4 selected</span>
              <button className="button-outline" disabled={comparison.length < 2} onClick={() => void runComparison()}>Compare worlds ↗</button>
            </div>
          )}
        </div>

        {error && <div className="notice error" role="alert">{error}</div>}
        {loading && <div className="notice">Loading catalog…</div>}

        {view === "systems" && !selectedSystem && !loading && (
          <div className="system-grid">
            {systems.map((system, index) => (
              <button className="system-card" key={system.system_id} onClick={() => void openSystem(system)}>
                <span className="card-index">SYS / {String(index + 1).padStart(2, "0")}</span>
                <span className="system-name">{system.system_name}</span>
                <span className="system-meta">{system.constellation_name ?? "Uncharted"} <i>·</i> {system.num_planets} planets</span>
                <span className="system-distance">{format(system.distance_ly)} <small>ly</small></span>
                <span className="card-arrow">↗</span>
              </button>
            ))}
            {!systems.length && <div className="empty">No star systems match this search.</div>}
          </div>
        )}

        {view === "systems" && selectedSystem && !loading && (
          <div className="detail-layout">
            <aside className="detail-aside">
              <button className="back-link" onClick={() => setSelectedSystem(null)}>← All systems</button>
              <p className="eyebrow">HOST SYSTEM</p>
              <h3>{selectedSystem.system_name}</h3>
              <p>{selectedSystem.constellation_name ?? "Constellation unassigned"}</p>
              <div className="metric-list">
                <span>Distance <b>{format(selectedSystem.distance_ly)} ly</b></span>
                <span>Planets <b>{selectedSystem.num_planets}</b></span>
                <span>Known stars <b>{selectedSystem.stars.length}</b></span>
              </div>
              <div className="star-list">
                <p className="eyebrow">CATALOGUED STARS</p>
                {selectedSystem.stars.map((star) => (
                  <div className="star-row" key={star.star_id}>
                    <strong>{star.star_name}</strong>
                    <span>{star.spectral_type ?? "Type unknown"} · {star.star_temp == null ? "—" : `${format(star.star_temp, 0)} K`}</span>
                  </div>
                ))}
              </div>
            </aside>
            <PlanetTable planets={visiblePlanets} onOpen={openPlanet} />
          </div>
        )}

        {view === "planets" && !loading && (
          <PlanetTable planets={planets} onOpen={openPlanet} selectable selected={compareIds} onToggle={toggleComparison} />
        )}

        {view === "compare" && !loading && (
          <div className="comparison">
            {compared.length >= 2 ? (
              <table>
                <thead><tr><th>ATTRIBUTE</th>{compared.map((planet) => <th key={planet.planet_id}>{planet.planet_name}</th>)}</tr></thead>
                <tbody>
                  {[
                    ["Host system", (planet: Planet) => planet.system_name],
                    ["Radius (R⊕)", (planet: Planet) => format(planet.radius_earth)],
                    ["Mass (M⊕)", (planet: Planet) => format(planet.mass_earth)],
                    ["Orbital period", (planet: Planet) => planet.orbital_period == null ? "—" : `${format(planet.orbital_period)} d`],
                    ["Surface temperature", (planet: Planet) => planet.planet_temp == null ? "—" : `${format(planet.planet_temp, 0)} K`],
                    ["Discovery method", (planet: Planet) => planet.discovery_method ?? "—"],
                    ["Earth Similarity Index", (planet: Planet) => format(planet.esi_score, 3)],
                    ["Habitable-zone assessment", (planet: Planet) => planet.esi.zone_status],
                  ].map(([label, getter]) => (
                    <tr key={String(label)}><th>{String(label)}</th>{compared.map((planet) => <td key={planet.planet_id}>{(getter as (p: Planet) => string)(planet)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="empty">Select two to four planets from the catalog to compare.</div>}
            <button className="back-link" onClick={() => setView("planets")}>← Browse planets</button>
          </div>
        )}

        {view === "analytics" && !loading && analytics && (
          <div className="analytics-grid">
            <Metric label="CONFIRMED WORLDS" value={analytics.planet_count.toLocaleString()} note="catalogued exoplanets" />
            <Metric label="HOST SYSTEMS" value={analytics.system_count.toLocaleString()} note="systems represented" />
            <Metric label="MEAN EARTH SIMILARITY" value={format(analytics.average_esi, 3)} note={`${analytics.scored_planet_count.toLocaleString()} scored with available measurements`} />
            <Metric label="LEADING DISCOVERY METHOD" value={analytics.top_discovery_method ?? "—"} note="most common in the catalog" />
          </div>
        )}
      </section>

      <footer><span>COSMODB-OOAD</span><span>DATA-LED EXPLORATION · SCIENTIFIC SCORES SHOWN WITH AVAILABLE DATA</span></footer>

      {selectedPlanet && <div className="modal-backdrop" onClick={() => setSelectedPlanet(null)}>
        <section className="planet-modal" role="dialog" aria-modal="true" aria-labelledby="planet-title" onClick={(event) => event.stopPropagation()}>
          <button className="modal-close" aria-label="Close planet details" onClick={() => setSelectedPlanet(null)}>×</button>
          <p className="eyebrow">PLANET PROFILE / {selectedPlanet.discovery_year ?? "YEAR UNKNOWN"}</p>
          <h2 id="planet-title">{selectedPlanet.planet_name}</h2>
          <p className="modal-host">{selectedPlanet.system_name} · {selectedPlanet.constellation_name ?? "Uncharted"}</p>
          <div className="profile-grid">
            <Metric label="RADIUS" value={`${format(selectedPlanet.radius_earth)} R⊕`} />
            <Metric label="MASS" value={`${format(selectedPlanet.mass_earth)} M⊕`} />
            <Metric label="ORBIT" value={`${format(selectedPlanet.orbit_radius)} AU`} />
            <Metric label="ORBITAL PERIOD" value={selectedPlanet.orbital_period == null ? "—" : `${format(selectedPlanet.orbital_period)} d`} />
            <Metric label="ESI" value={format(selectedPlanet.esi_score, 3)} note={selectedPlanet.esi.zone_status.replace("_", " ")} />
            <Metric label="DISCOVERY METHOD" value={selectedPlanet.discovery_method ?? "—"} />
          </div>
        </section>
      </div>}
    </main>
  );
}

function PlanetTable({ planets, onOpen, selectable = false, selected, onToggle }: {
  planets: Planet[];
  onOpen: (planet: Planet) => void;
  selectable?: boolean;
  selected?: Set<number>;
  onToggle?: (planet: Planet) => void;
}) {
  if (!planets.length) return <div className="empty">No planets found for this selection.</div>;
  return <div className="table-wrap"><table>
    <thead><tr><th>PLANET</th><th>HOST SYSTEM</th><th>RADIUS</th><th>MASS</th><th>PERIOD</th><th>ESI</th>{selectable && <th>COMPARE</th>}</tr></thead>
    <tbody>{planets.map((planet) => <tr key={planet.planet_id}>
      <td><button className="text-button" onClick={() => onOpen(planet)}>{planet.planet_name}</button><small>{planet.discovery_method ?? "Discovery unknown"}</small></td>
      <td>{planet.system_name}<small>{planet.constellation_name ?? "Uncharted"}</small></td>
      <td>{format(planet.radius_earth)} R⊕</td><td>{format(planet.mass_earth)} M⊕</td>
      <td>{planet.orbital_period == null ? "—" : `${format(planet.orbital_period)} d`}</td>
      <td><span className="esi">{format(planet.esi_score, 3)}</span></td>
      {selectable && <td><button className={selected?.has(planet.planet_id) ? "select-button chosen" : "select-button"} aria-label={`Toggle ${planet.planet_name} comparison`} onClick={() => onToggle?.(planet)}>{selected?.has(planet.planet_id) ? "✓" : "+"}</button></td>}
    </tr>)}</tbody>
  </table></div>;
}

function Metric({ label, value, note }: { label: string; value: string; note?: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong>{note && <small>{note}</small>}</div>;
}
