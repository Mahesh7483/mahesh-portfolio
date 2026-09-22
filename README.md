# Mahesh R — portfolio

One-page personal site: hand-written HTML, CSS and a little JavaScript. No framework, no build step.

- `index.html` — content and structure
- `styles.css` — design tokens (light/dark), layout, components
- `script.js` — theme toggle, mobile nav, active-section highlight, reveal-on-scroll (all progressive enhancement)
- `Mahesh_R_Resume.pdf` — linked from the page

## Run locally

Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8765
```

## Deploy

Static files at the repo root, so GitHub Pages ("Deploy from a branch", `main` / root) or a Vercel import works with no configuration.
