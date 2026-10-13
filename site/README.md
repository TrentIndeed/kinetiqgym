# KINETIQ website

Static HTML, CSS and JavaScript, served by a Cloudflare Worker with static assets (`../src/worker.js`; the Worker adds the
build-list and project-form endpoints). For a quick static preview:

```sh
python -m http.server 8770 --directory site
```

- `index.html`, `home.css`, `home.js`: the front page, `work.html` and `privacy.html`.
- `build.html`, `styles.css`, `app.js`: the build preview. The parts list reads `data/project.json`: the five builds (`motors`),
  the main list ranked by importance (`parts`), the accessory list and the have-it-made ranges (`outsourced`). Prices are planning
  figures, not live inventory or quotes. A visitor's own prices and chosen build stay in their browser's local storage.
- `data/parts.csv`: the same lists as a download.
- `data/community.json`: the donation checkout link. Payments are handled by the provider, never on this site.
- `docs/`: readable HTML copies of the public Markdown references. Keep both copies aligned.

The renders and the build preview are design illustrations, not photographs of validated hardware or a working app. The CAD,
build files and software are released after the prototype is tested; do not present anything here as a validated download.
