# Portfolio

A Material 3 Expressive portfolio. Everything on the page comes from `Config/`, `Work/` and `Reviews/`.
Edit them with **PortfolioEditor.exe** (Save & Build, then Start server / Open site), or by hand.

```
index.html          the page shell (the editor writes the title-card tags into it)
Config/             site.json (name, theme), seo.json (link preview), tabs.json, contact.json, pages/*.json
Work/ Reviews/      proof of work media, one folder per review
Site/app.js         the page's behaviour
Site/style.css      the page's look
Site/vendor/        md3e-web components, design tokens, Google Sans, Material Symbols (generated, committed)
src/                the editor's source (portfolio editor.py)
tools/              build scripts for Site/vendor
```

## Theme

`Config/site.json` -> `theme`:

| key | values |
| --- | --- |
| `seedColor` | any `#rrggbb`. Every colour is generated from it |
| `paletteVariant` | `tonal-spot`, `expressive`, `vibrant`, `neutral`, `fidelity`, `content`, `monochrome`, `rainbow`, `fruit-salad` |
| `colorMode` | `auto`, `light`, `dark` |
| `motion` | `expressive` (springy) or `standard` |
| `font` | `Google Sans` is built in; any other Google Fonts name is loaded from Google |
| `themePicker` / `shapes` | show the "Make it yours" button / the floating background shapes |

Visitors can change colour, mode, palette and motion themselves with the palette button. Their choice is kept in their browser only.

## Pages

`Config/pages/<id>.json` has `"layout": "cards"` or `"accordion"`, and sections with `heading`, `icon`, `text`, `items`, `badge`.
`icon` is a Material Symbols name. Only the icons listed in `tools/icons.txt` are installed.
Text supports `**bold**` and `[words](https://link)`.

## Rebuilding `Site/vendor`

Only needed to add a component, add icons, or upgrade the package:

```
npm install
npm run build     # bundles the components listed in tools/entry.js
npm run fonts     # downloads Google Sans + the icons in tools/icons.txt (keep that list under ~350 names)
```

The components are `@materialwebunofficial/md3e-web` (unofficial, Apache-2.0; its licence is in `Site/vendor`).

## Rebuilding the editor exe

```
python -m PyInstaller --noconfirm --clean --onefile --noconsole --name PortfolioEditor "src/portfolio editor.py"
```

Copy `dist/PortfolioEditor.exe` next to `index.html`.
