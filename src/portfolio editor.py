#!/usr/bin/env python3
"""
Portfolio Editor
================

Double-click Editor.bat (or run `python editor.py`) to open the editor.

    * edit your name, role, colours, title card, pages, work, reviews and contacts
    * previews for the header, the Twitter / X / Discord title card and every page
    * builds Work/index.json, Reviews/index.json and the <head> of index.html for you
    * starts / stops a local test server and opens the site in your browser

Command line (no window):

    python editor.py --build                    rebuild the index files + index.html
    python editor.py --serve [--port 5000]      only run the test server
    python editor.py --serve --lan --open       also reachable from your phone, open browser

Only the python standard library is required. Pillow (pip install pillow) is optional;
without it the previews can only show png / gif images.
"""

import argparse
import contextlib
import copy
import datetime
import functools
import hashlib
import html
import http.server
import json
import mimetypes
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import tkinter.font as tkfont
import urllib.parse
import urllib.request
import webbrowser
from tkinter import colorchooser, filedialog, messagebox, ttk

try:
	from PIL import Image, ImageChops, ImageDraw, ImageTk
	HAVE_PIL = True
except ImportError:
	HAVE_PIL = False

ROOT = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT, 'Config')
PAGES_DIR = os.path.join(CONFIG_DIR, 'pages')
WORK_DIR = os.path.join(ROOT, 'Work')
REVIEWS_DIR = os.path.join(ROOT, 'Reviews')
ASSETS_DIR = os.path.join(ROOT, 'Assets')
INDEX_HTML = os.path.join(ROOT, 'index.html')

VIDEO_EXTENSIONS = ('.mp4', '.webm', '.ogg', '.mov', '.m4v')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS + IMAGE_EXTENSIONS

BUILTIN_ICONS = ('discord', 'x', 'twitter', 'github', 'youtube', 'email', 'link')
TAB_TYPES = ('page', 'work', 'reviews', 'contact')
TAB_TYPE_HELP = {
	'page': 'Text page (sections with bullet points, paragraphs, badges)',
	'work': 'Proof of work gallery (images / videos from the Work folder)',
	'reviews': 'Client reviews (from the Reviews folder)',
	'contact': 'Contact links',
}

mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mp4', '.m4v')
mimetypes.add_type('video/webm', '.webm')
mimetypes.add_type('video/quicktime', '.mov')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('text/javascript', '.js')


# >> defaults

DEFAULT_SITE = {
	'name': 'Your Name',
	'role': 'Your Role',
	'avatar': 'Assets/profile.png',
	'theme': {
		'backgroundTop': '#500000',
		'backgroundBottom': '#ff0000',
		'cardOpacity': 0.72,
		'font': 'Inter',
	},
	'github': {'owner': '', 'repo': '', 'branch': 'main'},
}

DEFAULT_SEO = {
	'pageTitle': '',
	'title': '',
	'description': '',
	'image': '',
	'imageAlt': '',
	'url': '',
	'siteName': '',
	'twitterHandle': '',
	'cardType': 'summary_large_image',
	'themeColor': '',
	'locale': 'en_US',
}

DEFAULT_TABS = [
	{'id': 'home', 'label': 'Home', 'type': 'page', 'title': '', 'hash': '', 'enabled': True},
	{'id': 'work', 'label': 'Proof Of Work', 'type': 'work', 'title': 'Proof Of Work', 'hash': 'proofofwork', 'enabled': True},
	{'id': 'reviews', 'label': 'Reviews', 'type': 'reviews', 'title': 'Reviews', 'hash': 'reviews', 'enabled': True},
	{'id': 'contact', 'label': 'Contact', 'type': 'contact', 'title': 'Contact', 'hash': 'contact', 'enabled': True},
]


# >> small helpers

class ConfigError(Exception):
	pass


def rel(path):
	"""project-relative path with forward slashes, or None when outside the project."""
	try:
		full = os.path.abspath(path)
		if os.path.commonpath([full, ROOT]) != ROOT:
			return None
		return os.path.relpath(full, ROOT).replace('\\', '/')
	except ValueError:
		return None


def read_json(path, default):
	try:
		with open(path, 'r', encoding='utf-8-sig') as handle:
			return json.load(handle)
	except FileNotFoundError:
		return default
	except json.JSONDecodeError as error:
		raise ConfigError('%s is not valid JSON (line %d): %s' % (rel(path) or path, error.lineno, error.msg))


def write_json(path, data):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	temp = path + '.tmp'
	with open(temp, 'w', encoding='utf-8', newline='\n') as handle:
		json.dump(data, handle, indent=2, ensure_ascii=False)
		handle.write('\n')
	os.replace(temp, path)


def merge(defaults, data):
	out = copy.deepcopy(defaults)
	if isinstance(data, dict):
		for key, value in data.items():
			if isinstance(value, dict) and isinstance(out.get(key), dict):
				out[key] = merge(out[key], value)
			else:
				out[key] = value
	return out


def natural_key(text):
	return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', text)]


def slugify(text):
	return re.sub(r'[^A-Za-z0-9]+', '-', text).strip('-').lower() or 'item'


def unique_name(directory, name):
	if not os.path.exists(os.path.join(directory, name)):
		return name
	stem, ext = os.path.splitext(name)
	number = 2
	while os.path.exists(os.path.join(directory, '%s-%d%s' % (stem, number, ext))):
		number += 1
	return '%s-%d%s' % (stem, number, ext)


def is_url(value):
	return bool(re.match(r'https?://', value or '', re.I))


def lan_address():
	try:
		probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		probe.connect(('10.255.255.255', 1))
		address = probe.getsockname()[0]
		probe.close()
		return address
	except OSError:
		return None


def open_folder(path):
	os.makedirs(path, exist_ok=True)
	if sys.platform.startswith('win'):
		os.startfile(path)
	elif sys.platform == 'darwin':
		subprocess.Popen(['open', path])
	else:
		subprocess.Popen(['xdg-open', path])


def to_rgb(widget, color):
	"""any css-ish colour -> (r, g, b) 0..255."""
	color = (color or '').strip()
	match = re.fullmatch(r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})', color)
	if match:
		digits = match.group(1)
		if len(digits) == 3:
			digits = ''.join(ch * 2 for ch in digits)
		return tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))
	try:
		r, g, b = widget.winfo_rgb(color)
		return (r // 257, g // 257, b // 257)
	except tk.TclError:
		return (80, 0, 0)


def hex_color(rgb):
	return '#%02x%02x%02x' % tuple(max(0, min(255, int(v))) for v in rgb)


# >> seo values (shared by the builder and the previews)

def effective_seo(site, seo):
	"""fills in every blank seo field with a sensible automatic value."""
	name = (site.get('name') or '').strip()
	role = (site.get('role') or '').strip()
	theme = site.get('theme') or {}

	default_site_name = "%s's Portfolio" % name if name else 'Portfolio'
	default_title = '%s | %s' % (name, role) if name and role else (name or role or 'Portfolio')

	base = (seo.get('url') or '').strip()
	image = (seo.get('image') or '').strip()
	handle = (seo.get('twitterHandle') or '').strip()

	if handle and not handle.startswith('@'):
		handle = '@' + handle

	absolute_image = image

	if image and not is_url(image) and base:
		absolute_image = urllib.parse.urljoin(base if base.endswith('/') else base + '/', image.lstrip('/'))

	return {
		'pageTitle': (seo.get('pageTitle') or '').strip() or default_site_name,
		'title': (seo.get('title') or '').strip() or default_title,
		'description': (seo.get('description') or '').strip(),
		'image': absolute_image,
		'imageRaw': image,
		'imageAlt': (seo.get('imageAlt') or '').strip() or default_site_name,
		'url': base,
		'siteName': (seo.get('siteName') or '').strip() or default_site_name,
		'handle': handle,
		'cardType': seo.get('cardType') or 'summary_large_image',
		'themeColor': (seo.get('themeColor') or '').strip() or theme.get('backgroundBottom') or '#ff0000',
		'locale': (seo.get('locale') or '').strip() or 'en_US',
	}


# >> html generation

SAFE_CSS = re.compile(r'^[#\w(),.\s%-]+$')


def esc(value):
	return html.escape(str(value), quote=True)


def head_block(site, seo):
	e = effective_seo(site, seo)
	theme = site.get('theme') or {}
	lines = ['<!-- generated by editor.py from Config/site.json + Config/seo.json. do not edit by hand. -->']

	lines.append('<title>%s</title>' % esc(e['pageTitle']))

	if site.get('avatar'):
		lines.append('<link rel="icon" href="%s">' % esc(site['avatar']))

	if e['description']:
		lines.append('<meta name="description" content="%s">' % esc(e['description']))

	lines.append('')
	lines.append('<meta name="twitter:card" content="%s">' % esc(e['cardType']))
	lines.append('<meta name="twitter:title" content="%s">' % esc(e['title']))

	if e['description']:
		lines.append('<meta name="twitter:description" content="%s">' % esc(e['description']))

	if e['image']:
		lines.append('<meta name="twitter:image" content="%s">' % esc(e['image']))
		lines.append('<meta name="twitter:image:alt" content="%s">' % esc(e['imageAlt']))

	if e['handle']:
		lines.append('<meta name="twitter:site" content="%s">' % esc(e['handle']))
		lines.append('<meta name="twitter:creator" content="%s">' % esc(e['handle']))

	lines.append('')
	lines.append('<meta property="og:type" content="website">')
	lines.append('<meta property="og:title" content="%s">' % esc(e['title']))

	if e['description']:
		lines.append('<meta property="og:description" content="%s">' % esc(e['description']))

	if e['image']:
		lines.append('<meta property="og:image" content="%s">' % esc(e['image']))
		lines.append('<meta property="og:image:alt" content="%s">' % esc(e['imageAlt']))

	if e['url']:
		lines.append('<meta property="og:url" content="%s">' % esc(e['url']))

	lines.append('<meta property="og:site_name" content="%s">' % esc(e['siteName']))
	lines.append('<meta property="og:locale" content="%s">' % esc(e['locale']))
	lines.append('')
	lines.append('<meta name="theme-color" content="%s">' % esc(e['themeColor']))

	font = (theme.get('font') or '').strip()
	variables = []

	for variable, key in (('--bg-top', 'backgroundTop'), ('--bg-bottom', 'backgroundBottom')):
		value = str(theme.get(key) or '').strip()
		if value and SAFE_CSS.match(value):
			variables.append('%s: %s;' % (variable, value))

	try:
		variables.append('--card-alpha: %s;' % float(theme.get('cardOpacity')))
	except (TypeError, ValueError):
		pass

	if font and re.match(r'^[\w \-]+$', font):
		query = urllib.parse.quote(font).replace('%20', '+')
		lines.append('')
		lines.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
		lines.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
		lines.append('<link href="https://fonts.googleapis.com/css2?family=%s:wght@300;400;500;600;700&display=swap" rel="stylesheet">' % query)
		variables.append("--font: '%s';" % font)

	if variables:
		lines.append('<style>:root { %s }</style>' % ' '.join(variables))

	return '\n'.join(lines)


def header_block(site):
	lines = ['<!-- generated by editor.py from Config/site.json. do not edit by hand. -->']
	name = site.get('name') or ''
	role = site.get('role') or ''

	if site.get('avatar'):
		lines.append('<img class="avatar" src="%s" alt="%s"/>' % (esc(site['avatar']), esc(name)))

	lines.append('<div class="title">')
	lines.append('\t<h1>%s</h1>' % esc(name))

	if role:
		lines.append('\t<div class="role">%s</div>' % esc(role))

	lines.append('</div>')
	return '\n'.join(lines)


def inject(document, key, block, indent):
	pattern = re.compile(r'(<!-- CONFIG:%s:START -->).*?(<!-- CONFIG:%s:END -->)' % (key, key), re.S)
	match = pattern.search(document)

	if not match:
		raise ConfigError('index.html is missing the "CONFIG:%s" markers, so it cannot be updated.' % key)

	body = '\n'.join((indent + line) if line else '' for line in block.split('\n'))
	replacement = '%s\n%s\n%s%s' % (match.group(1), body, indent, match.group(2))

	return document[:match.start()] + replacement + document[match.end():]


# >> project (everything on disk, held in memory while editing)

class Project:
	def __init__(self):
		self.load()

	def load(self):
		self.site = merge(DEFAULT_SITE, read_json(os.path.join(CONFIG_DIR, 'site.json'), {}))
		self.seo = merge(DEFAULT_SEO, read_json(os.path.join(CONFIG_DIR, 'seo.json'), {}))

		tabs = read_json(os.path.join(CONFIG_DIR, 'tabs.json'), None)
		self.tabs = [merge({'title': '', 'hash': None, 'enabled': True}, tab) for tab in (tabs if isinstance(tabs, list) else copy.deepcopy(DEFAULT_TABS)) if isinstance(tab, dict) and tab.get('id')]
		self.contact = [merge({'label': '', 'url': '', 'icon': 'link'}, c) for c in read_json(os.path.join(CONFIG_DIR, 'contact.json'), []) if isinstance(c, dict)]

		self.pages = {}

		for tab in self.tabs:
			if tab.get('type') == 'page':
				self.page(tab['id'])

		self.pending_work_deletes = []
		self.pending_review_deletes = []
		self.work = self._work_from_manifest()
		self.rescan_work()
		self.reviews = self._reviews_from_manifest()
		self.rescan_reviews()

	# pages

	def page(self, tab_id):
		if tab_id not in self.pages:
			data = read_json(os.path.join(PAGES_DIR, tab_id + '.json'), {'sections': []})
			sections = []

			for section in data.get('sections', []):
				text = section.get('text', [])
				sections.append({
					'heading': section.get('heading', ''),
					'text': [text] if isinstance(text, str) else list(text),
					'items': list(section.get('items', [])),
					'badge': section.get('badge', ''),
				})

			self.pages[tab_id] = {'sections': sections}

		return self.pages[tab_id]

	# work

	def _work_from_manifest(self):
		entries = []

		for entry in read_json(os.path.join(WORK_DIR, 'index.json'), []):
			if isinstance(entry, str):
				entry = {'name': entry}

			if isinstance(entry, dict) and entry.get('name'):
				entries.append({'name': entry['name'], 'title': entry.get('title', '')})

		return entries

	def rescan_work(self):
		"""keeps the current order and titles, drops missing files, appends new ones."""
		os.makedirs(WORK_DIR, exist_ok=True)
		on_disk = {n for n in os.listdir(WORK_DIR) if n.lower().endswith(MEDIA_EXTENSIONS) and os.path.isfile(os.path.join(WORK_DIR, n))}
		pending = set(self.pending_work_deletes)
		self.work = [e for e in self.work if e['name'] in on_disk and e['name'] not in pending]
		known = {e['name'] for e in self.work}

		for name in sorted(on_disk - known - pending, key=natural_key):
			self.work.append({'name': name, 'title': ''})

	# reviews

	def _load_review(self, folder):
		data = read_json(os.path.join(REVIEWS_DIR, folder, 'index.json'), {})
		return {
			'folder': folder,
			'new': False,
			'pfp_src': None,
			'proof_src': None,
			'data': merge({'name': folder, 'text': '', 'pfp': '', 'proof': ''}, data),
		}

	def _reviews_from_manifest(self):
		reviews = []

		for entry in read_json(os.path.join(REVIEWS_DIR, 'index.json'), []):
			name = entry if isinstance(entry, str) else (entry.get('name') if isinstance(entry, dict) else None)

			if name and os.path.isdir(os.path.join(REVIEWS_DIR, name)):
				reviews.append(self._load_review(name))

		return reviews

	def rescan_reviews(self):
		os.makedirs(REVIEWS_DIR, exist_ok=True)
		on_disk = {n for n in os.listdir(REVIEWS_DIR) if os.path.isdir(os.path.join(REVIEWS_DIR, n)) and not n.startswith('.')}
		pending = set(self.pending_review_deletes)
		self.reviews = [r for r in self.reviews if r['new'] or (r['folder'] in on_disk and r['folder'] not in pending)]
		known = {r['folder'] for r in self.reviews if not r['new']}

		for folder in sorted(on_disk - known - pending, key=natural_key):
			self.reviews.append(self._load_review(folder))

	# saving

	def pending_description(self):
		lines = ['Work/' + name for name in self.pending_work_deletes]
		lines += ['Reviews/' + name + '/ (whole folder)' for name in self.pending_review_deletes]
		return lines

	def save_configs(self):
		write_json(os.path.join(CONFIG_DIR, 'site.json'), self.site)
		write_json(os.path.join(CONFIG_DIR, 'seo.json'), self.seo)

		tabs = []

		for tab in self.tabs:
			out = dict(tab)
			if out.get('hash') is None:
				out.pop('hash', None)
			tabs.append(out)

		write_json(os.path.join(CONFIG_DIR, 'tabs.json'), tabs)
		write_json(os.path.join(CONFIG_DIR, 'contact.json'), self.contact)

		for tab in self.tabs:
			if tab.get('type') != 'page':
				continue

			sections = []

			for section in self.page(tab['id'])['sections']:
				out = {'heading': section['heading']}
				if section['text']:
					out['text'] = section['text']
				if section['items']:
					out['items'] = section['items']
				if section['badge']:
					out['badge'] = section['badge']
				sections.append(out)

			write_json(os.path.join(PAGES_DIR, tab['id'] + '.json'), {'sections': sections})

	def _safe_remove(self, base, name, is_folder):
		target = os.path.abspath(os.path.join(base, name))

		if os.path.dirname(target) != os.path.abspath(base) or not name or name.startswith('.'):
			return

		if is_folder and os.path.isdir(target):
			shutil.rmtree(target)
		elif not is_folder and os.path.isfile(target):
			os.remove(target)

	def save_work(self):
		for name in self.pending_work_deletes:
			self._safe_remove(WORK_DIR, name, False)

		self.pending_work_deletes = []
		self.build_work_index()

	def build_work_index(self):
		entries = []

		for entry in self.work:
			out = {'name': entry['name']}
			if entry.get('title'):
				out['title'] = entry['title']
			entries.append(out)

		write_json(os.path.join(WORK_DIR, 'index.json'), entries)

	def save_reviews(self):
		for name in self.pending_review_deletes:
			self._safe_remove(REVIEWS_DIR, name, True)

		self.pending_review_deletes = []
		taken = {n.lower() for n in os.listdir(REVIEWS_DIR)} if os.path.isdir(REVIEWS_DIR) else set()

		for review in self.reviews:
			if review['new']:
				base = slugify(review['data'].get('name') or 'review')
				folder = base
				number = 2

				while folder.lower() in taken:
					folder = '%s-%d' % (base, number)
					number += 1

				review['folder'] = folder
				review['new'] = False
				taken.add(folder.lower())

			directory = os.path.join(REVIEWS_DIR, review['folder'])
			os.makedirs(directory, exist_ok=True)

			for key in ('pfp', 'proof'):
				source = review.get(key + '_src')

				if source and os.path.isfile(source):
					target = key + os.path.splitext(source)[1].lower()
					destination = os.path.join(directory, target)

					if os.path.abspath(source) != os.path.abspath(destination):
						shutil.copy2(source, destination)

					review['data'][key] = target

				review[key + '_src'] = None

			data = review['data']
			ordered = {'pfp': data.get('pfp', ''), 'name': data.get('name', ''), 'text': data.get('text', '')}

			if data.get('proof'):
				ordered['proof'] = data['proof']

			for key, value in data.items():
				if key != 'proof':
					ordered.setdefault(key, value)

			write_json(os.path.join(directory, 'index.json'), ordered)

		self.build_reviews_index()

	def build_reviews_index(self):
		write_json(os.path.join(REVIEWS_DIR, 'index.json'), [{'name': r['folder']} for r in self.reviews if not r['new']])

	def build_html(self):
		if not os.path.isfile(INDEX_HTML):
			raise ConfigError('index.html was not found next to editor.py.')

		with open(INDEX_HTML, 'r', encoding='utf-8', newline='') as handle:
			document = handle.read()

		document = inject(document, 'HEAD', head_block(self.site, self.seo), '\t')
		document = inject(document, 'HEADER', header_block(self.site), '\t\t\t')

		with open(INDEX_HTML, 'w', encoding='utf-8', newline='') as handle:
			handle.write(document)

	def save_all(self):
		self.save_configs()
		self.save_work()
		self.save_reviews()
		self.build_html()

	def check(self):
		"""returns a list of (level, message). level is 'error', 'warn' or 'ok'."""
		problems = []
		e = effective_seo(self.site, self.seo)

		def exists(path):
			return bool(path) and (is_url(path) or os.path.isfile(os.path.join(ROOT, path)))

		if not exists(self.site.get('avatar')):
			problems.append(('warn', 'Profile picture "%s" was not found.' % self.site.get('avatar')))

		if not e['image']:
			problems.append(('warn', 'Title card has no image, so links will not show a picture.'))
		elif not is_url(e['image']):
			problems.append(('warn', 'Title card image is a relative path. Set the Site URL so it becomes a full https:// link (Twitter needs that).'))
		elif not is_url(self.seo.get('image', '')) and not exists(self.seo.get('image')):
			problems.append(('warn', 'Title card image "%s" was not found.' % self.seo.get('image')))

		if not e['url']:
			problems.append(('warn', 'Site URL is empty (needed for the title card on Twitter / Discord once the site is online).'))

		if not e['description']:
			problems.append(('warn', 'Title card description is empty.'))
		elif len(e['description']) > 200:
			problems.append(('warn', 'Description is %d characters. Twitter cuts it off around 200.' % len(e['description'])))

		ids = [t['id'] for t in self.tabs]

		for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
			problems.append(('error', 'Two tabs share the id "%s".' % duplicate))

		if not any(t.get('enabled', True) for t in self.tabs):
			problems.append(('error', 'Every tab is disabled. The site would be empty.'))

		for entry in self.work:
			if not os.path.isfile(os.path.join(WORK_DIR, entry['name'])):
				problems.append(('error', 'Work file "%s" is missing.' % entry['name']))

		for review in self.reviews:
			label = review['data'].get('name') or review['folder']
			for key in ('pfp', 'proof'):
				value = review['data'].get(key)
				if value and not is_url(value) and not review.get(key + '_src') and not review['new'] and not os.path.isfile(os.path.join(REVIEWS_DIR, review['folder'], value)):
					problems.append(('error', 'Review "%s": %s file "%s" is missing.' % (label, key, value)))

		for contact in self.contact:
			icon = contact.get('icon') or ''
			if icon and icon not in BUILTIN_ICONS and not exists(icon):
				problems.append(('warn', 'Contact "%s": icon "%s" was not found.' % (contact.get('label'), icon)))

			if not contact.get('url'):
				problems.append(('warn', 'Contact "%s" has no link.' % contact.get('label')))

		if not problems:
			problems.append(('ok', 'Everything looks good.'))

		return problems


# >> test server

class RangeHandler(http.server.SimpleHTTPRequestHandler):
	"""static files with no caching and byte-range support (so videos can seek)."""

	protocol_version = 'HTTP/1.0'
	_range_left = None

	def end_headers(self):
		self.send_header('Cache-Control', 'no-store')
		super().end_headers()

	def log_message(self, format, *args):
		pass

	def log_request(self, code='-', size='-'):
		callback = getattr(self.server, 'log_callback', None)
		if callback:
			callback('%s %s  ->  %s' % (self.command, urllib.parse.unquote(self.path), code))

	def send_head(self):
		header = self.headers.get('Range')
		path = self.translate_path(self.path)

		if not header or not os.path.isfile(path):
			return super().send_head()

		match = re.match(r'bytes=(\d*)-(\d*)$', header.strip())

		if not match or (match.group(1) == '' and match.group(2) == ''):
			return super().send_head()

		size = os.path.getsize(path)

		if match.group(1) == '':
			start = max(0, size - int(match.group(2)))
			end = size - 1
		else:
			start = int(match.group(1))
			end = min(int(match.group(2)), size - 1) if match.group(2) else size - 1

		if start >= size or start > end:
			self.send_response(416)
			self.send_header('Content-Range', 'bytes */%d' % size)
			self.send_header('Content-Length', '0')
			self.end_headers()
			return None

		handle = open(path, 'rb')
		handle.seek(start)
		self._range_left = end - start + 1

		self.send_response(206)
		self.send_header('Content-Type', self.guess_type(path))
		self.send_header('Accept-Ranges', 'bytes')
		self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
		self.send_header('Content-Length', str(self._range_left))
		self.end_headers()

		return handle

	def copyfile(self, source, outputfile):
		try:
			if self._range_left is None:
				shutil.copyfileobj(source, outputfile)
				return

			left = self._range_left

			while left > 0:
				chunk = source.read(min(65536, left))
				if not chunk:
					break
				outputfile.write(chunk)
				left -= len(chunk)
		except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
			pass


class QuietServer(http.server.ThreadingHTTPServer):
	# on windows SO_REUSEADDR lets two programs share one port, which would hide "port already in use".
	allow_reuse_address = not sys.platform.startswith('win')
	daemon_threads = True


class SiteServer:
	def __init__(self, log=None):
		self.log = log or (lambda text: None)
		self.httpd = None
		self.thread = None
		self.port = None
		self.lan = False

	@property
	def running(self):
		return self.httpd is not None

	def start(self, port=5000, lan=False):
		if self.running:
			return self.port

		handler = functools.partial(RangeHandler, directory=ROOT)
		last_error = None

		for candidate in range(port, port + 25):
			try:
				server = QuietServer(('0.0.0.0' if lan else '127.0.0.1', candidate), handler)
			except OSError as error:
				last_error = error
				continue

			server.log_callback = self.log
			self.httpd = server
			self.port = candidate
			self.lan = lan
			self.thread = threading.Thread(target=server.serve_forever, daemon=True)
			self.thread.start()
			self.log('server started on port %d%s' % (candidate, ' (visible on your network)' if lan else ''))
			return candidate

		raise OSError('Could not open a port between %d and %d: %s' % (port, port + 24, last_error))

	def stop(self):
		if not self.httpd:
			return

		self.httpd.shutdown()
		self.httpd.server_close()
		self.httpd = None
		self.thread = None
		self.log('server stopped')

	def url(self, hash_part=''):
		return 'http://localhost:%d/%s' % (self.port, hash_part)

	def lan_url(self):
		address = lan_address()
		return 'http://%s:%d/' % (address, self.port) if address and self.lan else None


# >> preview images

class Images:
	"""loads, crops and caches preview images (local files or web urls)."""

	def __init__(self):
		self.cache = {}
		self.downloads = {}
		self.ready = queue.Queue()
		self.temp = tempfile.mkdtemp(prefix='portfolio-editor-')

	def local_path(self, ref):
		if not ref:
			return None

		if is_url(ref):
			state = self.downloads.get(ref)

			if state is None:
				self.downloads[ref] = 'pending'
				threading.Thread(target=self._download, args=(ref,), daemon=True).start()
				return None

			return state if state not in ('pending', 'failed') else None

		path = ref if os.path.isabs(ref) else os.path.join(ROOT, ref)
		return path if os.path.isfile(path) else None

	def _download(self, url):
		try:
			request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PortfolioEditor'})

			with urllib.request.urlopen(request, timeout=12) as response:
				data = response.read(15 * 1024 * 1024)

			extension = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or '.img'
			target = os.path.join(self.temp, hashlib.md5(url.encode()).hexdigest() + extension)

			with open(target, 'wb') as handle:
				handle.write(data)

			self.downloads[url] = target
		except Exception:
			self.downloads[url] = 'failed'

		self.ready.put(url)

	def get(self, ref, width, height, mode='contain', corners=None, radius=0):
		"""mode: contain | cover | circle. corners: None | all | top."""
		path = self.local_path(ref)

		if not path or width < 1 or height < 1:
			return None

		try:
			key = (path, os.path.getmtime(path), width, height, mode, corners, radius)
		except OSError:
			return None

		if key not in self.cache:
			try:
				self.cache[key] = self._make(path, width, height, mode, corners, radius)
			except Exception:
				self.cache[key] = None

		return self.cache[key]

	def _make(self, path, width, height, mode, corners, radius):
		if not HAVE_PIL:
			image = tk.PhotoImage(file=path)
			factor = max(1, int(max(image.width() / width, image.height() / height) + 0.999))
			return image.subsample(factor) if factor > 1 else image

		image = Image.open(path)
		image.seek(0)
		image = image.convert('RGBA')
		resample = Image.Resampling.LANCZOS

		if mode in ('cover', 'circle'):
			scale = max(width / image.width, height / image.height)
			resized = image.resize((max(width, round(image.width * scale)), max(height, round(image.height * scale))), resample)
			left = (resized.width - width) // 2
			top = (resized.height - height) // 2
			image = resized.crop((left, top, left + width, top + height))
		else:
			scale = min(width / image.width, height / image.height)
			image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), resample)

		w, h = image.size
		mask = None

		if mode == 'circle':
			mask = Image.new('L', (w * 4, h * 4), 0)
			ImageDraw.Draw(mask).ellipse((0, 0, w * 4 - 1, h * 4 - 1), fill=255)
		elif corners and radius:
			mask = Image.new('L', (w * 4, h * 4), 0)
			extra = radius * 4 if corners == 'top' else 0
			ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1 + extra), radius * 4, fill=255)

		if mask is not None:
			mask = mask.resize((w, h), resample)
			image.putalpha(ImageChops.multiply(image.getchannel('A'), mask))

		return ImageTk.PhotoImage(image)


# >> ui helpers

def rounded_rect(canvas, x1, y1, x2, y2, radius, **options):
	radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
	points = [
		x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
		x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
		x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
	]
	return canvas.create_polygon(points, smooth=True, **options)


def clamp_lines(text, font, width, max_lines):
	words = text.split()
	lines = []
	current = ''

	for word in words:
		trial = (current + ' ' + word).strip()

		if font.measure(trial) <= width or not current:
			current = trial
		else:
			lines.append(current)
			current = word

	if current:
		lines.append(current)

	if len(lines) > max_lines:
		lines = lines[:max_lines]
		last = lines[-1]

		while last and font.measure(last + '…') > width:
			last = last[:-1]

		lines[-1] = last.rstrip() + '…'

	return '\n'.join(lines)


def put_text(canvas, x, y, text, font, fill, width, max_lines=None):
	"""draws wrapped text, returns the y position below it."""
	if not text:
		return y

	if max_lines:
		text = clamp_lines(text, font, width, max_lines)

	item = canvas.create_text(x, y, text=text, font=font, fill=fill, anchor='nw', width=width)
	box = canvas.bbox(item)
	return box[3] if box else y


def move_item(items, index, delta):
	"""moves items[index] by delta. returns the new index, or None."""
	target = index + delta

	if index is None or target < 0 or target >= len(items):
		return None

	items[index], items[target] = items[target], items[index]
	return target


def ask_form(parent, title, fields):
	"""small modal form. fields: [(key, label, default, values_or_None)]. returns dict or None."""
	dialog = tk.Toplevel(parent)
	dialog.title(title)
	dialog.transient(parent)
	dialog.resizable(False, False)
	body = ttk.Frame(dialog, padding=16)
	body.pack(fill='both', expand=True)
	variables = {}
	first = None

	for row, (key, label, default, values) in enumerate(fields):
		ttk.Label(body, text=label).grid(row=row, column=0, sticky='w', padx=(0, 10), pady=5)
		variables[key] = tk.StringVar(value=default)

		if values:
			widget = ttk.Combobox(body, textvariable=variables[key], values=values, state='readonly', width=34)
		else:
			widget = ttk.Entry(body, textvariable=variables[key], width=36)

		widget.grid(row=row, column=1, sticky='ew', pady=5)
		first = first or widget

	result = {}

	def accept(event=None):
		result.update({key: var.get().strip() for key, var in variables.items()})
		dialog.destroy()

	buttons = ttk.Frame(body)
	buttons.grid(row=len(fields), column=0, columnspan=2, sticky='e', pady=(12, 0))
	ttk.Button(buttons, text='Cancel', command=dialog.destroy).pack(side='right', padx=(8, 0))
	ttk.Button(buttons, text='OK', command=accept).pack(side='right')
	dialog.bind('<Return>', accept)
	dialog.bind('<Escape>', lambda event: dialog.destroy())
	dialog.update_idletasks()
	x = parent.winfo_rootx() + (parent.winfo_width() - dialog.winfo_width()) // 2
	y = parent.winfo_rooty() + (parent.winfo_height() - dialog.winfo_height()) // 3
	dialog.geometry('+%d+%d' % (max(x, 0), max(y, 0)))
	dialog.grab_set()
	first.focus_set()
	parent.wait_window(dialog)

	return result or None


class ListPanel(ttk.Frame):
	"""a listbox with add / remove / move buttons."""

	def __init__(self, parent, on_select, on_add, on_remove, on_move, width=26, add_text='Add', height=14):
		super().__init__(parent)
		self.on_select = on_select
		self.listbox = tk.Listbox(self, width=width, height=height, exportselection=False, activestyle='none', borderwidth=1, relief='solid', highlightthickness=0, selectbackground='#2b6cb0', selectforeground='white')
		scrollbar = ttk.Scrollbar(self, command=self.listbox.yview)
		self.listbox.config(yscrollcommand=scrollbar.set)
		self.listbox.grid(row=0, column=0, sticky='nsew')
		scrollbar.grid(row=0, column=1, sticky='ns')
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)

		buttons = ttk.Frame(self)
		buttons.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(8, 0))
		ttk.Button(buttons, text=add_text, command=on_add).pack(side='left')
		ttk.Button(buttons, text='Remove', command=on_remove).pack(side='left', padx=(6, 0))
		ttk.Button(buttons, text='▼', width=3, command=lambda: on_move(1)).pack(side='right')
		ttk.Button(buttons, text='▲', width=3, command=lambda: on_move(-1)).pack(side='right', padx=(0, 4))

		self.listbox.bind('<<ListboxSelect>>', lambda event: self.on_select(self.current()))

	def set_items(self, labels, select=None):
		self.listbox.delete(0, 'end')

		for label in labels:
			self.listbox.insert('end', label)

		if select is not None and labels:
			index = max(0, min(select, len(labels) - 1))
			self.listbox.selection_set(index)
			self.listbox.see(index)

	def current(self):
		selection = self.listbox.curselection()
		return selection[0] if selection else None


class Tab(ttk.Frame):
	"""base class: widgets edit the project live, previews redraw after every change."""

	def __init__(self, notebook, app):
		super().__init__(notebook, padding=16)
		self.app = app
		self.project = app.project
		self._loading = False

	@contextlib.contextmanager
	def loading(self):
		old = self._loading
		self._loading = True
		try:
			yield
		finally:
			self._loading = old

	def var(self, value=''):
		variable = tk.StringVar(value=value)
		variable.trace_add('write', self.changed)
		return variable

	def text_box(self, parent, height, **options):
		options.setdefault('width', 20)
		box = tk.Text(parent, height=height, wrap='word', undo=True, borderwidth=1, relief='solid', highlightthickness=0, padx=6, pady=4, font=self.app.ui_font, **options)
		box.bind('<<Modified>>', lambda event: self._text_modified(box))
		return box

	def _text_modified(self, box):
		if box.edit_modified():
			box.edit_modified(False)
			self.changed()

	def set_text(self, box, value):
		box.delete('1.0', 'end')
		box.insert('1.0', value)
		box.edit_modified(False)

	def changed(self, *args):
		if self._loading:
			return

		self.pull()
		self.app.touch()

	def load(self):
		pass

	def pull(self):
		pass

	def refresh(self):
		pass

	def activate(self):
		pass

	def pick_file(self, title, kinds):
		return filedialog.askopenfilename(parent=self, title=title, filetypes=kinds)

	def file_row(self, parent, row, label, variable, command, hint=None, clear=None):
		ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=5)
		line = ttk.Frame(parent)
		line.grid(row=row, column=1, sticky='ew', pady=5)
		ttk.Entry(line, textvariable=variable).pack(side='left', fill='x', expand=True)
		ttk.Button(line, text='Browse…', command=command).pack(side='left', padx=(6, 0))

		if clear:
			ttk.Button(line, text='Clear', command=clear).pack(side='left', padx=(4, 0))

		if hint:
			ttk.Label(parent, text=hint, foreground='#777').grid(row=row + 1, column=1, sticky='w')

	def entry_row(self, parent, row, label, variable, hint=None, width=None):
		ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=5)
		entry = ttk.Entry(parent, textvariable=variable, width=width) if width else ttk.Entry(parent, textvariable=variable)
		entry.grid(row=row, column=1, sticky='ew', pady=5)

		if hint:
			ttk.Label(parent, text=hint, foreground='#777').grid(row=row + 1, column=1, sticky='w')

		return entry

	def color_row(self, parent, row, label, variable):
		ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=5)
		line = ttk.Frame(parent)
		line.grid(row=row, column=1, sticky='ew', pady=5)
		ttk.Entry(line, textvariable=variable, width=12).pack(side='left')
		swatch = tk.Label(line, width=4, relief='solid', borderwidth=1, cursor='hand2')
		swatch.pack(side='left', padx=(8, 0))

		def pick(event=None):
			chosen = colorchooser.askcolor(color=variable.get() or '#ffffff', parent=self, title=label)[1]
			if chosen:
				variable.set(chosen)

		def recolor(*args):
			try:
				swatch.config(bg=hex_color(to_rgb(self, variable.get())))
			except tk.TclError:
				pass

		swatch.bind('<Button-1>', pick)
		ttk.Button(line, text='Pick…', command=pick).pack(side='left', padx=(8, 0))
		variable.trace_add('write', recolor)
		recolor()


# >> tab: profile

class ProfileTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)

		form = ttk.Frame(self)
		form.grid(row=0, column=0, sticky='new', padx=(0, 24))
		form.columnconfigure(1, weight=1)

		self.name = self.var()
		self.role = self.var()
		self.avatar = self.var()
		self.top = self.var()
		self.bottom = self.var()
		self.alpha = tk.DoubleVar(value=0.72)
		self.alpha.trace_add('write', self.changed)
		self.font = self.var()
		self.gh_owner = self.var()
		self.gh_repo = self.var()
		self.gh_branch = self.var()

		ttk.Label(form, text='Your profile', font=app.heading_font).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))
		self.entry_row(form, 1, 'Name', self.name)
		self.entry_row(form, 2, 'Role / title', self.role)
		self.file_row(form, 3, 'Profile picture', self.avatar, self.browse_avatar, hint='A square image works best. Picking a file copies it into Assets/.')

		ttk.Separator(form).grid(row=5, column=0, columnspan=2, sticky='ew', pady=14)
		ttk.Label(form, text='Look & feel', font=app.heading_font).grid(row=6, column=0, columnspan=2, sticky='w', pady=(0, 6))
		self.color_row(form, 7, 'Background top', self.top)
		self.color_row(form, 8, 'Background bottom', self.bottom)

		ttk.Label(form, text='Card darkness').grid(row=9, column=0, sticky='w', padx=(0, 12), pady=5)
		line = ttk.Frame(form)
		line.grid(row=9, column=1, sticky='ew', pady=5)
		ttk.Scale(line, from_=0.2, to=1.0, variable=self.alpha, command=lambda value: self.alpha.set(round(float(value), 2))).pack(side='left', fill='x', expand=True)
		self.alpha_label = ttk.Label(line, width=5)
		self.alpha_label.pack(side='left', padx=(8, 0))

		self.entry_row(form, 10, 'Font', self.font, hint='Any Google Fonts name, e.g. Inter, Poppins, Roboto, Outfit.')

		ttk.Separator(form).grid(row=12, column=0, columnspan=2, sticky='ew', pady=14)
		ttk.Label(form, text='GitHub fallback (optional)', font=app.heading_font).grid(row=13, column=0, columnspan=2, sticky='w', pady=(0, 6))
		self.entry_row(form, 14, 'Owner', self.gh_owner)
		self.entry_row(form, 15, 'Repository', self.gh_repo)
		self.entry_row(form, 16, 'Branch', self.gh_branch, hint='Only used if Work/index.json or Reviews/index.json is missing online.')

		preview = ttk.Frame(self)
		preview.grid(row=0, column=1, sticky='n')
		ttk.Label(preview, text='Preview', font=app.heading_font).pack(anchor='w', pady=(0, 6))
		self.canvas = tk.Canvas(preview, width=440, height=330, highlightthickness=1, highlightbackground='#bbb')
		self.canvas.pack()
		self._photos = []

	def browse_avatar(self):
		path = self.pick_file('Choose a profile picture', [('Images', '*.png *.jpg *.jpeg *.webp *.gif'), ('All files', '*.*')])

		if path:
			self.avatar.set(self.app.import_asset(path, 'Assets'))

	def load(self):
		site = self.project.site
		theme = site['theme']

		with self.loading():
			self.name.set(site['name'])
			self.role.set(site['role'])
			self.avatar.set(site['avatar'])
			self.top.set(theme['backgroundTop'])
			self.bottom.set(theme['backgroundBottom'])
			self.alpha.set(float(theme['cardOpacity']))
			self.font.set(theme['font'])
			self.gh_owner.set(site['github']['owner'])
			self.gh_repo.set(site['github']['repo'])
			self.gh_branch.set(site['github']['branch'])

		self.refresh()

	def pull(self):
		site = self.project.site
		site['name'] = self.name.get()
		site['role'] = self.role.get()
		site['avatar'] = self.avatar.get().strip()
		site['theme'].update(
			backgroundTop=self.top.get().strip(),
			backgroundBottom=self.bottom.get().strip(),
			cardOpacity=round(float(self.alpha.get() or 0), 2),
			font=self.font.get().strip(),
		)
		site['github'] = {'owner': self.gh_owner.get().strip(), 'repo': self.gh_repo.get().strip(), 'branch': self.gh_branch.get().strip() or 'main'}

	def refresh(self):
		self.alpha_label.config(text='%d%%' % round(float(self.alpha.get() or 0) * 100))
		site = self.project.site
		canvas = self.canvas
		canvas.delete('all')
		self._photos = []
		width, height = 440, 330
		top = to_rgb(self, site['theme']['backgroundTop'])
		bottom = to_rgb(self, site['theme']['backgroundBottom'])
		alpha = float(site['theme']['cardOpacity'] or 0)
		card = (24, 24, width - 24, height - 24)

		radius = 18

		for y in range(height):
			t = y / (height - 1)
			color = [top[i] + (bottom[i] - top[i]) * t for i in range(3)]
			canvas.create_line(0, y, width, y, fill=hex_color(color))

			if card[1] <= y <= card[3]:
				edge = min(y - card[1], card[3] - y)
				inset = radius - (radius ** 2 - (radius - edge) ** 2) ** 0.5 if edge < radius else 0
				shade = [c * (1 - alpha) for c in color]
				canvas.create_line(card[0] + inset, y, card[2] - inset, y, fill=hex_color(shade))

		avatar =self.app.images.get(site['avatar'], 76, 76, mode='circle')
		cx = width / 2
		name_font = tkfont.Font(family=self.app.family, size=22, weight='bold')
		role_font = tkfont.Font(family=self.app.family, size=8)
		name = site['name'] or 'Your Name'
		role = (site['role'] or '').upper()
		block = 76 + 18 + name_font.measure(name) if avatar else name_font.measure(name)
		x = cx - max(block, role_font.measure(role) + (94 if avatar else 0)) / 2
		y = 62

		if avatar:
			self._photos.append(avatar)
			canvas.create_image(x, y, image=avatar, anchor='nw')
			text_x = x + 94
		else:
			canvas.create_oval(x, y, x + 76, y + 76, outline='#ffffff', fill='#4a1010')
			text_x = x + 94

		canvas.create_text(text_x, y + 22, text=name, anchor='w', fill='white', font=name_font)
		canvas.create_text(text_x, y + 50, text=role, anchor='w', fill='#b5a5a5', font=role_font)

		tabs = [t['label'] for t in self.project.tabs if t.get('enabled', True)][:6]
		pill_font = tkfont.Font(family=self.app.family, size=7)
		padding = 22

		while padding > 6 and sum(pill_font.measure(label) + padding + 4 for label in tabs) > card[2] - card[0] - 30:
			padding -= 2

		total = sum(pill_font.measure(label) + padding + 4 for label in tabs)
		px = cx - total / 2
		py = 176

		for index, label in enumerate(tabs):
			w = pill_font.measure(label) + padding
			rounded_rect(canvas, px, py, px + w, py + 26, 7, fill='#3a2a2a' if index == 0 else '', outline='')
			canvas.create_text(px + w / 2, py + 13, text=label, fill='white' if index == 0 else '#a89a9a', font=pill_font)
			px += w + 4

		canvas.create_line(card[0] + 30, 230, card[2] - 30, 230, fill='#3a2c2c')
		small = tkfont.Font(family=self.app.family, size=9)
		canvas.create_text(cx, 262, text='About me · strengths · coding practices…', fill='#8c7f7f', font=small)


# >> tab: title card

class TitleCardTab(Tab):
	FIELDS = [
		('pageTitle', 'Browser tab title', 'Shown on the browser tab.'),
		('title', 'Card title', 'The big title in the link preview.'),
		('imageAlt', 'Image description', 'Alt text for the card image.'),
		('url', 'Site URL', 'Where the site will live, e.g. https://you.github.io/'),
		('siteName', 'Site name', 'Small label above the title on Discord.'),
		('twitterHandle', 'Twitter / X handle', 'e.g. @yourname'),
	]

	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.columnconfigure(0, weight=1)
		self.vars = {}
		self.hints = {}

		form = ttk.Frame(self)
		form.grid(row=0, column=0, sticky='new', padx=(0, 24))
		form.columnconfigure(1, weight=1)
		row = 0
		ttk.Label(form, text='Link preview (title card)', font=app.heading_font).grid(row=row, column=0, columnspan=2, sticky='w')
		row += 1
		ttk.Label(form, text='This is what Twitter / X, Discord and others show when your link is posted. Leave a field blank to fill it in automatically.', foreground='#777', wraplength=420, justify='left').grid(row=row, column=0, columnspan=2, sticky='w', pady=(2, 10))
		row += 1

		for key, label, hint in self.FIELDS[:2]:
			self.vars[key] = self.var()
			self.entry_row(form, row, label, self.vars[key])
			self.hints[key] = ttk.Label(form, foreground='#777')
			self.hints[key].grid(row=row + 1, column=1, sticky='w')
			row += 2

		ttk.Label(form, text='Description').grid(row=row, column=0, sticky='nw', padx=(0, 12), pady=5)
		self.description = self.text_box(form, 4)
		self.description.grid(row=row, column=1, sticky='ew', pady=5)
		self.counter = ttk.Label(form, foreground='#777')
		self.counter.grid(row=row + 1, column=1, sticky='w')
		row += 2

		self.vars['image'] = self.var()
		self.file_row(form, row, 'Image', self.vars['image'], self.browse_image, hint='Best size 1200 x 630 (2:1). Pick a file, or paste a full https:// link.')
		row += 2

		for key, label, hint in self.FIELDS[2:]:
			self.vars[key] = self.var()
			self.entry_row(form, row, label, self.vars[key])
			self.hints[key] = ttk.Label(form, text=hint, foreground='#777')
			self.hints[key].grid(row=row + 1, column=1, sticky='w')
			row += 2

		self.vars['cardType'] = self.var()
		ttk.Label(form, text='Card style').grid(row=row, column=0, sticky='w', padx=(0, 12), pady=5)
		ttk.Combobox(form, textvariable=self.vars['cardType'], values=('summary_large_image', 'summary'), state='readonly').grid(row=row, column=1, sticky='ew', pady=5)
		row += 1

		self.vars['themeColor'] = self.var()
		self.color_row(form, row, 'Accent colour', self.vars['themeColor'])
		self.hints['themeColor'] = ttk.Label(form, foreground='#777')
		self.hints['themeColor'].grid(row=row + 1, column=1, sticky='w')
		row += 2

		self.vars['locale'] = self.var()
		self.entry_row(form, row, 'Locale', self.vars['locale'], width=12)

		side = ttk.Frame(self)
		side.grid(row=0, column=1, sticky='n')
		bar = ttk.Frame(side)
		bar.pack(anchor='w', pady=(0, 6))
		ttk.Label(bar, text='Preview', font=app.heading_font).pack(side='left', padx=(0, 16))
		self.mode = tk.StringVar(value='x')
		self.mode.trace_add('write', lambda *args: self.refresh())

		for value, text in (('x', 'X / Twitter'), ('classic', 'Twitter (classic)'), ('discord', 'Discord')):
			ttk.Radiobutton(bar, text=text, value=value, variable=self.mode).pack(side='left', padx=(0, 10))

		self.canvas = tk.Canvas(side, width=520, height=540, highlightthickness=1, highlightbackground='#bbb')
		self.canvas.pack()
		self.note = ttk.Label(side, foreground='#777', wraplength=520, justify='left')
		self.note.pack(anchor='w', pady=(8, 0))
		self._photos = []

		fonts = {
			'title': dict(size=11, weight='bold'),
			'body': dict(size=10),
			'small': dict(size=9),
		}
		self.fonts = {key: tkfont.Font(family=app.family, **value) for key, value in fonts.items()}

	def browse_image(self):
		path = self.pick_file('Choose the card image', [('Images', '*.png *.jpg *.jpeg *.webp *.gif'), ('All files', '*.*')])

		if path:
			self.vars['image'].set(self.app.import_asset(path, 'Assets'))

	def load(self):
		with self.loading():
			for key, variable in self.vars.items():
				variable.set(self.project.seo.get(key, ''))

			self.set_text(self.description, self.project.seo.get('description', ''))

		self.refresh()

	def pull(self):
		seo = self.project.seo

		for key, variable in self.vars.items():
			seo[key] = variable.get().strip()

		seo['description'] = self.description.get('1.0', 'end').strip().replace('\n', ' ')

	def image_ref(self, effective):
		raw = effective['imageRaw']

		if not raw:
			return None

		base = effective['url']

		if is_url(raw) and base:
			prefix = base if base.endswith('/') else base + '/'

			if raw.startswith(prefix):
				local = urllib.parse.unquote(raw[len(prefix):])

				if os.path.isfile(os.path.join(ROOT, local)):
					return local

		return raw

	def refresh(self):
		e = effective_seo(self.project.site, self.project.seo)
		length = len(e['description'])
		self.counter.config(text='%d characters%s' % (length, '  (Twitter cuts off around 200)' if length > 200 else ''))

		for key in ('pageTitle', 'title', 'themeColor'):
			if key in self.hints:
				blank = not self.project.seo.get(key, '').strip()
				self.hints[key].config(text=('Blank, so using: %s' % e[key]) if blank else '')

		canvas = self.canvas
		canvas.delete('all')
		self._photos = []
		mode = self.mode.get()
		ref = self.image_ref(e)
		large = e['cardType'] != 'summary'
		domain = urllib.parse.urlparse(e['url']).netloc or 'your-site.com'
		notes = []

		if not HAVE_PIL:
			notes.append('Install Pillow (pip install pillow) for exact cropping and jpg / webp previews.')

		if ref and not self.app.images.local_path(ref):
			notes.append('The image could not be loaded yet (missing file, unsupported format, or still downloading).')

		if e['image'] and not is_url(e['image']):
			notes.append('Set the Site URL: Twitter and Discord need a full https:// image link.')

		self.note.config(text='\n'.join(notes))

		if mode == 'discord':
			canvas.config(bg='#313338')
			self.draw_discord(e, ref, large)
		else:
			canvas.config(bg='#000000')
			self.draw_twitter(e, ref, large, domain, classic=(mode == 'classic'))

	def placeholder(self, x1, y1, x2, y2, fill='#16181c'):
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline='')
		self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text='no image', fill='#71767b', font=self.fonts['body'])

	def draw_twitter(self, e, ref, large, domain, classic):
		c = self.canvas
		fonts = self.fonts
		width = 480
		x0 = (520 - width) // 2
		y0 = 28

		if large:
			image_h = round(width / 1.91)
			image = self.app.images.get(ref, width - 2, image_h - 2, 'cover', 'all' if not classic else 'top', 15)
			text_h = 118 if classic else 0
			rounded_rect(c, x0, y0, x0 + width, y0 + image_h + text_h, 16, outline='#2f3336', fill='#000000')

			if image:
				self._photos.append(image)
				c.create_image(x0 + 1, y0 + 1, image=image, anchor='nw')
			else:
				self.placeholder(x0 + 2, y0 + 2, x0 + width - 2, y0 + image_h - 2)

			if classic:
				y = y0 + image_h + 10
				y = put_text(c, x0 + 14, y, domain, fonts['small'], '#71767b', width - 28, 1) + 2
				y = put_text(c, x0 + 14, y, e['title'], fonts['body'], '#e7e9ea', width - 28, 1) + 2
				put_text(c, x0 + 14, y, e['description'], fonts['body'], '#71767b', width - 28, 2)
			else:
				label = clamp_lines(e['title'], fonts['small'], width - 50, 1)
				text = c.create_text(x0 + 16, y0 + image_h - 14, text=label, anchor='sw', fill='white', font=fonts['small'])
				box = c.bbox(text)
				pill = rounded_rect(c, box[0] - 6, box[1] - 3, box[2] + 6, box[3] + 3, 5, fill='#1a1a1a', outline='')
				c.tag_lower(pill, text)
				c.create_text(x0 + 4, y0 + image_h + 16, text='From %s' % domain, anchor='w', fill='#71767b', font=fonts['small'])
		else:
			size = 125
			image = self.app.images.get(ref, size, size, 'cover', 'all', 12)
			rounded_rect(c, x0, y0, x0 + width, y0 + size + 2, 16, outline='#2f3336', fill='#000000')

			if image:
				self._photos.append(image)
				c.create_image(x0 + 1, y0 + 1, image=image, anchor='nw')
			else:
				self.placeholder(x0 + 2, y0 + 2, x0 + size, y0 + size)

			tx = x0 + size + 14
			tw = width - size - 28
			y = y0 + 14
			y = put_text(c, tx, y, domain, fonts['small'], '#71767b', tw, 1) + 2
			y = put_text(c, tx, y, e['title'], fonts['body'], '#e7e9ea', tw, 1) + 2
			put_text(c, tx, y, e['description'], fonts['body'], '#71767b', tw, 3)

	def draw_discord(self, e, ref, large):
		c = self.canvas
		fonts = self.fonts
		x0, y0 = 40, 28
		width = 440
		inner = width - 4 - 32
		y = y0 + 12
		tx = x0 + 4 + 16
		thumb = None

		if not large:
			thumb = self.app.images.get(ref, 80, 80, 'cover', 'all', 6)

		text_w = inner - (96 if not large else 0)
		y = put_text(c, tx, y, e['siteName'], fonts['small'], '#b5bac1', text_w, 1) + 4
		y = put_text(c, tx, y, e['title'], fonts['title'], '#00a8fc', text_w, 2) + 4
		bottom = put_text(c, tx, y, e['description'], fonts['body'], '#dbdee1', text_w, 4)

		if large:
			image = self.app.images.get(ref, inner, 280, 'contain', 'all', 6)
			bottom += 12

			if image:
				self._photos.append(image)
				c.create_image(tx, bottom, image=image, anchor='nw')
				bottom += image.height()
			else:
				self.placeholder(tx, bottom, tx + inner, bottom + 150, '#2b2d31')
				bottom += 150
		elif thumb:
			self._photos.append(thumb)
			c.create_image(x0 + width - 16 - 80, y0 + 12, image=thumb, anchor='nw')
			bottom = max(bottom, y0 + 12 + 80)
		else:
			self.placeholder(x0 + width - 16 - 80, y0 + 12, x0 + width - 16, y0 + 12 + 80, '#2b2d31')
			bottom = max(bottom, y0 + 12 + 80)

		bottom += 14
		card = rounded_rect(c, x0, y0, x0 + width, bottom, 6, fill='#2b2d31', outline='#1e1f22')
		bar = c.create_rectangle(x0, y0 + 2, x0 + 4, bottom - 2, fill=hex_color(to_rgb(self, e['themeColor'])), outline='')
		c.tag_lower(bar)
		c.tag_lower(card)


# >> tab: tabs

class TabsTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.sel = None
		self.columnconfigure(1, weight=1)

		self.panel = ListPanel(self, self.select, self.add, self.remove, self.move, add_text='Add tab')
		self.panel.grid(row=0, column=0, sticky='ns', padx=(0, 24))

		form = ttk.Frame(self)
		form.grid(row=0, column=1, sticky='new')
		form.columnconfigure(1, weight=1)
		ttk.Label(form, text='Site tabs', font=app.heading_font).grid(row=0, column=0, columnspan=2, sticky='w')
		ttk.Label(form, text='These are the buttons at the top of your site. The first tab is the landing page. Use ▲ ▼ to reorder.', foreground='#777', wraplength=460, justify='left').grid(row=1, column=0, columnspan=2, sticky='w', pady=(2, 10))

		self.label = self.var()
		self.type = self.var()
		self.heading = self.var()
		self.hash = self.var()
		self.enabled = tk.BooleanVar(value=True)
		self.enabled.trace_add('write', self.changed)

		self.entry_row(form, 2, 'Button text', self.label)
		ttk.Label(form, text='Kind of tab').grid(row=3, column=0, sticky='w', padx=(0, 12), pady=5)
		ttk.Combobox(form, textvariable=self.type, values=TAB_TYPES, state='readonly').grid(row=3, column=1, sticky='ew', pady=5)
		self.type_help = ttk.Label(form, foreground='#777', wraplength=420, justify='left')
		self.type_help.grid(row=4, column=1, sticky='w')
		self.entry_row(form, 5, 'Page heading', self.heading, hint='Big grey title above the content. Leave empty for none.')
		self.hash_entry = self.entry_row(form, 7, 'Web address part', self.hash, hint='yoursite.com/#this-part (lowercase, no spaces). The first tab has none.')
		ttk.Checkbutton(form, text='Show this tab on the site', variable=self.enabled).grid(row=9, column=1, sticky='w', pady=(10, 0))
		self.id_label = ttk.Label(form, foreground='#777')
		self.id_label.grid(row=10, column=1, sticky='w', pady=(4, 0))
		ttk.Button(form, text='Edit this tab’s content  →', command=self.goto_content).grid(row=11, column=1, sticky='w', pady=(14, 0))

	def labels(self):
		return [('' if t.get('enabled', True) else '(hidden) ') + t['label'] for t in self.project.tabs]

	def load(self):
		self.panel.set_items(self.labels(), self.sel if self.sel is not None else 0)
		self.select(self.panel.current())

	def select(self, index):
		self.sel = index

		with self.loading():
			tab = self.project.tabs[index] if index is not None and index < len(self.project.tabs) else None
			self.label.set(tab['label'] if tab else '')
			self.type.set(tab['type'] if tab else '')
			self.heading.set(tab['title'] if tab else '')
			self.hash.set((tab['hash'] if tab['hash'] is not None else tab['id']) if tab else '')
			self.enabled.set(tab.get('enabled', True) if tab else False)
			self.id_label.config(text=('Internal id: %s' % tab['id']) if tab else '')
			self.type_help.config(text=TAB_TYPE_HELP.get(tab['type'], '') if tab else '')
			self.hash_entry.config(state='disabled' if index == 0 else 'normal')

	def pull(self):
		if self.sel is None or self.sel >= len(self.project.tabs):
			return

		tab = self.project.tabs[self.sel]
		tab['label'] = self.label.get()
		tab['type'] = self.type.get() or 'page'
		tab['title'] = self.heading.get()
		tab['hash'] = (re.sub(r'[^a-z0-9_-]', '', self.hash.get().lower().lstrip('#')) or tab['id']) if self.sel != 0 else ''
		tab['enabled'] = bool(self.enabled.get())
		self.type_help.config(text=TAB_TYPE_HELP.get(tab['type'], ''))

		if tab['type'] == 'page':
			self.project.page(tab['id'])

		self.panel.listbox.delete(self.sel)
		self.panel.listbox.insert(self.sel, self.labels()[self.sel])
		self.panel.listbox.selection_set(self.sel)

	def add(self):
		answer = ask_form(self, 'Add a tab', [
			('label', 'Button text', 'New Tab', None),
			('type', 'Kind of tab', 'page', TAB_TYPES),
		])

		if not answer or not answer['label']:
			return

		base = slugify(answer['label'])
		ids = {t['id'] for t in self.project.tabs}
		tab_id = base
		number = 2

		while tab_id in ids:
			tab_id = '%s-%d' % (base, number)
			number += 1

		tab = {'id': tab_id, 'label': answer['label'], 'type': answer['type'] or 'page', 'title': answer['label'], 'hash': tab_id, 'enabled': True}
		self.project.tabs.append(tab)

		if tab['type'] == 'page':
			self.project.pages[tab_id] = {'sections': [{'heading': 'Heading', 'text': ['Write something here.'], 'items': [], 'badge': ''}]}

		self.sel = len(self.project.tabs) - 1
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.sel)
		self.app.touch()
		self.app.tab_list_changed()

	def remove(self):
		index = self.panel.current()

		if index is None:
			return

		tab = self.project.tabs[index]

		if not messagebox.askyesno('Remove tab', 'Remove the "%s" tab from the site?\n\nIts content files are not deleted, so you can add it back later.' % tab['label'], parent=self):
			return

		del self.project.tabs[index]
		self.sel = min(index, len(self.project.tabs) - 1) if self.project.tabs else None
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.panel.current())
		self.app.touch()
		self.app.tab_list_changed()

	def move(self, delta):
		index = self.panel.current()
		target = move_item(self.project.tabs, index, delta)

		if target is None:
			return

		self.sel = target
		self.panel.set_items(self.labels(), target)
		self.select(target)
		self.app.touch()
		self.app.tab_list_changed()

	def goto_content(self):
		if self.sel is None:
			return

		self.app.open_content_for(self.project.tabs[self.sel])

	def refresh(self):
		pass


# >> tab: pages

class PagesTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.tab_index = 0
		self.sel = None
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(1, weight=1)

		top = ttk.Frame(self)
		top.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 10))
		ttk.Label(top, text='Page:', font=app.heading_font).pack(side='left')
		self.page_choice = tk.StringVar()
		self.page_combo = ttk.Combobox(top, textvariable=self.page_choice, state='readonly', width=30)
		self.page_combo.pack(side='left', padx=8)
		self.page_combo.bind('<<ComboboxSelected>>', lambda event: self.choose_page())
		ttk.Label(top, text='Tip: **bold** makes bold text, [words](https://link) makes a link.', foreground='#777').pack(side='left', padx=12)

		self.panel = ListPanel(self, self.select, self.add, self.remove, self.move, add_text='Add section', width=24)
		self.panel.grid(row=1, column=0, sticky='ns', padx=(0, 18))

		form = ttk.Frame(self)
		form.grid(row=1, column=1, sticky='nsew', padx=(0, 18))
		form.columnconfigure(0, weight=1)
		self.heading = self.var()
		self.badge = self.var()
		ttk.Label(form, text='Section heading').grid(row=0, column=0, sticky='w')
		ttk.Entry(form, textvariable=self.heading).grid(row=1, column=0, sticky='ew', pady=(2, 10))
		ttk.Label(form, text='Paragraphs (leave a blank line between paragraphs)').grid(row=2, column=0, sticky='w')
		self.paragraphs = self.text_box(form, 7)
		self.paragraphs.grid(row=3, column=0, sticky='nsew', pady=(2, 10))
		ttk.Label(form, text='Bullet points (one per line)').grid(row=4, column=0, sticky='w')
		self.items = self.text_box(form, 8)
		self.items.grid(row=5, column=0, sticky='nsew', pady=(2, 10))
		ttk.Label(form, text='Highlight box (e.g. working hours, optional)').grid(row=6, column=0, sticky='w')
		ttk.Entry(form, textvariable=self.badge).grid(row=7, column=0, sticky='ew', pady=(2, 0))
		form.rowconfigure(3, weight=1)
		form.rowconfigure(5, weight=2)

		side = ttk.Frame(self)
		side.grid(row=1, column=2, sticky='nsew')
		side.rowconfigure(1, weight=1)
		side.columnconfigure(0, weight=1)
		ttk.Label(side, text='Preview', font=app.heading_font).grid(row=0, column=0, sticky='w', pady=(0, 6))
		self.preview = tk.Text(side, width=48, wrap='word', bg='#161212', fg='#a1a1aa', borderwidth=0, padx=16, pady=12, state='disabled', cursor='arrow', font=(app.family, 10))
		self.preview.grid(row=1, column=0, sticky='nsew')
		scroll = ttk.Scrollbar(side, command=self.preview.yview)
		scroll.grid(row=1, column=1, sticky='ns')
		self.preview.config(yscrollcommand=scroll.set)
		self.preview.tag_config('h2', foreground='#f4f4f5', font=(app.family, 11, 'bold'), spacing1=14, spacing3=4)
		self.preview.tag_config('b', foreground='#e4e4e7', font=(app.family, 10, 'bold'))
		self.preview.tag_config('a', foreground='#ffffff', underline=True)
		self.preview.tag_config('li', lmargin1=4, lmargin2=18, spacing1=2)
		self.preview.tag_config('p', spacing1=2, spacing3=4)
		self.preview.tag_config('badge', background='#26262a', foreground='#d4d4d8', lmargin1=6, spacing1=4)

	def page_tabs(self):
		return [t for t in self.project.tabs if t.get('type') == 'page']

	def current_page(self):
		tabs = self.page_tabs()

		if not tabs:
			return None

		return self.project.page(tabs[min(self.tab_index, len(tabs) - 1)]['id'])

	def load(self):
		tabs = self.page_tabs()
		self.page_combo.config(values=['%s   (%s)' % (t['label'], t['id']) for t in tabs])
		self.tab_index = min(self.tab_index, max(len(tabs) - 1, 0))

		if tabs:
			self.page_choice.set('%s   (%s)' % (tabs[self.tab_index]['label'], tabs[self.tab_index]['id']))
		else:
			self.page_choice.set('')

		self.sel = 0
		self.fill_list()
		self.select(self.panel.current())

	def choose_page(self):
		self.tab_index = self.page_combo.current()
		self.sel = 0
		self.fill_list()
		self.select(self.panel.current())

	def open_tab(self, tab_id):
		for index, tab in enumerate(self.page_tabs()):
			if tab['id'] == tab_id:
				self.tab_index = index
				self.load()
				return

	def sections(self):
		page = self.current_page()
		return page['sections'] if page else []

	def fill_list(self):
		self.panel.set_items([s['heading'] or '(no heading)' for s in self.sections()], self.sel)

	def select(self, index):
		self.sel = index
		sections = self.sections()

		with self.loading():
			section = sections[index] if index is not None and index < len(sections) else None
			self.heading.set(section['heading'] if section else '')
			self.set_text(self.paragraphs, '\n\n'.join(section['text']) if section else '')
			self.set_text(self.items, '\n'.join(section['items']) if section else '')
			self.badge.set(section['badge'] if section else '')

		self.refresh()

	def pull(self):
		sections = self.sections()

		if self.sel is None or self.sel >= len(sections):
			return

		section = sections[self.sel]
		section['heading'] = self.heading.get().strip()
		section['text'] = [' '.join(p.split()) for p in re.split(r'\n\s*\n', self.paragraphs.get('1.0', 'end').strip()) if p.strip()]
		section['items'] = [line.strip() for line in self.items.get('1.0', 'end').splitlines() if line.strip()]
		section['badge'] = self.badge.get().strip()
		self.panel.listbox.delete(self.sel)
		self.panel.listbox.insert(self.sel, section['heading'] or '(no heading)')
		self.panel.listbox.selection_set(self.sel)

	def add(self):
		sections = self.sections()

		if self.current_page() is None:
			return

		sections.append({'heading': 'New section', 'text': [], 'items': [], 'badge': ''})
		self.sel = len(sections) - 1
		self.fill_list()
		self.select(self.sel)
		self.app.touch()

	def remove(self):
		index = self.panel.current()
		sections = self.sections()

		if index is None:
			return

		if not messagebox.askyesno('Remove section', 'Remove the section "%s"?' % (sections[index]['heading'] or 'no heading'), parent=self):
			return

		del sections[index]
		self.sel = min(index, len(sections) - 1) if sections else None
		self.fill_list()
		self.select(self.panel.current())
		self.app.touch()

	def move(self, delta):
		target = move_item(self.sections(), self.panel.current(), delta)

		if target is None:
			return

		self.sel = target
		self.fill_list()
		self.select(target)
		self.app.touch()

	def render_rich(self, text, tags):
		position = 0

		for match in re.finditer(r'\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)', text):
			self.preview.insert('end', text[position:match.start()], tags)

			if match.group(1):
				self.preview.insert('end', match.group(1), tags + ('b',))
			else:
				self.preview.insert('end', match.group(2), tags + ('a',))

			position = match.end()

		self.preview.insert('end', text[position:], tags)

	def refresh(self):
		preview = self.preview
		preview.config(state='normal')
		preview.delete('1.0', 'end')

		for section in self.sections():
			if section['heading']:
				preview.insert('end', section['heading'] + '\n', ('h2',))

			for paragraph in section['text']:
				self.render_rich(paragraph, ('p',))
				preview.insert('end', '\n', ('p',))

			for item in section['items']:
				preview.insert('end', '•  ', ('li',))
				self.render_rich(item, ('li',))
				preview.insert('end', '\n', ('li',))

			if section['badge']:
				preview.insert('end', ' %s ' % section['badge'], ('badge',))
				preview.insert('end', '\n')

		preview.config(state='disabled')


# >> tab: work

class WorkTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.sel = None
		self._photo = None
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)

		self.panel = ListPanel(self, self.select, self.add, self.remove, self.move, add_text='Add files…', width=30)
		self.panel.grid(row=0, column=0, sticky='ns', padx=(0, 24))

		side = ttk.Frame(self)
		side.grid(row=0, column=1, sticky='nsew')
		side.columnconfigure(1, weight=1)
		ttk.Label(side, text='Proof of work', font=app.heading_font).grid(row=0, column=0, columnspan=2, sticky='w')
		ttk.Label(side, text='Everything in the Work folder shows up on the site (images and videos). Add files here or just drop them into the folder, then press Save & Build.', foreground='#777', wraplength=520, justify='left').grid(row=1, column=0, columnspan=2, sticky='w', pady=(2, 10))
		self.title_var = self.var()
		self.entry_row(side, 2, 'Caption', self.title_var, hint='Blank = use the file name.')
		self.file_label = ttk.Label(side, foreground='#777')
		self.file_label.grid(row=4, column=1, sticky='w', pady=(4, 8))
		self.preview = ttk.Label(side, anchor='center', relief='solid', borderwidth=1, background='#0b0b0b', foreground='#aaa')
		self.preview.grid(row=5, column=0, columnspan=2, sticky='nsew')
		side.rowconfigure(5, weight=1)
		buttons = ttk.Frame(side)
		buttons.grid(row=6, column=0, columnspan=2, sticky='w', pady=(10, 0))
		ttk.Button(buttons, text='Open Work folder', command=lambda: open_folder(WORK_DIR)).pack(side='left')
		ttk.Button(buttons, text='Rescan folder', command=self.rescan).pack(side='left', padx=8)

	def labels(self):
		return [e['title'] or e['name'] for e in self.project.work]

	def activate(self):
		self.rescan()

	def rescan(self):
		self.project.rescan_work()
		self.sel = min(self.sel or 0, len(self.project.work) - 1) if self.project.work else None
		self.load()

	def load(self):
		self.panel.set_items(self.labels(), self.sel if self.sel is not None else 0)
		self.select(self.panel.current())

	def select(self, index):
		self.sel = index

		with self.loading():
			entry = self.project.work[index] if index is not None and index < len(self.project.work) else None
			self.title_var.set(entry['title'] if entry else '')
			self.file_label.config(text=('File: Work/%s' % entry['name']) if entry else 'No files yet. Click "Add files…".')

		self.refresh()

	def pull(self):
		if self.sel is None or self.sel >= len(self.project.work):
			return

		self.project.work[self.sel]['title'] = self.title_var.get().strip()
		self.panel.listbox.delete(self.sel)
		self.panel.listbox.insert(self.sel, self.labels()[self.sel])
		self.panel.listbox.selection_set(self.sel)

	def add(self):
		paths = filedialog.askopenfilenames(parent=self, title='Add proof of work', filetypes=[('Images and videos', ' '.join('*' + ext for ext in MEDIA_EXTENSIONS)), ('All files', '*.*')])

		if not paths:
			return

		os.makedirs(WORK_DIR, exist_ok=True)

		for path in paths:
			if not path.lower().endswith(MEDIA_EXTENSIONS):
				continue

			name = os.path.basename(path)
			inside = os.path.abspath(os.path.dirname(path)) == os.path.abspath(WORK_DIR)

			if not inside:
				name = unique_name(WORK_DIR, name)
				shutil.copy2(path, os.path.join(WORK_DIR, name))

			if not any(e['name'] == name for e in self.project.work):
				self.project.work.append({'name': name, 'title': ''})

		self.sel = len(self.project.work) - 1
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.sel)
		self.app.touch()

	def remove(self):
		index = self.panel.current()

		if index is None:
			return

		entry = self.project.work[index]

		if not messagebox.askyesno('Remove from Work', 'Remove "%s"?\n\nThe file is deleted from the Work folder when you press Save & Build.' % entry['name'], parent=self):
			return

		self.project.pending_work_deletes.append(entry['name'])
		del self.project.work[index]
		self.sel = min(index, len(self.project.work) - 1) if self.project.work else None
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.panel.current())
		self.app.touch()

	def move(self, delta):
		target = move_item(self.project.work, self.panel.current(), delta)

		if target is None:
			return

		self.sel = target
		self.panel.set_items(self.labels(), target)
		self.select(target)
		self.app.touch()

	def refresh(self):
		entry = self.project.work[self.sel] if self.sel is not None and self.sel < len(self.project.work) else None
		self._photo = None

		if not entry:
			self.preview.config(image='', text='')
			return

		if entry['name'].lower().endswith(VIDEO_EXTENSIONS):
			self.preview.config(image='', text='▶  %s\n\n(video: plays on the site)' % entry['name'])
			return

		self._photo = self.app.images.get('Work/' + entry['name'], 560, 320)
		self.preview.config(image=self._photo or '', text='' if self._photo else 'No preview available for this file.')


# >> tab: reviews

class ReviewsTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.sel = None
		self._photos = []
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=1)

		self.panel = ListPanel(self, self.select, self.add, self.remove, self.move, add_text='Add review', width=22)
		self.panel.grid(row=0, column=0, sticky='ns', padx=(0, 20))

		form = ttk.Frame(self)
		form.grid(row=0, column=1, sticky='new', padx=(0, 20))
		form.columnconfigure(1, weight=1)
		ttk.Label(form, text='Client review', font=app.heading_font).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))
		self.name = self.var()
		self.pfp = self.var()
		self.proof = self.var()
		self.entry_row(form, 1, 'Client name', self.name)
		ttk.Label(form, text='Review text').grid(row=2, column=0, sticky='nw', padx=(0, 12), pady=5)
		self.text = self.text_box(form, 6)
		self.text.grid(row=2, column=1, sticky='ew', pady=5)
		self.file_row(form, 3, 'Profile picture', self.pfp, self.browse_pfp, hint='A file, or a full https:// link.')
		self.file_row(form, 5, 'Proof screenshot', self.proof, self.browse_proof, hint='Optional. Adds a "Show Proof" button.', clear=self.clear_proof)
		ttk.Button(form, text='Open Reviews folder', command=lambda: open_folder(REVIEWS_DIR)).grid(row=7, column=1, sticky='w', pady=(14, 0))

		side = ttk.Frame(self)
		side.grid(row=0, column=2, sticky='n')
		ttk.Label(side, text='Preview', font=app.heading_font).pack(anchor='w', pady=(0, 6))
		self.canvas = tk.Canvas(side, width=360, height=420, bg='#2a0d0d', highlightthickness=1, highlightbackground='#bbb')
		self.canvas.pack()

	def reviews(self):
		return self.project.reviews

	def labels(self):
		return [r['data'].get('name') or r['folder'] for r in self.reviews()]

	def activate(self):
		self.project.rescan_reviews()
		self.sel = min(self.sel or 0, len(self.reviews()) - 1) if self.reviews() else None
		self.load()

	def load(self):
		self.panel.set_items(self.labels(), self.sel if self.sel is not None else 0)
		self.select(self.panel.current())

	def current(self):
		return self.reviews()[self.sel] if self.sel is not None and self.sel < len(self.reviews()) else None

	def select(self, index):
		self.sel = index
		review = self.current()

		with self.loading():
			data = review['data'] if review else {}
			self.name.set(data.get('name', ''))
			self.set_text(self.text, data.get('text', ''))
			self.pfp.set(data.get('pfp', ''))
			self.proof.set(data.get('proof', ''))

		self.refresh()

	def set_asset(self, review, key, value):
		value = value.strip()
		review[key + '_src'] = None

		if value and not is_url(value) and os.path.isabs(value) and os.path.isfile(value):
			review[key + '_src'] = value
			value = key + os.path.splitext(value)[1].lower()

		review['data'][key] = value

	def pull(self):
		review = self.current()

		if not review:
			return

		review['data']['name'] = self.name.get().strip()
		review['data']['text'] = self.text.get('1.0', 'end').strip()

		for key, variable in (('pfp', self.pfp), ('proof', self.proof)):
			if variable.get().strip() != review['data'].get(key, ''):
				self.set_asset(review, key, variable.get())

		self.panel.listbox.delete(self.sel)
		self.panel.listbox.insert(self.sel, self.labels()[self.sel])
		self.panel.listbox.selection_set(self.sel)

	def browse(self, key, variable, title):
		path = self.pick_file(title, [('Images', '*.png *.jpg *.jpeg *.webp *.gif'), ('All files', '*.*')])
		review = self.current()

		if path and review:
			self.set_asset(review, key, os.path.abspath(path))

			with self.loading():
				variable.set(review['data'][key])

			self.app.touch()
			self.refresh()

	def browse_pfp(self):
		self.browse('pfp', self.pfp, 'Choose the client profile picture')

	def browse_proof(self):
		self.browse('proof', self.proof, 'Choose the proof screenshot')

	def clear_proof(self):
		self.proof.set('')

	def add(self):
		self.reviews().append({
			'folder': '',
			'new': True,
			'pfp_src': None,
			'proof_src': None,
			'data': {'name': 'New client', 'text': '', 'pfp': '', 'proof': ''},
		})
		self.sel = len(self.reviews()) - 1
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.sel)
		self.app.touch()

	def remove(self):
		index = self.panel.current()
		review = self.current()

		if review is None or index is None:
			return

		name = review['data'].get('name') or review['folder']
		extra = '' if review['new'] else '\n\nThe folder Reviews/%s (including its images) is deleted when you press Save & Build.' % review['folder']

		if not messagebox.askyesno('Remove review', 'Remove the review from "%s"?%s' % (name, extra), parent=self):
			return

		if not review['new']:
			self.project.pending_review_deletes.append(review['folder'])

		del self.reviews()[index]
		self.sel = min(index, len(self.reviews()) - 1) if self.reviews() else None
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.panel.current())
		self.app.touch()

	def move(self, delta):
		target = move_item(self.reviews(), self.panel.current(), delta)

		if target is None:
			return

		self.sel = target
		self.panel.set_items(self.labels(), target)
		self.select(target)
		self.app.touch()

	def asset_ref(self, review, key):
		source = review.get(key + '_src')

		if source:
			return source

		value = review['data'].get(key, '')

		if not value:
			return None

		return value if is_url(value) else 'Reviews/%s/%s' % (review['folder'], value)

	def refresh(self):
		c = self.canvas
		c.delete('all')
		self._photos = []
		review = self.current()

		if not review:
			c.create_text(180, 200, text='No reviews yet.\nClick "Add review".', fill='#c9a0a0', font=(self.app.family, 10), justify='center')
			return

		fonts = {
			'name': tkfont.Font(family=self.app.family, size=10, weight='bold'),
			'text': tkfont.Font(family=self.app.family, size=9),
		}
		x0, y0, width = 20, 20, 320
		pfp = self.app.images.get(self.asset_ref(review, 'pfp'), 40, 40, mode='circle')
		proof = self.app.images.get(self.asset_ref(review, 'proof'), width - 16 - 40 - 12 - 16, 140)
		text_x = x0 + 16 + 40 + 12
		text_w = width - 16 - 40 - 12 - 16
		y = y0 + 16
		y = put_text(c, text_x, y, review['data'].get('name') or 'Anonymous', fonts['name'], '#ffffff', text_w) + 3
		y = put_text(c, text_x, y, review['data'].get('text', ''), fonts['text'], '#c4b8b8', text_w) + 10

		if self.asset_ref(review, 'proof'):
			label = c.create_text(text_x + 11, y + 8, text='Show Proof', anchor='w', fill='#d4d4d8', font=fonts['text'])
			box = c.bbox(label)
			pill = rounded_rect(c, box[0] - 11, box[1] - 7, box[2] + 11, box[3] + 7, 6, outline='#4a3a3a', fill='#2f1a1a')
			c.tag_lower(pill, label)
			y = box[3] + 16

			if proof:
				self._photos.append(proof)
				c.create_image(text_x, y, image=proof, anchor='nw')
				y += proof.height()
			else:
				y += 4

		y += 16
		card = rounded_rect(c, x0, y0, x0 + width, y, 14, outline='#4a2a2a', fill='#341515')
		c.tag_lower(card)

		if pfp:
			self._photos.append(pfp)
			c.create_image(x0 + 16, y0 + 16, image=pfp, anchor='nw')
		else:
			c.create_oval(x0 + 16, y0 + 16, x0 + 56, y0 + 56, fill='#553030', outline='')
			c.create_text(x0 + 36, y0 + 36, text=(review['data'].get('name') or '?')[:1].upper(), fill='white', font=fonts['name'])


# >> tab: contact

class ContactTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.sel = None
		self._photo = None
		self.columnconfigure(1, weight=1)

		self.panel = ListPanel(self, self.select, self.add, self.remove, self.move, add_text='Add link', width=28)
		self.panel.grid(row=0, column=0, sticky='ns', padx=(0, 24))

		form = ttk.Frame(self)
		form.grid(row=0, column=1, sticky='new')
		form.columnconfigure(1, weight=1)
		ttk.Label(form, text='Contact links', font=app.heading_font).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))
		self.label = self.var()
		self.url = self.var()
		self.icon = self.var()
		self.entry_row(form, 1, 'Text shown', self.label, hint='e.g. @yourname')
		self.entry_row(form, 3, 'Link', self.url, hint='e.g. https://discord.com/users/123 or mailto:you@example.com')
		ttk.Label(form, text='Icon').grid(row=5, column=0, sticky='w', padx=(0, 12), pady=5)
		line = ttk.Frame(form)
		line.grid(row=5, column=1, sticky='ew', pady=5)
		ttk.Combobox(line, textvariable=self.icon, values=BUILTIN_ICONS).pack(side='left', fill='x', expand=True)
		ttk.Button(line, text='Browse…', command=self.browse_icon).pack(side='left', padx=(6, 0))
		ttk.Label(form, text='Pick a built-in icon (discord, x, github, youtube, email, link) or choose your own image.', foreground='#777').grid(row=6, column=1, sticky='w')
		self.preview = ttk.Label(form, foreground='#777')
		self.preview.grid(row=7, column=1, sticky='w', pady=(14, 0))

	def labels(self):
		return [c['label'] or c['url'] or '(empty)' for c in self.project.contact]

	def load(self):
		self.panel.set_items(self.labels(), self.sel if self.sel is not None else 0)
		self.select(self.panel.current())

	def select(self, index):
		self.sel = index

		with self.loading():
			contact = self.project.contact[index] if index is not None and index < len(self.project.contact) else None
			self.label.set(contact['label'] if contact else '')
			self.url.set(contact['url'] if contact else '')
			self.icon.set(contact['icon'] if contact else '')

		self.refresh()

	def pull(self):
		if self.sel is None or self.sel >= len(self.project.contact):
			return

		contact = self.project.contact[self.sel]
		contact['label'] = self.label.get().strip()
		contact['url'] = self.url.get().strip()
		contact['icon'] = self.icon.get().strip()
		self.panel.listbox.delete(self.sel)
		self.panel.listbox.insert(self.sel, self.labels()[self.sel])
		self.panel.listbox.selection_set(self.sel)

	def browse_icon(self):
		path = self.pick_file('Choose an icon image', [('Images', '*.png *.jpg *.jpeg *.webp *.gif *.svg'), ('All files', '*.*')])

		if path:
			self.icon.set(self.app.import_asset(path, 'Assets'))

	def add(self):
		self.project.contact.append({'label': '@yourname', 'url': 'https://', 'icon': 'link'})
		self.sel = len(self.project.contact) - 1
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.sel)
		self.app.touch()

	def remove(self):
		index = self.panel.current()

		if index is None:
			return

		del self.project.contact[index]
		self.sel = min(index, len(self.project.contact) - 1) if self.project.contact else None
		self.panel.set_items(self.labels(), self.sel)
		self.select(self.panel.current())
		self.app.touch()

	def move(self, delta):
		target = move_item(self.project.contact, self.panel.current(), delta)

		if target is None:
			return

		self.sel = target
		self.panel.set_items(self.labels(), target)
		self.select(target)
		self.app.touch()

	def refresh(self):
		icon = self.icon.get().strip()
		self._photo = None

		if not icon:
			self.preview.config(image='', text='')
		elif icon in BUILTIN_ICONS:
			self.preview.config(image='', text='Built-in "%s" icon (shown on the site)' % icon)
		else:
			self._photo = self.app.images.get(icon, 48, 48)
			self.preview.config(image=self._photo or '', text='' if self._photo else 'Icon image not found / not previewable.', compound='left')


# >> tab: test server

class ServerTab(Tab):
	def __init__(self, notebook, app):
		super().__init__(notebook, app)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.rowconfigure(1, weight=1)

		control = ttk.LabelFrame(self, text=' Test server ', padding=12)
		control.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
		control.columnconfigure(1, weight=1)
		ttk.Label(control, text='Port').grid(row=0, column=0, sticky='w', pady=4)
		self.port = tk.StringVar(value='5000')
		ttk.Entry(control, textvariable=self.port, width=8).grid(row=0, column=1, sticky='w', pady=4)
		self.lan = tk.BooleanVar(value=False)
		ttk.Checkbutton(control, text='Let my phone / other devices on my Wi-Fi open it', variable=self.lan).grid(row=1, column=0, columnspan=2, sticky='w', pady=4)
		line = ttk.Frame(control)
		line.grid(row=2, column=0, columnspan=2, sticky='w', pady=(6, 4))
		self.start_button = ttk.Button(line, text='Start server', command=app.toggle_server)
		self.start_button.pack(side='left')
		ttk.Button(line, text='Open site in browser', command=app.open_site).pack(side='left', padx=8)
		self.status = ttk.Label(control, text='Server is stopped.')
		self.status.grid(row=3, column=0, columnspan=2, sticky='w', pady=(8, 0))
		self.url_label = ttk.Label(control, foreground='#1a5fb4', cursor='hand2')
		self.url_label.grid(row=4, column=0, columnspan=2, sticky='w')
		self.url_label.bind('<Button-1>', lambda event: app.copy_url())
		self.lan_label = ttk.Label(control, foreground='#1a5fb4', cursor='hand2')
		self.lan_label.grid(row=5, column=0, columnspan=2, sticky='w')
		self.lan_label.bind('<Button-1>', lambda event: app.copy_url(lan=True))

		ttk.Label(control, text='Open a specific tab:').grid(row=6, column=0, columnspan=2, sticky='w', pady=(12, 2))
		jump = ttk.Frame(control)
		jump.grid(row=7, column=0, columnspan=2, sticky='w')
		self.jump = tk.StringVar()
		self.jump_combo = ttk.Combobox(jump, textvariable=self.jump, state='readonly', width=24)
		self.jump_combo.pack(side='left')
		ttk.Button(jump, text='Open', command=self.open_jump).pack(side='left', padx=6)

		folders = ttk.Frame(control)
		folders.grid(row=8, column=0, columnspan=2, sticky='w', pady=(14, 0))
		ttk.Button(folders, text='Open project folder', command=lambda: open_folder(ROOT)).pack(side='left')
		ttk.Button(folders, text='Open Config folder', command=lambda: open_folder(CONFIG_DIR)).pack(side='left', padx=8)

		health = ttk.LabelFrame(self, text=' Health check ', padding=12)
		health.grid(row=0, column=1, sticky='nsew')
		health.columnconfigure(0, weight=1)
		health.rowconfigure(0, weight=1)
		self.health = tk.Text(health, height=11, wrap='word', borderwidth=0, state='disabled', background=self.app.cget('background'), font=app.ui_font)
		self.health.grid(row=0, column=0, sticky='nsew')
		self.health.tag_config('error', foreground='#b3261e')
		self.health.tag_config('warn', foreground='#8a5a00')
		self.health.tag_config('ok', foreground='#1b6e2e')
		ttk.Button(health, text='Re-check', command=self.refresh).grid(row=1, column=0, sticky='w', pady=(8, 0))

		log = ttk.LabelFrame(self, text=' Requests ', padding=8)
		log.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(12, 0))
		log.columnconfigure(0, weight=1)
		log.rowconfigure(0, weight=1)
		self.log = tk.Text(log, height=8, wrap='none', state='disabled', borderwidth=1, relief='solid', background='#101418', foreground='#c9d1d9', font=('Consolas', 9))
		self.log.grid(row=0, column=0, sticky='nsew')
		scroll = ttk.Scrollbar(log, command=self.log.yview)
		scroll.grid(row=0, column=1, sticky='ns')
		self.log.config(yscrollcommand=scroll.set)

	def open_jump(self):
		index = self.jump_combo.current()
		enabled = [t for t in self.project.tabs if t.get('enabled', True)]

		if 0 <= index < len(enabled):
			self.app.open_site(enabled[index], index)

	def update_tabs(self):
		enabled = [t for t in self.project.tabs if t.get('enabled', True)]
		self.jump_combo.config(values=[t['label'] for t in enabled])

		if enabled and self.jump_combo.current() < 0:
			self.jump_combo.current(0)

	def update_status(self):
		server = self.app.server

		if server.running:
			self.start_button.config(text='Stop server')
			self.status.config(text='Server is running. Click a link to copy it.')
			self.url_label.config(text=server.url())
			self.lan_label.config(text=('On your network: %s' % server.lan_url()) if server.lan_url() else '')
		else:
			self.start_button.config(text='Start server')
			self.status.config(text='Server is stopped.')
			self.url_label.config(text='')
			self.lan_label.config(text='')

	def append_log(self, line):
		self.log.config(state='normal')
		self.log.insert('end', '%s  %s\n' % (datetime.datetime.now().strftime('%H:%M:%S'), line))

		if int(self.log.index('end-1c').split('.')[0]) > 500:
			self.log.delete('1.0', '100.0')

		self.log.see('end')
		self.log.config(state='disabled')

	def refresh(self):
		self.update_tabs()
		self.update_status()
		self.health.config(state='normal')
		self.health.delete('1.0', 'end')

		for level, message in self.project.check():
			mark = {'error': '✖ ', 'warn': '▲ ', 'ok': '✔ '}[level]
			self.health.insert('end', mark + message + '\n', level)

		self.health.config(state='disabled')

	def activate(self):
		self.refresh()


# >> app

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('Portfolio Editor')
		self.geometry('1240x820')
		self.minsize(1040, 700)
		self.dirty = False
		self._preview_job = None
		self.project = Project()
		self.images = Images()
		self.log_queue = queue.Queue()
		self.server = SiteServer(self.log_queue.put)

		style = ttk.Style(self)

		for theme in ('vista', 'clam'):
			if theme in style.theme_names():
				style.theme_use(theme)
				break

		base = tkfont.nametofont('TkDefaultFont')
		self.family = base.actual('family')
		self.ui_font = tkfont.Font(family=self.family, size=10)
		self.heading_font = tkfont.Font(family=self.family, size=11, weight='bold')
		base.configure(size=10)
		tkfont.nametofont('TkTextFont').configure(size=10)
		style.configure('TNotebook.Tab', padding=(14, 7))
		style.configure('Save.TButton', font=(self.family, 10, 'bold'))

		self.build_toolbar()
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 6))

		self.status = tk.StringVar(value='Ready.')
		ttk.Label(self, textvariable=self.status, anchor='w', padding=(12, 4)).pack(fill='x')

		self.tabs = {}

		for key, title, cls in (
			('profile', 'Profile', ProfileTab),
			('card', 'Title card', TitleCardTab),
			('tabs', 'Tabs', TabsTab),
			('pages', 'Pages', PagesTab),
			('work', 'Proof of work', WorkTab),
			('reviews', 'Reviews', ReviewsTab),
			('contact', 'Contact', ContactTab),
			('server', 'Test & check', ServerTab),
		):
			tab = cls(self.notebook, self)
			self.tabs[key] = tab
			self.notebook.add(tab, text=title)

		for tab in self.tabs.values():
			tab.load()

		self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
		self.bind('<Control-s>', lambda event: self.save())
		self.protocol('WM_DELETE_WINDOW', self.on_close)
		self.update_toolbar()
		self.after(200, self.poll)
		self.tabs['server'].update_tabs()
		self.set_status('Ready. Changes you make are previewed live; press Save & Build to write them to your site.')

	# toolbar

	def build_toolbar(self):
		bar = ttk.Frame(self, padding=(10, 10, 10, 8))
		bar.pack(fill='x')
		self.save_button = ttk.Button(bar, text='Save & Build  (Ctrl+S)', style='Save.TButton', command=self.save)
		self.save_button.pack(side='left')
		self.server_button = ttk.Button(bar, text='▶  Start server', command=self.toggle_server)
		self.server_button.pack(side='left', padx=(10, 0))
		ttk.Button(bar, text='Open site', command=self.open_site).pack(side='left', padx=(6, 0))
		self.url_label = ttk.Label(bar, foreground='#1a5fb4', cursor='hand2')
		self.url_label.pack(side='left', padx=14)
		self.url_label.bind('<Button-1>', lambda event: self.copy_url())
		self.dirty_label = ttk.Label(bar, foreground='#8a5a00')
		self.dirty_label.pack(side='right')

	def update_toolbar(self):
		running = self.server.running
		self.server_button.config(text='■  Stop server' if running else '▶  Start server')
		self.url_label.config(text=self.server.url() if running else '')
		self.dirty_label.config(text='● unsaved changes' if self.dirty else '')
		self.title('Portfolio Editor%s' % (' *' if self.dirty else ''))

		if 'server' in self.tabs:
			self.tabs['server'].update_status()

	def set_status(self, text):
		self.status.set(text)

	# editing state

	def touch(self):
		if not self.dirty:
			self.dirty = True
			self.update_toolbar()

		if self._preview_job:
			self.after_cancel(self._preview_job)

		self._preview_job = self.after(120, self.refresh_current)

	def current_tab(self):
		return self.nametowidget(self.notebook.select())

	def refresh_current(self):
		self._preview_job = None
		self.current_tab().refresh()

	def on_tab_changed(self, event=None):
		tab = self.current_tab()
		tab.activate()
		tab.refresh()

	def tab_list_changed(self):
		self.tabs['pages'].load()
		self.tabs['server'].update_tabs()
		self.tabs['profile'].refresh()

	def open_content_for(self, tab):
		target = {'page': 'pages', 'work': 'work', 'reviews': 'reviews', 'contact': 'contact'}.get(tab.get('type'))

		if not target:
			return

		if target == 'pages':
			self.tabs['pages'].open_tab(tab['id'])

		self.notebook.select(self.tabs[target])

	def import_asset(self, path, folder):
		"""returns a project-relative path, copying the file into folder if it is outside the project."""
		inside = rel(path)

		if inside:
			return inside

		directory = os.path.join(ROOT, folder)
		os.makedirs(directory, exist_ok=True)
		name = unique_name(directory, os.path.basename(path))
		shutil.copy2(path, os.path.join(directory, name))
		return '%s/%s' % (folder, name)

	# saving

	def save(self):
		pending = self.project.pending_description()

		if pending:
			message = 'These will be permanently deleted from your project:\n\n  ' + '\n  '.join(pending[:12])

			if len(pending) > 12:
				message += '\n  … and %d more' % (len(pending) - 12)

			if not messagebox.askokcancel('Delete removed files?', message + '\n\nContinue?', icon='warning', parent=self):
				return False

		try:
			self.project.save_all()
		except (ConfigError, OSError) as error:
			messagebox.showerror('Could not save', str(error), parent=self)
			return False

		self.dirty = False
		self.update_toolbar()

		for key in ('work', 'reviews'):
			self.tabs[key].load()

		self.tabs['server'].refresh()
		self.set_status('Saved and built at %s. Work/index.json, Reviews/index.json and index.html are up to date. %s' % (datetime.datetime.now().strftime('%H:%M:%S'), 'Refresh your browser to see it.' if self.server.running else ''))
		return True

	# server

	def toggle_server(self):
		if self.server.running:
			self.server.stop()
		else:
			try:
				port = int(self.tabs['server'].port.get())
			except ValueError:
				port = 5000

			try:
				actual = self.server.start(port, self.tabs['server'].lan.get())
			except OSError as error:
				messagebox.showerror('Could not start the server', str(error), parent=self)
				return

			self.tabs['server'].port.set(str(actual))

		self.update_toolbar()

	def open_site(self, tab=None, index=0):
		if self.dirty and not self.save():
			return

		if not self.server.running:
			self.toggle_server()

		if not self.server.running:
			return

		fragment = ''

		if tab and index > 0:
			fragment = '#' + (tab.get('hash') if tab.get('hash') is not None else tab['id'])

		webbrowser.open(self.server.url() + fragment)

	def copy_url(self, lan=False):
		url = self.server.lan_url() if lan else (self.server.url() if self.server.running else None)

		if url:
			self.clipboard_clear()
			self.clipboard_append(url)
			self.set_status('Copied %s' % url)

	def poll(self):
		try:
			while True:
				self.tabs['server'].append_log(self.log_queue.get_nowait())
		except queue.Empty:
			pass

		refresh = False

		try:
			while True:
				self.images.ready.get_nowait()
				refresh = True
		except queue.Empty:
			pass

		if refresh:
			self.refresh_current()

		self.after(200, self.poll)

	def on_close(self):
		if self.dirty:
			answer = messagebox.askyesnocancel('Unsaved changes', 'Save and build before closing?', parent=self)

			if answer is None:
				return

			if answer and not self.save():
				return

		self.server.stop()
		shutil.rmtree(self.images.temp, ignore_errors=True)
		self.destroy()


# >> command line

def main(argv=None):
	parser = argparse.ArgumentParser(description='Portfolio editor and test server.')
	parser.add_argument('--build', action='store_true', help='rebuild Work/index.json, Reviews/index.json and index.html, then exit')
	parser.add_argument('--serve', action='store_true', help='only run the test server (no window)')
	parser.add_argument('--port', type=int, default=5000)
	parser.add_argument('--lan', action='store_true', help='make the server reachable from other devices on your network')
	parser.add_argument('--open', action='store_true', help='open the browser (with --serve)')
	args = parser.parse_args(argv)

	try:
		if args.build:
			project = Project()
			project.build_work_index()
			project.build_reviews_index()
			project.build_html()
			print('Built Work/index.json (%d files), Reviews/index.json (%d reviews) and index.html.' % (len(project.work), len(project.reviews)))
			return 0

		if args.serve:
			server = SiteServer(print)
			port = server.start(args.port, args.lan)
			print('Serving %s' % ROOT)
			print('Open  %s' % server.url())

			if server.lan_url():
				print('Phone %s' % server.lan_url())

			print('Press Ctrl+C to stop.')

			if args.open:
				webbrowser.open(server.url())

			try:
				threading.Event().wait()
			except KeyboardInterrupt:
				server.stop()

			return 0

		App().mainloop()
		return 0
	except ConfigError as error:
		print('Problem: %s' % error, file=sys.stderr)

		try:
			root = tk.Tk()
			root.withdraw()
			messagebox.showerror('Portfolio Editor', str(error))
			root.destroy()
		except tk.TclError:
			pass

		return 1


if __name__ == '__main__':
	sys.exit(main())
