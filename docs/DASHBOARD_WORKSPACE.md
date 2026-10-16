# Biomechanics Dashboard | Workspace v0.3 academic baseline

**Status:** exploratory user interface proposal, separate from the Gait Detection Engine.

## Product responsibility

The Dashboard enables researchers to inspect, interact with, and contextualize biomechanics signals. It consumes output from the engine but does not implement filtering or gait-event detection algorithms. KINORYX remains local-first, vendor-neutral, free to run, and without a hosted patient-data service.

## Academic visual direction

The dashboard now adopts an **article-first visual system** designed for researchers who want to export figures and place them into manuscripts, theses, or conference material with minimal redesign.

### Grounding principles

- Figure text and chart labels should follow the conservative font choices repeatedly accepted by major publishers: **Arial/Helvetica class sans-serif** for figure text and axis labels.
- Layout should prioritize readability: visible axis lines, tick marks, units, restrained decoration, and no dependence on red-versus-green color contrast.
- Supporting explanatory text should behave like a **figure legend**: a short title followed by a concise description of what is shown and what the symbols mean.
- Export should support downstream manuscript assembly, so the Plotly download action is configured for **SVG output** by default.
- The overall KINORYX identity for the dashboard should feel scholarly rather than consumer-tech: quiet surfaces, a neutral Chat Gray palette, high contrast, and typography that does not fight with the data.

## Visual system decisions implemented

### 1. Typography

- **Titles and section headers:** a single heavier display face based on locally available Arial Black / Arial bold fallbacks.
- **Charts, axes, legends and tables:** Arial / Helvetica style sans-serif.
- **Narrative and explanatory copy:** Georgia / Times New Roman style serif to evoke the cadence of article legends and manuscript body text.

### 2. Color strategy

- Primary identity background: **Chat Gray #F5F5F4** (approved Option 01), flat and neutral without gradients or bone texture; white #FFFFFF panels, discreet cool-gray borders and charcoal text.
- Left and right signals use a **high-contrast, publication-safe pair** rather than red-green.
- Signal differentiation also relies on **line style and marker shape**, not color alone.

### 3. Figure behavior

- Exported figure background is plain white (#FFFFFF), with no interface tint, gradients, shadows or brand panels. The surrounding interface uses Chat Gray #F5F5F4. This protects readability and compatibility with journal manuscript layout.
- Gridlines are suppressed by default.
- Axes remain explicit with tick marks and units.
- The chart export tool defaults to **SVG**, appropriate for vector-based article assembly.
- Candidate peak markers are clearly labeled as **exploratory** and **unvalidated**.

## User experience

1. Open the application locally. The default, clearly labeled example uses **synthetic** foot-gyro-like data.
2. Optionally load a canonical CSV. The application validates it using the existing engine ingestion contract.
3. Review recording duration, estimated sampling rate, available channels and number of **unvalidated peak candidates**.
4. Inspect raw and filtered signals with independent visibility controls, selecting both feet or one side.
5. Copy or export a figure with manuscript-appropriate typographic treatment.
6. Read the legend-style contextual note and inspect the candidate table.

## Screen architecture

- Persistent identity block and academic framing at the top.
- Input section with local CSV dropzone.
- Metrics cards describing recording context.
- Main figure card for signals and article-ready export.
- Side panel with figure-note narrative, candidate peak table, and methodological notes.

## Scientific boundaries

- The Dashboard **does not validate** gait events.
- Peak candidates are **not** initial contact, toe-off, stance, swing, or subphases.
- The article-ready visual styling must never be mistaken for validated clinical output.

## Next dashboard milestones

1. Add a formal figure export preset system (single-column and double-column dimensions).
2. Add optional panel lettering for multi-panel manuscript figures.
3. Add downloadable caption text and source-data export for the current view.
4. Add cycle-normalized views and paired summary panels once the engine is scientifically ready.
5. Add user-configurable but guarded styling presets for specific journal families.

## Source publication specifications reviewed

- Nature Research figure guide: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- Nature figures: https://www.nature.com/nature/for-authors/final-submission
- PLOS Biology figure requirements: https://journals.plos.org/plosbiology/s/figures
- Elsevier artwork overview: https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview

Guidance differs by journal. KINORYX does not claim universal publisher approval or clinical validation. Figure legends are displayed in the interface but are not embedded in exported SVG figures by default; include them in manuscript captions.
## Visual decision, 15 October 2026

The previously explored warm bone / parchment palette was **rejected**. The user approved **Option 01, Gris Chat (#F5F5F4)**, with white cards, gray dividers and neutral charcoal typography. Do not restore gold/bone textures without explicit approval. Academic figure-export standards remain unchanged, including pure-white plot backgrounds and SVG output.
