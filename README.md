# Mahesh R — portfolio

One-page personal site. Hand-written HTML, CSS and a little JavaScript: no framework, no build step, no images.

**Signature look:** a dark glass panel floating on a live violet→aqua aurora, gradient display type, a CSS-only 3-D glass cube with an iridescent gem inside, floating crystals, and frosted surfaces whose specular highlight follows the pointer.

- `index.html` — content and structure
- `styles.css` — design tokens, layout, the aurora / glass / cube system, responsive and fallback rules
- `script.js` — mobile nav, active-section highlight, reveal-on-scroll, pointer-driven parallax and glass light (all progressive enhancement)
- `Mahesh_R_Resume.pdf` — linked from the page

All motion is `transform`/`opacity` only (compositor-friendly). Honours `prefers-reduced-motion` and `prefers-reduced-transparency`; degrades to solid surfaces where `backdrop-filter` is unsupported.

## Run locally

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8765
```

## Deploy

Static files at the repo root, so GitHub Pages ("Deploy from a branch", `main` / root) or a Vercel import works with no configuration.
