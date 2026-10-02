# KINETIQ website

Static HTML, CSS and JavaScript. Serve this directory over HTTP:

```sh
python -m http.server 8770 --directory site
```

The editable shopping budget uses `data/project.json`; each row records quantity, unit price, price basis, applicable build and source. Unknown costs are explicit allowances. Prices are not live inventory or quotes. User edits and owned-item selections stay in browser local storage; CSV export includes the selected build.

`docs/` contains readable HTML copies of the public Markdown references. Keep both copies aligned when changing engineering documentation. The website does not contain the private hosting account configuration.

The assembly animation and control software are pending. Do not replace their labels with download buttons until those artifacts exist.
