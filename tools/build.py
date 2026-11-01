#!/usr/bin/env python3
"""Build the DexLab site: content/strings.json -> /fr/, /en/, /ar/ index pages + root redirect + 404.

Edit text in content/strings.json, then run:  python3 tools/build.py
Styles live in assets/css/site.css, behaviour in assets/js/site.js.
"""
import html
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "content", "strings.json"), encoding="utf-8"))
SITE = S["site"]
LANGS = [("ar", "العربية", "عربي", "rtl"), ("fr", "Français", "FR", "ltr"), ("en", "English", "EN", "ltr")]
IDS = ["web", "automation", "clinic", "work", "contact"]
e = html.escape


def asset_url(path):
    """New content gets a new URL, avoiding stale CSS/JS after a Pages deploy."""
    with open(os.path.join(ROOT, path.lstrip('/')), 'rb') as asset:
        version = hashlib.sha256(asset.read()).hexdigest()[:12]
    return f'{path}?v={version}'

ICON = {
    "web": "M3 4h18v16H3zM3 9h18", "order": "M5 4h14v16H5zM8.5 9l1.5 1.5L13 7.5M8.5 15h7",
    "landing": "M4 4h16v16H4zM8 9h8M8 13h5M8 17h3", "admin": "M3 3h7v18H3zM13 3h3a5 5 0 0 1 0 10h-3zM13 17h8",
    "cal": "M3 5h18v16H3zM3 10h18M8 3v4M16 3v4M8 14h3v3H8z",
    "person": "M12 4a4 4 0 1 1 0 8a4 4 0 1 1 0-8M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1",
    "notes": "M5 3h14v18H5zM8 8h8M8 12h8M8 16h5", "rx": "M6 3h9l4 4v14H6zM9 11h7M9 15h7",
    "bill": "M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2zM9 8h6M9 12h6",
    "phone": "M5 3h5l2 5-3 2a11 11 0 0 0 5 5l2-3 5 2v5a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2",
    "sheet": "M3 4h18v16H3zM3 10h18M3 15h18M9 4v16", "memo": "M12 3a9 9 0 1 1 0 18a9 9 0 1 1 0-18M12 7v5l3 3",
}


def icon(name, size=32, sw="1.75"):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="square" aria-hidden="true"><path d="{ICON[name]}"/></svg>')


ARROW = ('<svg class="arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2" stroke-linecap="square" aria-hidden="true"><path d="M4 12h15M14 7l5 5-5 5"/></svg>')
CHECK = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.25" '
         'stroke-linecap="square" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>')


def lang_links(cur, cls=""):
    out = []
    for code, label, short, d in LANGS:
        c = ' aria-current="true"' if code == cur else ""
        out.append(f'<a href="/{code}/" lang="{code}" hreflang="{code}" data-lang="{code}"{c}{cls}>{label}</a>')
    return out


def page(lang):
    t = S[lang]
    d = "rtl" if lang == "ar" else "ltr"
    app = S["app"]
    sfx = "_en" if lang == "en" else ""          # Arabic shows the app in French (the app is FR/EN)
    cur = [l for l in LANGS if l[0] == lang][0]
    nav = "".join(f'<a href="#{i}">{e(l)}</a>' for i, l in zip(IDS, t["nav"]))
    mnav = "".join(f'<a class="m-link" href="#{i}">{e(l)}</a>' for i, l in zip(IDS, t["nav"]))
    alts = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{SITE["url"]}/{c}/">' for c, *_ in LANGS)
    email = SITE["email"]

    starter_cards = "".join(
        f'<a class="starter-card rv" href="#contact" data-project="{e(c[0])}" style="--i:{n}">'
        f'<span class="starter-top"><span class="num">0{n + 1}</span>{icon(["web", "admin", "cal"][n], 28)}</span>'
        f'<h3>{e(c[1])}</h3><p>{e(c[2])}</p><span class="starter-tags">{e(c[3])}</span>'
        f'<span class="starter-action">{e(t["starter"]["action"])}{ARROW}</span></a>'
        for n, c in enumerate(t["starter"]["cards"]))
    process_steps = "".join(
        f'<li class="process-step rv" style="--i:{n}"><span class="step-number">0{n + 1}</span>'
        f'<h3>{e(step[0])}</h3><p>{e(step[1])}</p></li>'
        for n, step in enumerate(t["process"]["steps"]))
    faq_items = "".join(
        f'<details class="faq-item"><summary>{e(q)}<span class="faq-mark" aria-hidden="true"></span></summary>'
        f'<p>{e(a)}</p></details>' for q, a in t["faq"]["items"])
    social_cards = "".join(
        f'<a class="social-card" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{e(s["name"])} — {e(t["social"]["newTab"])}">'
        f'<span class="social-card-top"><span class="label" lang="en">{e(s["name"])}</span><span aria-hidden="true">↗</span></span>'
        f'<b dir="ltr" class="ltr">{e(s["handle"])}</b><span class="social-action">{e(t["social"]["action"])}</span></a>'
        for s in SITE["socials"])
    social_links = "".join(
        f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{e(s["name"])} — {e(t["social"]["newTab"])}"><bdi lang="en">{e(s["name"])}</bdi><span aria-hidden="true"> ↗</span></a>'
        for s in SITE["socials"])

    web_cards = "".join(
        f'<article class="card rv" style="--i:{n}"><span class="num">0{n + 1}</span>{icon(c[2])}'
        f'<h3>{e(c[0])}</h3><p>{e(c[1])}</p></article>' for n, c in enumerate(t["web"]["cards"]))
    notes = "".join(f'<div class="note">{icon(b[1], 20)}<span>{e(b[0])}</span></div>' for b in t["auto"]["beforeItems"])
    after = "".join(f'<li style="--i:{n}">{CHECK}<span>{e(a)}</span></li>' for n, a in enumerate(t["auto"]["afterItems"]))
    mods = "".join(f'<li class="rv" style="--i:{n}">{icon(m[2], 24)}<b>{e(m[0])}</b><span>{e(m[1])}</span></li>'
                   for n, m in enumerate(t["clinic"]["mods"]))
    on = ' class="on"'
    side = "".join(f'<span{on if i == 0 else ""}>{e(x)}</span>' for i, x in enumerate(app["side" + sfx]))
    cols = "".join(f"<span>{e(c)}</span>" for c in app["cols" + sfx])
    labels = e(json.dumps(app["status" + sfx], ensure_ascii=False))
    rows = "".join(
        f'<div class="tr"><span class="time">{r[0]}</span><span>{e(r[1])}</span>'
        f'<span class="reason">{e(r[3] if lang == "en" else r[2])}</span>'
        f'<button type="button" class="stbtn s{s}" data-s="{s}" data-labels="{labels}">{e(app["status" + sfx][s])}</button></div>'
        for r, s in zip(app["rows"], app["start"]))
    tabs = "".join(f'<div class="tab"><span>{e(k)}</span><i class="bar" style="width:{w}"></i><i class="bar2"></i></div>'
                   for k, w in zip(app["tabs" + sfx], ["70%", "55%", "40%"]))
    projects = "".join(
        f'<a class="project project-link rv" href="{e(p[3])}" target="_blank" rel="noopener noreferrer" style="--i:{n}" '
        f'aria-label="{e(p[0])} — {e(t["work"]["visit"])} ({e(t["social"]["newTab"])})">'
        f'<div class="project-cover"><img src="{asset_url(p[4])}" alt="{e(p[5])}" width="1600" height="1000" loading="lazy" decoding="async"></div>'
        f'<div class="p-body"><div class="tags"><span>{e(p[1])}</span></div><h3 lang="en" dir="ltr">{e(p[0])}</h3><p>{e(p[2])}</p>'
        f'<span class="project-visit"><bdi dir="ltr" class="ltr">{e(p[3].split("//")[-1].rstrip("/"))}</bdi><span>{e(t["work"]["visit"])} ↗</span></span></div></a>'
        for n, p in enumerate(t["work"]["cards"]))
    chips = "".join(
        f'<label><input type="radio" name="type" value="{v}"{" checked" if v == "clinic" else ""}><span>{e(c)}</span></label>'
        for v, c in zip(["web", "automation", "clinic", "unsure"], t["contact"]["chips"]))
    words = " ".join(f'<span class="w">{e(w)}</span>' for w in t["hero"]["h1"].split(" "))

    return f"""<!doctype html>
<html lang="{lang}" dir="{d}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(t["meta"]["title"])}</title>
<meta name="description" content="{e(t["meta"]["description"])}">
<meta name="theme-color" content="#F3F1EC">
<link rel="canonical" href="{SITE["url"]}/{lang}/">
{alts}
<link rel="alternate" hreflang="x-default" href="{SITE["url"]}/fr/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DexLab">
<meta property="og:title" content="{e(t["meta"]["title"])}">
<meta property="og:description" content="{e(t["meta"]["description"])}">
<meta property="og:url" content="{SITE["url"]}/{lang}/">
<meta property="og:image" content="{SITE["url"]}/assets/img/og-{lang}.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/{"ibm-plex-sans-arabic-arabic-700-normal" if lang == "ar" else "instrument-sans-latin-700-normal"}.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset_url('/assets/css/site.css')}">
<script>if(!matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("play");</script>
</head>
<body>
<a class="skip" href="#main">{e(t["skip"])}</a>
<div class="progress" aria-hidden="true"><span></span></div>

<header class="site-head">
<div class="wrap head-row">
<a class="brand" href="/{lang}/" dir="ltr" aria-label="DexLab"><img src="/assets/img/logo.svg" alt="DexLab" width="136" height="27"></a>
<nav class="nav" aria-label="{e(t["navLabel"])}">{nav}</nav>
<div class="head-end">
<button type="button" class="lang-btn" aria-haspopup="true" aria-expanded="false" aria-controls="lang-list" aria-label="{e(t["langLabel"])}">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>
<span class="full">{cur[1]}</span><span class="short">{cur[2]}</span>
<svg class="chev" width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>
</button>
<div class="lang-list" id="lang-list" role="group" aria-label="{e(t["langLabel"])}">{"".join(lang_links(lang))}</div>
<a class="btn btn-ink" href="#contact">{e(t["cta"])}</a>
<button type="button" class="menu-btn" aria-expanded="false" aria-controls="mobile-menu" aria-label="{e(t["menuOpen"])}" data-open="{e(t["menuOpen"])}" data-close="{e(t["menuClose"])}">
<svg class="bars" width="20" height="14" viewBox="0 0 20 14" aria-hidden="true"><path d="M0 1h20M0 7h20M0 13h20" stroke="#F3F1EC" stroke-width="2"/></svg>
<svg class="x" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 2l12 12M14 2L2 14" stroke="#F3F1EC" stroke-width="2"/></svg>
</button>
</div>
</div>
<nav class="mobile-menu" id="mobile-menu" aria-label="{e(t["navLabel"])}">
{mnav}
<span class="small">{e(t["langLabel"])}</span>
<div class="seg">{"".join(lang_links(lang))}</div>
<a class="btn btn-pri" href="#contact">{e(t["cta"])}</a>
</nav>
</header>

<main id="main">
<section class="wrap hero" id="top">
<div class="hero-copy">
<a class="chip-link" href="#clinic"><span class="tag">{e(t["hero"]["tag"])}</span><span>{e(t["hero"]["chip"])}</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" aria-hidden="true"><path d="M4 12h15M14 7l5 5-5 5"/></svg></a>
<h1>{words}</h1>
<p class="lead">{e(t["hero"]["sub"])}</p>
<div class="actions"><a class="btn btn-pri" href="#contact">{e(t["cta"])}{ARROW}</a><a class="btn btn-sec" href="#work">{e(t["hero"]["cta2"])}</a></div>
</div>
<button type="button" class="motif" dir="ltr" aria-label="{e(t["hero"]["replay"])}">
<span class="mod block" dir="{d}"><span>01 {e(t["m"]["web"])}</span></span>
<span class="mod disc" dir="{d}"><span>02 {e(t["m"]["sys"])}</span></span>
<span class="chip c1" dir="{d}">{e(t["m"]["order"])}</span>
<span class="chip c2" dir="{d}">{e(t["m"]["admin"])}</span>
<span class="chip c3" dir="{d}">{e(t["m"]["clinic"])}</span>
<span class="chip c4" dir="{d}">{e(t["m"]["flow"])}</span>
<span class="replay" dir="{d}" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12a8 8 0 1 0 3-6.2M4 4v5h5"/></svg>{e(t["hero"]["replay"])}</span>
</button>
</section>

<section class="starter" aria-labelledby="starter-heading">
<div class="wrap sec-in">
<div class="starter-heading"><div><span class="label">{e(t["starter"]["label"])}</span><h2 id="starter-heading">{e(t["starter"]["h2"])}</h2></div><p>{e(t["starter"]["intro"])}</p></div>
<div class="starter-grid">{starter_cards}</div>
</div>
</section>

<section class="sec" id="web">
<div class="wrap sec-in">
<div class="sec-head rv"><div><span class="label">{e(t["web"]["label"])}</span><h2 class="h2">{e(t["web"]["h2"])}</h2></div><p class="lead">{e(t["web"]["intro"])}</p></div>
<div class="cards">{web_cards}</div>
</div>
</section>

<section class="sec dark" id="automation">
<div class="wrap sec-in">
<div class="sec-head rv"><div><span class="label">{e(t["auto"]["label"])}</span><h2 class="h2">{e(t["auto"]["h2"])}</h2></div><p class="lead">{e(t["auto"]["intro"])}</p></div>
<div class="ba">
<div class="before"><span class="k">{e(t["auto"]["before"])}</span>{notes}</div>
<div class="after"><span class="k">{ARROW}{e(t["auto"]["after"])}</span><ul>{after}</ul>
<div class="status-row"><span class="st st-info">{e(t["auto"]["s1"])}</span><span class="st st-warn">{e(t["auto"]["s2"])}</span><span class="st st-ok">{e(t["auto"]["s3"])}</span></div></div>
</div>
</div>
</section>

<section class="sec clinic" id="clinic">
<div class="wrap sec-in">
<div class="clinic-copy">
<span class="badge">{e(t["clinic"]["label"])}</span>
<h2 class="h2 rv">{e(t["clinic"]["h2"])}</h2>
<p class="lead rv">{e(t["clinic"]["intro"])}</p>
<ul class="mods">{mods}</ul>
<div class="actions"><a class="btn btn-pri" href="#contact" data-project="clinic">{e(t["clinic"]["cta"])}{ARROW}</a></div>
</div>
<figure class="rv">
<div class="screen-wrap" dir="ltr" tabindex="0" role="region" aria-label="{e(t["clinic"]["figLabel"])}">
<div class="screen" dir="ltr" lang="{"en" if lang == "en" else "fr"}">
<div class="top"><span class="logo-ph">LOGO</span><b>{e(app["clinicName"])}</b><span class="doc">{e(app["doctor"])}</span></div>
<div class="side">{side}</div>
<div class="main">
<div class="main-h"><b>{e(app["title" + sfx])}</b><span class="new">{e(app["newBtn" + sfx])}</span></div>
<div><div class="tr th">{cols}</div>{rows}</div>
<div class="tabs">{tabs}</div>
</div>
</div>
</div>
<figcaption><span class="try">{e(t["clinic"]["tryIt"])}</span>{e(t["clinic"]["note"])}</figcaption>
</figure>
</div>
</section>

<section class="sec" id="work">
<div class="wrap sec-in">
<div class="work-head rv"><div><span class="label">{e(t["work"]["label"])}</span><h2 class="h2">{e(t["work"]["h2"])}</h2></div><span class="side-note">{e(t["work"]["note"])}</span></div>
<div class="projects">{projects}</div>
</div>
</section>

<section class="sec process" id="process" aria-labelledby="process-heading">
<div class="wrap sec-in">
<div class="sec-head rv"><div><span class="label">{e(t["process"]["label"])}</span><h2 class="h2" id="process-heading">{e(t["process"]["h2"])}</h2></div><p class="lead">{e(t["process"]["intro"])}</p></div>
<ol class="process-grid">{process_steps}</ol>
</div>
</section>

<section class="sec faq" id="faq" aria-labelledby="faq-heading">
<div class="wrap faq-grid">
<div class="faq-heading"><span class="label">{e(t["faq"]["label"])}</span><h2 class="h2" id="faq-heading">{e(t["faq"]["h2"])}</h2><a class="btn btn-sec" href="#contact">{e(t["cta"])}{ARROW}</a></div>
<div class="faq-list">{faq_items}</div>
</div>
</section>

<section class="social-band" id="social" aria-labelledby="social-heading">
<div class="wrap social-layout">
<div class="social-copy"><span class="label">{e(t["social"]["label"])}</span><h2 class="h2" id="social-heading">{e(t["social"]["h2"])}</h2><p>{e(t["social"]["intro"])}</p></div>
<div class="social-cards">{social_cards}</div>
</div>
</section>

<section class="sec contact" id="contact">
<div class="wrap sec-in">
<div class="contact-copy">
<span class="label">{e(t["contact"]["label"])}</span>
<h2>{e(t["contact"]["h2"])}</h2>
<p class="lead">{e(t["contact"]["intro"])}</p>
<div class="mini" aria-hidden="true"><span class="b"></span><span class="d"></span></div>
<dl><div><dt>{e(t["contact"]["emailK"])}</dt><dd><a href="mailto:{email}"><bdi dir="ltr" class="ltr">{email}</bdi></a></dd></div></dl>
<div class="contact-social"><span class="label">{e(t["social"]["short"])}</span><div class="social-links">{social_links}</div></div>
</div>
<form class="cform rv" novalidate data-to="{email}" data-subject="{e(t["contact"]["subject"])}">
<p class="project-feedback" role="status" aria-live="polite" data-label="{e(t["starter"]["selected"])}"></p>
<div class="field"><label for="f-name">{e(t["contact"]["name"])}</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="f-reach">{e(t["contact"]["reach"])}</label><input id="f-reach" name="reach" type="text" class="ltr" dir="ltr" autocomplete="email" inputmode="email"></div>
<fieldset class="field" style="border:0;margin:0;padding:0"><legend class="lbl" style="padding:0;margin-bottom:8px">{e(t["contact"]["type"])}</legend><div class="chips">{chips}</div></fieldset>
<div class="field"><label for="f-msg">{e(t["contact"]["msg"])}</label><textarea id="f-msg" name="msg" rows="4" required></textarea></div>
<div class="msg err" role="alert" hidden>{e(t["contact"]["required"])}</div>
<div class="msg ok" role="status" hidden>{CHECK}<span>{e(t["contact"]["ok"])}</span></div>
<button type="submit" class="btn btn-pri">{e(t["contact"]["send"])}{ARROW}</button>
<p class="form-note">{e(t["emailHint"])}</p>
</form>
</div>
</section>
</main>

<footer class="foot">
<div class="wrap foot-grid">
<div><span dir="ltr"><img src="/assets/img/logo-dark.svg" alt="DexLab" width="140" height="27"></span><span class="tag">{e(t["foot"]["tag"])}</span><div class="social-links">{social_links}</div></div>
<nav aria-label="{e(t["navLabel"])}"><div>{nav.replace('<a ', '<a class="f" ')}</div></nav>
<div><span class="k">{e(t["langLabel"])}</span>{"".join(lang_links(lang))}</div>
<div><span class="k">{e(t["contact"]["emailK"])}</span><a href="mailto:{email}"><bdi dir="ltr" class="ltr">{email}</bdi></a><a href="{SITE["url"]}" dir="ltr" class="ltr">dexlab.store</a></div>
</div>
<div class="wrap foot-bottom"><span dir="ltr" class="ltr">© <span data-year>2026</span> DexLab · M’Sila</span><img class="creator-signature" src="{asset_url('/assets/img/signature.png')}" alt="Developer signature" width="48" height="24" loading="lazy" decoding="async"><a href="#top">{e(t["foot"]["top"])} ↑</a></div>
</footer>
<script src="{asset_url('/assets/js/site.js')}" defer></script>
</body>
</html>
"""


ROOT_INDEX = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DexLab · Sites web et systèmes sur mesure</title>
<meta name="description" content="DexLab · Websites and custom systems from M'Sila, Algeria. Français · العربية · English.">
<link rel="canonical" href="https://dexlab.store/fr/">
<link rel="alternate" hreflang="fr" href="https://dexlab.store/fr/">
<link rel="alternate" hreflang="ar" href="https://dexlab.store/ar/">
<link rel="alternate" hreflang="en" href="https://dexlab.store/en/">
<link rel="alternate" hreflang="x-default" href="https://dexlab.store/fr/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:image" content="https://dexlab.store/assets/img/og-fr.png">
<script>
(function(){var l;try{l=localStorage.getItem("dexlab-lang")}catch(e){}
if(!l){var n=(navigator.languages||[navigator.language||"fr"]).join(",").toLowerCase();l=/(^|,)ar/.test(n)?"ar":/(^|,)fr/.test(n)?"fr":/(^|,)en/.test(n)?"en":"fr";}
location.replace("/"+l+"/"+location.hash);})();
</script>
<noscript><meta http-equiv="refresh" content="0; url=/fr/"></noscript>
<style>body{margin:0;background:#F3F1EC;color:#15171C;font:16px/1.6 system-ui,sans-serif;display:grid;place-items:center;min-height:100vh}a{color:#2F4BE0;margin:0 8px}</style>
</head>
<body><p><a href="/fr/">Français</a><a href="/ar/" lang="ar">العربية</a><a href="/en/">English</a></p></body>
</html>
"""

NOT_FOUND = """<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DexLab · 404</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/css/site.css"></head>
<body>
<main class="wrap" style="min-height:100vh;display:flex;flex-direction:column;justify-content:center;gap:24px;padding-block:48px">
<div class="mini" aria-hidden="true"><span class="b"></span><span class="d"></span></div>
<h1 style="font-size:var(--h1);line-height:1;letter-spacing:-.035em">404</h1>
<p class="lead">Cette page n'existe pas. · This page doesn't exist. · <span lang="ar" dir="rtl">هذه الصفحة غير موجودة.</span></p>
<p style="display:flex;gap:16px;flex-wrap:wrap"><a href="/fr/">Accueil</a><a href="/ar/" lang="ar">الرئيسية</a><a href="/en/">Home</a></p>
</main>
</body>
</html>
"""

MANIFEST = {
    "name": "DexLab", "short_name": "DexLab", "start_url": "/", "display": "standalone",
    "background_color": "#F3F1EC", "theme_color": "#F3F1EC",
    "icons": [{"src": "/assets/img/favicon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/assets/img/favicon-512.png", "sizes": "512x512", "type": "image/png"}],
}


def main():
    for lang in ("fr", "en", "ar"):
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        with open(os.path.join(ROOT, lang, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(lang))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(ROOT_INDEX)
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(NOT_FOUND.replace('/assets/css/site.css', asset_url('/assets/css/site.css')))
    json.dump(MANIFEST, open(os.path.join(ROOT, "site.webmanifest"), "w"), indent=2)
    urls = "".join(f"<url><loc>{SITE['url']}/{c}/</loc></url>" for c in ("fr", "ar", "en"))
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    print("built fr, en, ar, index, 404")


if __name__ == "__main__":
    main()
