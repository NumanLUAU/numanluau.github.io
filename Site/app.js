// Material 3 Expressive portfolio.
// everything shown comes from the Config folder (plus Work / Reviews). edit it with the editor, or by hand.

const CONFIG_DIR = 'Config';
const THEME_STORE = 'portfolio-theme-v1';

const VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg', '.mov', '.m4v'];
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp', '.gif'];

// the 35 md3e shapes that look good as avatars / icon blobs.
const FACE_SHAPES = ['9-sided-cookie', 'sunny', 'soft-burst', 'flower', '6-sided-cookie', 'puffy', '4-sided-cookie', 'very-sunny', '12-sided-cookie', 'clam-shell', 'pentagon', '4-leaf-clover'];
const BLOB_SHAPES = ['sunny', 'flower', '9-sided-cookie', 'soft-burst', 'puffy', '4-leaf-clover', 'very-sunny'];
const CONFETTI_SHAPES = ['sunny', 'flower', 'soft-burst', 'heart', '4-leaf-clover', 'puffy', 'pill', '6-sided-cookie'];

const TONES = ['primary', 'surface', 'tertiary', 'secondary'];

const TYPE_ICONS = { page: 'person', work: 'play_circle', reviews: 'reviews', contact: 'alternate_email' };

// (keyword in a heading) -> icon, so pages look right even without an "icon" in the json.
const HEADING_ICONS = [
	[/about|profile|bio/i, 'person'],
	[/strength|skill/i, 'bolt'],
	[/weak|limit/i, 'warning_amber'],
	[/practice|code|standard/i, 'code'],
	[/hour|avail|time|schedule/i, 'schedule'],
	[/requirement/i, 'checklist'],
	[/document|design/i, 'description'],
	[/structure|workflow|process/i, 'dashboard'],
	[/scope|change/i, 'tune'],
	[/communicat|contact|message/i, 'forum'],
	[/commission/i, 'work'],
	[/part-?time/i, 'schedule'],
	[/task/i, 'task_alt'],
	[/month/i, 'calendar_month'],
	[/deadline/i, 'timer'],
	[/paypal|payment|price|pricing|cost|robux/i, 'payments'],
	[/confirm/i, 'check_circle'],
];

const FALLBACK_ICONS = ['auto_awesome', 'star', 'favorite', 'bolt', 'palette', 'extension'];

// brand icons. anything else is an image path, or a material symbol name.
const ICONS = {
	discord: 'M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z',
	x: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z',
	github: 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12',
	youtube: 'M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z',
	email: 'M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z',
	link: 'M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z',
};

ICONS.twitter = ICONS.x;

const SEED_PRESETS = [
	['#6750A4', 'Violet'], ['#00639B', 'Ocean'], ['#006A60', 'Teal'], ['#386A20', 'Forest'],
	['#7D5700', 'Amber'], ['#C2410C', 'Ember'], ['#BA1A1A', 'Cherry'], ['#B4236A', 'Berry'],
];

const PALETTE_STYLES = [
	['tonal-spot', 'Tonal spot'], ['expressive', 'Expressive'], ['vibrant', 'Vibrant'],
	['neutral', 'Neutral'], ['rainbow', 'Rainbow'], ['fruit-salad', 'Fruit salad'], ['monochrome', 'Mono'],
];

let md3 = null;
let site = {};
let seo = {};
let tabList = [];
let theme = {};
let activeId = null;
const loadedTabs = new Set();

const $ = (selector, root = document) => root.querySelector(selector);
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

// >> helpers

// fetches a json file, returns the fallback if it is missing.
async function fetchJson(path, fallback) {
	try {
		const response = await fetch(path, { cache: 'no-cache' });

		if (!response.ok) {
			return fallback;
		}

		return await response.json();
	} catch (error) {
		return fallback;
	}
}

// safely escapes text before inserting it into the page.
function escapeHtml(value) {
	return String(value ?? '')
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#039;');
}

// escapes text, then turns **bold** and [label](url) into html.
function richText(value) {
	let html = escapeHtml(value);

	html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

	html = html.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (match, label, url) => {
		if (!/^(https?:\/\/|mailto:|\.\/|\/|#)/i.test(url)) {
			return match;
		}

		return `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
	});

	return html;
}

function plainText(value) {
	return String(value ?? '').replace(/\*\*(.+?)\*\*/g, '$1').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

// makes a path relative to the folder of another file.
function resolveFrom(base, path) {
	return path ? new URL(path, new URL(base, window.location.href)).href : '';
}

function fileTitle(name) {
	return String(name).replace(/\.[^/.]+$/, '');
}

function make(tag, props = {}, children = []) {
	const node = document.createElement(tag);

	for (const [key, value] of Object.entries(props)) {
		if (value === undefined || value === null || value === false) {
			continue;
		}

		if (key === 'class') {
			node.className = value;
		} else if (key === 'text') {
			node.textContent = value;
		} else if (key === 'html') {
			node.innerHTML = value;
		} else {
			node.setAttribute(key, value === true ? '' : value);
		}
	}

	for (const child of [].concat(children)) {
		if (child) {
			node.append(child);
		}
	}

	return node;
}

function cssVar(name) {
	return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function spring() {
	const easing = cssVar('--md-sys-motion-spatial-medium-easing');

	return {
		easing: easing && CSS.supports('animation-timing-function', easing) ? easing : 'cubic-bezier(0.2, 0, 0, 1)',
		duration: parseFloat(cssVar('--md-sys-motion-spatial-medium-duration')) || 500,
	};
}

// makes the elements pop in one after another with the theme's spring.
function springIn(nodes, { from = 28, step = 55, max = 12 } = {}) {
	if (reducedMotion.matches) {
		return;
	}

	const { easing, duration } = spring();

	[...nodes].forEach((node, index) => {
		node.animate(
			[
				{ opacity: 0, transform: `translateY(${from}px) scale(0.92)` },
				{ opacity: 1, transform: 'none' },
			],
			{ duration: duration + 250, delay: Math.min(index, max) * step, easing, fill: 'backwards' }
		);
	});
}

function loader(size = 'large', label = 'Loading') {
	return make('md-loading-indicator', { variant: 'contained', size, 'aria-label': label });
}

function loadingBlock(text) {
	return make('div', { class: 'loading' }, [loader(72), make('div', { text })]);
}

function shapeIcon(icon, shape = '6-sided-cookie') {
	return make('div', { class: 'shape-icon', 'aria-hidden': 'true' }, [
		make('md-shape', { name: shape, color: 'var(--tone-accent, var(--md-sys-color-primary))' }),
		make('span', { class: 'material-symbols-rounded icon', text: icon }),
	]);
}

// >> toast

function toast(message) {
	const bar = $('#toast');

	if (bar?.show) {
		bar.show(message, undefined, 2600);
	}
}

// >> theme

function loadPrefs() {
	try {
		return JSON.parse(localStorage.getItem(THEME_STORE)) || {};
	} catch (error) {
		return {};
	}
}

function savePrefs(prefs) {
	try {
		localStorage.setItem(THEME_STORE, JSON.stringify(prefs));
	} catch (error) {
		//// storage can be blocked (private windows). the theme just won't be remembered.
	}
}

// the site's own settings, with sensible defaults for anything missing in site.json.
function configTheme() {
	const configured = site.theme || {};

	return {
		seedColor: configured.seedColor || '#BA1A1A',
		paletteVariant: configured.paletteVariant || 'tonal-spot',
		colorMode: configured.colorMode || 'auto',
		motion: configured.motion || 'expressive',
		contrast: configured.contrast || 'standard',
		themePicker: configured.themePicker !== false,
		shapes: configured.shapes !== false,
	};
}

let prefs = loadPrefs();

function applyTheme() {
	theme = { ...configTheme(), ...prefs };

	const dark = theme.colorMode === 'dark' || (theme.colorMode === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);

	md3.Theme.applyGlobal({
		scheme: theme.motion,
		motionScheme: theme.motion,
		colorMode: dark ? 'dark' : 'light',
		paletteVariant: theme.paletteVariant,
		primarySeed: theme.seedColor,
		contrast: theme.contrast,
	});

	const surface = cssVar('--md-sys-color-surface');

	if (surface) {
		$('meta[name="theme-color"]')?.setAttribute('content', surface);
	}
}

// Google Sans is built in. any other font from site.json is loaded from google fonts.
function applyFont() {
	const font = String((site.theme || {}).font || '').trim().replace(/['"<>]/g, '');
	const root = document.documentElement.style;

	if (!font || font.toLowerCase() === 'google sans') {
		root.removeProperty('--md-sys-typescale-font-family');
		return;
	}

	const url = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(font).replace(/%20/g, '+')}:wght@400;500;600;700&display=swap`;

	if (![...document.querySelectorAll('link[rel=stylesheet]')].some(link => link.href === url)) {
		document.head.append(make('link', { rel: 'stylesheet', href: url }));
	}

	root.setProperty('--md-sys-typescale-font-family', `'${font}', 'Google Sans', sans-serif`);
}

matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
	if (theme.colorMode === 'auto') {
		applyTheme();
	}
});

// changes the theme with a circle of the new colours growing out of the thing that was clicked.
function changeTheme(patch, origin) {
	prefs = { ...prefs, ...patch };
	savePrefs(prefs);

	if (!document.startViewTransition || reducedMotion.matches) {
		applyTheme();
		syncThemeSheet();
		return;
	}

	const x = origin?.x ?? window.innerWidth / 2;
	const y = origin?.y ?? window.innerHeight / 2;
	const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
	const transition = document.startViewTransition(() => {
		applyTheme();
		syncThemeSheet();
	});

	transition.ready.then(() => {
		document.documentElement.animate(
			{ clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
			{ duration: 750, easing: 'cubic-bezier(0.2, 0, 0, 1)', pseudoElement: '::view-transition-new(root)' }
		);
	}).catch(() => {});
}

// >> background shapes

const BLOBS = [
	{ shape: 'sunny', color: 'primary-container', size: 'clamp(220px, 34vw, 420px)', x: '-6%', y: '-4%', depth: 26, time: 80, opacity: 0.55 },
	{ shape: 'flower', color: 'tertiary-container', size: 'clamp(160px, 24vw, 300px)', x: '82%', y: '8%', depth: -34, time: 64, opacity: 0.6 },
	{ shape: '9-sided-cookie', color: 'secondary-container', size: 'clamp(200px, 30vw, 380px)', x: '72%', y: '62%', depth: 22, time: 90, opacity: 0.5 },
	{ shape: 'soft-burst', color: 'primary-container', size: 'clamp(120px, 16vw, 200px)', x: '6%', y: '70%', depth: -42, time: 54, opacity: 0.55 },
	{ shape: 'puffy', color: 'tertiary-container', size: 'clamp(90px, 12vw, 150px)', x: '44%', y: '88%', depth: 30, time: 72, opacity: 0.5 },
];

function buildBackdrop() {
	const backdrop = $('#backdrop');
	backdrop.innerHTML = '';

	if (!theme.shapes) {
		return;
	}

	for (const blob of BLOBS) {
		backdrop.append(make('div', {
			class: 'blob',
			style: `--s:${blob.size};--x:${blob.x};--y:${blob.y};--d:${blob.depth};--t:${blob.time}s;--o:${blob.opacity}`,
		}, [make('md-shape', { name: blob.shape, color: `var(--md-sys-color-${blob.color})` })]));
	}

	if (reducedMotion.matches) {
		return;
	}

	// the shapes follow the pointer, springing after it.
	const target = { x: 0, y: 0 };
	const current = { x: 0, y: 0 };
	let running = false;

	const tick = () => {
		current.x += (target.x - current.x) * 0.06;
		current.y += (target.y - current.y) * 0.06;
		backdrop.style.setProperty('--px', current.x.toFixed(3));
		backdrop.style.setProperty('--py', current.y.toFixed(3));

		if (Math.abs(target.x - current.x) > 0.002 || Math.abs(target.y - current.y) > 0.002) {
			requestAnimationFrame(tick);
		} else {
			running = false;
		}
	};

	window.addEventListener('pointermove', event => {
		target.x = event.clientX / window.innerWidth - 0.5;
		target.y = event.clientY / window.innerHeight - 0.5;

		if (!running) {
			running = true;
			requestAnimationFrame(tick);
		}
	}, { passive: true });
}

// >> confetti

// a burst of little shapes. used for the avatar and the theme picker.
function burst(x, y, count = 10) {
	if (reducedMotion.matches) {
		return;
	}

	const colors = ['primary', 'secondary', 'tertiary', 'primary-container', 'tertiary-container'];

	for (let i = 0; i < count; i++) {
		const size = 14 + Math.random() * 20;
		const piece = make('md-shape', {
			name: CONFETTI_SHAPES[i % CONFETTI_SHAPES.length],
			color: `var(--md-sys-color-${colors[i % colors.length]})`,
			style: `position:fixed;left:${x - size / 2}px;top:${y - size / 2}px;width:${size}px;height:${size}px;z-index:150;pointer-events:none`,
		});

		document.body.append(piece);

		const angle = (Math.PI * 2 * i) / count + Math.random() * 0.6;
		const distance = 70 + Math.random() * 110;
		const animation = piece.animate(
			[
				{ transform: 'translate(0, 0) scale(0.2) rotate(0deg)', opacity: 1 },
				{ transform: `translate(${Math.cos(angle) * distance * 0.7}px, ${Math.sin(angle) * distance * 0.7}px) scale(1.15) rotate(${Math.random() * 200 - 100}deg)`, opacity: 1, offset: 0.55 },
				{ transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance + 30}px) scale(0.3) rotate(${Math.random() * 360 - 180}deg)`, opacity: 0 },
			],
			{ duration: 750 + Math.random() * 400, easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)', fill: 'forwards' }
		);

		animation.onfinish = () => piece.remove();
	}
}

// >> header

let faceIndex = 0;

function renderHeader() {
	const header = $('#header');
	const name = site.name || '';
	header.innerHTML = '';

	if (site.avatar) {
		const face = make('span', { class: 'face' }, [
			make('md-shape', { name: FACE_SHAPES[faceIndex], mask: true }, [make('img', { src: site.avatar, alt: name, draggable: 'false' })]),
		]);

		const halo = make('span', { class: 'halo', 'aria-hidden': 'true' }, [
			make('md-shape', { name: FACE_SHAPES[(faceIndex + 4) % FACE_SHAPES.length], color: 'var(--md-sys-color-tertiary-container)' }),
		]);

		const avatar = make('button', { class: 'avatar', type: 'button', 'aria-label': `${name}: change the shape` }, [halo, face]);

		avatar.addEventListener('click', event => {
			faceIndex = (faceIndex + 1) % FACE_SHAPES.length;
			face.firstElementChild.setAttribute('name', FACE_SHAPES[faceIndex]);
			halo.firstElementChild.setAttribute('name', FACE_SHAPES[(faceIndex + 4) % FACE_SHAPES.length]);

			if (!reducedMotion.matches) {
				const { easing, duration } = spring();
				avatar.animate(
					[{ transform: 'scale(1) rotate(0)' }, { transform: 'scale(0.78) rotate(-14deg)', offset: 0.25 }, { transform: 'scale(1) rotate(0)' }],
					{ duration: duration + 200, easing }
				);
			}

			const box = avatar.getBoundingClientRect();
			burst(box.left + box.width / 2, box.top + box.height / 2);
		});

		header.append(avatar);
	}

	const title = make('h1', { class: 'name', 'aria-label': name });

	[...name].forEach(character => {
		title.append(make('span', { class: 'ch', 'aria-hidden': 'true', text: character }));
	});

	header.append(title);

	if (site.role) {
		header.append(make('md-chip', { class: 'role', variant: 'assist', icon: 'auto_awesome', label: site.role }));
	}

	if (!reducedMotion.matches) {
		const { easing, duration } = spring();

		[...title.children].forEach((letter, index) => {
			letter.animate(
				[
					{ opacity: 0, transform: 'translateY(70%) rotate(-12deg) scale(0.4)' },
					{ opacity: 1, transform: 'none' },
				],
				{ duration: duration + 300, delay: 160 + index * 55, easing, fill: 'backwards' }
			);
		});

		springIn([header.querySelector('.avatar'), header.querySelector('.role')].filter(Boolean), { from: 10, step: 260 });
	}

	document.title = seo.pageTitle || (name ? `${name}'s Portfolio` : 'Portfolio');
}

// >> tabs

// the first tab is always the landing tab and has no hash.
function hashFor(tab, index) {
	if (index === 0) {
		return '';
	}

	return String(tab.hash ?? tab.id).replace(/^#/, '').toLowerCase();
}

function tabIcon(tab) {
	return tab.icon || TYPE_ICONS[tab.type] || 'star';
}

function buildNav() {
	const pill = $('#nav-pill');
	const bar = $('#nav-bar');
	pill.innerHTML = '';
	bar.innerHTML = '';

	if (tabList.length < 2) {
		$('#nav').hidden = true;
		return;
	}

	const group = make('md-button-group', { variant: 'connected', selection: 'single', 'aria-label': 'Sections' });

	tabList.forEach(tab => {
		group.append(make('md-button', { label: tab.label || tab.id, icon: tabIcon(tab), 'data-tab': tab.id }));
	});

	group.addEventListener('selection-change', event => {
		switchTab(tabList[event.detail.index].id);
	});

	pill.append(group);

	const items = tabList.map(tab => ({ icon: tabIcon(tab), label: tab.label || tab.id }));
	const navigation = make('md-navigation-bar', { items: JSON.stringify(items), selected: '0', 'aria-label': 'Sections' });

	navigation.addEventListener('change', event => {
		const tab = tabList[event.detail.index];

		if (tab && tab.id !== activeId) {
			switchTab(tab.id);
		}
	});

	bar.append(navigation);

	// the pill grows a shadow once it floats over the content.
	const sentinel = $('#nav-sentinel');

	new IntersectionObserver(([entry]) => {
		$('#nav').classList.toggle('stuck', !entry.isIntersecting);
	}, { rootMargin: '-16px 0px 0px 0px' }).observe(sentinel);
}

function buildPanels() {
	const panels = $('#panels');
	panels.innerHTML = '';

	tabList.forEach(tab => {
		panels.append(make('section', { class: 'panel', id: `tab-${tab.id}`, 'aria-label': tab.label || tab.id }));
	});
}

function syncNav(index) {
	const group = $('#nav-pill md-button-group');
	const navigation = $('#nav-bar md-navigation-bar');

	group?.querySelectorAll('md-button').forEach((button, i) => {
		button.toggleAttribute('selected', i === index);
	});

	if (navigation && navigation.getAttribute('selected') !== String(index)) {
		navigation.setAttribute('selected', String(index));
	}
}

// switches the currently visible portfolio tab.
function switchTab(tabId, updateHash = true) {
	const index = tabList.findIndex(tab => tab.id === tabId);

	if (index === -1) {
		return;
	}

	const first = activeId === null;
	activeId = tabId;

	document.querySelectorAll('.panel').forEach(panel => {
		panel.classList.toggle('active', panel.id === `tab-${tabId}`);
	});

	syncNav(index);

	const panel = $(`#tab-${tabId}`);
	const fresh = loadTab(tabList[index], panel);

	if (!fresh && !first) {
		springIn(panel.querySelectorAll('[data-pop]'), { from: 22, step: 40, max: 10 });
	}

	if (updateHash) {
		const hash = hashFor(tabList[index], index);
		const newHash = hash ? `#${hash}` : '';

		if (window.location.hash !== newHash) {
			history.pushState(null, '', `${window.location.pathname}${window.location.search}${newHash}`);
		}
	}

	if (!first) {
		const top = $('#nav').getBoundingClientRect().top + window.scrollY - 14;

		if (window.scrollY > top) {
			window.scrollTo({ top, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
		}
	}
}

function openHashTab() {
	const hash = window.location.hash.replace(/^#/, '').toLowerCase();
	const index = hash ? tabList.findIndex((tab, i) => hashFor(tab, i) === hash) : 0;

	switchTab(tabList[Math.max(index, 0)].id, false);
}

// fills a tab the first time it is opened. returns true if it was filled just now.
function loadTab(tab, panel) {
	if (loadedTabs.has(tab.id)) {
		return false;
	}

	loadedTabs.add(tab.id);

	const body = make('div', { class: 'panel-body' });

	if (tab.title) {
		panel.append(make('div', { class: 'panel-head', 'data-pop': true }, [make('h2', { class: 'panel-title', text: tab.title })]));
	}

	panel.append(body);

	const loaders = { page: loadPage, work: loadWork, reviews: loadReviews, contact: loadContact };

	(loaders[tab.type] || loadPage)(tab, body, panel);

	return true;
}

function revealPanel(panel) {
	// while the boot splash is up the first reveal is done by init().
	if (document.documentElement.classList.contains('booting')) {
		return;
	}

	springIn(panel.querySelectorAll('[data-pop]'), { from: 30, step: 60, max: 12 });
}

// >> pages

function autoIcon(heading, index) {
	const match = HEADING_ICONS.find(([pattern]) => pattern.test(heading || ''));

	return match ? match[1] : FALLBACK_ICONS[index % FALLBACK_ICONS.length];
}

function sectionContent(section) {
	const parts = [];

	[].concat(section.text || []).forEach(paragraph => {
		parts.push(make('p', { class: 'card-text', html: richText(paragraph) }));
	});

	if (section.items && section.items.length) {
		parts.push(make('ul', { class: 'bullets' }, section.items.map(item => make('li', { html: richText(item) }))));
	}

	return parts;
}

// renders a text page from Config/pages/<id>.json.
async function loadPage(tab, body, panel) {
	body.append(loadingBlock('Loading'));

	const page = await fetchJson(`${CONFIG_DIR}/pages/${tab.id}.json`, null);
	body.innerHTML = '';

	if (!page || !(page.sections || []).length) {
		body.append(make('div', { class: 'empty', text: 'Nothing here yet.' }));
		return;
	}

	const sections = page.sections;

	if (page.layout === 'accordion') {
		const accordion = make('div', { class: 'accordion' });

		sections.forEach((section, index) => {
			const content = make('div', { class: 'panel-content' }, sectionContent(section));

			if (section.badge) {
				content.append(make('md-chip', { class: 'card-badge', variant: 'assist', icon: section.icon || autoIcon(section.heading, index), label: plainText(section.badge) }));
			}

			const item = make('md-expansion-panel', { headline: section.heading || '', 'data-pop': true, open: index === 0 }, [
				make('span', { slot: 'leading-icon', class: 'material-symbols-rounded panel-icon', text: section.icon || autoIcon(section.heading, index) }),
				content,
			]);

			accordion.append(item);
		});

		body.append(accordion);
		revealPanel(panel);
		return;
	}

	const bento = make('div', { class: 'bento' });

	sections.forEach((section, index) => {
		const icon = section.icon || autoIcon(section.heading, index);
		const inner = make('div', { class: 'card-body' }, [
			make('div', { class: 'card-head' }, [
				shapeIcon(icon, FACE_SHAPES[(index * 5) % FACE_SHAPES.length]),
				section.heading ? make('h3', { class: 'card-title', text: section.heading }) : null,
			]),
			...sectionContent(section),
			section.badge ? make('md-chip', { class: 'card-badge', variant: 'assist', icon, label: plainText(section.badge) }) : null,
		]);

		bento.append(make('md-card', { class: `tone tone-${TONES[index % TONES.length]}`, variant: 'filled', 'data-pop': true }, [inner]));
	});

	body.append(bento);
	revealPanel(panel);
}

// >> work

// the github api is only used if Work/index.json is missing and a github repo is set in site.json.
function githubApi(folder) {
	const github = site.github || {};

	if (!github.owner || !github.repo) {
		return null;
	}

	const branch = github.branch || 'main';

	return {
		list: `https://api.github.com/repos/${github.owner}/${github.repo}/contents/${folder}?ref=${branch}`,
		raw: `https://raw.githubusercontent.com/${github.owner}/${github.repo}/${branch}`,
	};
}

// gets all files inside the Work folder.
async function getWorkFiles() {
	const manifest = await fetchJson('Work/index.json', null);

	if (Array.isArray(manifest)) {
		return manifest.map(file => {
			const name = typeof file === 'string' ? file : file.name;

			return {
				name,
				title: typeof file === 'string' ? '' : file.title,
				url: (typeof file !== 'string' && file.url) || `Work/${encodeURIComponent(name)}`,
			};
		});
	}

	const github = githubApi('Work');

	if (!github) {
		throw new Error('Work/index.json is missing. Open the editor and press Save & Build.');
	}

	const response = await fetch(github.list);

	if (!response.ok) {
		throw new Error('Unable to load the Work folder.');
	}

	return (await response.json())
		.filter(file => file.type === 'file')
		.map(file => ({ name: file.name, title: '', url: file.download_url }));
}

function formatDuration(seconds) {
	const total = Math.round(seconds);
	const minutes = Math.floor(total / 60);

	return `${minutes}:${String(total % 60).padStart(2, '0')}`;
}

// a loading indicator that covers a video / image until it is ready. created on demand so that a finished one stops animating.
function bufferOverlay(frame) {
	let overlay = null;

	return {
		show() {
			if (!overlay) {
				overlay = make('div', { class: 'buffer' }, [loader(64)]);
				frame.append(overlay);
			}
		},
		hide() {
			if (overlay) {
				const done = overlay;
				overlay = null;
				done.classList.add('done');
				setTimeout(() => done.remove(), 350);
			}
		},
	};
}

// creates a work item from an image or a video. videos only start loading when they come near the screen.
function createWorkItem(file, observer) {
	const lowerName = file.name.toLowerCase();
	const isVideo = VIDEO_EXTENSIONS.some(type => lowerName.endsWith(type));
	const isImage = IMAGE_EXTENSIONS.some(type => lowerName.endsWith(type));

	if (!isVideo && !isImage) {
		return null;
	}

	const frame = make('div', { class: 'work-frame' });
	const buffer = bufferOverlay(frame);
	const meta = make('div', { class: 'work-meta' }, [make('h3', { class: 'work-name', text: file.title || fileTitle(file.name), title: file.title || fileTitle(file.name) })]);
	buffer.show();

	if (isVideo) {
		const video = make('video', { controls: true, muted: true, playsinline: true, preload: 'none', 'aria-label': file.title || fileTitle(file.name) });
		video.dataset.src = file.url;
		video.addEventListener('loadedmetadata', () => {
			meta.append(make('md-chip', { variant: 'assist', icon: 'play_arrow', label: formatDuration(video.duration) }));
		}, { once: true });
		video.addEventListener('loadeddata', () => buffer.hide());
		video.addEventListener('canplay', () => buffer.hide());
		video.addEventListener('waiting', () => buffer.show());
		video.addEventListener('playing', () => buffer.hide());
		video.addEventListener('error', () => {
			buffer.hide();
			frame.append(make('div', { class: 'buffer', html: '<span class="material-symbols-rounded" style="font-size:40px;color:var(--md-sys-color-error)">error</span>' }));
		});
		frame.prepend(video);
		observer.observe(video);
	} else {
		const image = make('img', { src: file.url, alt: file.title || fileTitle(file.name), loading: 'lazy' });
		image.addEventListener('load', () => buffer.hide());
		image.addEventListener('error', () => buffer.hide());
		frame.prepend(image);
		meta.append(make('md-chip', { variant: 'assist', icon: 'image', label: 'Image' }));
	}

	return make('md-card', { class: 'tone work-card tone-surface', variant: 'filled', 'data-pop': true }, [
		make('div', { class: 'card-body' }, [frame, meta]),
	]);
}

// loads all proof of work media.
async function loadWork(tab, body, panel) {
	body.append(loadingBlock('Loading work'));

	try {
		const files = await getWorkFiles();
		const observer = new IntersectionObserver(entries => {
			entries.forEach(entry => {
				if (entry.isIntersecting) {
					const video = entry.target;
					video.src = video.dataset.src;
					video.preload = 'metadata';
					observer.unobserve(video);
				}
			});
		}, { rootMargin: '700px 0px' });

		const items = files.map(file => createWorkItem(file, observer)).filter(Boolean);
		body.innerHTML = '';

		if (!items.length) {
			body.append(make('div', { class: 'empty', text: 'No proof of work has been added yet.' }));
			return;
		}

		const head = panel.querySelector('.panel-head');

		if (head) {
			head.append(make('md-chip', { variant: 'assist', icon: 'play_circle', label: `${items.length} ${items.length === 1 ? 'project' : 'projects'}` }));
		}

		body.append(make('div', { class: 'work-grid' }, items));
		revealPanel(panel);
	} catch (error) {
		console.error(error);
		loadedTabs.delete(tab.id);
		body.innerHTML = '';
		body.append(make('div', { class: 'empty', text: error.message || 'Unable to load proof of work.' }));
	}
}

// >> reviews

// gets the list of review folders.
async function getReviewFiles() {
	const manifest = await fetchJson('Reviews/index.json', null);

	if (Array.isArray(manifest)) {
		return manifest.map(entry => {
			const name = typeof entry === 'string' ? entry : entry.name;

			return { name, url: `Reviews/${encodeURIComponent(name)}/index.json` };
		});
	}

	const github = githubApi('Reviews');

	if (!github) {
		throw new Error('Reviews/index.json is missing. Open the editor and press Save & Build.');
	}

	const response = await fetch(github.list);

	if (!response.ok) {
		throw new Error('Unable to load the Reviews folder.');
	}

	return (await response.json())
		.filter(entry => entry.type === 'dir')
		.map(client => ({ name: client.name, url: `${github.raw}/Reviews/${encodeURIComponent(client.name)}/index.json` }));
}

function openLightbox(src, alt) {
	const dialog = $('#lightbox');
	const image = $('img', dialog);

	image.src = src;
	image.alt = alt;
	dialog.showModal();
}

// creates a review card from json data.
function createReview(review, index) {
	const name = review.name || 'Anonymous';
	const tone = TONES[(index + 1) % TONES.length];

	const picture = make('div', { class: 'review-pfp' });
	const initial = make('div', { class: 'fallback', text: name.slice(0, 1).toUpperCase() });
	const shape = make('md-shape', { name: FACE_SHAPES[(index * 3) % FACE_SHAPES.length], mask: true }, [initial]);

	if (review.pfp) {
		// not lazy: this image is not in the page until it has loaded, so a lazy one would never start.
		const image = make('img', { src: review.pfp, alt: name, draggable: 'false' });
		image.addEventListener('load', () => initial.replaceWith(image));
	}

	picture.append(shape);

	const inner = make('div', { class: 'card-body' }, [
		make('div', { class: 'review-top' }, [picture, make('h3', { class: 'review-name', text: name })]),
		make('p', { class: 'review-text', text: review.text || '' }),
	]);

	if (review.proof) {
		const loaderBox = make('div', { class: 'loading', style: 'padding:18px 0 0' }, [loader(48)]);
		const image = make('img', { alt: `Proof from ${name}` });

		// the image sits in a real button: md-card swallows clicks on plain elements.
		const zoom = make('button', { class: 'proof-zoom', type: 'button', 'aria-label': 'View the proof full size' }, [image]);
		const inner2 = make('div', { class: 'proof-inner' }, [loaderBox, zoom]);
		const proof = make('div', { class: 'proof' }, [inner2]);
		const button = make('md-button', { variant: 'tonal', size: 'xs', icon: 'image', label: 'Show proof' });
		let loaded = false;

		image.addEventListener('load', () => loaderBox.remove());
		zoom.addEventListener('click', () => openLightbox(review.proof, image.alt));
		button.addEventListener('click', () => {
			const open = proof.classList.toggle('open');

			if (open && !loaded) {
				loaded = true;
				image.src = review.proof;
			}

			button.setAttribute('label', open ? 'Hide proof' : 'Show proof');
			button.setAttribute('icon', open ? 'expand_less' : 'image');
		});

		inner.append(make('div', { class: 'review-actions' }, [button]), proof);
	}

	return make('md-card', { class: `tone review tone-${tone}`, variant: 'filled', 'data-pop': true }, [inner]);
}

// loads review json files.
async function loadReviews(tab, body, panel) {
	body.append(loadingBlock('Loading reviews'));

	try {
		const files = await getReviewFiles();

		const reviews = await Promise.all(
			files.map(async file => {
				const review = await fetchJson(file.url, null);

				if (!review) {
					return null;
				}

				// pfp and proof are relative to the review's own folder.
				review.pfp = resolveFrom(file.url, review.pfp);
				review.proof = resolveFrom(file.url, review.proof);

				return review;
			})
		);

		body.innerHTML = '';

		const valid = reviews.filter(Boolean);

		if (!valid.length) {
			body.append(make('div', { class: 'empty', text: 'No reviews have been added yet.' }));
			return;
		}

		const head = panel.querySelector('.panel-head');

		if (head) {
			head.append(make('md-chip', { variant: 'assist', icon: 'star', label: `${valid.length} ${valid.length === 1 ? 'review' : 'reviews'}` }));
		}

		body.append(make('div', { class: 'review-cols' }, valid.map(createReview)));
		revealPanel(panel);
	} catch (error) {
		console.error('Failed to load reviews:', error);
		loadedTabs.delete(tab.id);
		body.innerHTML = '';
		body.append(make('div', { class: 'empty', text: error.message || 'Unable to load reviews.' }));
	}
}

// >> contact

function contactIcon(icon, index) {
	const shapeName = FACE_SHAPES[(index * 2 + 1) % FACE_SHAPES.length];

	if (ICONS[icon]) {
		return make('div', { class: 'contact-icon', 'aria-hidden': 'true' }, [
			make('md-shape', { name: shapeName, color: 'var(--tone-accent)' }),
			make('span', { html: `<svg viewBox="0 0 24 24"><path d="${ICONS[icon]}"/></svg>` }),
		]);
	}

	if (/[./]/.test(icon)) {
		// a picture: it takes the shape itself.
		return make('div', { class: 'contact-icon', 'aria-hidden': 'true' }, [
			make('md-shape', { name: shapeName, mask: true, style: 'position:absolute;inset:0;width:100%;height:100%' }, [make('img', { src: icon, alt: '', style: 'width:100%;height:100%;object-fit:cover' })]),
		]);
	}

	return make('div', { class: 'contact-icon', 'aria-hidden': 'true' }, [
		make('md-shape', { name: shapeName, color: 'var(--tone-accent)' }),
		make('span', { class: 'material-symbols-rounded icon', text: icon }),
	]);
}

async function copyText(text) {
	try {
		await navigator.clipboard.writeText(text);
		toast(`Copied ${text}`);
	} catch (error) {
		toast('Could not copy that');
	}
}

// loads the contact links from Config/contact.json.
async function loadContact(tab, body, panel) {
	const contacts = await fetchJson(`${CONFIG_DIR}/contact.json`, []);

	if (!contacts.length) {
		body.append(make('div', { class: 'empty', text: 'No contact links have been added yet.' }));
		return;
	}

	const grid = make('div', { class: 'contact-grid' });

	contacts.forEach((contact, index) => {
		const label = contact.label || contact.url || '';
		const link = make('a', { class: 'sr-only', href: contact.url || '#', target: '_blank', rel: 'noopener noreferrer', text: `Open ${label}` });
		const copy = make('md-icon-button', { icon: 'content_copy', 'aria-label': `Copy ${label}`, title: 'Copy', style: 'position:relative;z-index:2' });
		copy.addEventListener('click', event => {
			event.stopPropagation();
			copyText(label);
			const box = copy.getBoundingClientRect();
			burst(box.left + box.width / 2, box.top + box.height / 2, 7);
		});

		const card = make('md-card', { class: `tone contact-card tone-${TONES[index % TONES.length]}`, variant: 'filled', interactive: true, 'data-pop': true }, [
			make('div', { class: 'card-body' }, [
				contactIcon(contact.icon || 'link', index),
				make('div', { class: 'contact-label' }, [make('span', { text: label })]),
				make('div', { class: 'contact-actions' }, [copy, make('span', { class: 'material-symbols-rounded', 'aria-hidden': 'true', text: 'arrow_outward', style: 'align-self:center;padding:12px' })]),
			]),
			link,
		]);

		card.style.cursor = 'pointer';
		card.addEventListener('click', () => {
			window.open(contact.url, '_blank', 'noopener,noreferrer');
		});

		grid.append(card);
	});

	body.append(grid);
	revealPanel(panel);
}

// >> theme sheet

function buildThemeSheet() {
	const sheet = $('#theme-sheet');
	const stored = () => ({ ...configTheme(), ...prefs });

	const swatches = make('div', { class: 'swatches', role: 'radiogroup', 'aria-label': 'Colour' });
	const siteSeed = configTheme().seedColor;
	const seeds = [[siteSeed, 'Site colour'], ...SEED_PRESETS.filter(([hex]) => hex.toLowerCase() !== siteSeed.toLowerCase())];

	seeds.forEach(([hex, label]) => {
		const swatch = make('button', { class: 'swatch', type: 'button', role: 'radio', style: `--sw:${hex}`, 'data-seed': hex, 'aria-label': label, title: label }, [
			make('span', { class: 'material-symbols-rounded tick', text: 'check' }),
		]);

		swatch.addEventListener('click', event => {
			changeTheme({ seedColor: hex }, { x: event.clientX, y: event.clientY });
			burst(event.clientX, event.clientY, 6);
		});

		swatches.append(swatch);
	});

	const picker = make('input', { type: 'color', value: stored().seedColor.slice(0, 7), 'aria-label': 'Pick any colour' });
	picker.addEventListener('input', () => changeTheme({ seedColor: picker.value }, null));
	swatches.append(make('label', { class: 'swatch custom', title: 'Any colour' }, [make('span', { class: 'material-symbols-rounded', style: 'color:#fff;mix-blend-mode:difference', text: 'colorize' }), picker]));

	const mode = make('md-segmented-button', {
		'aria-label': 'Colour mode',
		items: JSON.stringify([{ label: 'Auto', icon: 'brightness_auto' }, { label: 'Light', icon: 'light_mode' }, { label: 'Dark', icon: 'dark_mode' }]),
		'selected-index': '0',
	});

	mode.addEventListener('change', event => {
		const box = mode.getBoundingClientRect();
		changeTheme({ colorMode: ['auto', 'light', 'dark'][event.detail.selectedIndex] }, { x: box.left + box.width / 2, y: box.top });
	});

	const chips = make('div', { class: 'chips', role: 'radiogroup', 'aria-label': 'Palette style' });

	PALETTE_STYLES.forEach(([value, label]) => {
		const chip = make('md-chip', { variant: 'filter', label, 'data-variant': value });
		chip.addEventListener('change', event => {
			if (event.detail.selected) {
				changeTheme({ paletteVariant: value }, null);
			} else {
				syncThemeSheet();
			}
		});
		chips.append(chip);
	});

	const motion = make('md-segmented-button', {
		'aria-label': 'Motion',
		items: JSON.stringify([{ label: 'Expressive', icon: 'animation' }, { label: 'Standard', icon: 'speed' }]),
		'selected-index': '0',
	});

	motion.addEventListener('change', event => {
		const box = motion.getBoundingClientRect();
		changeTheme({ motion: ['expressive', 'standard'][event.detail.selectedIndex] }, { x: box.left + box.width / 2, y: box.top });
		toast(event.detail.selectedIndex === 0 ? 'Bouncy, springy motion' : 'Calm, subtle motion');
	});

	const close = make('md-icon-button', { icon: 'close', 'aria-label': 'Close', variant: 'tonal' });
	close.addEventListener('click', () => sheet.close());

	const reset = make('md-button', { variant: 'text', label: 'Reset', icon: 'restart_alt' });
	reset.addEventListener('click', event => {
		prefs = {};
		savePrefs(prefs);
		changeTheme({}, { x: event.clientX, y: event.clientY });
	});

	const done = make('md-button', { variant: 'filled', label: 'Done' });
	done.addEventListener('click', () => sheet.close());

	sheet.append(make('div', { class: 'sheet-body' }, [
		make('div', { class: 'sheet-head' }, [make('h2', { text: 'Make it yours' }), close]),
		make('div', {}, [make('p', { class: 'field-label', text: 'Colour mode' }), mode]),
		make('div', {}, [make('p', { class: 'field-label', text: 'Colour' }), swatches]),
		make('div', {}, [make('p', { class: 'field-label', text: 'Palette style' }), chips]),
		make('div', {}, [make('p', { class: 'field-label', text: 'Motion' }), motion]),
		make('div', { class: 'sheet-foot' }, [reset, done]),
	]));

	sheet.addEventListener('click', event => {
		if (event.target === sheet) {
			sheet.close();
		}
	});

	sheet._parts = { mode, swatches, chips, motion, picker };
}

// shows the current settings in the sheet's controls.
function syncThemeSheet() {
	const parts = $('#theme-sheet')?._parts;

	if (!parts) {
		return;
	}

	parts.mode.setAttribute('selected-index', String(['auto', 'light', 'dark'].indexOf(theme.colorMode)));
	parts.motion.setAttribute('selected-index', String(theme.motion === 'standard' ? 1 : 0));

	parts.swatches.querySelectorAll('.swatch[data-seed]').forEach(swatch => {
		const on = swatch.dataset.seed.toLowerCase() === theme.seedColor.toLowerCase();
		swatch.classList.toggle('on', on);
		swatch.setAttribute('aria-checked', String(on));
	});

	parts.chips.querySelectorAll('md-chip').forEach(chip => {
		chip.toggleAttribute('selected', chip.dataset.variant === theme.paletteVariant);
	});

	parts.picker.value = theme.seedColor.slice(0, 7);
}

function buildFab() {
	const fab = $('#fab');

	if (!theme.themePicker) {
		fab.hidden = true;
		return;
	}

	buildThemeSheet();

	const sheet = $('#theme-sheet');
	const button = make('md-fab', { size: 'medium', color: 'tertiary-container', icon: 'palette', label: 'Make it yours', expanded: true, 'aria-label': 'Open the theme settings' });

	button.addEventListener('click', () => {
		syncThemeSheet();
		sheet.showModal();
	});

	fab.append(button);

	// the label folds away after a moment, and comes back when you point at it.
	const collapse = () => button.setAttribute('expanded', 'false');
	const expand = () => button.setAttribute('expanded', '');
	const timer = setTimeout(collapse, 4500);

	window.addEventListener('scroll', () => {
		clearTimeout(timer);
		collapse();
	}, { once: true, passive: true });

	button.addEventListener('pointerenter', expand);
	button.addEventListener('pointerleave', collapse);
	button.addEventListener('focus', expand);
	button.addEventListener('blur', collapse);
}

function buildLightbox() {
	const dialog = $('#lightbox');
	const close = make('md-icon-button', { icon: 'close', 'aria-label': 'Close', variant: 'tonal' });
	close.addEventListener('click', () => dialog.close());
	$('.bar', dialog).append(close);
	dialog.addEventListener('click', event => {
		if (event.target === dialog) {
			dialog.close();
		}
	});
}

// >> start

function showFailure(message) {
	const boot = $('#boot');
	boot.innerHTML = '';
	boot.append(make('div', { class: 'notice', style: 'max-width:520px;padding:24px;text-align:center;line-height:1.6;font-family:system-ui,sans-serif', html: message }));
	document.documentElement.classList.remove('booting');
	boot.style.opacity = '1';
	boot.style.visibility = 'visible';
	boot.style.pointerEvents = 'auto';
}

async function init() {
	try {
		md3 = await import('./vendor/md3e.js');
	} catch (error) {
		console.error(error);
		showFailure('<b>The page could not load its components.</b><br>Make sure the <code>Site</code> folder is uploaded next to <code>index.html</code>.');
		return;
	}

	const [siteData, seoData, tabData] = await Promise.all([
		fetchJson(`${CONFIG_DIR}/site.json`, null),
		fetchJson(`${CONFIG_DIR}/seo.json`, {}),
		fetchJson(`${CONFIG_DIR}/tabs.json`, null),
	]);

	if (!siteData || !Array.isArray(tabData)) {
		showFailure(window.location.protocol === 'file:'
			? '<b>The site could not load its settings.</b><br>This page was opened straight from the file system, which browsers block. Start the test server: run the editor and press <i>Start server</i>.'
			: '<b>The site could not load its settings.</b><br>Config/site.json was not found. Make sure the Config folder is uploaded next to index.html.');
		return;
	}

	site = siteData;
	seo = seoData || {};
	tabList = tabData.filter(tab => tab.enabled !== false && tab.id);

	if (!tabList.length) {
		tabList = [{ id: 'home', label: 'Home', type: 'page' }];
	}

	applyFont();
	applyTheme();
	renderHeader();
	buildBackdrop();
	buildNav();
	buildPanels();
	buildFab();
	buildLightbox();

	$('#year').textContent = new Date().getFullYear();
	$('#foot-name').textContent = site.name || '';

	openHashTab();

	// let the boot splash finish its first morph, then reveal.
	setTimeout(() => {
		document.documentElement.classList.remove('booting');
		springIn(document.querySelectorAll('#panels .panel.active [data-pop]'), { from: 30, step: 60, max: 12 });
	}, 650);
}

window.addEventListener('hashchange', () => {
	if (tabList.length) {
		openHashTab();
	}
});

init();
