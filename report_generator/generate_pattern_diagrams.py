"""
generate_pattern_diagrams.py
Generates Before vs. After UML class diagrams for each of the 4 GoF design patterns.
Uses PIL/Pillow to draw clean, publication-ready UML class box diagrams.
"""
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")

# Colors
BG_COLOR = (255, 255, 255)
HEADER_BG_BEFORE = (180, 50, 50)      # Muted red for "Before"
HEADER_BG_AFTER  = (40, 110, 60)       # Muted green for "After"
HEADER_FG = (255, 255, 255)
CLASS_BG = (248, 248, 252)
CLASS_BORDER = (80, 80, 100)
IFACE_BORDER = (40, 90, 160)
IFACE_BG = (235, 242, 255)
ARROW_COLOR = (80, 80, 100)
LABEL_COLOR = (60, 60, 60)
TITLE_COLOR = (27, 54, 93)            # Academic navy
STEREOTYPE_COLOR = (100, 100, 140)
NOTE_BG = (255, 255, 220)
NOTE_BORDER = (200, 180, 100)

# Fonts - try to use clean fonts available on Windows
def get_fonts():
    sizes = {}
    for name, sz in [("title", 22), ("label", 16), ("class_name", 15),
                     ("member", 12), ("stereotype", 11), ("note", 11), ("arrow_label", 11)]:
        try:
            sizes[name] = ImageFont.truetype("arial.ttf", sz)
        except OSError:
            try:
                sizes[name] = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", sz)
            except OSError:
                sizes[name] = ImageFont.load_default()
    # Bold fonts
    for name, sz in [("title_bold", 24), ("class_name_bold", 15), ("label_bold", 16)]:
        try:
            sizes[name] = ImageFont.truetype("arialbd.ttf", sz)
        except OSError:
            try:
                sizes[name] = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", sz)
            except OSError:
                sizes[name] = sizes.get("title", ImageFont.load_default())
    # Italic
    for name, sz in [("stereotype_italic", 11), ("note_italic", 11)]:
        try:
            sizes[name] = ImageFont.truetype("ariali.ttf", sz)
        except OSError:
            try:
                sizes[name] = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", sz)
            except OSError:
                sizes[name] = sizes.get("stereotype", ImageFont.load_default())
    return sizes

FONTS = get_fonts()

# ---------------------------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------------------------

def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_class_box(draw, x, y, name, attributes, methods, 
                   is_interface=False, stereotype=None, min_width=180):
    """Draw a UML class box and return (x, y, w, h)."""
    font_name = FONTS["class_name_bold"]
    font_member = FONTS["member"]
    font_stereo = FONTS["stereotype_italic"]
    
    bg = IFACE_BG if is_interface else CLASS_BG
    border = IFACE_BORDER if is_interface else CLASS_BORDER
    
    # Calculate widths
    pad_x, pad_y = 12, 6
    lines_all = [name] + attributes + methods
    if stereotype:
        lines_all.append(stereotype)
    
    max_w = min_width
    for line in attributes + methods:
        w, _ = text_size(draw, line, font_member)
        max_w = max(max_w, w + 2 * pad_x)
    nw, _ = text_size(draw, name, font_name)
    max_w = max(max_w, nw + 2 * pad_x)
    if stereotype:
        sw, _ = text_size(draw, stereotype, font_stereo)
        max_w = max(max_w, sw + 2 * pad_x)
    
    box_w = max_w + 4
    
    # Heights
    line_h = 18
    stereo_h = line_h if stereotype else 0
    name_h = line_h + 4
    attr_h = max(len(attributes) * line_h, line_h // 2) + pad_y
    meth_h = max(len(methods) * line_h, line_h // 2) + pad_y
    box_h = stereo_h + name_h + attr_h + meth_h + 2 * pad_y
    
    # Draw box
    draw.rectangle([x, y, x + box_w, y + box_h], fill=bg, outline=border, width=2)
    
    cur_y = y + pad_y
    
    # Stereotype
    if stereotype:
        sw, _ = text_size(draw, stereotype, font_stereo)
        draw.text((x + (box_w - sw) // 2, cur_y), stereotype, fill=STEREOTYPE_COLOR, font=font_stereo)
        cur_y += stereo_h
    
    # Name (centered, bold)
    nw, _ = text_size(draw, name, font_name)
    draw.text((x + (box_w - nw) // 2, cur_y), name, fill=(30, 30, 30), font=font_name)
    cur_y += name_h
    
    # Separator line 1
    draw.line([(x, cur_y), (x + box_w, cur_y)], fill=border, width=1)
    cur_y += 3
    
    # Attributes
    for attr in attributes:
        draw.text((x + pad_x, cur_y), attr, fill=LABEL_COLOR, font=font_member)
        cur_y += line_h
    if not attributes:
        cur_y += line_h // 2
    cur_y += 3
    
    # Separator line 2
    draw.line([(x, cur_y), (x + box_w, cur_y)], fill=border, width=1)
    cur_y += 3
    
    # Methods
    for meth in methods:
        draw.text((x + pad_x, cur_y), meth, fill=LABEL_COLOR, font=font_member)
        cur_y += line_h
    
    return (x, y, box_w, box_h)

def draw_arrow(draw, x1, y1, x2, y2, style="solid", label=None, head="closed"):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    import math
    if style == "dashed":
        # Draw dashed line
        total_len = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        dash_len = 8
        gap_len = 5
        dx = (x2-x1) / total_len
        dy = (y2-y1) / total_len
        pos = 0
        while pos < total_len:
            sx = x1 + dx * pos
            sy = y1 + dy * pos
            end = min(pos + dash_len, total_len)
            ex = x1 + dx * end
            ey = y1 + dy * end
            draw.line([(sx, sy), (ex, ey)], fill=ARROW_COLOR, width=2)
            pos += dash_len + gap_len
    else:
        draw.line([(x1, y1), (x2, y2)], fill=ARROW_COLOR, width=2)
    
    # Arrowhead
    import math
    angle = math.atan2(y2-y1, x2-x1)
    arrow_len = 12
    arrow_angle = math.pi / 7
    
    ax1 = x2 - arrow_len * math.cos(angle - arrow_angle)
    ay1 = y2 - arrow_len * math.sin(angle - arrow_angle)
    ax2 = x2 - arrow_len * math.cos(angle + arrow_angle)
    ay2 = y2 - arrow_len * math.sin(angle + arrow_angle)
    
    if head == "closed":
        draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=ARROW_COLOR)
    elif head == "open":
        draw.line([(ax1, ay1), (x2, y2)], fill=ARROW_COLOR, width=2)
        draw.line([(ax2, ay2), (x2, y2)], fill=ARROW_COLOR, width=2)
    elif head == "diamond":
        mid_x = (ax1 + ax2) / 2
        mid_y = (ay1 + ay2) / 2
        far_x = mid_x - (x2 - mid_x)
        far_y = mid_y - (y2 - mid_y)
        draw.polygon([(x2, y2), (ax1, ay1), (far_x, far_y), (ax2, ay2)], 
                     fill=BG_COLOR, outline=ARROW_COLOR)
    
    if label:
        lw, lh = text_size(draw, label, FONTS["arrow_label"])
        mx = (x1 + x2) // 2 - lw // 2
        my = (y1 + y2) // 2 - lh - 4
        draw.text((mx, my), label, fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])

def draw_note_box(draw, x, y, lines, max_width=220):
    """Draw a UML note (folded corner) box."""
    font = FONTS["note"]
    pad = 8
    line_h = 16
    h = len(lines) * line_h + 2 * pad
    w = max_width
    fold = 14
    
    # Note shape with folded corner
    points = [(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)]
    draw.polygon(points, fill=NOTE_BG, outline=NOTE_BORDER)
    # Fold triangle
    draw.polygon([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)],
                 fill=(240, 240, 200), outline=NOTE_BORDER)
    
    cur_y = y + pad
    for line in lines:
        draw.text((x + pad, cur_y), line, fill=LABEL_COLOR, font=font)
        cur_y += line_h
    
    return (x, y, w, h)

def draw_section_header(draw, x, y, w, text, is_before=True):
    """Draw a colored banner header for Before/After sections."""
    h = 32
    bg = HEADER_BG_BEFORE if is_before else HEADER_BG_AFTER
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    tw, th = text_size(draw, text, FONTS["label_bold"])
    draw.text((x + (w - tw) // 2, y + (h - th) // 2), text, fill=HEADER_FG, font=FONTS["label_bold"])
    return h

# ---------------------------------------------------------------------------
# DIAGRAM GENERATORS
# ---------------------------------------------------------------------------

def generate_builder_diagram():
    """Generate Before vs After UML diagram for Builder Pattern."""
    img = Image.new("RGB", (1100, 520), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Title
    title = "Figure 8: Builder Pattern — Before vs. After Class Diagram"
    tw, _ = text_size(draw, title, FONTS["title_bold"])
    draw.text(((1100 - tw) // 2, 10), title, fill=TITLE_COLOR, font=FONTS["title_bold"])
    
    # Divider
    draw.line([(545, 42), (545, 510)], fill=(180, 180, 200), width=2)
    
    # === BEFORE ===
    bh = draw_section_header(draw, 10, 45, 525, "BEFORE (Procedural — crud.py)", is_before=True)
    
    # Single monolithic function box
    draw_class_box(draw, 60, 95, "crud.py", 
        ["  (no classes)"],
        ["+ create_planet(planet_name,",
         "    sys_id, disc_id, is_cb,",
         "    p_per, p_rad, p_re, p_me,",
         "    p_den, p_ecc, p_insol,",
         "    p_temp, ttv): dict",
         "  → 13 raw positional params",
         "  → inline SQL INSERT",
         "  → no validation"],
        min_width=240)
    
    # Note
    draw_note_box(draw, 330, 110, [
        "⚠ No domain validation",
        "⚠ 13 positional %s args",
        "⚠ Swap radius/mass →",
        "   silent data corruption",
        "⚠ MySQL CHECK is only",
        "   safety net (HTTP 500)"
    ], max_width=200)
    
    # Arrow from function to DB
    draw_class_box(draw, 150, 380, "MySQL", 
        ["planet table"],
        ["INSERT INTO planet ..."],
        min_width=180)
    draw_arrow(draw, 180, 310, 210, 380, label="raw SQL")
    
    # === AFTER ===
    ah = draw_section_header(draw, 560, 45, 530, "AFTER (OO — PlanetBuilder)", is_before=False)
    
    # Planet entity
    draw_class_box(draw, 580, 95, "Planet",
        ["- planet_id: int", "- name: str",
         "- radius_earth: float", "- mass_earth: float",
         "- density: float"],
        ["+ __init__(**attrs)"],
        min_width=190)
    
    # PlanetBuilder
    b = draw_class_box(draw, 830, 95, "PlanetBuilder",
        ["- _attrs: dict"],
        ["+ set(name, value): self",
         "+ build(): Planet",
         "- _validate_physics()",
         "- _compute_fallbacks()"],
        min_width=210)
    
    # Arrow: Builder creates Planet
    draw_arrow(draw, 830, 185, 770, 185, label="«creates»", style="dashed", head="open")
    
    # Service uses Builder
    draw_class_box(draw, 650, 360, "PlanetCatalogService",
        ["- _repo: IPlanetRepository"],
        ["+ create(values): dict"],
        min_width=220)
    
    draw_arrow(draw, 870, 310, 800, 360, label="uses", style="dashed", head="open")
    draw_arrow(draw, 760, 310, 700, 360, style="dashed", head="open")
    
    # Note
    draw_note_box(draw, 900, 350, [
        "✓ Named parameters",
        "✓ Domain validation",
        "✓ Auto-derive density",
        "✓ Fail-fast invariants"
    ], max_width=180)
    
    img.save(os.path.join(DIAGRAMS_DIR, "pattern_builder.png"), "PNG", dpi=(150, 150))
    print("  ✓ pattern_builder.png")


def generate_repository_diagram():
    """Generate Before vs After UML diagram for Repository/Adapter Pattern."""
    img = Image.new("RGB", (1100, 520), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    title = "Figure 9: Repository/Adapter Pattern — Before vs. After Class Diagram"
    tw, _ = text_size(draw, title, FONTS["title_bold"])
    draw.text(((1100 - tw) // 2, 10), title, fill=TITLE_COLOR, font=FONTS["title_bold"])
    
    draw.line([(545, 42), (545, 510)], fill=(180, 180, 200), width=2)
    
    # === BEFORE ===
    draw_section_header(draw, 10, 45, 525, "BEFORE (Procedural — main.py)", is_before=True)
    
    draw_class_box(draw, 50, 95, "main.py (Route Handler)",
        ["  (no classes)"],
        ["+ get_observatory():",
         "    db = get_db()",
         "    cur = db.cursor()",
         "    cur.execute(SQL_JOIN)",
         "    rows = cur.fetchall()",
         "    return format_json(rows)"],
        min_width=260)
    
    draw_class_box(draw, 350, 95, "mysql.connector",
        ["- host, port, user"],
        ["+ connect(): Connection",
         "+ cursor(): Cursor",
         "+ execute(sql): None"],
        min_width=170)
    
    draw_arrow(draw, 310, 180, 350, 180, label="direct import")
    
    draw_note_box(draw, 60, 340, [
        "⚠ Route ↔ MySQL tightly coupled",
        "⚠ Cannot unit test without DB",
        "⚠ Database swap = rewrite all"
    ], max_width=250)
    
    # === AFTER ===
    draw_section_header(draw, 560, 45, 530, "AFTER (OO — Repository/Adapter)", is_before=False)
    
    # Interface
    draw_class_box(draw, 700, 95, "IPlanetRepository",
        [],
        ["+ find_by_id(id): Planet",
         "+ list(...): list[Planet]",
         "+ create(planet): Planet",
         "+ delete(id): bool"],
        is_interface=True, stereotype="«interface»",
        min_width=210)
    
    # Concrete impl
    draw_class_box(draw, 650, 320, "MySQLPlanetRepository",
        ["- _conn_factory: Callable"],
        ["+ find_by_id(id): Planet",
         "+ list(...): list[Planet]",
         "+ create(planet): Planet",
         "+ delete(id): bool",
         "- _map_to_entity(row)"],
        min_width=230)
    
    # Service depends on interface
    draw_class_box(draw, 580, 95, "PlanetCatalogService",
        ["- _repo: IPlanetRepository"],
        ["+ browse(): PageDTO"],
        min_width=120)
    
    # Arrows
    draw_arrow(draw, 630, 140, 700, 140, style="dashed", head="open")  # Service → Interface
    draw_arrow(draw, 765, 320, 765, 260, style="dashed", head="open")  # Impl → Interface (implements)
    
    # Implements label
    lw, _ = text_size(draw, "«implements»", FONTS["arrow_label"])
    draw.text((770, 282), "«implements»", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    
    draw_note_box(draw, 900, 340, [
        "✓ Testable with mocks",
        "✓ DB-agnostic service",
        "✓ Dependency inversion"
    ], max_width=180)
    
    img.save(os.path.join(DIAGRAMS_DIR, "pattern_repository.png"), "PNG", dpi=(150, 150))
    print("  ✓ pattern_repository.png")


def generate_strategy_diagram():
    """Generate Before vs After UML diagram for Strategy Pattern."""
    img = Image.new("RGB", (1100, 540), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    title = "Figure 10: Strategy Pattern — Before vs. After Class Diagram"
    tw, _ = text_size(draw, title, FONTS["title_bold"])
    draw.text(((1100 - tw) // 2, 10), title, fill=TITLE_COLOR, font=FONTS["title_bold"])
    
    draw.line([(545, 42), (545, 530)], fill=(180, 180, 200), width=2)
    
    # === BEFORE ===
    draw_section_header(draw, 10, 45, 525, "BEFORE (Procedural — utils.py)", is_before=True)
    
    draw_class_box(draw, 60, 100, "utils.py",
        ["  (no classes)"],
        ["+ calculate_esi(radius,",
         "    mass, temp, density,",
         "    flux, star_lum,",
         "    penalize_hz=False):",
         "  if penalize_hz:",
         "    score *= 0.1",
         "  return score"],
        min_width=250)
    
    draw_note_box(draw, 340, 110, [
        "⚠ Boolean flag toggles",
        "   behavior internally",
        "⚠ New policy = modify",
        "   existing function",
        "⚠ Violates Open/Closed"
    ], max_width=190)
    
    # === AFTER ===
    draw_section_header(draw, 560, 45, 530, "AFTER (OO — Strategy Pattern)", is_before=False)
    
    # Context
    draw_class_box(draw, 570, 100, "ESICalculator",
        ["- _strategy: IESIScoringStrategy"],
        ["+ calculate(planet): ESIResult"],
        min_width=230)
    
    # Interface
    draw_class_box(draw, 700, 260, "IESIScoringStrategy",
        [],
        ["+ score(base, zone): float"],
        is_interface=True, stereotype="«interface»",
        min_width=200)
    
    # Concrete A
    draw_class_box(draw, 580, 410, "StandardESIStrategy",
        [],
        ["+ score(base, zone): float",
         "  → return base"],
        min_width=200)
    
    # Concrete B
    draw_class_box(draw, 850, 410, "HabitabilityWeighted\nStrategy",
        [],
        ["+ score(base, zone): float",
         "  → penalty if !HZ"],
        min_width=200)
    
    # Arrows
    draw_arrow(draw, 720, 210, 770, 260, style="dashed", head="open")  # Context → Interface
    draw.text((730, 225), "uses ▸", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    
    draw_arrow(draw, 680, 410, 740, 350, style="dashed", head="open")  # Std → Interface
    draw_arrow(draw, 920, 410, 850, 350, style="dashed", head="open")  # Weighted → Interface
    
    draw.text((620, 375), "«implements»", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    draw.text((870, 375), "«implements»", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    
    draw_note_box(draw, 900, 100, [
        "✓ New policy = new class",
        "✓ No modification needed",
        "✓ Runtime substitution"
    ], max_width=180)
    
    img.save(os.path.join(DIAGRAMS_DIR, "pattern_strategy.png"), "PNG", dpi=(150, 150))
    print("  ✓ pattern_strategy.png")


def generate_observer_diagram():
    """Generate Before vs After UML diagram for Observer Pattern."""
    img = Image.new("RGB", (1100, 540), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    title = "Figure 11: Observer Pattern — Before vs. After Class Diagram"
    tw, _ = text_size(draw, title, FONTS["title_bold"])
    draw.text(((1100 - tw) // 2, 10), title, fill=TITLE_COLOR, font=FONTS["title_bold"])
    
    draw.line([(545, 42), (545, 530)], fill=(180, 180, 200), width=2)
    
    # === BEFORE ===
    draw_section_header(draw, 10, 45, 525, "BEFORE (Procedural — crud.py)", is_before=True)
    
    draw_class_box(draw, 40, 100, "crud.py",
        ["  (no classes)"],
        ["+ delete_planet(id):",
         "  DELETE FROM planet ...",
         "  UPDATE StarSystem SET",
         "   num_planets -= 1",
         "  # NO cache invalidation",
         "  # NO audit logging"],
        min_width=240)
    
    draw_class_box(draw, 310, 100, "analytics.py",
        ["  (no classes)"],
        ["+ get_charts():",
         "  # Re-runs ALL queries",
         "  # every single request",
         "  # NO caching at all"],
        min_width=200)
    
    draw_note_box(draw, 60, 370, [
        "⚠ Manual counter UPDATE",
        "⚠ No notification system",
        "⚠ analytics.py re-queries",
        "   6154 planets each visit",
        "⚠ No audit trail"
    ], max_width=220)
    
    # Dashed line showing "no connection"
    draw.text((310, 280), "no link between", fill=(180, 50, 50), font=FONTS["note"])
    draw.text((310, 296), "mutation ↔ analytics", fill=(180, 50, 50), font=FONTS["note"])
    
    # === AFTER ===
    draw_section_header(draw, 560, 45, 530, "AFTER (OO — Observer Pattern)", is_before=False)
    
    # Publisher (Subject)
    draw_class_box(draw, 650, 100, "CatalogEventPublisher",
        ["- _listeners: list[Listener]"],
        ["+ subscribe(listener): void",
         "+ publish(event): void"],
        min_width=230)
    
    # Interface
    draw_class_box(draw, 650, 270, "ICatalogChangeListener",
        [],
        ["+ on_catalog_change(event)"],
        is_interface=True, stereotype="«interface»",
        min_width=220)
    
    # Concrete Observer A
    draw_class_box(draw, 570, 420, "AnalyticsCache\nObserver",
        ["- _invalidate: Callable"],
        ["+ on_catalog_change(e)"],
        min_width=170)
    
    # Concrete Observer B
    draw_class_box(draw, 810, 420, "CatalogAuditLog\nObserver",
        ["- _logger: Logger"],
        ["+ on_catalog_change(e)"],
        min_width=170)
    
    # Arrows
    draw_arrow(draw, 765, 210, 765, 270, style="dashed", head="open")
    draw.text((772, 230), "notifies ▾", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    
    draw_arrow(draw, 660, 420, 710, 365, style="dashed", head="open")
    draw_arrow(draw, 880, 420, 820, 365, style="dashed", head="open")
    
    draw.text((590, 395), "«implements»", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    draw.text((835, 395), "«implements»", fill=STEREOTYPE_COLOR, font=FONTS["arrow_label"])
    
    # Service publishes
    draw_class_box(draw, 920, 130, "PlanetCatalog\nService",
        [],
        ["+ delete(id)",
         "+ create(vals)"],
        min_width=140)
    
    draw_arrow(draw, 920, 170, 880, 170, label="publishes", head="open")
    
    draw_note_box(draw, 920, 270, [
        "✓ Auto cache eviction",
        "✓ Auto audit logging",
        "✓ Loosely coupled",
        "✓ Add observers freely"
    ], max_width=160)
    
    img.save(os.path.join(DIAGRAMS_DIR, "pattern_observer.png"), "PNG", dpi=(150, 150))
    print("  ✓ pattern_observer.png")


def main():
    os.makedirs(DIAGRAMS_DIR, exist_ok=True)
    print("Generating Before vs. After UML class diagrams for Design Patterns...")
    generate_builder_diagram()
    generate_repository_diagram()
    generate_strategy_diagram()
    generate_observer_diagram()
    print(f"All 4 pattern diagrams saved to: {DIAGRAMS_DIR}")


if __name__ == "__main__":
    main()
