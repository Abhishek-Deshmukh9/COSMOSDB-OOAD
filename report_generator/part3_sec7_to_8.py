"""
part3_sec7_to_8.py
Generates Sections 7 and 8 of the OOAD Case Study Report (OO Design Principles & Design Patterns).
Uses authentic procedural code from CosmosDB report.txt as the baseline BEFORE state.
"""
import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_style import (
    COLOR_NAVY, COLOR_TEXT_MAIN,
    add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_item, add_table_caption,
    format_academic_table, add_code_block, add_figure, add_callout_box
)

def build_part3(doc, diagrams_dir):
    # =========================================================================
    # SECTION 7: OBJECT-ORIENTED DESIGN & DESIGN PRINCIPLES - UNIT IV
    # =========================================================================
    add_heading_1(doc, "7. Object-Oriented Design and Design Principles – Unit IV")
    add_body_p(doc, "Unit IV focuses on evaluating software architectures against formal design corollaries, analyzing coupling and cohesion metrics, enforcing the SOLID principles, designing visibility protocols, and eliminating hazardous design pitfalls. This section documents the transformation of our legacy procedural DBMS codebase (documented in CosmosDB report.txt) into a resilient, maintainable object-oriented system.", bold_prefix="Design Axioms and Quality Engineering: ")

    # 7.1 Bahrami Design Corollaries Evaluation
    add_heading_2(doc, "7.1 Evaluation of Ali Bahrami's Six Design Corollaries")
    add_body_p(doc, "In his seminal treatise on Object-Oriented Systems Development [2], Ali Bahrami establishes six fundamental design corollaries derived from the axioms of independence and information hiding. We evaluated our original procedural implementation against each corollary, contrasting the actual code in report.txt (such as main.py and crud.py) with the refactored OO architecture:")

    add_table_caption(doc, "Table 11: Evaluation of Ali Bahrami's Six Design Corollaries Against Original Codebase")
    corollaries_table = doc.add_table(rows=1, cols=4)
    c_headers = ["No.", "Bahrami Design Corollary", "State in Original Procedural System (report.txt)", "Architectural Refactoring Applied in OOAD Redesign"]
    c_widths = [Inches(0.4), Inches(1.8), Inches(2.1), Inches(2.2)]
    c_data = [
        ["1", "Corollary 1: Uncoupled design with less information content", 
         "In main.py and crud.py, route handlers directly called get_db(), opened raw MySQL cursors, composed dynamic SQL strings, handled transaction commit/rollback, and performed inline data validation, creating extreme informational coupling.", 
         "Decoupled into 4 clean layers: Presentation (FastAPI routes), Application (Services), Domain (Pure entities and calculators), and Infrastructure (MySQL repositories) mediated by abstract interfaces (IPlanetRepository)."],
        ["2", "Corollary 2: Single purpose classes", 
         "In crud.py, the delete_planet() function executed raw SQL DELETE, then manually ran UPDATE StarSystem SET num_planets = num_planets - 1, then checked whether the system was empty and executed cascading DELETE on Star and StarSystem — mixing DML, counter synchronization, and orphan cleanup in a single 35-line route handler.", 
         "Decomposed into single-purpose components: Planet (entity with identity), IPlanetRepository (persistence port), CatalogEventPublisher (event notification), and PlanetCatalogService (application orchestration)."],
        ["3", "Corollary 3: Large number of simpler classes", 
         "The original procedural system concentrated all backend functionality in 4 sprawling scripts: main.py (all read queries), crud.py (all write DML), utils.py (procedural ESI math), and analytics.py (un-cached SQL aggregations), each exceeding 150-300 lines of mixed concerns.", 
         "Introduced 14 specialized classes across domain, application, and infrastructure packages with average method length < 15 lines, single responsibilities, and isolated unit testability without requiring a live database."],
        ["4", "Corollary 4: Strong mapping to problem domain", 
         "The domain model was driven entirely by relational table shapes. In ingest_planets.py, spatial constellation assignment was done via an ad-hoc linear for-loop checking min_ra <= ra <= max_ra against raw dictionary records, failing on meridian wraparounds.", 
         "Directly mirrors the physical universe: StarSystem encapsulates host Stars through UML composition (1 ◆-- 1..*), Planet references host system by identity, and Constellation encapsulates CelestialBoundingBox value objects handling spherical wraparound."],
        ["5", "Corollary 5: Standardization & reusability", 
         "In report.txt, parameter validation (check_range, clean_val, parse_bool) was duplicated across ingest_planets.py, crud.py, and main.py, and SQL connection management (try/finally closing cursors) was repeated in every single endpoint.", 
         "Standardized into reusable domain services (ESICalculator, PlanetClassifier), a centralized ConnectionPool in infrastructure, and uniform repository interfaces adhering to Python's typing and ABC standards."],
        ["6", "Corollary 6: Designing with inheritance & polymorphism", 
         "In utils.py, the ESI calculation was a single procedural routine with hardcoded constants. Any variation in habitability assessment or weighting required adding boolean parameters and if-else branches inside the calculation function.", 
         "Implemented a polymorphic Strategy pattern hierarchy (IESIScoringStrategy -> StandardESIStrategy and HabitabilityWeightedStrategy), allowing runtime substitution of habitability scoring policies without modifying the calculation core."]
    ]
    format_academic_table(corollaries_table, c_widths, c_headers, c_data, alt_shading=True)

    # 7.2 Coupling and Cohesion Analysis
    add_heading_2(doc, "7.2 Coupling and Cohesion Analysis")
    add_body_p(doc, "Coupling measures the degree of interdependence between software modules, while cohesion evaluates how strongly related and focused the responsibilities within a single module are. We evaluated three core components across both architectural paradigms:")

    add_bullet_item(doc, "Procedural Baseline (crud.py): Afferent Coupling Ca=3, Efferent Coupling Ce=6 (coupled directly to mysql.connector, HTTPException, StarSystem table, Planet table, Star table, and Discovery table). Cohesion: Extremely low — a single function performed database connection management, SQL execution, counter synchronization, and cascade deletion. Refactored OO Architecture (PlanetCatalogService): Ca=1 (FastAPI presentation router), Ce=3 (IPlanetRepository abstraction, ESICalculator domain service, CatalogEventPublisher). Cohesion: Maximum functional cohesion — focuses exclusively on orchestrating exoplanet use cases.", bold_prefix="1. Application Service Layer (PlanetCatalogService vs. crud.py): ")

    add_bullet_item(doc, "Procedural Baseline (utils.py): Cohesion was moderate, but coupling was tangled because helper functions were imported directly into route handlers alongside raw database cursors, mixing mathematical evaluation with SQL row parsing. Refactored OO Architecture (ESICalculator): Cohesion: Pure functional cohesion. Coupling: Minimal (Ce=1 to IESIScoringStrategy, zero database or framework imports). Can be executed, tested, and benchmarked 100% in-memory.", bold_prefix="2. Domain Calculation Layer (ESICalculator vs. utils.py): ")

    add_bullet_item(doc, "Procedural Baseline (main.py): Embedded SQL query strings directly in endpoint definitions, binding HTTP routing logic directly to MySQL dialect details and column aliases like ANY_VALUE(st.star_temp). Refactored OO Architecture (MySQLPlanetRepository): Cohesion: High data-access cohesion. Encapsulates all SQL dialect generation, query parameterization, and entity mapping behind the IPlanetRepository interface.", bold_prefix="3. Persistence Layer (MySQLPlanetRepository vs. main.py): ")

    add_heading_3(doc, "Before vs. After Refactoring: Deletion and Referential Cleanup")
    add_body_p(doc, "To demonstrate the concrete architectural transformation, Listing 4 shows the authentic procedural implementation of delete_planet() from crud.py as documented in report.txt (Section 13-H):")

    add_code_block(doc,
'''# BEFORE REFACTORING: Authentic Procedural Deletion from crud.py (report.txt, lines 627-662)
# Tangled Concerns: Direct DB cursor, manual counter update, manual orphan deletion, inline HTTP error handling
@crud_router.delete("/planets/{planet_id}")
def delete_planet(planet_id: int):
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT system_id FROM Planet WHERE planet_id=%s", (planet_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Planet not found")
        sys_id = row['system_id']

        # Step 1 — Remove the planet
        cur.execute("DELETE FROM Planet WHERE planet_id=%s", (planet_id,))

        # Step 2 — Keep denormalized counter in sync (Fragile manual synchronization)
        cur.execute(
            "UPDATE StarSystem SET num_planets = num_planets - 1 WHERE system_id = %s",
            (sys_id,)
        )

        # Step 3 — Destroy orphaned system hierarchy if no planets remain
        cur.execute("SELECT num_planets FROM StarSystem WHERE system_id=%s", (sys_id,))
        sys_row = cur.fetchone()
        if sys_row and sys_row['num_planets'] <= 0:
            cur.execute("DELETE FROM Star WHERE system_id=%s", (sys_id,))
            cur.execute("DELETE FROM StarSystem WHERE system_id=%s", (sys_id,))

        db.commit()            # Atomically persist all changes
        return {"status": "success"}
    except Exception as e:
        db.rollback()          # Revert entire sequence on any failure
        raise HTTPException(500, str(e))
    finally:
        cur.close()
        db.close()             # Always release connection to prevent pool exhaustion''',
    caption="Listing 4: Authentic Procedural delete_planet() from crud.py (Antipattern: Tangled DML & Manual Sync)")

    add_body_p(doc, "Following our OOAD redesign, this routine was decomposed into clean architectural components. The application service orchestrates the deletion via the repository interface and publishes an event; the repository encapsulates SQL deletion; and the planet count is derived dynamically rather than requiring manual UPDATE synchronization:")

    add_code_block(doc,
'''# AFTER REFACTORING: Clean Architecture Service Method (cosmosdb/application/services.py)
# High Cohesion: Delegates persistence to IPlanetRepository port, notifies observers via CatalogEventPublisher
class PlanetCatalogService:
    def __init__(self, planet_repo: IPlanetRepository, system_repo: IStarSystemRepository,
                 publisher: CatalogEventPublisher, esi_calc: ESICalculator):
        self._planet_repo = planet_repo
        self._system_repo = system_repo
        self._publisher = publisher
        self._esi_calc = esi_calc

    def delete(self, planet_id: int) -> bool:
        planet = self._planet_repo.get_by_id(planet_id)
        if not planet:
            raise EntityNotFoundError(f"Planet with id {planet_id} not found.")

        # Repository encapsulates data access; dynamic COUNT(*) eliminates manual counter drift
        success = self._planet_repo.delete(planet_id)
        if success:
            # Observer pattern decouples cache eviction and audit logging
            self._publisher.publish(
                CatalogChangeEvent(
                    event_type="DELETE",
                    entity_type="Planet",
                    entity_id=planet_id,
                    system_id=planet.system_id
                )
            )
        return success''',
    caption="Listing 5: Refactored High-Cohesion PlanetCatalogService.delete() with Observer Notification")

    # 7.3 SOLID Principles Comprehensive Audit
    add_heading_2(doc, "7.3 Comprehensive SOLID Principles Audit")
    add_body_p(doc, "The refactored COSMOSDB-OOAD architecture strictly embodies all five SOLID design principles, contrasting sharply with the procedural violations identified in report.txt:")

    add_bullet_item(doc, "Procedural Violation in report.txt: In crud.py's create_planet(), a single 78-line function handled discovery deduplication, new system creation with midpoint spatial interpolation, star creation, planet creation, and counter synchronization. OOAD Compliance: Each class has a single, well-defined reason to change. ESICalculator changes only if astrophysical formulas are revised; MySQLPlanetRepository changes only if MySQL schema or connection details change; PlanetCatalogService changes only if application workflow rules evolve.", bold_prefix="Single Responsibility Principle (SRP): ")

    add_bullet_item(doc, "Procedural Violation in report.txt: In utils.py, supporting a new habitability scoring variation required modifying the existing calculate_esi() function by inserting boolean flags and if-else branches. OOAD Compliance: The domain calculation engine is open for extension but closed for modification. New scoring policies are added by implementing IESIScoringStrategy without changing a single line of calculation code in ESICalculator.", bold_prefix="Open/Closed Principle (OCP): ")

    add_bullet_item(doc, "Procedural Violation in report.txt: There was no polymorphism or subtyping; all logic relied on concrete functions and dictionary lookups. OOAD Compliance: Concrete strategy implementations (StandardESIStrategy and HabitabilityWeightedStrategy) honor the contract of IESIScoringStrategy, ensuring that any strategy can be substituted at runtime without breaking mathematical invariants or client expectations.", bold_prefix="Liskov Substitution Principle (LSP): ")

    add_bullet_item(doc, "Procedural Violation in report.txt: A single bloated DB cursor interface (mysql.connector.cursor) was passed everywhere, exposing dozens of methods (fetchall, execute, executemany, callproc) to code that only needed a simple read. OOAD Compliance: Clients depend only on focused, role-specific interfaces: IPlanetRepository exposes only planet persistence operations, IStarSystemRepository exposes system operations, and ICatalogChangeListener exposes only on_catalog_change().", bold_prefix="Interface Segregation Principle (ISP): ")

    add_bullet_item(doc, "Procedural Violation in report.txt: In main.py and crud.py, route handlers depended directly on concrete low-level infrastructure modules: import mysql.connector and get_db(). A database engine change would break every API handler. OOAD Compliance: High-level policy modules (PlanetCatalogService) depend strictly on abstractions (IPlanetRepository, IStarSystemRepository) defined in cosmosdb.application.ports. Concrete infrastructure classes (MySQLPlanetRepository) implement these ports, completely inverting the dependency direction.", bold_prefix="Dependency Inversion Principle (DIP): ")

    # 7.4 UML Visibility Protocols and Method Signatures
    add_heading_2(doc, "7.4 UML Visibility Notation and Protocol Design")
    add_body_p(doc, "In accordance with strict object-oriented information hiding, internal state is marked private (-) or protected (#) using underscore prefixes, while clean public protocols (+) are exposed to collaborating objects:")

    add_table_caption(doc, "Table 12: Public and Internal UML Protocol Signatures Across Core Classes")
    proto_table = doc.add_table(rows=1, cols=3)
    p_headers = ["Class Name", "UML Visibility & Operation Signature", "Protocol Classification & Purpose"]
    p_widths = [Inches(1.8), Inches(3.2), Inches(1.5)]
    p_data = [
        ["Planet", "+ calculate_bulk_density(): float\n+ estimate_semi_major_axis(): float\n- _radius_earth: float\n- _mass_earth: float", "Public Business Protocol\nInternal Encapsulated State"],
        ["PlanetBuilder", "+ set(name: str, value: Any): PlanetBuilder\n+ build(): Planet\n- _validate_physics(): void\n- _compute_fallbacks(): void", "Public Fluent Interface\nInternal Validation Guard"],
        ["ESICalculator", "+ calculate(planet: Planet): ESIResult\n- _calculate_interior(r: float, d: float): float\n- _calculate_surface(t: float, v: float): float", "Public Service Protocol\nPrivate Algorithmic Steps"],
        ["PlanetCatalogService", "+ compare(ids: list[int]): ComparisonResultDTO\n+ browse(page: int, limit: int, ...): PageDTO\n- _serialize(planet: Planet): dict", "Public Application Protocol\nPrivate Serialization Helper"],
        ["CatalogEventPublisher", "+ subscribe(listener: ICatalogChangeListener): void\n+ publish(event: CatalogChangeEvent): void\n- _listeners: list[ICatalogChangeListener]", "Public Observer Interface\nPrivate Observer Registry"]
    ]
    format_academic_table(proto_table, p_widths, p_headers, p_data, alt_shading=True)

    # 7.5 Design Pitfalls Found and Fixed
    add_heading_2(doc, "7.5 Design Pitfalls Identified and Resolved")
    add_body_p(doc, "During the architectural review of the original procedural DBMS codebase (report.txt), two severe design pitfalls were uncovered and systematically eliminated:")

    add_heading_3(doc, "Pitfall 1: God Route Handlers Mixing SQL, Business Logic, and Presentation")
    add_body_p(doc, "Evidence in report.txt: In main.py (Section 13-E, lines 545-573), the Observatory catalog endpoint dynamically constructed a sprawling 5-table LEFT JOIN query with ANY_VALUE() aggregations, parsed query parameters, executed the SQL statement against a raw cursor, handled pagination calculations, and formatted JSON dictionaries—all within a single function. A bug in any single concern (SQL syntax, pagination math, or serialization) broke the entire endpoint.")
    add_body_p(doc, "Solution in OOAD: We dismantled this monolithic God Handler into distinct, single-responsibility collaborators: (1) FastAPI controller handles HTTP routing and parameter validation; (2) PlanetCatalogService coordinates the use case; (3) MySQLPlanetRepository executes the parameterized SQL query and maps relational rows to Planet entities; and (4) ESICalculator and PlanetClassifier compute derived properties. Each component is independently unit-testable.")

    add_heading_3(doc, "Pitfall 2: Primitive Obsession and Relational State Drift")
    add_body_p(doc, "Evidence in report.txt: (a) In ingest_planets.py (Section 13-D, lines 504-515), celestial coordinates were treated as raw floating-point numbers (ra, dec), and constellation bounding was evaluated through a naive for-loop: (c['min_ra'] <= ra <= c['max_ra']) and (c['min_dec'] <= dec <= c['max_dec']). This naive comparison completely failed for constellations crossing the 360°/0° Right Ascension meridian (e.g., Cassiopeia spanning 345° to 52.5°), assigning null constellation IDs. (b) In schema.sql (Section 13-A, line 346) and report.txt (Section 10, line 263), StarSystem stored a denormalized num_planets integer column. Report.txt explicitly admitted this was a 'deliberate 3NF violation' requiring manual UPDATE synchronization on every write. In practice, concurrent insertions or bulk scripts frequently failed to update this counter, causing severe state drift where systems with 5 planets reported num_planets=1.")
    add_body_p(doc, "Solution in OOAD: (a) Replaced primitive floats with immutable domain value objects: CelestialCoordinates(ra, dec) and CelestialBoundingBox(min_ra, max_ra, min_dec, max_dec). CelestialBoundingBox encapsulates spherical wraparound logic via its contains() method, correctly handling intervals where min_ra > max_ra. (b) Eliminated the mutable num_planets column from the domain model; planet counts are now derived dynamically via IPlanetRepository.count_by_system(system_id) using an indexed COUNT(*) query, guaranteeing zero state drift under concurrent mutations.")

    doc.add_page_break()

    # =========================================================================
    # SECTION 8: DESIGN PATTERNS & ARCHITECTURE - UNIT V
    # =========================================================================
    add_heading_1(doc, "8. Design Patterns and Architecture – Unit V")
    add_body_p(doc, "Unit V requires selecting, justifying, and implementing design patterns across all three GoF categories (Creational, Structural, Behavioral) and mapping the resulting system to an architectural pattern. We implemented four genuine GoF patterns that directly resolve concrete architectural defects identified in the original procedural codebase (report.txt):", bold_prefix="Gang of Four Design Patterns: ")

    # 8.1 Creational Pattern: PlanetBuilder
    add_heading_2(doc, "8.1 Creational Pattern: PlanetBuilder (Builder Pattern)")
    add_body_p(doc, "Problem in report.txt: In crud.py (Section 13-I, lines 724-733), adding a new planet executed an INSERT INTO Planet with 13 positional %s arguments: (planet_name, sys_id, discovery_id, is_cb, p_per, p_rad, p_re, p_me, p_den, p_ecc, p_insol, p_temp, ttv). Because these are raw positional values, a developer could easily swap orbital period and orbit radius without any error being raised. Furthermore, the procedural code relied entirely on MySQL CHECK constraints at the database layer; if invalid physical data (e.g. negative radius or mass) was passed, the database threw an unhandled SQL error that aborted the transaction, returning an uninformative HTTP 500.")
    
    add_body_p(doc, "Why Chosen Over Alternatives: The Telescoping Constructor pattern is brittle and error-prone in Python. The Factory Method pattern is insufficient because exoplanet records require multi-step assembly with complex fallback derivations (e.g., calculating density when mass and radius are present). The Builder pattern provides a fluent, step-by-step construction interface with centralized domain invariant validation prior to instantiation.")

    # Before vs. After Class Diagram for Builder
    fig_builder_path = os.path.join(diagrams_dir, "pattern_builder.png")
    add_figure(doc, fig_builder_path, 8, "Builder Pattern — Before vs. After UML Class Diagram",
        "The left panel shows the procedural approach in crud.py where create_planet() accepted 13 raw positional parameters with no domain validation, relying entirely on MySQL CHECK constraints. The right panel shows the refactored Builder pattern where PlanetBuilder provides named set() calls, centralized invariant validation in build(), and automatic scientific fallback derivations (e.g., density from mass and radius), producing a fully validated Planet entity.",
        width_inches=5.8)

    add_code_block(doc,
'''class PlanetBuilder:
    def __init__(self):
        self._attrs = {}

    def set(self, name: str, value: Any) -> "PlanetBuilder":
        self._attrs[name] = value
        return self

    def build(self) -> Planet:
        # Centralized Domain Invariant Guard (replaces late SQL CHECK constraint errors)
        radius = float(self._attrs.get("radius_earth", 0) or 0)
        mass = float(self._attrs.get("mass_earth", 0) or 0)
        if radius < 0 or mass < 0:
            raise InvalidMeasurementError("Physical planetary measurements cannot be negative.")
        
        # Automatic Scientific Fallback Calculation
        density = self._attrs.get("density")
        if (density is None or density <= 0) and (radius > 0 and mass > 0):
            # Derivation from bulk planetary volume: rho = M / ((4/3) * pi * R^3)
            self._attrs["density"] = round(5.51 * (mass / (radius ** 3)), 2)

        return Planet(**self._attrs)''',
    caption="Listing 6: Concrete Builder Pattern Implementation (PlanetBuilder)")

    # 8.2 Structural Pattern: Repository / Adapter & Facade
    add_heading_2(doc, "8.2 Structural Pattern: Repository / Adapter and Service Facade")
    add_body_p(doc, "Problem in report.txt: In main.py (Section 13-E/F/G), every route handler directly called get_db(), opened a dictionary cursor, and executed raw SQL strings: cur.execute(\"SELECT * FROM star WHERE system_id = %s\", (system_id,)). The business logic was inextricably coupled to the mysql-connector-python driver. It was impossible to write unit tests without spinning up a live MySQL server, and impossible to migrate to a different database engine without rewriting every endpoint in the application.")

    add_body_p(doc, "Why Chosen Over Alternatives: Direct DAO (Data Access Object) classes still leak database operations to the caller. The Repository pattern acts as an in-memory collection facade and object-relational Adapter, mapping low-level SQL tabular result sets into rich domain entities while completely shielding application services behind abstract interfaces (IPlanetRepository, IStarSystemRepository).")

    # Before vs. After Class Diagram for Repository/Adapter
    fig_repo_path = os.path.join(diagrams_dir, "pattern_repository.png")
    add_figure(doc, fig_repo_path, 9, "Repository/Adapter Pattern — Before vs. After UML Class Diagram",
        "The left panel shows route handlers in main.py directly importing and invoking mysql.connector, making business logic inseparable from database infrastructure. The right panel shows the refactored architecture where PlanetCatalogService depends on the abstract IPlanetRepository interface, while MySQLPlanetRepository implements it as a concrete Adapter, enabling unit testing with mocks and database-agnostic service logic.",
        width_inches=5.8)

    add_code_block(doc,
'''class MySQLPlanetRepository(IPlanetRepository):
    """Structural Adapter mapping MySQL relational records to Planet Entities."""
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def get_by_id(self, planet_id: int) -> Planet | None:
        sql = "SELECT * FROM planets WHERE planet_id = %s"
        with self._pool.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, (planet_id,))
                row = cursor.fetchone()
                return self._map_to_entity(row) if row else None''',
    caption="Listing 7: Structural Adapter Implementation (MySQLPlanetRepository)")

    # 8.3 Behavioral Pattern 1: Strategy Pattern (IESIScoringStrategy)
    add_heading_2(doc, "8.3 Behavioral Pattern: IESIScoringStrategy (Strategy Pattern)")
    add_body_p(doc, "Problem in report.txt: In utils.py, the Earth Similarity Index formula was implemented as a single procedural function that computed a raw mathematical score. However, planetary scientists disagree on whether ESI should measure purely physical terrestrial similarity (radius, density, temperature) or be explicitly penalized if the planet orbits outside the host star's habitable zone. In the procedural system, supporting both approaches required passing boolean flags (penalize_habitable_zone=True) and adding nested if-else branches inside the math routines, violating the Open/Closed Principle.")

    add_body_p(doc, "Why Chosen Over Alternatives: Subclassing ESICalculator leads to class explosion. The Strategy pattern cleanly encapsulates interchangeable scoring policies behind the IESIScoringStrategy interface, allowing users to select StandardESIStrategy or HabitabilityWeightedStrategy at runtime without modifying calculation formulas.")

    # Before vs. After Class Diagram for Strategy
    fig_strategy_path = os.path.join(diagrams_dir, "pattern_strategy.png")
    add_figure(doc, fig_strategy_path, 10, "Strategy Pattern — Before vs. After UML Class Diagram",
        "The left panel shows the procedural approach in utils.py where a single calculate_esi() function used boolean flags to toggle behavior internally, violating the Open/Closed Principle. The right panel shows the refactored Strategy hierarchy: ESICalculator (context) delegates scoring to an IESIScoringStrategy interface, with StandardESIStrategy and HabitabilityWeightedStrategy as concrete interchangeable policies selected at runtime.",
        width_inches=5.8)

    add_code_block(doc,
'''class IESIScoringStrategy(ABC):
    @abstractmethod
    def score(self, base_score: float, zone_status: str) -> float:
        raise NotImplementedError

class StandardESIStrategy(IESIScoringStrategy):
    def score(self, base_score: float, zone_status: str) -> float:
        return round(base_score, 4)

class HabitabilityWeightedStrategy(IESIScoringStrategy):
    def score(self, base_score: float, zone_status: str) -> float:
        if zone_status in ("TOO_HOT", "TOO_COLD"):
            return round(base_score * 0.10, 4)  # Explicit 90% penalty policy
        return round(base_score, 4)''',
    caption="Listing 8: Behavioral Strategy Pattern Implementation (IESIScoringStrategy)")

    # 8.4 Behavioral Pattern 2: Observer Pattern (CatalogEventPublisher)
    add_heading_2(doc, "8.4 Behavioral Pattern: CatalogEventPublisher (Observer Pattern)")
    add_body_p(doc, "Problem in report.txt: In analytics.py, computing the 9 mission-control charts required heavy SQL aggregations across 6,154 planets. In the procedural system, there was NO caching at all—every visit to the analytics dashboard fired fresh GROUP BY queries against MySQL. Furthermore, when crud.py inserted or deleted a planet, it had no mechanism to notify downstream systems other than manually running an UPDATE on the StarSystem counter, creating tight coupling and missed notifications.")

    add_body_p(doc, "Why Chosen Over Alternatives: Polling the database for changes introduces latency and server load. Synchronous method calls inside the service couple catalog mutation logic to caching infrastructure. The Observer pattern establishes an event-driven subscription model: PlanetCatalogService simply publishes a CatalogChangeEvent, and registered observers (AnalyticsCacheObserver, CatalogAuditLogObserver) automatically react without coupling the service to caching infrastructure.")

    # Before vs. After Class Diagram for Observer
    fig_observer_path = os.path.join(diagrams_dir, "pattern_observer.png")
    add_figure(doc, fig_observer_path, 11, "Observer Pattern — Before vs. After UML Class Diagram",
        "The left panel shows the procedural system where crud.py manually updated denormalized counters with no notification mechanism, while analytics.py independently re-queried all 6,154 planets on every request with no caching. The right panel shows the refactored Observer pattern: CatalogEventPublisher (Subject) notifies registered ICatalogChangeListener observers—AnalyticsCacheObserver for automatic cache invalidation and CatalogAuditLogObserver for audit logging—upon any catalog mutation.",
        width_inches=5.8)

    add_code_block(doc,
'''class CatalogEventPublisher:
    def __init__(self):
        self._listeners: list[ICatalogChangeListener] = []

    def subscribe(self, listener: ICatalogChangeListener) -> None:
        self._listeners.append(listener)

    def publish(self, event: CatalogChangeEvent) -> None:
        for listener in self._listeners:
            listener.on_catalog_change(event)

class AnalyticsCacheObserver(ICatalogChangeListener):
    def __init__(self, analytics_service: AnalyticsService):
        self._analytics = analytics_service

    def on_catalog_change(self, event: CatalogChangeEvent) -> None:
        # Automated cache invalidation upon any catalog mutation
        self._analytics.invalidate_all_caches()''',
    caption="Listing 9: Behavioral Observer Pattern Implementation (CatalogEventPublisher)")

    # 8.5 Layered Clean Architecture Mapping
    add_heading_2(doc, "8.5 Architectural Pattern Mapping: Layered Clean Architecture")
    add_body_p(doc, "The entire COSMOSDB-OOAD system is structured following the Clean Architecture paradigm (Layers / Hexagonal Architecture), enforcing strict inward-pointing dependency rules:")

    add_bullet_item(doc, "FastAPI HTTP REST endpoints and React 18 / TypeScript single-page application. Handles HTTP serialization, route validation, and interactive canvas visualizations.", bold_prefix="1. Presentation Layer (Outer Layer): ")

    add_bullet_item(doc, "PlanetCatalogService, StarSystemCatalogService, AnalyticsService, and CatalogEventPublisher. Orchestrates workflows and defines abstract repository interfaces (ports).", bold_prefix="2. Application Layer: ")

    add_bullet_item(doc, "Planet, StarSystem, Star, Constellation, ESICalculator, and PlanetClassifier. Pure Python entities and scientific calculators with zero framework dependencies.", bold_prefix="3. Domain Layer (Core Business Rules): ")

    add_bullet_item(doc, "MySQLPlanetRepository, MySQLStarSystemRepository, connection pooling, and configuration loaders. Implements repository interfaces defined in the application layer.", bold_prefix="4. Infrastructure Layer (Adapters): ")

    # Figure 12 Package & Component Architecture Diagram
    fig8_path = os.path.join(diagrams_dir, "figure8_package_component.png")
    add_figure(doc, fig8_path, 12, "Layered Package and Component Architecture Diagram",
        "The package and component diagram formalizes the Clean Architecture boundaries and dependency inversion direction. The presentation layer (FastAPI and React UI) and infrastructure layer (MySQL repositories) both depend inward toward application interfaces (IPlanetRepository) and domain entities (Planet, StarSystem), ensuring that the core scientific algorithms remain completely insulated from database drivers or transport protocols.",
        width_inches=6.0)

    doc.add_page_break()
    return doc
