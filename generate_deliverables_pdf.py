"""Generate final project deliverables PDF for OddsWatch."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos


class DeliverablesPDF(FPDF):
    """Custom PDF with header/footer for OddsWatch deliverables."""

    def header(self):
        """Render page header."""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "OddsWatch  |  MGMT 59000 Cloud Data Engineering  |  Final Project", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        """Render page footer with page number."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, number: str, title: str):
        """Render a numbered section heading."""
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(25, 60, 120)
        self.cell(0, 12, f"{number}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(25, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_heading(self, text: str):
        """Render a sub-heading."""
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def body_text(self, text: str):
        """Render body text."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text: str, indent: int = 15):
        """Render a bullet point."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def table_row(self, cols: list[str], widths: list[int], bold: bool = False):
        """Render a table row with text wrapping support."""
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 9)
        self.set_text_color(40, 40, 40)
        line_h = 5
        x_start = self.l_margin
        y_start = self.get_y()

        # First pass: calculate required height for each cell
        max_h = line_h
        for i, col in enumerate(cols):
            # Use multi_cell in dry-run to count lines
            n_lines = 1
            w = widths[i] - 2
            if w > 0:
                words = col.split(" ")
                line = ""
                for word in words:
                    test = f"{line} {word}".strip()
                    if self.get_string_width(test) > w:
                        n_lines += 1
                        line = word
                    else:
                        line = test
            cell_h = n_lines * line_h
            if cell_h > max_h:
                max_h = cell_h

        # Check if row fits on current page, otherwise add page break
        if y_start + max_h > self.h - self.b_margin:
            self.add_page()
            y_start = self.get_y()

        # Disable auto page break while drawing cells to prevent mid-row splits
        saved_auto_pb = self.auto_page_break
        self.auto_page_break = False

        # Second pass: draw cells
        for i, col in enumerate(cols):
            x = x_start + sum(widths[:i])
            if bold:
                self.set_fill_color(230, 238, 250)
                self.rect(x, y_start, widths[i], max_h, "DF")
            else:
                self.rect(x, y_start, widths[i], max_h)
            self.set_xy(x + 1, y_start + 1)
            self.multi_cell(widths[i] - 2, line_h, col)

        # Restore auto page break
        self.auto_page_break = saved_auto_pb
        self.set_xy(x_start, y_start + max_h)


def build_pdf() -> None:
    """Build the complete deliverables PDF."""
    pdf = DeliverablesPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── TITLE PAGE ──────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(25, 60, 120)
    pdf.cell(0, 14, "OddsWatch", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Real-Time Sports Betting Odds & Line-Movement Platform", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_draw_color(25, 60, 120)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "MGMT 59000 - Cloud Data Engineering", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "Final Project Deliverables", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    pdf.cell(0, 8, "Danny Affleck", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "July 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 1  ARCHITECTURE DIAGRAM + PATTERN JUSTIFICATION ────────
    pdf.add_page()
    pdf.section_title("1", "Architecture Diagram & Pattern Justification")

    pdf.sub_heading("1.1  Pattern: Medallion Lakehouse Architecture")
    pdf.body_text(
        "OddsWatch follows a Medallion Lakehouse architecture (Bronze / Silver / Gold) "
        "running on AWS. This pattern was chosen because the project ingests semi-structured "
        "data from heterogeneous public sources (MLB ELO ratings and FIFA World Cup results), "
        "progressively refines it through normalization and enrichment stages, and ultimately "
        "serves it as a star schema optimized for analytical queries. The Lakehouse pattern "
        "combines the low-cost scalability of a data lake (S3 + Parquet) with the schema "
        "enforcement and catalog capabilities of a data warehouse (Glue Data Catalog), "
        "making it ideal for a batch-oriented analytics pipeline that may later add a "
        "streaming layer."
    )

    pdf.sub_heading("1.2  Architecture Diagram")
    pdf.body_text(
        "The following diagram shows the end-to-end data flow through the OddsWatch system. "
        "Each box represents a component in the pipeline; arrows indicate data movement."
    )

    pdf.ln(2)
    # ── Draw the architecture diagram programmatically ──
    box_h = 12
    y_start = pdf.get_y()

    def draw_box(x: float, y: float, w: float, h: float, label: str,
                 fill_r: int = 230, fill_g: int = 238, fill_b: int = 250,
                 font_size: int = 7, two_line: str = ""):
        pdf.set_fill_color(fill_r, fill_g, fill_b)
        pdf.set_draw_color(25, 60, 120)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, w, h, "DF")
        pdf.set_font("Helvetica", "B", font_size)
        pdf.set_text_color(25, 60, 120)
        if two_line:
            pdf.set_xy(x, y + 1)
            pdf.cell(w, h / 2 - 1, label, align="C")
            pdf.set_font("Helvetica", "", font_size - 1)
            pdf.set_text_color(80, 80, 80)
            pdf.set_xy(x, y + h / 2)
            pdf.cell(w, h / 2 - 1, two_line, align="C")
        else:
            pdf.set_xy(x, y + 1)
            pdf.cell(w, h - 2, label, align="C")

    def draw_arrow_right(x1: float, y: float, x2: float):
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.4)
        pdf.line(x1, y, x2, y)
        pdf.line(x2, y, x2 - 1.5, y - 1.5)
        pdf.line(x2, y, x2 - 1.5, y + 1.5)

    def draw_arrow_down(x: float, y1: float, y2: float):
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.4)
        pdf.line(x, y1, x, y2)
        pdf.line(x, y2, x - 1.5, y2 - 1.5)
        pdf.line(x, y2, x + 1.5, y2 - 1.5)

    def draw_label(x: float, y: float, text: str):
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(120, 120, 120)
        pdf.set_xy(x, y)
        pdf.cell(30, 4, text)

    # Column headers
    draw_label(12, y_start - 1, "DATA SOURCES")
    draw_label(62, y_start - 1, "PIPELINE")
    draw_label(118, y_start - 1, "STORAGE")
    draw_label(165, y_start - 1, "SERVING")

    # Horizontal separator under headers
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(10, y_start + 3, 195, y_start + 3)

    # Row 1: Bronze
    r1 = y_start + 6
    rh = 14
    draw_box(12, r1, 22, rh, "FiveThirtyEight", 255, 200, 130, 7, "MLB ELO")
    draw_box(36, r1, 22, rh, "GitHub", 255, 200, 130, 7, "FIFA World Cup")
    draw_arrow_right(58, r1 + rh / 2, 63)
    draw_box(63, r1, 46, rh, "Ingest (httpx)", 255, 220, 200, 7, "Download + Upload to S3")
    draw_arrow_right(109, r1 + rh / 2, 115)
    draw_box(115, r1, 40, rh, "S3: bronze/", 205, 185, 145, 7, "CSV (raw)")

    # Bronze badge
    pdf.set_fill_color(205, 170, 125)
    pdf.rect(163, r1 + 1, 25, rh - 2, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(163, r1 + 2)
    pdf.cell(25, rh - 4, "BRONZE", align="C")

    # Arrow down
    draw_arrow_down(135, r1 + rh, r1 + rh + 6)

    # Row 2: Silver
    r2 = r1 + rh + 8
    draw_box(63, r2, 46, rh, "bronze_to_silver", 200, 200, 240, 7,
             "Normalize + Synth. odds")
    draw_arrow_right(109, r2 + rh / 2, 115)
    draw_box(115, r2, 40, rh, "S3: silver/", 180, 190, 210, 7,
             "Parquet (SilverGame)")

    # Silver badge
    pdf.set_fill_color(150, 165, 195)
    pdf.rect(163, r2 + 1, 25, rh - 2, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(163, r2 + 2)
    pdf.cell(25, rh - 4, "SILVER", align="C")

    # Arrow down
    draw_arrow_down(135, r2 + rh, r2 + rh + 6)

    # Row 3: Gold
    r3 = r2 + rh + 8
    draw_box(63, r3, 46, rh, "silver_to_gold", 200, 200, 240, 7,
             "Star schema (4 dim + 1 fact)")
    draw_arrow_right(109, r3 + rh / 2, 115)
    draw_box(115, r3, 40, rh, "S3: gold/", 220, 190, 80, 7,
             "Parquet (5 tables)")

    # Gold badge
    pdf.set_fill_color(200, 170, 50)
    pdf.rect(163, r3 + 1, 25, rh - 2, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(163, r3 + 2)
    pdf.cell(25, rh - 4, "GOLD", align="C")

    # Arrow down to serving
    draw_arrow_down(135, r3 + rh, r3 + rh + 6)

    # Row 4: Serving
    r4 = r3 + rh + 8
    draw_box(115, r4, 28, rh, "Glue Catalog", 210, 190, 230, 7)
    draw_arrow_right(143, r4 + rh / 2, 150)
    draw_box(150, r4, 28, rh, "Athena SQL", 210, 190, 230, 7)

    # dbt box (left side, aligned with gold row)
    draw_box(12, r3, 28, rh, "dbt Project", 60, 160, 100, 7, "7 models / 45 tests")
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(100, 100, 100)
    pdf.set_xy(41, r3 + 3)
    pdf.cell(20, 8, "reads Glue")
    draw_arrow_right(42, r3 + rh / 2, 63)

    # Orchestrator
    draw_box(12, r4, 40, rh, "Pipeline Orchestrator", 240, 240, 220, 7, "(pipeline.py)")

    # Footer
    pdf.set_y(r4 + rh + 4)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Format: CSV (bronze) | Parquet with Snappy (silver, gold)   "
             "Catalog: AWS Glue Data Catalog   Pattern: Medallion Lakehouse",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.sub_heading("1.3  Component Summary")
    components = [
        ("Ingestion (httpx)", "Downloads raw data from FiveThirtyEight (MLB ELO) and GitHub "
         "(FIFA World Cup results) via HTTP, uploads as CSV to S3 bronze layer."),
        ("Bronze Layer (S3)", "Raw CSV files stored unmodified. Source of truth for replay."),
        ("Silver Transform", "Normalizes two heterogeneous schemas into a unified SilverGame "
         "model. Generates synthetic closing odds (spread, total, moneyline) seeded for "
         "reproducibility."),
        ("Gold Transform", "Builds a star schema: 4 dimension tables (DimTeam, DimGame, "
         "DimDate, DimMarket) and 1 fact table (FactGameOdds) with derived metrics "
         "(cover, over/under result)."),
        ("S3 Storage", "All silver and gold data stored as Parquet (Snappy compression) "
         "for columnar query performance."),
        ("Glue Data Catalog", "Registers all tables as EXTERNAL_TABLEs with column schemas, "
         "enabling SQL access via Athena."),
        ("Pipeline Orchestrator", "pipeline.py coordinates the full end-to-end run: "
         "ingest, transform (bronze-to-silver, silver-to-gold), upload, and catalog registration."),
    ]
    for name, desc in components:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 6, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(2)

    pdf.sub_heading("1.4  Why Lakehouse Over Alternatives")
    pdf.body_text(
        "Lambda Architecture was considered but rejected because OddsWatch currently runs "
        "as a batch-only pipeline. Maintaining separate batch and speed layers would add "
        "complexity with no benefit until real-time odds streaming is implemented. "
        "Data Mesh was also considered but is premature for a two-source, single-team project. "
        "The Lakehouse pattern gives us the flexibility to add a streaming layer (Kinesis / "
        "Kafka) alongside the batch layer later, while keeping a single source of truth in S3."
    )

    # ── 2  DATA MODEL + SCHEMA + SCD STRATEGY ─────────────────
    pdf.add_page()
    pdf.section_title("2", "Data Model, Schema & SCD Strategy")

    pdf.sub_heading("2.1  Three-Layer Schema Overview")
    pdf.body_text(
        "Data progresses through three layers. Each layer has a distinct purpose: Bronze "
        "preserves raw fidelity, Silver normalizes and enriches, and Gold optimizes for "
        "analytical queries via a star schema."
    )

    # Bronze table
    pdf.sub_heading("2.2  Bronze Layer (Raw Ingestion)")
    pdf.body_text(
        "Two source-specific schemas, stored as CSV. No transformations applied."
    )
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "BronzeMLBGame (8 columns)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    widths_b = [40, 25, 120]
    pdf.table_row(["Column", "Type", "Description"], widths_b, bold=True)
    mlb_cols = [
        ("date", "str", "Game date (YYYY-MM-DD)"),
        ("season", "int", "Season year"),
        ("neutral", "int", "1 if neutral site, 0 otherwise"),
        ("playoff", "str|None", "Playoff round indicator or None"),
        ("team1", "str", "Home team abbreviation"),
        ("team2", "str", "Away team abbreviation"),
        ("score1", "float", "Home team score"),
        ("score2", "float", "Away team score"),
    ]
    for col, dtype, desc in mlb_cols:
        pdf.table_row([col, dtype, desc], widths_b)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "BronzeWorldCupMatch (9 columns)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    wc_cols = [
        ("date", "str", "Match date (YYYY-MM-DD)"),
        ("home_team", "str", "Home team name"),
        ("away_team", "str", "Away team name"),
        ("home_score", "int", "Home team goals"),
        ("away_score", "int", "Away team goals"),
        ("tournament", "str", "Tournament name (filtered to FIFA World Cup)"),
        ("city", "str", "Host city"),
        ("country", "str", "Host country"),
        ("neutral", "str", "Neutral venue flag"),
    ]
    for col, dtype, desc in wc_cols:
        pdf.table_row([col, dtype, desc], widths_b)
    pdf.ln(4)

    # Silver table — needs ~100mm for heading + 15 rows; start new page if tight
    if pdf.get_y() > 170:
        pdf.add_page()
    pdf.sub_heading("2.3  Silver Layer (Unified & Enriched)")
    pdf.body_text(
        "Both sources are normalized into a single SilverGame schema (14 columns). "
        "Synthetic closing odds are generated deterministically from actual game outcomes "
        "using seeded random noise, rounded to half-point precision."
    )
    widths_s = [48, 22, 115]
    pdf.table_row(["Column", "Type", "Description"], widths_s, bold=True)
    silver_cols = [
        ("game_id", "str", "Unique ID: {sport}_{date}_{team1}_{team2}_{idx}"),
        ("sport", "str", "Sport identifier (mlb or world_cup)"),
        ("date", "date", "Game date as Python date object"),
        ("season", "int", "Season/tournament year"),
        ("home_team", "str", "Home team name (uppercase normalized)"),
        ("away_team", "str", "Away team name (uppercase normalized)"),
        ("home_score", "int", "Home team final score"),
        ("away_score", "int", "Away team final score"),
        ("stage", "str|None", "Game stage (playoff, regular_season, or None)"),
        ("venue", "str|None", "Venue or city (None for MLB)"),
        ("closing_spread", "float", "Synthetic point spread (half-point rounded)"),
        ("closing_total", "float", "Synthetic over/under line (min 0.5)"),
        ("closing_moneyline_home", "int", "American moneyline odds for home team"),
        ("closing_moneyline_away", "int", "American moneyline odds for away team"),
    ]
    for col, dtype, desc in silver_cols:
        pdf.table_row([col, dtype, desc], widths_s)
    pdf.ln(4)

    # Gold tables
    pdf.add_page()
    pdf.sub_heading("2.4  Gold Layer (Star Schema)")
    pdf.body_text(
        "The gold layer implements a star schema with four dimension tables surrounding "
        "one central fact table. This design optimizes for analytical queries such as "
        "'What percentage of home favorites covered the spread on weekends?'"
    )

    # ── Draw star schema diagram ──
    schema_y = pdf.get_y() + 2

    def schema_box(x: float, y: float, w: float, h: float, title: str,
                   cols: list[str], fill_r: int, fill_g: int, fill_b: int,
                   title_r: int = 25, title_g: int = 60, title_b: int = 120):
        pdf.set_fill_color(fill_r, fill_g, fill_b)
        pdf.set_draw_color(title_r, title_g, title_b)
        pdf.set_line_width(0.4)
        pdf.rect(x, y, w, h, "DF")
        # Title
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(title_r, title_g, title_b)
        pdf.set_xy(x + 1, y + 1)
        pdf.cell(w - 2, 5, title, align="C")
        # Separator line
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.2)
        pdf.line(x + 2, y + 7, x + w - 2, y + 7)
        # Columns
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(60, 60, 60)
        for i, col in enumerate(cols):
            pdf.set_xy(x + 2, y + 8 + i * 4)
            if "(PK)" in col or "(FK)" in col:
                pdf.set_font("Helvetica", "B", 6)
                pdf.set_text_color(70, 130, 200)
            else:
                pdf.set_font("Helvetica", "", 6)
                pdf.set_text_color(60, 60, 60)
            pdf.cell(w - 4, 4, col)

    # Central fact table
    fact_x, fact_y = 68, schema_y + 12
    fact_w, fact_h = 55, 52
    schema_box(fact_x, fact_y, fact_w, fact_h, "FactGameOdds",
               ["game_key (FK)", "date_key (FK)", "home_team_key (FK)",
                "away_team_key (FK)", "sport", "closing_spread | closing_total",
                "moneyline_home | moneyline_away",
                "home_score | away_score",
                "cover (bool) | over_under_result"],
               255, 243, 215, 200, 130, 40)

    # DimTeam - top left
    schema_box(10, schema_y, 48, 24, "DimTeam",
               ["team_key (PK)", "team_id | team_name", "sport"],
               220, 232, 250)
    # Arrow from DimTeam to fact
    draw_arrow_right(58, schema_y + 12, fact_x)

    # DimDate - top right
    schema_box(133, schema_y, 48, 28, "DimDate",
               ["date_key (PK)", "date | day_of_week", "month | year", "is_weekend"],
               220, 232, 250)
    # Arrow from DimDate to fact (leftward)
    pdf.set_draw_color(100, 100, 100)
    pdf.set_line_width(0.4)
    pdf.line(133, schema_y + 14, fact_x + fact_w, schema_y + 14)
    pdf.line(fact_x + fact_w, schema_y + 14, fact_x + fact_w + 1.5, schema_y + 14 - 1.5)
    pdf.line(fact_x + fact_w, schema_y + 14, fact_x + fact_w + 1.5, schema_y + 14 + 1.5)

    # DimGame - bottom left
    schema_box(10, schema_y + 40, 48, 28, "DimGame",
               ["game_key (PK)", "game_id | sport | season", "date | stage | venue",
                "home_team_key | away_team_key"],
               220, 232, 250)
    draw_arrow_right(58, schema_y + 54, fact_x)

    # DimMarket - bottom right
    schema_box(133, schema_y + 44, 48, 20, "DimMarket (static)",
               ["market_key (PK)", "spread | total | moneyline"],
               220, 232, 250)
    pdf.set_draw_color(100, 100, 100)
    pdf.set_line_width(0.4)
    pdf.line(133, schema_y + 54, fact_x + fact_w, schema_y + 54)
    pdf.line(fact_x + fact_w, schema_y + 54, fact_x + fact_w + 1.5, schema_y + 54 - 1.5)
    pdf.line(fact_x + fact_w, schema_y + 54, fact_x + fact_w + 1.5, schema_y + 54 + 1.5)

    pdf.set_y(schema_y + 72)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Star schema: 4 dimension tables surround 1 central fact table  |  "
             "13 fact columns  |  Derived metrics: cover, over_under_result",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Column detail tables on next page
    pdf.add_page()
    pdf.sub_heading("2.4.1  Gold Table Column Details")

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "DimTeam", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    widths_g = [45, 22, 118]
    pdf.table_row(["Column", "Type", "Description"], widths_g, bold=True)
    for col, dtype, desc in [
        ("team_key", "int", "Surrogate key (sequential)"),
        ("team_id", "str", "Derived ID (lowercase, underscores)"),
        ("team_name", "str", "Display name"),
        ("sport", "str", "Sport (mlb or world_cup)"),
        ("group_or_conference", "str|None", "Reserved for future enrichment"),
        ("country", "str|None", "Reserved for future enrichment"),
    ]:
        pdf.table_row([col, dtype, desc], widths_g)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "DimGame", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.table_row(["Column", "Type", "Description"], widths_g, bold=True)
    for col, dtype, desc in [
        ("game_key", "int", "Surrogate key"),
        ("game_id", "str", "Natural key from silver layer"),
        ("sport", "str", "Sport identifier"),
        ("season", "int", "Season year"),
        ("date", "date", "Game date"),
        ("stage", "str|None", "Playoff/regular season/None"),
        ("home_team_key", "int", "FK to DimTeam"),
        ("away_team_key", "int", "FK to DimTeam"),
        ("venue", "str|None", "Venue name or city"),
    ]:
        pdf.table_row([col, dtype, desc], widths_g)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "DimDate", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.table_row(["Column", "Type", "Description"], widths_g, bold=True)
    for col, dtype, desc in [
        ("date_key", "int", "Surrogate key"),
        ("date", "date", "Calendar date"),
        ("day_of_week", "str", "Day name (Monday, Tuesday, ...)"),
        ("month", "int", "Month number (1-12)"),
        ("year", "int", "Calendar year"),
        ("is_weekend", "bool", "True if Saturday or Sunday"),
    ]:
        pdf.table_row([col, dtype, desc], widths_g)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "DimMarket (static, 3 rows)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.table_row(["Column", "Type", "Description"], widths_g, bold=True)
    for col, dtype, desc in [
        ("market_key", "int", "Surrogate key (1, 2, 3)"),
        ("market_type", "str", "spread / total / moneyline"),
        ("description", "str", "Human-readable label"),
    ]:
        pdf.table_row([col, dtype, desc], widths_g)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "FactGameOdds (central fact table)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.table_row(["Column", "Type", "Description"], widths_g, bold=True)
    for col, dtype, desc in [
        ("game_key", "int", "FK to DimGame"),
        ("date_key", "int", "FK to DimDate"),
        ("home_team_key", "int", "FK to DimTeam"),
        ("away_team_key", "int", "FK to DimTeam"),
        ("sport", "str", "Sport degenerate dimension"),
        ("closing_spread", "float", "Closing point spread"),
        ("closing_total", "float", "Closing over/under line"),
        ("closing_moneyline_home", "int", "Home moneyline odds"),
        ("closing_moneyline_away", "int", "Away moneyline odds"),
        ("home_score", "int", "Home team final score"),
        ("away_score", "int", "Away team final score"),
        ("cover", "bool", "True if home team covered spread"),
        ("over_under_result", "str", "over / under / push"),
    ]:
        pdf.table_row([col, dtype, desc], widths_g)
    pdf.ln(6)

    # SCD strategy
    pdf.sub_heading("2.5  Slowly Changing Dimension (SCD) Strategy")
    pdf.body_text(
        "The following SCD strategies are applied to each dimension table:"
    )
    widths_scd = [40, 30, 115]
    pdf.table_row(["Dimension", "SCD Type", "Rationale"], widths_scd, bold=True)
    for dim, scd, rationale in [
        ("DimTeam", "Type 1", "Team names/abbrevs rarely change. Overwrite on refresh; "
         "no need to track historical names for odds analysis."),
        ("DimGame", "Type 0", "Game facts (date, score, teams) are immutable once "
         "recorded. No updates expected."),
        ("DimDate", "Type 0", "Calendar attributes are fixed and deterministic. "
         "Never changes."),
        ("DimMarket", "Type 0", "Static reference table with 3 rows. Market types "
         "do not change."),
        ("DimBook*", "Type 2", "Sportsbook fee structures and odds formats change "
         "over time. valid_from / valid_to / is_current fields track history."),
    ]:
        pdf.table_row([dim, scd, rationale], widths_scd)
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "* DimBook is defined in the data model for future streaming use; "
             "not populated in the current batch pipeline.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.body_text(
        "In the current batch pipeline, all gold tables are rebuilt from scratch on each "
        "run (full refresh). This is appropriate given the data volume (~200K rows total) "
        "and batch cadence. When the streaming layer is added, incremental upsert logic "
        "with SCD Type 2 tracking will be applied to DimBook via the valid_from/valid_to/"
        "is_current fields already defined in the Pydantic model."
    )

    # ── 3  AWS vs. GCP TOOL MEMO ──────────────────────────────
    pdf.add_page()
    pdf.section_title("3", "AWS vs. GCP Service Mapping Memo")

    pdf.body_text(
        "This memo maps each pipeline component to its AWS service (used in the current "
        "implementation) and the equivalent GCP service. The final column provides the "
        "rationale for choosing AWS."
    )

    widths_cloud = [32, 35, 35, 83]
    pdf.table_row(["Component", "AWS (Current)", "GCP Equivalent", "Rationale for AWS"],
                  widths_cloud, bold=True)
    cloud_rows = [
        ("Object Storage", "Amazon S3", "Cloud Storage", "S3 is the de facto standard for data "
         "lakes. Native integration with Glue, Athena, and the broader AWS analytics stack."),
        ("Data Catalog", "AWS Glue Catalog", "Data Catalog", "Glue Catalog provides Hive-"
         "compatible metastore that Athena queries directly. No separate metastore to manage."),
        ("ETL / Transform", "AWS Glue Jobs", "Dataflow / Dataproc", "Glue supports serverless "
         "Spark and Python shell jobs. Current pipeline uses Python scripts that can be "
         "deployed as Glue Python Shell jobs."),
        ("SQL Analytics", "Amazon Athena", "BigQuery", "Athena is serverless, pay-per-query, "
         "and reads directly from S3+Glue Catalog. No data loading step required."),
        ("Orchestration", "Step Functions", "Cloud Composer", "Step Functions integrates "
         "natively with Glue and Lambda for serverless orchestration of the batch pipeline."),
        ("Compute", "AWS Lambda", "Cloud Functions", "Lambda handles lightweight ingestion "
         "tasks (HTTP downloads, S3 uploads) within the 15-min/10GB limits."),
        ("Streaming*", "Kinesis Data Streams", "Pub/Sub", "Kinesis integrates with Glue "
         "Streaming and Lambda for future real-time odds ingestion."),
        ("IAM & Security", "AWS IAM", "Cloud IAM", "IAM roles and policies control access "
         "to S3 buckets, Glue databases, and Athena workgroups."),
    ]
    for component, aws, gcp, rationale in cloud_rows:
        pdf.table_row([component, aws, gcp, rationale], widths_cloud)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "* Streaming component is planned for future implementation.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.sub_heading("3.1  Why AWS Over GCP")
    pdf.body_text(
        "AWS was selected for three reasons: (1) the S3 + Glue + Athena stack provides a "
        "tightly integrated, serverless analytics platform that requires minimal infrastructure "
        "management; (2) the course curriculum is built around AWS services; and (3) the "
        "boto3 SDK provides mature Python support for all services used. GCP's BigQuery "
        "offers superior query performance on large datasets but requires data loading, "
        "which adds complexity for a pipeline that already stores data in a lakehouse format."
    )

    # ── 4  CLOUD COST ESTIMATE ────────────────────────────────
    pdf.add_page()
    pdf.section_title("4", "Cloud Cost Estimate")

    pdf.body_text(
        "Back-of-envelope cost estimate based on current data volumes and a daily batch "
        "pipeline cadence. All prices are us-east-1 on-demand rates as of mid-2026."
    )

    pdf.sub_heading("4.1  Data Volume Assumptions")
    pdf.bullet("MLB ELO dataset: ~230,000 rows, ~12 MB CSV, ~3 MB Parquet")
    pdf.bullet("World Cup dataset: ~1,000 rows, ~80 KB CSV, ~25 KB Parquet")
    pdf.bullet("Gold layer (all 5 tables): ~5 MB Parquet total")
    pdf.bullet("Total S3 footprint: ~20 MB (all layers combined)")
    pdf.bullet("Pipeline runs: 1x daily (batch)")
    pdf.ln(2)

    pdf.sub_heading("4.2  Monthly Cost Breakdown")
    widths_cost = [55, 50, 40, 40]
    pdf.table_row(["Service", "Usage", "Unit Price", "Monthly Cost"],
                  widths_cost, bold=True)
    cost_rows = [
        ("S3 Storage", "~20 MB", "$0.023/GB", "$0.01"),
        ("S3 PUT Requests", "~300 PUTs/month", "$0.005/1K", "$0.01"),
        ("S3 GET Requests", "~900 GETs/month", "$0.0004/1K", "$0.01"),
        ("Glue Catalog Storage", "12 tables", "Free (< 1M)", "$0.00"),
        ("Glue API Requests", "~360 calls/month", "$1.00/1M", "$0.01"),
        ("Athena Queries", "~100 queries, 5 MB ea", "$5.00/TB scanned", "$0.01"),
        ("Lambda (Ingestion)", "30 invocations, 30s ea", "$0.20/1M + compute", "$0.01"),
        ("Data Transfer", "~50 MB out/month", "First 100 GB free", "$0.00"),
    ]
    for service, usage, price, cost in cost_rows:
        pdf.table_row([service, usage, price, cost], widths_cost)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(25, 60, 120)
    pdf.cell(0, 8, "Estimated Total: < $1.00 / month", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.body_text(
        "At current volumes, costs are negligible and fall within AWS Free Tier limits "
        "for the first 12 months. The dominant cost driver at scale would be Athena query "
        "scanning and S3 storage, both of which are addressed in the scale analysis below."
    )

    pdf.sub_heading("4.3  Cost at 10x Scale")
    pdf.body_text(
        "At 10x data volume (~200 MB total storage, ~2.3M rows), monthly costs remain "
        "under $5.00. Athena becomes the primary cost driver at $5/TB scanned. "
        "Partitioning gold tables by sport and season would reduce scan volume by 50-70%, "
        "keeping Athena costs proportional to the data actually queried rather than total "
        "stored. At 100x (~2 GB, 23M rows), estimated cost rises to ~$15-25/month, still "
        "very manageable for an analytics workload."
    )

    # ── 5  SCALE ANALYSIS ─────────────────────────────────────
    pdf.add_page()
    pdf.section_title("5", "Scale Analysis: What Breaks at 10x")

    pdf.body_text(
        "This section analyzes what components of the OddsWatch pipeline would degrade or "
        "fail if data volume increased by 10x (from ~230K rows to ~2.3M rows) and how each "
        "bottleneck can be resolved."
    )

    pdf.sub_heading("5.1  Ingestion Layer")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Current: Single-threaded HTTP download via httpx", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "Risk: At 10x, the raw CSV download from FiveThirtyEight grows from ~12 MB to "
        "~120 MB. A single HTTP GET remains feasible but takes ~30-60 seconds on a "
        "typical connection. At 100x, API rate limits and download times become blocking."
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Mitigation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet("Paginate or chunk large downloads using Range headers or API pagination.")
    pdf.bullet("Parallelize ingestion across multiple data sources using async httpx.")
    pdf.bullet("Add incremental ingestion: track last-ingested date, only fetch new records.")
    pdf.ln(2)

    pdf.sub_heading("5.2  Transform Layer")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Current: In-memory pandas DataFrames, single-process", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "Risk: The bronze-to-silver transform iterates row-by-row to generate synthetic "
        "odds (Python for-loop with random seeding per row). At 2.3M rows, this loop "
        "becomes the primary bottleneck (~5-10 minutes). The silver-to-gold transform "
        "uses vectorized pandas operations and scales linearly; it remains feasible at 10x."
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Mitigation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet("Vectorize synthetic odds generation using numpy.random with array-level seeds "
               "instead of per-row seeding, reducing O(n) Python loop to O(1) numpy call.")
    pdf.bullet("At 100x, migrate to PySpark on Glue for distributed processing.")
    pdf.bullet("Partition output Parquet by sport and season for parallel write.")
    pdf.ln(2)

    pdf.sub_heading("5.3  Storage Layer")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Current: Single Parquet file per table, no partitioning", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "Risk: Single-file writes work at 20 MB but become inefficient at 200 MB+. "
        "Athena must scan entire files even for queries targeting a single sport or season. "
        "No partition pruning is possible."
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Mitigation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet("Introduce Hive-style partitioning: gold/fact_game_odds/sport=mlb/season=2024/")
    pdf.bullet("Use PyArrow write_to_dataset() with partition_cols for automatic partitioning.")
    pdf.bullet("Register partition keys in Glue Catalog for Athena partition pruning.")
    pdf.ln(2)

    pdf.sub_heading("5.4  Catalog & Query Layer")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Current: Glue Catalog with unpartitioned tables", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "Risk: Athena scans all data for every query. At 10x, a simple aggregation query "
        "scans ~200 MB ($0.001 per query). Costs are still low but query latency increases "
        "to 5-10 seconds. At 100x, full scans become both slow and expensive."
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Mitigation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet("Add partition columns to Glue table definitions for partition pruning.")
    pdf.bullet("Use Parquet columnar projection (Athena only reads referenced columns).")
    pdf.bullet("Consider converting to Iceberg table format for ACID transactions and "
               "time-travel queries at warehouse scale.")
    pdf.ln(2)

    pdf.sub_heading("5.5  Orchestration")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, "Current: Single-function pipeline.py running locally", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "Risk: The monolithic pipeline.py runs all stages sequentially in a single process. "
        "At 10x, a failure in the gold transform requires re-running the entire pipeline "
        "from ingestion. No checkpointing or retry logic exists."
    )
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Mitigation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet("Deploy as AWS Step Functions state machine with per-stage error handling "
               "and retry policies.")
    pdf.bullet("Add idempotency: each stage checks for existing output before re-processing.")
    pdf.bullet("Enable parallel execution of independent stages (e.g., MLB and World Cup "
               "ingestion can run concurrently).")
    pdf.ln(4)

    pdf.sub_heading("5.6  Summary Table")
    widths_scale = [35, 55, 55, 40]
    pdf.table_row(["Component", "Breaks At", "Symptom", "Fix"],
                  widths_scale, bold=True)
    scale_rows = [
        ("Ingestion", "100x (120+ MB)", "Timeout / OOM", "Chunked + async"),
        ("Transform", "10x (2.3M rows)", "Slow row-by-row loop", "Vectorize / Spark"),
        ("Storage", "10x (200+ MB)", "No partition pruning", "Hive partitioning"),
        ("Catalog/Query", "10x (200+ MB scans)", "Slow queries, cost", "Partition + Iceberg"),
        ("Orchestration", "10x", "No retry, full re-run", "Step Functions"),
    ]
    for comp, breaks, symptom, fix in scale_rows:
        pdf.table_row([comp, breaks, symptom, fix], widths_scale)

    # ── 6  DOMINANT DIMENSION (Slide 42 Question) ─────────────
    pdf.add_page()
    pdf.section_title("6", "Trade-Off Analysis: Dominant Dimension")

    pdf.body_text(
        "Per the Session 7 framework, every system has a dominant design dimension. "
        "The six dimensions from the course are: Caching, CAP Theorem, Fan-out, "
        "Geo-distribution, Streaming, and combined (Everything). For OddsWatch, the "
        "analysis is as follows:"
    )

    pdf.sub_heading("6.1  Dominant Dimension: Streaming")
    pdf.body_text(
        "The core value proposition of OddsWatch is tracking odds movement over time. "
        "While the current implementation is batch-only, the system is designed to evolve "
        "toward real-time streaming of odds ticks from multiple sportsbooks. The data model "
        "already includes FactOddsTick and DimBook tables for this purpose. As the platform "
        "matures, the dominant challenge is ingesting, windowing, and serving high-frequency "
        "odds updates with low latency. This makes Streaming the dominant dimension."
    )

    pdf.sub_heading("6.2  Dimensions Sacrificed")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, "1. Geo-distribution (Sacrificed)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "OddsWatch runs entirely in us-east-1. Sports betting odds are not latency-sensitive "
        "for analytics (millisecond edge matters for trading, not for historical analysis). "
        "Multi-region replication would add cost and complexity with no analytical benefit."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, "2. Fan-out (Sacrificed)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "The system has a single producer (the pipeline) and a small number of consumers "
        "(analysts running Athena queries). There is no fan-out challenge: no push "
        "notifications, no timeline assembly, no follower graph. Queries are pull-based "
        "and ad-hoc. This eliminates the need for caching layers, CDNs, or pre-computed "
        "materialized views."
    )

    pdf.sub_heading("6.3  Dimensions Preserved (But Not Dominant)")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, "CAP: Eventual Consistency Accepted", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "The batch pipeline prioritizes availability (the pipeline always completes) over "
        "strict consistency (gold tables may be briefly stale during a run). This is "
        "acceptable because analysts query completed snapshots, not in-flight data."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, "Caching: Not Required Today, Natural Fit Later", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body_text(
        "At current query volumes, Athena scans are fast and cheap. If a front-end "
        "dashboard is added, a Redis or ElastiCache layer for hot queries would be the "
        "first optimization, but it is not a current design constraint."
    )

    # ── Output ────────────────────────────────────────────────
    output_path = "docs/OddsWatch_Final_Project_Deliverables.pdf"
    pdf.output(output_path)
    print(f"PDF written to {output_path}")


if __name__ == "__main__":
    build_pdf()
