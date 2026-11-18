import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color palette: Academic Navy / Slate
COLOR_NAVY = RGBColor(0x1B, 0x36, 0x5D)
COLOR_TEXT_MAIN = RGBColor(0x22, 0x22, 0x22)
COLOR_MUTED = RGBColor(0x55, 0x55, 0x55)
HEX_HEADER_BG = "1B365D"       # Deep academic navy
HEX_ALT_ROW = "F7F9FB"         # Very soft icy slate
HEX_CODE_BG = "F4F5F7"         # Clean light gray
HEX_CALLOUT_BG = "EDF2F7"      # Soft blue-gray
HEX_BORDER = "CCCCCC"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner margins (padding) for a table cell in dxa (1/20 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, hex_color):
    """Set background color of a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left=None, right=None, sz="4"):
    """Set custom borders on a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'w:top': top, 'w:bottom': bottom, 'w:left': left, 'w:right': right}
    for border_name, color in borders.items():
        if color:
            b = OxmlElement(border_name)
            b.set(qn('w:val'), 'single')
            b.set(qn('w:sz'), sz)
            b.set(qn('w:space'), '0')
            b.set(qn('w:color'), color)
            tcBorders.append(b)
        else:
            b = OxmlElement(border_name)
            b.set(qn('w:val'), 'none')
            tcBorders.append(b)
    tcPr.append(tcBorders)

def create_report_document():
    """Create and configure base Document matching RIT CSE556 guidelines."""
    doc = Document()
    
    # 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Configure Header and Footer for subsequent pages
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("COSMOSDB-OOAD | Case Study Report (CSE556)")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.italic = True
        hrun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Department of Computer Science & Engineering, Ramaiah Institute of Technology")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # Base style
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(12)
    normal.font.color.rgb = COLOR_TEXT_MAIN
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.space_before = Pt(0)
    
    return doc

def add_heading_1(doc, text):
    """Add Level 1 Section Heading (16 pt, Bold)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def add_heading_2(doc, text):
    """Add Level 2 Sub-Heading (14 pt, Bold)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def add_heading_3(doc, text):
    """Add Level 3 Sub-Heading (13 pt, Bold/Italic)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.italic = True
    run.font.color.rgb = COLOR_TEXT_MAIN
    return p

def add_body_p(doc, text, bold_prefix=None, italic_prefix=None):
    """Add standard justified 12pt body paragraph with 1.5 line spacing."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(0)
    
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(12)
        r_bold.font.bold = True
        r_bold.font.color.rgb = COLOR_TEXT_MAIN
        
    if italic_prefix:
        r_it = p.add_run(italic_prefix)
        r_it.font.name = 'Times New Roman'
        r_it.font.size = Pt(12)
        r_it.font.italic = True
        r_it.font.color.rgb = COLOR_TEXT_MAIN

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12)
    r_text.font.color.rgb = COLOR_TEXT_MAIN
    return p

def add_bullet_item(doc, text, bold_prefix=None):
    """Add a bullet point paragraph."""
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(0)
    
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(12)
        r_b.font.bold = True
        
    r_t = p.add_run(text)
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(12)
    return p

def add_table_caption(doc, caption_text):
    """Add Table caption ABOVE table (12 pt Bold, centered or left)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(caption_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def format_academic_table(table, col_widths, headers, data, alt_shading=True):
    """Construct a clean, publication-ready academic table with header styling and borders."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_shading(hdr_cells[i], HEX_HEADER_BG)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        set_cell_borders(hdr_cells[i], top="1B365D", bottom="1B365D", sz="8")
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    # Data rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = HEX_ALT_ROW if (r_idx % 2 == 1 and alt_shading) else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_shading(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            set_cell_borders(row_cells[c_idx], top="E0E0E0", bottom="E0E0E0", sz="4")
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.color.rgb = COLOR_TEXT_MAIN

    # Set column widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

def add_code_block(doc, code_str, caption=None):
    """Add a beautifully shaded and bordered code box in Consolas 9.5pt."""
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cp.paragraph_format.space_before = Pt(6)
        cp.paragraph_format.space_after = Pt(2)
        cp.paragraph_format.keep_with_next = True
        crun = cp.add_run(caption)
        crun.font.name = 'Times New Roman'
        crun.font.size = Pt(10.5)
        crun.font.bold = True
        crun.font.italic = True
        crun.font.color.rgb = COLOR_NAVY

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_shading(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    set_cell_borders(cell, top="CCCCCC", bottom="CCCCCC", left="1B365D", right="CCCCCC", sz="12")
    
    lines = code_str.strip().split('\n')
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.1
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.line_spacing = 1.1
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x2A, 0x2A, 0x2A)
        
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(4)

def add_figure(doc, image_path, fig_num, caption_title, explanation_text, width_inches=6.0):
    """Add full-width centered diagram with caption BELOW and architectural explanation."""
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        run_img.add_picture(image_path, width=Inches(width_inches))
    else:
        # Placeholder box if image path is invalid
        p_box = doc.add_paragraph()
        p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_ph = p_box.add_run(f"[Diagram Image: {os.path.basename(image_path)}]")
        run_ph.font.name = 'Times New Roman'
        run_ph.font.size = Pt(11)
        run_ph.font.italic = True
        run_ph.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)

    # Caption BELOW image
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(3)
    p_cap.paragraph_format.space_after = Pt(4)
    p_cap.paragraph_format.keep_with_next = True
    r_cap_lbl = p_cap.add_run(f"Figure {fig_num}: {caption_title}")
    r_cap_lbl.font.name = 'Times New Roman'
    r_cap_lbl.font.size = Pt(11)
    r_cap_lbl.font.bold = True
    r_cap_lbl.font.color.rgb = COLOR_NAVY
    
    # 2-3 sentence architectural explanation and design justification
    p_exp = doc.add_paragraph()
    p_exp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_exp.paragraph_format.line_spacing = 1.3
    p_exp.paragraph_format.space_before = Pt(2)
    p_exp.paragraph_format.space_after = Pt(8)
    r_exp_lbl = p_exp.add_run("Architectural Justification: ")
    r_exp_lbl.font.name = 'Times New Roman'
    r_exp_lbl.font.size = Pt(10.5)
    r_exp_lbl.font.bold = True
    r_exp_lbl.font.italic = True
    
    r_exp = p_exp.add_run(explanation_text)
    r_exp.font.name = 'Times New Roman'
    r_exp.font.size = Pt(10.5)
    r_exp.font.italic = True
    r_exp.font.color.rgb = COLOR_MUTED

def add_callout_box(doc, text_list, title=None):
    """Add a shaded highlight callout box with a navy accent border on the left."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_shading(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    set_cell_borders(cell, top=None, bottom=None, left="1B365D", right=None, sz="24")
    
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    
    if title:
        rt = p.add_run(title + "\n")
        rt.font.name = 'Times New Roman'
        rt.font.size = Pt(11)
        rt.font.bold = True
        rt.font.color.rgb = COLOR_NAVY
        
    for i, line in enumerate(text_list):
        if i > 0 or title:
            p_sub = cell.add_paragraph()
            p_sub.paragraph_format.line_spacing = 1.25
            p_sub.paragraph_format.space_before = Pt(0)
            p_sub.paragraph_format.space_after = Pt(2)
            r = p_sub.add_run(line)
        else:
            r = p.add_run(line)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_MAIN
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)
