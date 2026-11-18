// bundles the md3e-web components into Site/vendor and copies the design tokens.
// run with: npm run build        (only needed when tools/entry.js changes or the package is upgraded)
import { build } from 'esbuild';
import { readFile, writeFile, copyFile, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pkgDir = join(root, 'node_modules', '@materialwebunofficial', 'md3e-web');
const vendor = join(root, 'Site', 'vendor');
const version = JSON.parse(await readFile(join(pkgDir, 'package.json'), 'utf8')).version;

await mkdir(vendor, { recursive: true });

const result = await build({
	entryPoints: [join(root, 'tools', 'entry.js')],
	outfile: join(vendor, 'md3e.js'),
	bundle: true,
	minify: true,
	format: 'esm',
	target: 'es2022',
	legalComments: 'none',
	banner: { js: `/*! @materialwebunofficial/md3e-web ${version} (Apache-2.0, see md3e-web-LICENSE.txt). Bundled by tools/build.mjs */` },
	metafile: true,
	logLevel: 'warning',
});

const size = Object.values(result.metafile.outputs)[0].bytes;
console.log(`Site/vendor/md3e.js  ${(size / 1024).toFixed(0)} KB (md3e-web ${version})`);

// tokens.css without the Roboto font-face rules: the portfolio uses Google Sans (Site/vendor/fonts.css).
let tokens = await readFile(join(pkgDir, 'dist', 'tokens.min.css'), 'utf8');
const before = tokens.length;
tokens = tokens.replace(/@font-face\s*\{[^}]*font-family:\s*['"]?Roboto['"]?[^}]*\}/g, '');
await writeFile(join(vendor, 'tokens.css'), tokens);
console.log(`Site/vendor/tokens.css  ${(tokens.length / 1024).toFixed(0)} KB (removed ${before - tokens.length} bytes of Roboto font-face rules)`);

await copyFile(join(pkgDir, 'LICENSE'), join(vendor, 'md3e-web-LICENSE.txt'));
await copyFile(join(pkgDir, 'NOTICE'), join(vendor, 'md3e-web-NOTICE.txt'));
console.log('copied LICENSE + NOTICE');
