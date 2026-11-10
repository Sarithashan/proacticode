"""All custom CSS and small HTML helpers for the dashboard live here."""

CSS = """
<style>
.stApp { background: #f5f6fb; }
.block-container { padding-top: 1.4rem; max-width: 1180px; }

/* ---------- hero banner ---------- */
.hero { background: linear-gradient(135deg,#4f46e5 0%,#7c3aed 55%,#06b6d4 100%);
        color: #fff; padding: 30px 34px; border-radius: 20px; margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(79,70,229,.25); }
.hero h1 { color:#fff; margin:0; font-size:2.3rem; letter-spacing:-.5px; }
.hero p  { margin:8px 0 0; font-size:1.05rem; opacity:.92; }
.hero .chips { margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
.hero .chip { background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.3);
              padding:3px 12px; border-radius:999px; font-size:.82rem; }

/* ---------- cards ---------- */
.card { background:#fff; border:1px solid #e6e8f0; border-radius:16px; padding:18px 20px;
        box-shadow:0 1px 3px rgba(16,24,40,.05); height:100%; }
.kpi .label { font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; color:#6b7280; }
.kpi .value { font-size:2rem; font-weight:700; color:#111827; line-height:1.25; }
.kpi .sub   { font-size:.82rem; color:#6b7280; }

/* ---------- badges ---------- */
.badge { display:inline-block; padding:3px 13px; border-radius:999px; font-weight:600; font-size:.85rem; }
.b-low  { background:#dcfce7; color:#166534; }
.b-mod  { background:#fef3c7; color:#92400e; }
.b-high { background:#fee2e2; color:#991b1b; }

/* ---------- gate decision banner ---------- */
.decision { padding:18px 22px; border-radius:16px; font-size:1.2rem; font-weight:700; margin:6px 0 12px;
            border-left:8px solid; }
.decision small { display:block; font-weight:400; font-size:.92rem; margin-top:4px; }
.d-approve { background:#ecfdf5; color:#065f46; border-color:#10b981; }
.d-flag    { background:#fffbeb; color:#92400e; border-color:#f59e0b; }
.d-request { background:#fef2f2; color:#991b1b; border-color:#ef4444; }

/* ---------- pipeline steps ---------- */
.steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; margin:10px 0 18px; }
.step { background:#fff; border:1px solid #e6e8f0; border-top:5px solid var(--c); border-radius:14px;
        padding:14px 16px; box-shadow:0 1px 3px rgba(16,24,40,.05); }
.step .n { font-size:.75rem; font-weight:700; color:var(--c); letter-spacing:.08em; }
.step b  { display:block; font-size:1.02rem; margin:2px 0 6px; }
.step span { font-size:.86rem; color:#4b5563; line-height:1.4; display:block; }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:none; }
.stTabs [data-baseweb="tab"] { background:#fff; border:1px solid #e6e8f0; border-radius:12px;
                               padding:8px 18px; height:auto; }
.stTabs [aria-selected="true"] { background:#4f46e5; color:#fff !important; border-color:#4f46e5; }
.stTabs [aria-selected="true"] p { color:#fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }

/* ---------- misc ---------- */
.stButton > button { background:#4f46e5; color:#fff; border:none; border-radius:12px; padding:.55rem 1.4rem;
                     font-weight:600; }
.stButton > button:hover { background:#4338ca; color:#fff; }
h2, h3 { color:#1f2937; letter-spacing:-.2px; }
.note { background:#eef2ff; border:1px solid #c7d2fe; color:#3730a3; padding:12px 16px; border-radius:12px;
        font-size:.92rem; }
.warnbox { background:#fef2f2; border:1px solid #fecaca; color:#991b1b; padding:14px 18px; border-radius:12px; }
</style>
"""


def hero(title, subtitle, chips):
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    return f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p><div class="chips">{chip_html}</div></div>'


def kpi(label, value, sub=""):
    return (f'<div class="card kpi"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>')


def badge(category):
    cls = {"Low": "b-low", "Moderate": "b-mod", "High": "b-high"}.get(category, "b-low")
    return f'<span class="badge {cls}">{category} risk</span>'


def decision_banner(decision, reasons):
    cls = {"Approve": "d-approve", "Flag for review": "d-flag", "Request changes": "d-request"}[decision]
    icon = {"Approve": "&#10003;", "Flag for review": "&#9873;", "Request changes": "&#10005;"}[decision]
    why = "; ".join(reasons)
    return f'<div class="decision {cls}">{icon} {decision}<small>Why: {why}</small></div>'


def steps(items):
    """items = [(number, title, text, colour)]"""
    html = "".join(f'<div class="step" style="--c:{c}"><div class="n">STEP {n}</div><b>{t}</b><span>{d}</span></div>'
                   for n, t, d, c in items)
    return f'<div class="steps">{html}</div>'
