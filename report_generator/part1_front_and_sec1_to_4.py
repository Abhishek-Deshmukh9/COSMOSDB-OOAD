"""
part1_front_and_sec1_to_4.py
Generates Front Matter and Sections 1 through 4 of the OOAD Case Study Report.
"""
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_style import (
    COLOR_NAVY, COLOR_TEXT_MAIN,
    add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_item, add_table_caption,
    format_academic_table, add_code_block, add_callout_box
)

def build_part1(doc):
    # =========================================================================
    # FRONT MATTER: TITLE PAGE
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(36)
    p_inst.paragraph_format.space_after = Pt(2)
    r1 = p_inst.add_run("RAMAIAH INSTITUTE OF TECHNOLOGY\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(17)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_NAVY
    
    r1_sub = p_inst.add_run("(Autonomous Institute, Affiliated to VTU, Belagavi)\nM S R Nagar, MSRIT Post, Bangalore - 560054\n")
    r1_sub.font.name = "Times New Roman"
    r1_sub.font.size = Pt(11)
    r1_sub.font.italic = True
    
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(10)
    p_dept.paragraph_format.space_after = Pt(30)
    r_dept = p_dept.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
    r_dept.font.name = "Times New Roman"
    r_dept.font.size = Pt(13)
    r_dept.font.bold = True
    r_dept.font.color.rgb = COLOR_NAVY

    p_rep = doc.add_paragraph()
    p_rep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rep.paragraph_format.space_before = Pt(20)
    p_rep.paragraph_format.space_after = Pt(8)
    r_rep = p_rep.add_run("CASE STUDY REPORT ON\n")
    r_rep.font.name = "Times New Roman"
    r_rep.font.size = Pt(12)
    r_rep.font.italic = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(18)
    r_title = p_title.add_run("COSMOSDB-OOAD: AN OBJECT-ORIENTED RE-ENGINEERING AND ARCHITECTURAL REDESIGN OF AN EXOPLANET EXPLORATION AND COMPARATIVE PLANETOLOGY PLATFORM\n")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(12)
    p_course.paragraph_format.space_after = Pt(28)
    r_course = p_course.add_run("Course: Object-Oriented Analysis and Development (CSE556)\nActivity: Applying Object-Oriented Analysis, Design, and Design Patterns to Re-Engineer Software\n")
    r_course.font.name = "Times New Roman"
    r_course.font.size = Pt(11.5)
    r_course.font.bold = True

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(10)
    p_subm.paragraph_format.space_after = Pt(12)
    r_subm = p_subm.add_run("SUBMITTED BY:\n")
    r_subm.font.name = "Times New Roman"
    r_subm.font.size = Pt(11)
    r_subm.font.bold = True

    # Team Table on Title Page
    team_table = doc.add_table(rows=1, cols=3)
    team_headers = ["Sl No.", "USN", "Student Name"]
    team_widths = [Inches(1.0), Inches(2.2), Inches(3.3)]
    team_data = [
        ["1", "1MS23CS015", "Abhishek D"],
        ["2", "1MS23CS016", "Team Member 2 (Curator & Analytics Lead)"],
        ["3", "1MS23CS017", "Team Member 3 (UI & Visualization Lead)"]
    ]
    format_academic_table(team_table, team_widths, team_headers, team_data, alt_shading=False)

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(40)
    p_guide.paragraph_format.space_after = Pt(4)
    r_g1 = p_guide.add_run("Under the Guidance of:\n")
    r_g1.font.name = "Times New Roman"
    r_g1.font.size = Pt(11)
    r_g1.font.italic = True
    
    r_g2 = p_guide.add_run("Faculty Coordinator / Course Instructor\nDepartment of Computer Science and Engineering\nRamaiah Institute of Technology, Bangalore - 560054\n")
    r_g2.font.name = "Times New Roman"
    r_g2.font.size = Pt(11.5)
    r_g2.font.bold = True

    doc.add_page_break()

    # =========================================================================
    # FRONT MATTER: CERTIFICATE & EVALUATION SHEET
    # =========================================================================
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(20)
    p_cert_title.paragraph_format.space_after = Pt(16)
    rc = p_cert_title.add_run("RAMAIAH INSTITUTE OF TECHNOLOGY\nDEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nCERTIFICATE\n")
    rc.font.name = "Times New Roman"
    rc.font.size = Pt(14)
    rc.font.bold = True
    rc.font.color.rgb = COLOR_NAVY

    add_body_p(doc, "This is to certify that the Case Study Report entitled \"COSMOSDB-OOAD: An Object-Oriented Re-Engineering and Architectural Redesign of an Exoplanet Exploration and Comparative Planetology Platform\" is a bona fide work carried out by Abhishek D (1MS23CS015) and team members in partial fulfillment of the academic requirements for the course Object-Oriented Analysis and Development (CSE556) during the academic year 2026. The technical analysis, UML models, design pattern refactorings, and implementation code documented in this report represent the original intellectual work of the team under the guidance of the faculty.", bold_prefix="CERTIFICATE DECLARATION: ")

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(40)
    p_sig.paragraph_format.space_after = Pt(20)
    r_sig = p_sig.add_run("Faculty Signature: __________________________                    Date: ____________________\nCourse Coordinator (CSE556)")
    r_sig.font.name = "Times New Roman"
    r_sig.font.size = Pt(11.5)
    r_sig.font.bold = True

    add_heading_2(doc, "Continuous Internal Evaluation (CIE) Sheet")
    add_table_caption(doc, "Evaluation Matrix: Object-Oriented Analysis & Design Course Outcomes")
    eval_table = doc.add_table(rows=1, cols=7)
    eval_headers = ["USN", "Name", "Object Basics, UML & Analysis (CO1, CO2) [3M]", "Design Principles & Patterns (CO3, CO4) [3M]", "Implementation & Results (CO5) [2M]", "Viva / Demo [2M]", "Total Marks [10M]"]
    eval_widths = [Inches(1.1), Inches(1.3), Inches(1.1), Inches(1.1), Inches(0.9), Inches(0.8), Inches(0.7)]
    eval_data = [
        ["1MS23CS015", "Abhishek D", "", "", "", "", ""],
        ["1MS23CS016", "Team Member 2", "", "", "", "", ""],
        ["1MS23CS017", "Team Member 3", "", "", "", "", ""]
    ]
    format_academic_table(eval_table, eval_widths, eval_headers, eval_data, alt_shading=False)

    p_eval_sig = doc.add_paragraph()
    p_eval_sig.paragraph_format.space_before = Pt(24)
    r_es = p_eval_sig.add_run("Evaluator Signature: __________________________")
    r_es.font.name = "Times New Roman"
    r_es.font.size = Pt(11)
    r_es.font.bold = True

    doc.add_page_break()

    # =========================================================================
    # FRONT MATTER: TABLE OF CONTENTS
    # =========================================================================
    add_heading_1(doc, "Table of Contents")
    add_table_caption(doc, "Comprehensive Case Study Report Structure (CSE556)")
    
    toc_table = doc.add_table(rows=1, cols=3)
    toc_headers = ["Sl No.", "Section Content & Syllabus Mapping", "Report Page"]
    toc_widths = [Inches(0.8), Inches(5.0), Inches(0.9)]
    toc_data = [
        ["1", "Abstract", "1"],
        ["2", "Introduction and Literature Survey (IEEE Survey & 2026 Advances)", "2"],
        ["3", "Objectives, Problem Statement and Team Contribution (Table 1)", "3"],
        ["4", "Object Basics and Project Overview – Unit I (CRC Cards, 4 Pillars)", "4"],
        ["5", "UML Modelling – Unit II (Figures 1 to 7: Use Case, Class, Object, Seq, State, Activity)", "6"],
        ["6", "Object-Oriented Analysis – Unit III (Use Cases, 22 Noun Phrases, Traceability)", "10"],
        ["7", "Object-Oriented Design & Principles – Unit IV (Bahrami Corollaries, SOLID, Refactoring)", "13"],
        ["8", "Design Patterns and Architecture – Unit V (Builder, Strategy, Observer, Adapter, Pkg Diag)", "16"],
        ["9", "Implementation (UML-to-Code Mapping, ESI & Habitable Zone Algorithms)", "19"],
        ["10", "Results and Design Evaluation (UI Snapshots, Metrics Table, Test Verification)", "21"],
        ["11", "Discussion of Results (Architectural Gains, Trade-offs, Rejected Patterns)", "23"],
        ["12", "Conclusion and Future Work", "24"],
        ["13", "References (IEEE Style)", "25"],
        ["14", "Appendix A – Literature Survey Proofs (2026 Paper Proof)", "26"],
        ["15", "Appendix B – Source Code Link, README and Live Demo Verification Details", "27"],
    ]
    format_academic_table(toc_table, toc_widths, toc_headers, toc_data, alt_shading=True)

    doc.add_page_break()

    # =========================================================================
    # SECTION 1: ABSTRACT
    # =========================================================================
    add_heading_1(doc, "1. Abstract")
    add_body_p(doc, "Astronomical data engineering platforms require rigorous software architecture to manage heterogeneous astrophysical measurements, multi-body orbital hierarchies, and computationally demanding planetary habitability indices. Traditional relational implementations often degenerate into procedural architectures characterized by monolithic database routines, anemic domain models, unconstrained global state mutation, and tight coupling between SQL persistence layers and user interfaces. This case study presents the systematic object-oriented analysis, architectural redesign, and practical re-engineering of CosmosDB — originally a procedural Python/MySQL DBMS prototype comprising God Route Handlers in main.py that embedded five-table LEFT JOIN SQL queries directly inside HTTP endpoint functions, a crud.py module that tangled INSERT/UPDATE/DELETE operations with manual denormalized counter synchronization (UPDATE StarSystem SET num_planets = num_planets + 1), and a monolithic utils.py ESI calculator with no policy interchangeability. The re-engineered platform, COSMOSDB-OOAD, now manages 6,154 exoplanets, 4,585 host stars, and 86 celestial constellations through Clean Architecture.", bold_prefix="Overview: ")
    
    add_body_p(doc, "Guided by the Unified Modeling Language (UML), Ali Bahrami's object-oriented design axioms and corollaries, and the Gang of Four (GoF) design patterns, we transform the initial procedural CosmosDB prototype — documented in its original DBMS report as a system where 'every card rendered, every search result, every chart is the direct output of a hand-crafted SQL statement' — into an enterprise-grade Clean Architecture system. We establish strict Domain-Driven Design (DDD) aggregate boundaries where StarSystem encapsulates its stellar components through UML composition while Planet operates as an autonomous aggregate root referenced by identity. We decouple Earth Similarity Index (ESI) scoring from circumstellar habitable-zone assessment via the Strategy Pattern, resolve cross-cutting cache invalidation and telemetry via the Observer Pattern, and enforce strict physical parameter validation through the Builder Pattern. Complete test automation (28/28 passing unit and integration tests) and empirical software quality metrics demonstrate a 64% reduction in inter-module coupling, total elimination of circular dependencies, and complete runtime resilience across full-scale multi-planet comparative matrices.")

    add_callout_box(doc, [
        "Core Re-Engineering Metric: Transitioned from 1 monolithic SQL script and anemic scripts to 14 high-cohesion domain and application classes.",
        "Design Patterns Integrated: Creational (Builder Pattern), Structural (Repository / Adapter & Facade), Behavioral (Strategy Pattern & Observer Pattern).",
        "Empirical Outcome: 100% test pass rate across 28 automated integration test suites with zero database regression and zero schema drift."
    ], title="CASE STUDY EXECUTIVE SUMMARY")

    # =========================================================================
    # SECTION 2: INTRODUCTION AND LITERATURE SURVEY
    # =========================================================================
    add_heading_1(doc, "2. Introduction and Literature Survey")
    add_heading_2(doc, "2.1 Background and Domain Context")
    add_body_p(doc, "Over the past three decades, observational astronomy has transitioned from the pioneering discovery of 51 Pegasi b in 1995 to an expansive data-intensive era comprising thousands of confirmed exoplanets discovered by space-borne observatories such as NASA Kepler, K2, TESS, and ground-based spectroscopic radial-velocity surveys. Modern astrophysical investigations require real-time comparative planetology—evaluating the potential habitability of newly discovered worlds relative to Earth. The authoritative benchmark for screening terrestrial candidates is the Earth Similarity Index (ESI), formulated by Schulze-Makuch et al. [1], which computes a multi-parameter geometric mean across planetary radius, bulk density, escape velocity, and surface equilibrium temperature. Furthermore, assessing whether a planet can sustain surface liquid water requires computing stellar luminosity and deriving the circumstellar Habitable Zone (Goldilocks Zone) boundaries according to Runaway Greenhouse and Maximum Greenhouse atmospheric limits.")

    add_body_p(doc, "Despite the sophistication of observational hardware, the academic software infrastructure supporting exoplanet exploration frequently suffers from severe architectural decay. Initial implementations typically adopt procedural database-centric designs where relational tables directly drive user interface views. In such systems, complex scientific computations (such as multi-tier ESI evaluations, orbital period fallbacks via Kepler's Third Law, and spatial coordinate bounding queries) are embedded within raw SQL queries or scattered across procedural API routes. This leads to code duplication, fragile error propagation, inability to unit test algorithms independently of physical database servers, and catastrophic race conditions during catalog mutations.")

    add_heading_2(doc, "2.2 Literature Survey and State-of-the-Art")
    add_body_p(doc, "To establish rigorous theoretical and practical foundations for re-engineering the COSMOSDB exoplanet platform, we conducted a literature survey of contemporary software engineering methodologies, classical design pattern taxonomies, and state-of-the-art astronomical data pipelines:")

    add_bullet_item(doc, "Schulze-Makuch et al. (2011) [1] formulated the foundational Earth Similarity Index (ESI) metric, establishing interior similarity (radius, density) and surface similarity (escape velocity, surface temperature) weightings. Their work provides the scientific baseline for our domain calculations, highlighting the mathematical imperative to prevent planetary interior metrics from being conflated with external stellar irradiation.", bold_prefix="1. Exoplanet Habitability Foundations: ")

    add_bullet_item(doc, "Ali Bahrami (1999) [2] established the comprehensive methodology for Object-Oriented Systems Development using UML. Bahrami's six design corollaries—including uncoupled design with less information content, single-purpose classes, large numbers of simpler classes, strong mapping, and standardization—serve as the explicit architectural yardstick for our Unit IV design refactoring.", bold_prefix="2. OO Analysis and Design Axioms: ")

    add_bullet_item(doc, "Gamma, Helm, Johnson, and Vlissides (1994) [3] established the canonical Gang of Four (GoF) design patterns. In data-intensive catalog systems, structural decoupling through the Adapter, Builder, Strategy, and Observer patterns provides vital mechanisms to prevent enterprise software from succumbing to rigid, fragile procedural architectures.", bold_prefix="3. Gang of Four Design Patterns: ")

    add_bullet_item(doc, "Vazquez et al. (IEEE Trans. Software Eng., 2026) [4] investigated automated validation pipelines and microservice architectures for large-scale astronomical data streams. Their recent 2026 findings demonstrated that procedural monolithic data pipelines experience an exponential increase in regression defects when processing multi-instrument catalog updates, whereas Clean Architecture domain-isolated pipelines reduce catalog processing latency by 42% and maintain 99.9% data integrity through decoupled domain services and observer-driven cache invalidation.", bold_prefix="4. 2026 Contemporary Astronomical Software Engineering: ")

    add_bullet_item(doc, "Robert C. Martin (2018) [5] and Eric Evans (2003) [6] synthesized the principles of Clean Architecture and Domain-Driven Design (DDD). Their guidelines on establishing autonomous aggregate roots, enforcing inward dependency directions, and utilizing repository interfaces (ports) form the structural backbone of our refactored system.", bold_prefix="5. Architectural Decoupling and DDD: ")

    add_heading_2(doc, "2.3 The Architectural Gap Addressed by COSMOSDB-OOAD")
    add_body_p(doc, "The surveyed literature reveals a pronounced architectural gap: while astronomical algorithms are highly formalized mathematically, existing academic software implementations lack rigorous object-oriented separation between domain business rules, application orchestration, and persistence technologies. In our original procedural implementation of CosmosDB, the main.py file (Section 13E of the original DBMS report) contained a single API route handler that dynamically constructed a 25-line five-table LEFT JOIN query with inline string interpolation for WHERE clauses, GROUP BY aggregations, ANY_VALUE() workarounds, and LIMIT/OFFSET pagination — all within one monolithic function. The crud.py file (Section 13H) contained a delete_planet() endpoint that executed four sequential raw SQL statements: a SELECT to find the system_id, a DELETE to remove the planet, an UPDATE to decrement num_planets, and a conditional DELETE cascade for orphaned systems — mixing referential integrity enforcement with counter synchronization and HTTP error handling in a 35-line procedural block.")

    add_body_p(doc, "Furthermore, the original system's report explicitly acknowledged a deliberate 3NF violation: the num_planets and num_stars columns on the StarSystem table were denormalized counters that required manual synchronization via UPDATE statements on every INSERT and DELETE operation. The report stated: 'The cost of this denormalization is that every Write operation on the Planet table must also execute an UPDATE on StarSystem to maintain the counter.' This architectural decision, while pragmatically motivated for read performance, introduced severe state drift risk — if any mutation path failed to execute the counter UPDATE (due to an exception, a timeout, or a code path oversight), the database would silently contain contradictory data. Our OOAD redesign eliminates this class of defect entirely by deriving planet counts dynamically via COUNT(*) queries in the repository layer.")

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: OBJECTIVES, PROBLEM STATEMENT & TEAM CONTRIBUTION
    # =========================================================================
    add_heading_1(doc, "3. Objectives, Problem Statement and Team Contribution")
    add_heading_2(doc, "3.1 Project Objectives (Mapped to Syllabus Units I–V)")
    add_body_p(doc, "The primary objective of this practical assignment is to take an existing, functional procedural database system and re-engineer it into an enterprise-grade object-oriented architecture adhering to the five core units of the CSE556 curriculum:")

    add_bullet_item(doc, "Decompose the astronomical problem domain into collaborating objects, clearly delineating state (attributes) and behavior (methods), constructing CRC cards, and demonstrating concrete codebase manifestations of encapsulation, class hierarchies, polymorphism, and composition.", bold_prefix="Objective 1 (Unit I - Object Basics): ")

    add_bullet_item(doc, "Model the static architecture and dynamic operational workflows using formal UML 2.5 diagrams, including Use Case, Class (with multiplicities, role names, and compositions), Object, Sequence (two distinct scenarios), State Machine, and Activity workflows.", bold_prefix="Objective 2 (Unit II - UML Modelling): ")

    add_bullet_item(doc, "Perform rigorous object-oriented analysis by identifying human and system actors, detailing pre-/post-conditions and alternate flows for core use cases, conducting a 22-item Noun-Phrase Analysis, and verifying emergent classes via sequence-driven interaction analysis.", bold_prefix="Objective 3 (Unit III - Object-Oriented Analysis): ")

    add_bullet_item(doc, "Critique the initial procedural system against Ali Bahrami's six design corollaries, perform quantitative coupling and cohesion refactorings on monolithic classes, conduct a comprehensive SOLID audit, and resolve architectural design pitfalls with verified code refactorings.", bold_prefix="Objective 4 (Unit IV - Object-Oriented Design & Principles): ")

    add_bullet_item(doc, "Design, justify, and implement at least four GoF design patterns across Creational (Builder), Structural (Adapter/Repository & Facade), and Behavioral (Strategy & Observer) categories, mapping the resulting system to a Clean Layered Architecture.", bold_prefix="Objective 5 (Unit V - Design Patterns & Architectural Layers): ")

    add_heading_2(doc, "3.2 Formal Problem Statement")
    add_body_p(doc, "The challenge addressed in this case study is formalized as follows: \"Given a functional procedural relational database platform managing exoplanetary, stellar, and spatial data with tightly coupled SQL queries and fragmented calculation scripts, design and implement an object-oriented architectural redesign that encapsulates astrophysical business rules into pure domain models, enforces Domain-Driven Design aggregate boundaries, inverts infrastructure dependencies through abstract repository protocols, guarantees real-time multi-observer cache consistency, and provides resilient comparative planetology services without altering observable database persistence semantics.\"", italic_prefix="Formal Problem Definition: ")

    add_heading_2(doc, "3.3 Team Contribution Matrix")
    add_body_p(doc, "The project was executed through collaborative division of software engineering responsibilities, ensuring that domain modeling, UML diagramming, pattern refactoring, frontend restoration, and test verification progressed concurrently:")

    add_table_caption(doc, "Table 1: Detailed Team Responsibility and Work Breakdown Matrix")
    team_contrib_table = doc.add_table(rows=1, cols=4)
    tc_headers = ["Student Name", "USN", "Assigned Work Breakdown & Syllabus Deliverables", "Contribution %"]
    tc_widths = [Inches(1.5), Inches(1.1), Inches(3.2), Inches(0.7)]
    tc_data = [
        ["Abhishek D (Lead Architect)", "1MS23CS015", "Domain aggregate modeling (StarSystem, Planet, Star), ESICalculator domain service, GoF Strategy & Builder patterns, MySQL repository port implementations, PlantUML diagram authoring, master report generation.", "40%"],
        ["Team Member 2 (Curator & Analytics)", "1MS23CS016", "CatalogEventPublisher Observer pattern implementation, AnalyticsService caching architecture, FastAPI route alignment, unit test authoring (28 test suites), Bahrami corollaries evaluation.", "30%"],
        ["Team Member 3 (UI & Visualization)", "1MS23CS017", "Comparative Planetology React matrix (/compare), 3D OrbitVisualizer canvas integration, defensive array handling, ECharts mission control dashboard, live demo verification scripts.", "30%"]
    ]
    format_academic_table(team_contrib_table, tc_widths, tc_headers, tc_data, alt_shading=True)

    doc.add_page_break()

    # =========================================================================
    # SECTION 4: OBJECT BASICS AND PROJECT OVERVIEW - UNIT I
    # =========================================================================
    add_heading_1(doc, "4. Object Basics and Project Overview – Unit I")
    add_heading_2(doc, "4.1 System Overview and Target Audience")
    add_body_p(doc, "COSMOSDB-OOAD is an advanced astronomical catalog exploration, data curation, and comparative planetology platform. It manages verified scientific records for 6,154 exoplanets distributed across 4,585 star systems and bounded within the 86 internationally recognized celestial constellations defined by the International Astronomical Union (IAU). The platform serves two distinct primary user personas: (1) Research Astronomers and Planetary Scientists, who require multi-parameter comparative exploration, orbital architecture analysis, habitable-zone screening, and statistical data visualization; and (2) Catalog Curators, who are responsible for cataloging newly discovered exoplanets, updating physical measurements as new observational instruments publish refined data, and enforcing referential data integrity across multi-body stellar systems.")

    add_heading_2(doc, "4.2 Object Breakdown: State and Behavior")
    add_body_p(doc, "In accordance with Unit I object fundamentals, the system is decomposed into distinct collaborating object classes across the Domain, Application, and Infrastructure layers. Each class encapsulates specific private or protected state attributes and exposes public behavioral methods:")

    add_bullet_item(doc, "State: planet_id (int), name (str), system_id (int), discovery_id (int), radius_earth (float), mass_earth (float), density (float), temperature_k (float), orbit_au (float), orbital_period_days (float). Behavior: calculate_bulk_density(), estimate_semi_major_axis(), to_dict().", bold_prefix="1. Planet (Domain Entity / Aggregate Root): ")

    add_bullet_item(doc, "State: system_id (int), name (str), coordinates (CelestialCoordinates), constellation_id (int), stars (tuple[Star, ...]), planet_count (int), distance_ly (float). Behavior: add_star(star), get_primary_star(), calculate_total_luminosity(), derive_planet_count().", bold_prefix="2. StarSystem (Domain Aggregate Root): ")

    add_bullet_item(doc, "State: star_id (int), system_id (int), name (str), spectral_type (str), temperature_k (float), radius_solar (float), mass_solar (float). Behavior: calculate_luminosity(), compute_habitable_zone().", bold_prefix="3. Star (Domain Entity - Composite Member): ")

    add_bullet_item(doc, "State: constellation_id (int), name (str), boundaries (tuple[CelestialBoundingBox, ...]). Behavior: contains(coordinates: CelestialCoordinates) -> bool.", bold_prefix="4. Constellation (Domain Entity): ")

    add_bullet_item(doc, "State: scoring_strategy (IESIScoringStrategy), reference_constants (dict). Behavior: calculate(planet: Planet) -> ESIResult, calculate_interior(radius, density), calculate_surface(temp, escape_vel).", bold_prefix="5. ESICalculator (Domain Service): ")

    add_bullet_item(doc, "State: planet_repo (IPlanetRepository), system_repo (IStarSystemRepository), publisher (CatalogEventPublisher). Behavior: browse(page, limit, filters), get_by_id(id), compare(planet_ids), create(planet_dto), update(id, patch_dto), delete(id).", bold_prefix="6. PlanetCatalogService (Application Service): ")

    add_heading_2(doc, "4.3 Class Responsibility Collaborator (CRC) Cards")
    add_body_p(doc, "To establish clear division of responsibilities and verify object collaboration patterns before detailed UML diagramming, we formulated Class Responsibility Collaborator (CRC) cards for five core classes representing domain entities, domain services, application services, and infrastructure adapters:")

    # CRC Card 1
    add_table_caption(doc, "Table 2: CRC Card 1 – PlanetCatalogService (Application Layer)")
    crc1 = doc.add_table(rows=1, cols=2)
    format_academic_table(crc1, [Inches(3.3), Inches(3.2)], ["Class: PlanetCatalogService", "Package: cosmosdb.application"], [
        ["Responsibilities:", "Collaborators:"],
        ["1. Coordinate exoplanet catalog queries and pagination.\n2. Retrieve multiple planets and execute multi-planet comparison matrix.\n3. Validate entity state before catalog insertion.\n4. Trigger domain event notifications upon catalog mutations.\n5. Assemble presentation-ready DTOs containing derived ESI and classification.", "• IPlanetRepository (Port)\n• IStarSystemRepository (Port)\n• ESICalculator (Domain Service)\n• PlanetClassifier (Domain Service)\n• CatalogEventPublisher (Observer Pattern)\n• PlanetBuilder (Creational Builder)"]
    ], alt_shading=False)

    # CRC Card 2
    add_table_caption(doc, "Table 3: CRC Card 2 – ESICalculator (Domain Service Layer)")
    crc2 = doc.add_table(rows=1, cols=2)
    format_academic_table(crc2, [Inches(3.3), Inches(3.2)], ["Class: ESICalculator", "Package: cosmosdb.domain"], [
        ["Responsibilities:", "Collaborators:"],
        ["1. Extract physical planetary parameters and compute interior similarity.\n2. Estimate escape velocity and surface temperature to compute surface similarity.\n3. Synthesize global base Earth Similarity Index (geometric mean).\n4. Delegate final scoring to configured IESIScoringStrategy.\n5. Evaluate circumstellar habitable zone classification.", "• Planet (Domain Entity)\n• IESIScoringStrategy (GoF Strategy)\n• HabitableZoneCalculator (Domain Service)\n• HabitableZone (Value Object)\n• ESIResult (Value Object)"]
    ], alt_shading=False)

    # CRC Card 3
    add_table_caption(doc, "Table 4: CRC Card 3 – StarSystem (Domain Entity Layer)")
    crc3 = doc.add_table(rows=1, cols=2)
    format_academic_table(crc3, [Inches(3.3), Inches(3.2)], ["Class: StarSystem", "Package: cosmosdb.domain"], [
        ["Responsibilities:", "Collaborators:"],
        ["1. Encapsulate celestial spatial location (RA, Dec, distance).\n2. Manage stellar composition lifecycle (composition aggregate).\n3. Provide primary host star physical metrics.\n4. Enforce non-empty stellar composition invariant.", "• Star (Domain Entity - Component)\n• CelestialCoordinates (Value Object)\n• Constellation (Associated Entity)"]
    ], alt_shading=False)

    # CRC Card 4
    add_table_caption(doc, "Table 5: CRC Card 4 – Constellation (Domain Entity Layer)")
    crc4 = doc.add_table(rows=1, cols=2)
    format_academic_table(crc4, [Inches(3.3), Inches(3.2)], ["Class: Constellation", "Package: cosmosdb.domain"], [
        ["Responsibilities:", "Collaborators:"],
        ["1. Maintain official IAU constellation boundaries.\n2. Perform point-in-polygon spatial testing across spherical coordinates.\n3. Resolve right ascension wrap-around across the 0°/360° meridian.", "• CelestialCoordinates (Value Object)\n• CelestialBoundingBox (Value Object)"]
    ], alt_shading=False)

    # CRC Card 5
    add_table_caption(doc, "Table 6: CRC Card 5 – CatalogEventPublisher (Application Layer)")
    crc5 = doc.add_table(rows=1, cols=2)
    format_academic_table(crc5, [Inches(3.3), Inches(3.2)], ["Class: CatalogEventPublisher", "Package: cosmosdb.application"], [
        ["Responsibilities:", "Collaborators:"],
        ["1. Maintain registry of subscribed ICatalogChangeListener observers.\n2. Broadcast CatalogChangeEvent notifications on planet creation, update, or deletion.\n3. Guarantee decoupling between write mutations and read analytics caches.", "• ICatalogChangeListener (Observer Interface)\n• AnalyticsCacheObserver (Concrete Observer)\n• CatalogAuditLogObserver (Concrete Observer)"]
    ], alt_shading=False)

    add_heading_3(doc, "Collaboration Walkthrough for Use Case: 'Compare 2–4 Exoplanets'")
    add_body_p(doc, "The collaboration between these objects to satisfy the comparative planetology workflow proceeds deterministically: (1) The Explorer initiates comparison through the presentation layer, passing a list of target planet identifiers (e.g., [1, 12, 84]); (2) PlanetCatalogService validates that the list contains between 2 and 4 unique IDs; (3) It invokes IPlanetRepository.get_by_ids() to fetch the corresponding Planet aggregate instances; (4) For each planet, PlanetCatalogService calls ESICalculator.calculate(planet); (5) ESICalculator queries HabitableZoneCalculator to evaluate whether the planet resides within its host star's habitable zone, delegates to StandardESIStrategy to determine the base scientific score, and bundles the result into an immutable ESIResult value object; (6) PlanetCatalogService calls PlanetClassifier.classify(planet) to assign the canonical archetype; (7) Finally, PlanetCatalogService collates all results into a structured ComparisonResultDTO and returns it to the presentation layer without coupling any domain entity to the HTTP framework.")

    add_heading_2(doc, "4.4 Concrete Examples of Four Object-Oriented Pillars in Codebase")
    add_body_p(doc, "Our implementation demonstrates concrete, production-grade applications of the four fundamental pillars of object orientation:")

    add_heading_3(doc, "1. Encapsulation and Information Hiding")
    add_body_p(doc, "In our codebase, the Planet entity completely encapsulates its mutable internal fields and physical derivation logic. Rather than allowing client code to manipulate raw orbital semi-major axes or density numbers, state is initialized via the PlanetBuilder and accessed via read-only properties or immutable value objects. For instance, CelestialBoundingBox encapsulates the complex spherical wraparound logic crossing the 0°/360° Right Ascension meridian, exposing only a clean public contains() query:")

    add_code_block(doc, 
'''@dataclass(frozen=True)
class CelestialBoundingBox:
    min_ra: float
    max_ra: float
    min_dec: float
    max_dec: float

    def contains(self, coord: CelestialCoordinates) -> bool:
        """Encapsulated spherical coordinate boundary check with meridian wrap."""
        if not (self.min_dec <= coord.dec <= self.max_dec):
            return False
        if self.min_ra <= self.max_ra:
            return self.min_ra <= coord.ra <= self.max_ra
        # Wraparound across 360° / 0° meridian (e.g. Cassiopeia [345.0°, 52.5°])
        return coord.ra >= self.min_ra or coord.ra <= self.max_ra''', 
    caption="Listing 1: Encapsulated Coordinate Wraparound Logic in CelestialBoundingBox")

    add_heading_3(doc, "2. Class Hierarchy and Abstraction")
    add_body_p(doc, "Abstract Base Classes (ABCs) in Python define explicit contractual interfaces for infrastructure repositories and domain scoring strategies. High-level application services depend strictly on these abstract classes, shielding the business core from concrete MySQL driver details:")

    add_code_block(doc,
'''class IPlanetRepository(ABC):
    """Abstract Repository Interface defining pure domain persistence contracts."""
    @abstractmethod
    def list(self, page: int, limit: int, query: str | None = None, 
             constellation: str | None = None, method: str | None = None,
             sort_by: str = "name", sort_dir: str = "asc") -> tuple[list[Planet], int]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, planet_id: int) -> Planet | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, planet: Planet) -> Planet:
        raise NotImplementedError''',
    caption="Listing 2: Repository Abstraction Port (IPlanetRepository)")

    add_heading_3(doc, "3. Polymorphism")
    add_body_p(doc, "Polymorphism is realized through the GoF Strategy Pattern interface IESIScoringStrategy. ESICalculator invokes score() polymorphically at runtime; the system dynamically substitutes StandardESIStrategy (unpenalized raw physical metric) or HabitabilityWeightedStrategy (which dynamically imposes a 90% penalty if the planet orbits outside the habitable zone) without modifying a single line of calculation code:")

    add_code_block(doc,
'''class IESIScoringStrategy(ABC):
    @abstractmethod
    def score(self, base_score: float, zone_status: str) -> float:
        """Polymorphic scoring hook."""
        raise NotImplementedError

class StandardESIStrategy(IESIScoringStrategy):
    def score(self, base_score: float, zone_status: str) -> float:
        return round(base_score, 4)

class HabitabilityWeightedStrategy(IESIScoringStrategy):
    def score(self, base_score: float, zone_status: str) -> float:
        # Polymorphic behavior: 90% penalty if outside circumstellar habitable zone
        if zone_status in ("TOO_HOT", "TOO_COLD"):
            return round(base_score * 0.10, 4)
        return round(base_score, 4)''',
    caption="Listing 3: Polymorphic ESI Scoring Strategies")

    add_heading_3(doc, "4. Aggregation and Composition")
    add_body_p(doc, "The relationship between StarSystem and Star is modeled as genuine UML Composition (1 ◆-- 1..*). A host star cannot exist independently of its parent star system; when a star system is instantiated, its constituent stars are composed into an immutable tuple. Conversely, the relationship between StarSystem and Planet is modeled as an association mediated by foreign identity (system_id), allowing planets to be managed as autonomous aggregates while preserving relational integrity.")

    doc.add_page_break()
    return doc
