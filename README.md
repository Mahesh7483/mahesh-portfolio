# Mahesh R — portfolio

One-page personal site. Hand-written HTML, CSS and a little JavaScript: no framework, no build step, no images.

**Signature look:** a dark glass panel floating on a live violet→aqua aurora, gradient display type, a CSS-only 3-D glass cube with an iridescent gem inside, floating crystals, and frosted surfaces whose specular highlight follows the pointer.

- `index.html` — content and structure
- `styles.css` — design tokens, the measured first-screen layout, glass cube, lower sections, responsive and fallback rules
- `crystals.css` — the three crystals' faces, **generated** by `tools/polyhedra.py`; do not edit by hand
- `tools/polyhedra.py` — builds convex polyhedra (icosahedra) as flat HTML faces with baked lighting: `python tools/polyhedra.py > crystals.css`
- `script.js` — mobile nav, active-section highlight, reveal-on-scroll, motion switch, pointer-driven tilt and glass light (all progressive enhancement)
- `Mahesh_R_Resume.pdf` — linked from the page

The first screen is laid out in the panel's own proportions with container-query units (`cqw`), so the composition holds at any desktop width; below 1000px it becomes a stacked layout. The glass cube's pose was solved from a reference design's corners (rotateZ 11.9°, rotateX −22.7°, rotateY 45.9°).

All motion is `transform`/`opacity` only. A motion switch in the footer turns animation off and remembers the choice; without JavaScript an OS reduced-motion preference does the same.

## Run locally

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8765
```

## Deploy

Static files at the repo root, so GitHub Pages ("Deploy from a branch", `main` / root) or a Vercel import works with no configuration.
