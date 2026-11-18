"""
part2_sec5_to_6.py
Generates Sections 5 and 6 of the OOAD Case Study Report (UML Modelling & OO Analysis).
"""
import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_style import (
    COLOR_NAVY, COLOR_TEXT_MAIN,
    add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_item, add_table_caption,
    format_academic_table, add_figure, add_callout_box
)

def build_part2(doc, diagrams_dir):
    # =========================================================================
    # SECTION 5: UML MODELLING - UNIT II
    # =========================================================================
    add_heading_1(doc, "5. UML Modelling – Unit II")
    add_body_p(doc, "In accordance with Unit II requirements, this section models the static structure and dynamic runtime behaviors of COSMOSDB-OOAD through a comprehensive suite of formal UML 2.5 diagrams authored in PlantUML. Each diagram captures specific structural, behavioral, or architectural invariants of the system, accompanied by an explicit architectural justification.", bold_prefix="UML 2.5 Modeling Suite: ")

    # 5.1 Use Case Diagram (Figure 1)
    add_heading_2(doc, "5.1 Use Case Diagram")
    add_body_p(doc, "The Use Case Diagram defines the functional scope of COSMOSDB-OOAD, identifying the interactions between human actors and system boundaries. Two primary actors interact with the system: the Explorer (representing astronomers, astrophysicists, and public researchers) and the Curator (representing scientific data administrators responsible for catalog integrity).")
    
    fig1_path = os.path.join(diagrams_dir, "figure1_use_case.png")
    add_figure(doc, fig1_path, 1, "Use Case Diagram for COSMOSDB-OOAD",
        "The use case model delineates the behavioral boundary between public exploration and privileged catalog administration. The Explorer actor initiates goal-driven read operations such as 'Search system', 'View system details', 'View planet details and ESI', and 'Compare 2–4 planets', while the Curator actor owns 'Manage planet catalog record'. The <<extend>> relationship to 'View analytics summary' decouples real-time analytical reporting from transactional browsing while preserving user workflow continuity.",
        width_inches=5.8)

    # 5.2 Class Diagram (Figure 2)
    add_heading_2(doc, "5.2 Complete Class Diagram")
    add_body_p(doc, "The Class Diagram models the static architecture of the entire system across the Clean Architecture layers, capturing entities, value objects, domain services, application services, abstract repository ports, concrete MySQL adapters, and presentation endpoints.")

    fig2_path = os.path.join(diagrams_dir, "figure2_class_diagram.png")
    add_figure(doc, fig2_path, 2, "Complete Class Diagram of Domain, Application, and Infrastructure Layers",
        "The class diagram enforces the Dependency Inversion Principle (DIP) by routing all application service persistence requests through abstract interfaces (IPlanetRepository, IStarSystemRepository, IConstellationRepository) rather than concrete database classes. It models StarSystem's ownership of Star as a genuine UML composition (1 ◆-- 1..*), establishes Planet as an independent aggregate root referencing its host system via identity (system_id), and formalizes the Strategy and Observer design patterns through explicit interfaces.",
        width_inches=6.4)

    # 5.3 Object Diagram (Figure 3)
    add_heading_2(doc, "5.3 Object Diagram (Snapshot of Running System)")
    add_body_p(doc, "To verify the relational fidelity and attribute types of our object model against real-world astronomical data, the Object Diagram depicts a concrete runtime instance snapshot of the Kepler-186 planetary system, located in the constellation Cygnus at a distance of 579.2 light-years.")

    fig3_path = os.path.join(diagrams_dir, "figure3_object_diagram.png")
    add_figure(doc, fig3_path, 3, "Object Diagram for Kepler-186 System Snapshot",
        "This object instance snapshot grounds the class model in empirical observational data from the NASA Exoplanet Archive. It demonstrates that keplerPlanet (Kepler-186 f) is linked to keplerSystem by foreign identity (system_id=1862) while keplerStar (an M1-type red dwarf) is physically composed within keplerSystem. The snapshot also confirms that cygnus (Constellation) encapsulates spatial bounding boxes correctly encapsulating Kepler-186's celestial coordinates (RA 298.66°, Dec +44.28°).",
        width_inches=5.9)

    # 5.4 Sequence Diagram 1: Compare Planets (Figure 4)
    add_heading_2(doc, "5.4 Sequence Diagram: Compare Exoplanets Scenario")
    add_body_p(doc, "The first sequence diagram models the dynamic message flow during the execution of Use Case 2 ('Compare 2–4 Exoplanets'). It tracks the synchronous request-reply lifecycle from the React UI down to domain calculations.")

    fig4_path = os.path.join(diagrams_dir, "figure4_seq_compare.png")
    add_figure(doc, fig4_path, 4, "Sequence Diagram for Multi-Planet Comparative Analysis Scenario",
        "The interaction sequence illustrates high-cohesion, low-coupling choreography: the presentation controller delegates directly to PlanetCatalogService.compare(ids), which validates the multi-id cardinality (2 to 4 distinct IDs), fetches the entities via the repository abstraction, and orchestrates ESICalculator and PlanetClassifier in a loop without exposing internal calculation algorithms to the caller. The resulting comparison matrix is returned as a decoupled presentation DTO.",
        width_inches=5.9)

    # 5.5 Sequence Diagram 2: Search Star System (Figure 5)
    add_heading_2(doc, "5.5 Sequence Diagram: Star System Search Scenario")
    add_body_p(doc, "The second sequence diagram captures the operational sequence when an Explorer queries the catalog for star systems matching a text query and constellation filter.")

    fig5_path = os.path.join(diagrams_dir, "figure5_seq_search.png")
    add_figure(doc, fig5_path, 5, "Sequence Diagram for Star System Search and Exploration Workflow",
        "This scenario highlights our architectural decision regarding planet counts: StarSystemCatalogService retrieves star systems matching search parameters and dynamically queries IPlanetRepository to derive the exact planet count via COUNT(*). This eliminates redundant data synchronization between StarSystem and Planet records while preserving real-time consistency during active catalog mutations.",
        width_inches=5.9)

    # 5.6 State Chart Diagram: Planet Catalog Record (Figure 6)
    add_heading_2(doc, "5.6 State Chart Diagram: Planet Catalog Record Lifecycle")
    add_body_p(doc, "The State Machine diagram models the lifecycle of an exoplanet record within the scientific catalog. It reflects domain-driven state transitions rather than database CRUD flags.")

    fig6_path = os.path.join(diagrams_dir, "figure6_state_record.png")
    add_figure(doc, fig6_path, 6, "State Chart Diagram for Planet Catalog Record Lifecycle",
        "The state machine models the genuine domain lifecycle of a cataloged planet: transitioning from Draft (under initial validation and physical parameter sanity checking) to Cataloged (published and active in search queries and comparative indices). Mutation operations in the Cataloged state trigger observer events that immediately invalidate the analytical cache, while deletion transitions the entity to Removed, ensuring proper audit trails and referential cleanup.",
        width_inches=4.8)

    # 5.7 Activity Diagram: ESI and Habitable Zone Workflow (Figure 7)
    add_heading_2(doc, "5.7 Activity Diagram: ESI Calculation and System Search Workflow")
    add_body_p(doc, "The Activity Diagram models the step-by-step control and data flow executed by ESICalculator and HabitableZoneCalculator to process physical measurements, apply scientific fallbacks, and compute multi-term similarity scores.")

    fig7_path = os.path.join(diagrams_dir, "figure7b_activity_esi.png")
    if not os.path.exists(fig7_path):
        fig7_path = os.path.join(diagrams_dir, "figure7a_activity_search.png")
    add_figure(doc, fig7_path, 7, "Activity Diagram for Earth Similarity Index and Habitable Zone Workflow",
        "The activity workflow models the defensive calculation pipeline: upon receiving a Planet entity, the service evaluates whether bulk density is recorded; if missing, it dynamically calculates density from mass and radius. It then computes interior and surface similarity terms, derives stellar luminosity, evaluates habitable zone boundaries, applies the configured IESIScoringStrategy, and bundles the result into an immutable ESIResult value object.",
        width_inches=5.0)

    doc.add_page_break()

    # =========================================================================
    # SECTION 6: OBJECT-ORIENTED ANALYSIS - UNIT III
    # =========================================================================
    add_heading_1(doc, "6. Object-Oriented Analysis – Unit III")
    add_heading_2(doc, "6.1 Actor Specifications")
    add_body_p(doc, "Object-oriented analysis begins with formal actor profiling to establish operational permissions, interaction modalities, and domain expectations:")

    add_bullet_item(doc, "An academic researcher, astrophysicist, or planetary enthusiast who interacts with the system via web clients or scientific APIs. The Explorer seeks to discover multi-planet architectures, compare terrestrial exoplanets against Earth benchmarks, inspect 3D orbital dynamics, and explore statistical distributions across discovery methods and stellar spectral types.", bold_prefix="1. Explorer (Primary Business Actor): ")

    add_bullet_item(doc, "A designated astronomical data curator or observatory administrator with write permissions. The Curator is responsible for entering newly verified exoplanet discoveries, updating physical parameters resulting from revised astronomical observations (e.g., transit timing variations or radial velocity updates), and retiring deprecated or disproven candidate records while maintaining system integrity.", bold_prefix="2. Curator (Administrative Business Actor): ")

    add_heading_2(doc, "6.2 Detailed Use Case Descriptions")
    add_body_p(doc, "We specify three core use cases that drive the structural and behavioral design of COSMOSDB-OOAD, detailing formal pre-conditions, main success flows, alternate exception flows, and post-conditions:")

    # Use Case 1 Table
    add_table_caption(doc, "Table 7: Use Case Specification 1 – Search and Explore Star Systems")
    uc1_table = doc.add_table(rows=1, cols=2)
    format_academic_table(uc1_table, [Inches(2.0), Inches(4.5)], ["Field", "Specification Details"], [
        ["Use Case ID & Name", "UC-1: Search and Explore Multi-Planet Star Systems"],
        ["Primary Actor", "Explorer"],
        ["Pre-conditions", "The COSMOSDB backend API is operational and MySQL connection pool is healthy. Star system and constellation tables are populated."],
        ["Main Success Flow", "1. Explorer inputs text query (e.g. 'Kepler') and optional constellation filter.\n2. Presentation layer sends GET /api/systems?q=... to FastAPI.\n3. StarSystemCatalogService validates pagination parameters (page >= 1, limit <= 100).\n4. Service invokes IStarSystemRepository.list() with search filters.\n5. Repository executes parameterized SQL query returning StarSystem entities.\n6. For each system, service dynamically queries IPlanetRepository for planet count.\n7. Service serializes StarSystemDTOs with primary star metrics and returns JSON array.\n8. Explorer views paginated system cards and selects a system for 3D orbital inspection."],
        ["Alternate Flows", "4a. Empty query with no matches: Service returns empty array with total=0; UI renders 'No star systems found'.\n3a. Invalid pagination (e.g. page=0): Service raises PaginationValidationError; API returns HTTP 422 Unprocessable Entity.\n5a. Database connection timeout: Repository raises PersistenceConnectionError; API returns HTTP 503 with user-friendly recovery instructions."],
        ["Post-conditions", "Explorer successfully inspects star system coordinates, distance in light-years, spectral classification of host stars, and child exoplanet counts."]
    ], alt_shading=False)

    # Use Case 2 Table
    add_table_caption(doc, "Table 8: Use Case Specification 2 – Perform Comparative Planetology on 2–4 Exoplanets")
    uc2_table = doc.add_table(rows=1, cols=2)
    format_academic_table(uc2_table, [Inches(2.0), Inches(4.5)], ["Field", "Specification Details"], [
        ["Use Case ID & Name", "UC-2: Multi-Planet Comparative Analysis Matrix"],
        ["Primary Actor", "Explorer"],
        ["Pre-conditions", "At least two valid exoplanet records exist in the catalog."],
        ["Main Success Flow", "1. Explorer selects between 2 and 4 exoplanets from the catalog (e.g., Kepler-186 f, Proxima Centauri b, TRAPPIST-1 e).\n2. Presentation layer calls GET /api/planets/compare?planet_ids=1&planet_ids=2...\n3. PlanetCatalogService verifies that 2 <= len(ids) <= 4 and all IDs are distinct.\n4. Service calls IPlanetRepository.get_by_ids(ids) to retrieve Planet aggregate instances.\n5. For each planet, service invokes ESICalculator.calculate(planet).\n6. ESICalculator extracts physical metrics, calculates interior/surface terms, queries HabitableZoneCalculator, and evaluates IESIScoringStrategy.\n7. Service invokes PlanetClassifier.classify(planet) to determine archetype (e.g. Super-Earth).\n8. Service compiles ComparisonResultDTO containing aligned parameter matrix, ESI gauge dials, and habitable zone tags, returning JSON response to UI."],
        ["Alternate Flows", "3a. Fewer than 2 or more than 4 IDs provided: Service raises ComparisonValidationError; API returns HTTP 400 Bad Request.\n4a. Non-existent planet ID supplied: Service raises EntityNotFoundError; API returns HTTP 404 with missing ID details.\n5a. Incomplete planetary measurements: ESICalculator executes Keplerian and density fallbacks; sets confidence flags accordingly."],
        ["Post-conditions", "Explorer visualizes side-by-side scientific comparison matrix with habitability dials and physical parameter tables."]
    ], alt_shading=False)

    # Use Case 3 Table
    add_table_caption(doc, "Table 9: Use Case Specification 3 – Curate and Catalog Exoplanet Record")
    uc3_table = doc.add_table(rows=1, cols=2)
    format_academic_table(uc3_table, [Inches(2.0), Inches(4.5)], ["Field", "Specification Details"], [
        ["Use Case ID & Name", "UC-3: Curate and Catalog Newly Discovered Exoplanet"],
        ["Primary Actor", "Curator"],
        ["Pre-conditions", "Curator possesses administrative authentication. Host StarSystem exists in catalog."],
        ["Main Success Flow", "1. Curator enters exoplanet measurements (name, system_id, radius, mass, temperature, orbit).\n2. Presentation layer sends POST /api/planets with JSON payload.\n3. PlanetCatalogService verifies host star system existence via IStarSystemRepository.\n4. Service invokes PlanetBuilder, setting attributes and triggering physical validation.\n5. PlanetBuilder verifies radius > 0, mass > 0, computes fallback density, and instantiates Planet.\n6. PlanetCatalogRecord initializes in Draft state, executes validate(), and transitions to Cataloged.\n7. Service invokes IPlanetRepository.create(planet) to persist relational record.\n8. Service triggers CatalogEventPublisher.publish(CatalogChangeEvent(type='CREATE')).\n9. AnalyticsCacheObserver receives event and immediately evicts all 9 analytical caches.\n10. API returns HTTP 201 Created with serialized Planet entity."],
        ["Alternate Flows", "3a. Target system_id does not exist: Service raises HostSystemNotFoundError; API returns HTTP 400.\n4a. Negative radius or non-physical measurement supplied: PlanetBuilder raises InvalidMeasurementError; API returns HTTP 422.\n7a. Duplicate planet name in system: Repository raises DatabaseConstraintConflict; API returns HTTP 409 Conflict."],
        ["Post-conditions", "New exoplanet is permanently cataloged; analytics cache is evicted; global planet count is dynamically incremented on next query."]
    ], alt_shading=False)

    doc.add_page_break()

    # 6.3 Noun-Phrase Analysis Table (22 Items)
    add_heading_2(doc, "6.3 Noun-Phrase Analysis (22 Extracted Candidates)")
    add_body_p(doc, "To rigorously derive domain entities and filter out noise, we applied the Noun-Phrase approach to our use case specifications. Every noun was isolated, analyzed, and categorized as a Relevant Class, an Irrelevant attribute/concept, or a Fuzzy concept requiring domain refinement:")

    add_table_caption(doc, "Table 10: Comprehensive 22-Item Noun-Phrase Classification Matrix")
    noun_table = doc.add_table(rows=1, cols=4)
    n_headers = ["Sl", "Extracted Noun Phrase", "Classification", "Architectural Justification / Disposition"]
    n_widths = [Inches(0.5), Inches(1.8), Inches(1.4), Inches(2.8)]
    n_data = [
        ["1", "Planet / Exoplanet", "Relevant Class", "Core domain entity and aggregate root representing a confirmed celestial body."],
        ["2", "Star System", "Relevant Class", "Core domain aggregate root encapsulating celestial coordinates and host stars."],
        ["3", "Star", "Relevant Class", "Domain entity composed within StarSystem; possesses spectral type and luminosity."],
        ["4", "Constellation", "Relevant Class", "Domain entity representing spatial IAU celestial region with boundary checking."],
        ["5", "Discovery Record", "Relevant Class", "Domain entity capturing historical discovery year, detection method, and facility."],
        ["6", "Earth Similarity Index (ESI)", "Relevant Class", "Dedicated domain service (ESICalculator) encapsulating scientific scoring equations."],
        ["7", "Habitable Zone", "Relevant Class", "Domain value object (HabitableZone) and calculator derived from stellar luminosity."],
        ["8", "Scoring Policy", "Relevant Class", "Abstract Strategy pattern interface (IESIScoringStrategy) for interchangeable scoring."],
        ["9", "Catalog Record", "Relevant Class", "Stateful domain wrapper (PlanetCatalogRecord) managing Draft-Cataloged-Removed states."],
        ["10", "Catalog Event Publisher", "Relevant Class", "Observer pattern publisher (CatalogEventPublisher) managing change broadcasts."],
        ["11", "Explorer", "Irrelevant (Actor)", "External human user role; interacts via presentation layer, not a domain entity."],
        ["12", "Curator", "Irrelevant (Actor)", "External administrative user role; authenticated at presentation layer."],
        ["13", "Planet Radius", "Irrelevant (Attribute)", "Physical floating-point measurement modeled as a private attribute of Planet."],
        ["14", "Planetary Mass", "Irrelevant (Attribute)", "Physical measurement modeled as a private attribute of Planet."],
        ["15", "Bulk Density", "Irrelevant (Attribute)", "Derived or measured physical property encapsulated inside Planet / PlanetBuilder."],
        ["16", "Equilibrium Temperature", "Irrelevant (Attribute)", "Thermodynamic property encapsulated as an attribute within Planet."],
        ["17", "Right Ascension / Declination", "Relevant Class", "Modeled as an immutable domain value object (CelestialCoordinates)."],
        ["18", "Spatial Bounding Box", "Relevant Class", "Modeled as an immutable domain value object (CelestialBoundingBox)."],
        ["19", "MySQL Database", "Irrelevant (Infra)", "External persistence technology encapsulated behind repository interfaces."],
        ["20", "Web Browser / React UI", "Irrelevant (UI)", "Client-side presentation technology completely decoupled from domain layer."],
        ["21", "Planet Count", "Fuzzy -> Derived", "Initially considered as an attribute; refined to a dynamic derivation to prevent state drift."],
        ["22", "Comparison Matrix", "Fuzzy -> DTO", "Initially considered as an entity; refined to a transient Application DTO."]
    ]
    format_academic_table(noun_table, n_widths, n_headers, n_data, alt_shading=True)

    add_heading_2(doc, "6.4 Use-Case Driven Class Confirmation & Emergent Behaviors")
    add_body_p(doc, "By tracing interaction lifecycles in the sequence diagrams, we confirmed the behavioral contracts required of each domain and application class:")

    add_bullet_item(doc, "Sequence diagram 4 confirmed the necessity of PlanetCatalogService.compare(ids), ESICalculator.calculate(planet), and PlanetClassifier.classify(planet). It confirmed that Planet must provide pure numeric getters for mass, radius, and temperature, and that HabitableZone must provide a classify(orbit_au) -> str predicate.", bold_prefix="Comparison Sequence Confirmation: ")

    add_bullet_item(doc, "Sequence diagram 5 confirmed that StarSystemCatalogService must not rely on a stale persisted planet_count column. Instead, it coordinates IStarSystemRepository.list() and invokes IPlanetRepository.count_by_system(system_id) to dynamically compute accurate multi-planet counts.", bold_prefix="Search Sequence Confirmation: ")

    add_bullet_item(doc, "The curation use case confirmed that PlanetBuilder must intercept invalid measurements prior to object instantiation, and that CatalogEventPublisher must expose a synchronous notify() loop to trigger AnalyticsCacheObserver.invalidate().", bold_prefix="Curation Sequence Confirmation: ")

    add_heading_2(doc, "6.5 Final Class Relationships and Structural Bindings")
    add_body_p(doc, "The analysis culminates in explicit structural bindings across the domain model:")

    add_bullet_item(doc, "StarSystem composites Star with multiplicity 1 ◆-- 1..* (a star system must possess at least one star, and stars have no lifecycle outside their parent system).", bold_prefix="Composition: ")

    add_bullet_item(doc, "Planet references StarSystem via a directed 0..* --> 1 association mediated by foreign identity (system_id). Constellation associates with StarSystem with multiplicity 0..1 to 0..*.", bold_prefix="Association: ")

    add_bullet_item(doc, "StandardESIStrategy and HabitabilityWeightedStrategy realize the abstract IESIScoringStrategy interface. AnalyticsCacheObserver and CatalogAuditLogObserver realize ICatalogChangeListener.", bold_prefix="Generalization / Realization: ")

    doc.add_page_break()
    return doc
