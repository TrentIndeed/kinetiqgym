# KINETIQ website

Static HTML, CSS and JavaScript. Serve this directory over HTTP:

```sh
python -m http.server 8770 --directory site
```

The editable shopping budget uses `data/project.json`; each row records quantity, unit price, price basis, applicable build and source. Unknown costs are explicit allowances. Prices are not live inventory or quotes. User edits and owned-item selections stay in browser local storage; CSV export includes the selected build.

`docs/` contains readable HTML copies of the public Markdown references. Keep both copies aligned when changing engineering documentation. The website does not contain the private hosting account configuration.

The illustrated CNC build and phone app are concept previews extracted from the Blender film. The updated CAD release, confirmed parts list, final build instructions and control software are pending. Do not present them as validated downloads.

`data/community.json` contains the public proposal email and donation checkout URL. Empty fields show honest “coming soon” states. Set `proposalEmail` to the owner's approved public address and `donationUrl` to an HTTPS checkout on the chosen provider; `donationProvider` names it in the checkout description. Payments are handled by that provider, not collected on this website. No donation totals or equipment budget are invented.

The website links to the public GitHub proposal form and contribution guide. The initial review owner is `@TrentIndeed`; `.github/CODEOWNERS` and the main-branch ruleset enforce reviews for community changes. Additional moderators must be appointed by the repository owner.

The four illustrated stages have a standalone guide in `docs/cnc-build-preview.md` and `.html`. When replacing film stills, keep their revision and concept status clear.
