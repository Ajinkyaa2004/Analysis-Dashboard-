# UI Enhancement Plan: Professional & Minimalistic Analytics Dashboard

**Goal:** Transform the existing Streamlit dashboard into a professional, advanced, and minimalistic analytics tool.
**Design Philosophy:** Clean whitespace, subtle shadows, professional typography, consistent color palette, and clear visual hierarchy.

---

## Phase 1: Foundation & Global Styling (The "Look")
*Focus: Setting up the design system, colors, fonts, and layout structure.*

### 1.1 Custom CSS Architecture (`assets/style.css`)
- [ ] Create `assets/` directory and `style.css` file.
- [ ] **Color Palette Variables:** Define CSS variables for the new professional palette.
    -   Background: `#F0F2F6` (Light Blue-Grey)
    -   Surface (Cards): `#FFFFFF` (White)
    -   Primary: `#2563EB` (Professional Blue)
    -   Text Primary: `#1E293B` (Slate 800)
    -   Text Secondary: `#64748B` (Slate 500)
    -   Success: `#10B981` (Emerald)
    -   Danger: `#EF4444` (Red)
- [ ] **Typography:** Import a clean sans-serif font (e.g., 'Inter' or system defaults) and standardize headers (`h1`, `h2`, `h3`). Remove default Streamlit padding discrepancies.
- [ ] **App Container:** Customize the main `.stApp` background and max-width settings for a "dashboard" feel rather than a "doc" feel.

### 1.2 Sidebar Overhaul
- [ ] Style the sidebar to distinguish it clearly from the main content (darker or lighter contrast).
- [ ] Refine file uploader components to be compact and clean.
- [ ] Group settings into collapsible `st.expander` sections to reduce clutter.

---

## Phase 2: Key Performance Indicators (KPIs) & Cards
*Focus: Presenting high-level numbers clearly and professionally.*

### 2.1 Custom Metric Cards
- [ ] Replace standard `st.metric` with custom HTML/CSS component cards.
- [ ] **Design:**
    -   White card background with `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1)`.
    -   Rounded corners (`border-radius: 12px`).
    -   Icon integration (using a library like FontAwesome or simple SVG).
- [ ] **Content:** Total Sales, Avg Weekly Sales, Active vs. Dropping Customers.
- [ ] **Layout:** Use a 4-column grid layout for the top KPI section.

---

## Phase 3: Advanced Data Visualization
*Focus: Making charts beautiful, consistent, and easy to interpret.*

### 3.1 Unify Plotly Theme
- [ ] Create a reusable `update_chart_layout(fig)` function.
- [ ] **Styling:**
    -   Transparent background.
    -   Minimal grid lines (light grey, dotted).
    -   Clean font application.
    -   Remove clutter (legends inside chart area if space permits, or standardized position).

### 3.2 Specific Chart upgrades
- [ ] **Bar Charts (Financial Year):** Use a professional monochromatic or dual-tone color scheme instead of rainbow colors. Add data labels on hover or top of bars.
- [ ] **Line Charts (Trends):** Smoother lines, subtle area fill (gradients), and remove noise.
- [ ] **Donut Chart:** Thinner ring, center text displaying the total, cleaner segment labels.

---

## Phase 4: Data Grids & Tabular Views
*Focus: Improving readability of raw data and detailed reports.*

### 4.1 Professional Table Styling
- [ ] Move away from default `st.dataframe` styling where possible or heavily customize it using Pandas Styler.
- [ ] **Features:**
    -   Clean headers with distinct background.
    -   Zebra striping (subtle).
    -   Number formatting (monospaced fonts for figures).
    -   Sticky headers for long lists.
- [ ] **Conditional Formatting:** Replace harsh "Red/Green" backgrounds with subtle text colors or badges/pills.

### 4.2 Interactive Filters
- [ ] Move filters closer to the data they affect (e.g., "Select Branch" right above the specific chart card).
- [ ] Use "pills" or "tags" for selection instead of standard multi-select boxes where appropriate.

---

## Phase 5: User Experience & Polish
*Focus: Transitions, Empty States, and Instructions.*

### 5.1 Onboarding & Empty States
- [ ] Design a clean "Welcome/Upload" state when no data is present (SVG illustration + clear steps).
- [ ] Remove the "Instruction" wall of text and replace it with a guided experience.

### 5.2 Responsive Adjustments
- [ ] Ensure cards stack correctly on smaller screens.
- [ ] Adjust padding for mobile/tablet views.

---

## Execution Strategy
We will implement this starting from **Phase 1**.
1. Set up the CSS and basic layout.
2. Verify the look.
3. Move to Components (Phase 2).
4. Update Charts (Phase 3).
5. Finalize Tables (Phase 4).
