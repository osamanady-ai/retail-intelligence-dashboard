"""Small shared visual system: inline SVG icons, accessible motion and Plotly theme.
No external icon/font/CDN requests are needed. Copied into each standalone project.
"""
from html import escape
import streamlit as st
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go

PATHS={
 'grid':'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
 'trend':'<path d="m3 17 6-6 4 4 8-10M15 5h6v6"/>',
 'return':'<path d="M9 7 4 12l5 5M4 12h10a6 6 0 0 1 6 6M4 4v3M18 3v5"/>',
 'wallet':'<rect x="3" y="5" width="18" height="15" rx="3"/><path d="M3 9h18M16 13h5v4h-5zM6 5V3h11"/>',
 'bag':'<path d="M5 7h14l2 14H3L5 7ZM8 8V6a4 4 0 0 1 8 0v2"/>',
 'target':'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
 'globe':'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 7h14M5 17h14"/>',
 'sliders':'<path d="M4 7h16M4 17h16M8 3v8M16 13v8"/><circle cx="8" cy="7" r="2"/><circle cx="16" cy="17" r="2"/>',
 'shield':'<path d="m12 3 8 3v5c0 5-4 8-8 10-4-2-8-5-8-10V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
 'layers':'<path d="m12 3 10 5-10 5L2 8l10-5ZM3 13l9 5 9-5M3 18l9 5 9-5"/>',
 'bird':'<path d="M8 6a4 4 0 0 1 8 0v4c4 8 1 11-4 11S4 18 8 10V6Z"/><path d="m16 6 4 2-4 1M10 7h1M7 13l-4 4M17 13l4 4M9 21l-2 1M15 21l2 1"/>',
 'ruler':'<path d="m3 15 12-12 6 6L9 21l-6-6ZM12 6l3 3M9 9l2 2M6 12l3 3"/>',
 'scale':'<path d="M4 21h16M12 4v17M4 7h16M4 7l-3 7h6L4 7ZM20 7l-3 7h6l-3-7Z"/>',
 'info':'<circle cx="12" cy="12" r="9"/><path d="M12 10v7M12 6v1"/>',
 'chart':'<path d="M3 3v18h18M7 17v-5M12 17V8M17 17V5"/>',
}


def icon(name,size=22):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{PATHS.get(name,PATHS["grid"])}</svg>'


def setup(mode):
    ecology=mode=='ecology'
    accent='#0d9488' if ecology else '#5753d9'
    accent_light='#e3f5ed' if ecology else '#eeedff'
    st.markdown(f'''<style>
:root{{--accent:{accent};--accent-light:{accent_light};--ink:#142033;--muted:#66758a}}
.stApp{{background:#f4f6fa;color:var(--ink)}}
.block-container{{padding:2.3rem 2.5rem 3rem;max-width:1600px}}
header[data-testid="stHeader"]{{background:transparent;height:2rem}}
h1,h2,h3{{color:var(--ink);letter-spacing:-.035em}}
section[data-testid="stSidebar"]{{background:#111d30;border-right:1px solid #233147}}
section[data-testid="stSidebar"] *{{color:#d4deec}}
section[data-testid="stSidebar"] [data-baseweb="select"] *{{color:#243147}}
section[data-testid="stSidebar"] [data-baseweb="input"] *{{color:#243147}}
section[data-testid="stSidebar"] input{{color:#243147!important}}
section[data-testid="stSidebar"] [data-testid="stDateInputField"] *{{color:#243147!important}}
section[data-testid="stSidebar"] [data-testid="stDateInput"] input{{-webkit-text-fill-color:#243147!important;color:#243147!important}}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input{{-webkit-text-fill-color:#243147!important;color:#243147!important}}
section[data-testid="stSidebar"] label p{{font-size:12px;color:#b4c3d8;letter-spacing:.015em}}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"]{{background:var(--accent)}}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] *{{color:white}}
section[data-testid="stSidebar"] h2{{font-size:1rem;margin-top:1rem;color:white}}
.brand{{display:flex;gap:11px;align-items:center;color:#fff;font-size:18px;font-weight:750;letter-spacing:-.025em;margin:10px 0 26px}}
.brand-mark{{display:grid;place-items:center;width:40px;height:40px;border-radius:12px;background:var(--accent);color:#fff}}
.side-label{{font-size:10px;color:#8da0ba!important;letter-spacing:.16em;font-weight:700;margin-top:26px;margin-bottom:12px}}
.side-footer{{padding:16px;border:1px solid #354256;border-radius:12px;font-size:11px;line-height:1.7;color:#aebcd0!important;margin-top:30px}}
.workspace-top{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:22px}}
.breadcrumb{{display:flex;align-items:center;gap:9px;color:#67768d;font-size:12px;font-weight:600}}
.workspace-chip{{border:1px solid #dbe3ed;padding:6px 10px;border-radius:20px;font-size:10px;letter-spacing:.08em;color:#506078;background:#fff;white-space:nowrap}}
.hero{{position:relative;overflow:hidden;border-radius:20px;padding:26px 30px;background:#14223b;color:white;display:flex;align-items:center;justify-content:space-between;gap:28px;box-shadow:0 10px 30px #182a4710;margin-bottom:22px;animation:arrive .5s ease-out both}}
.hero:after{{content:'';position:absolute;right:-40px;top:-90px;width:330px;height:330px;border:1px solid #ffffff12;border-radius:50%;box-shadow:0 0 0 45px #ffffff05,0 0 0 90px #ffffff03;pointer-events:none}}
.hero .eyebrow{{display:flex;align-items:center;gap:7px;font-size:10px;letter-spacing:.16em;font-weight:650;color:#b7c7e5;margin-bottom:12px}}
.hero h1{{font-family:Arial,sans-serif;color:white!important;font-size:35px;line-height:1.15;margin:0 0 12px;padding:0;letter-spacing:-.04em;font-weight:750}}
.hero p{{color:#b7c7e0;font-size:13px;max-width:570px;line-height:1.7;margin:0}}
.hero-badge{{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border:1px solid #55728c;border-radius:7px;color:#c9e9db;font-size:10px;margin-top:17px;background:#ffffff06}}
.hero-stamp{{position:relative;z-index:1;min-width:145px;padding:20px;border-left:1px solid #ffffff25;color:#9fb5d7}}
.hero-stamp strong{{display:block;font-size:30px;letter-spacing:-.05em;color:white;margin:8px 0 3px}}
.hero-stamp small{{font-size:11px;color:#a5b8d5}}
div[data-testid="stMetric"]{{background:#fff;border:1px solid #e3e8f0;border-radius:14px;padding:16px 18px;min-height:112px;box-shadow:0 3px 9px #182a4703;transition:transform .18s,box-shadow .18s;animation:arrive .5s ease-out both}}
div[data-testid="stMetric"]:hover{{transform:translateY(-3px);box-shadow:0 10px 25px #182a4710}}
div[data-testid="stMetricValue"]{{font-size:28px!important;font-weight:720;letter-spacing:-.04em;color:var(--ink)}}
div[data-testid="stMetricLabel"] p{{font-size:11px!important;color:#63728a!important;font-weight:600}}
.metric-icon{{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;color:var(--accent);background:var(--accent-light);margin-bottom:9px}}
.section-title{{display:flex;align-items:center;gap:9px;margin:24px 0 6px;font-size:17px;letter-spacing:-.025em;font-weight:700;color:var(--ink)}}
.section-title span{{display:grid;place-items:center;color:var(--accent)}}
div[data-testid="stTabs"] [role="tablist"]{{background:white;border:1px solid #e3e8f0;border-radius:12px;padding:5px;gap:4px;margin:12px 0 4px}}
div[data-testid="stTabs"] [role="tab"]{{padding:9px 16px;border-radius:8px;height:auto;min-height:40px}}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"]{{background:var(--accent-light);color:var(--accent);font-weight:700}}
div[data-testid="stTabs"] [role="tab"] p{{font-size:12px}}
div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{{display:none}}
div[data-testid="stPlotlyChart"]{{background:white;border:1px solid #e3e8f0;border-radius:14px;overflow:hidden;box-shadow:0 2px 8px #182a4703;animation:arrive .6s ease-out both}}
div[data-testid="stAlert"]{{border-radius:10px;font-size:12px}}
div[data-testid="stAlert"] p{{font-size:12px}}
.stCaption p{{font-size:11px;color:#718098}}
div[data-testid="stDataFrame"]{{border-radius:12px;overflow:hidden}}
div[data-testid="stDownloadButton"] button{{border-radius:8px;color:var(--accent);border-color:#dce3ee}}
.insight-strip{{display:flex;align-items:flex-start;gap:11px;background:var(--accent-light);border:1px solid #d9e6e7;padding:14px 17px;border-radius:12px;margin:8px 0 14px;color:#36536a;font-size:12px;line-height:1.7}}
.insight-strip svg{{color:var(--accent);flex:none;margin-top:2px}}
@keyframes arrive{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
@media(prefers-reduced-motion:reduce){{*,*:before,*:after{{animation:none!important;transition:none!important;scroll-behavior:auto!important}}}}
@media(max-width:700px){{.block-container{{padding:3rem 1rem}}.workspace-chip{{display:none}}.hero{{padding:23px 20px;display:block}}.hero h1{{font-size:30px}}.hero-stamp{{display:none}}div[data-testid="stMetric"]{{min-height:95px}}.metric-icon{{display:none}}div[data-testid="stTabs"] [role="tablist"]{{overflow:auto}}}}
</style>''',unsafe_allow_html=True)
    palette=['#0d9488','#f4a640','#7281d8','#d86583'] if ecology else ['#5753d9','#16a899','#f4b04b','#e47594']
    template=go.layout.Template(layout=go.Layout(
        font=dict(family='Arial, sans-serif',color='#63728a',size=11),
        paper_bgcolor='#ffffff',plot_bgcolor='#ffffff',colorway=palette,
        title=dict(font=dict(size=15,color='#17263d'),x=.055,y=.94),
        margin=dict(l=54,r=28,t=70,b=50),
        xaxis=dict(showgrid=False,linecolor='#e5eaf2',zeroline=False,title_font_size=11),
        yaxis=dict(gridcolor='#eef1f6',zeroline=False,title_font_size=11),
        legend=dict(title_text='',font_size=10,bgcolor='rgba(255,255,255,.8)'),
        hoverlabel=dict(bgcolor='#14223b',font_color='white',bordercolor='#14223b'),
        transition=dict(duration=400,easing='cubic-in-out')))
    pio.templates['portfolio']=template
    pio.templates.default='portfolio'
    px.defaults.template='portfolio';px.defaults.color_discrete_sequence=palette


def header(mode):
    eco=mode=='ecology'
    brand='FIELDNOTES' if eco else 'RETAIL / IQ'
    logo='bird' if eco else 'grid'
    st.sidebar.markdown(f'<div class="brand"><div class="brand-mark">{icon(logo,23)}</div>{brand}</div><div class="side-label">ANALYTICS WORKSPACE</div>',unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="breadcrumb">{icon("sliders",17)}<span>Filter & explore</span></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="workspace-top"><div class="breadcrumb">{icon(logo,17)}<span>Portfolio / {"Ecology" if eco else "Commerce"} / Overview</span></div><div class="workspace-chip">REAL DATA · LOCAL WORKSPACE</div></div>',unsafe_allow_html=True)
    title='Penguin Field Notes' if eco else 'Retail Intelligence'
    description='A closer look at species, size and the shape of a real Antarctic field sample.' if eco else 'From individual transactions to the bigger picture. Explore sales, credits and customer behavior.'
    source='PALMER ARCHIPELAGO / 2007-2009' if eco else 'UCI ONLINE RETAIL / 2010-2011'
    stamp='344' if eco else '541,909'
    noun='real penguin observations' if eco else 'original transaction lines'
    st.markdown(f'<div class="hero"><div><div class="eyebrow">{icon("chart",15)} {source}</div><h1>{title}</h1><p>{description}</p><div class="hero-badge">{icon("shield",14)} Source-attributed · No synthetic data</div></div><div class="hero-stamp">{icon("layers",28)}<strong>{stamp}</strong><small>{noun}</small></div></div>',unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="side-footer">{icon("shield",18)}<br><strong>Transparent by design</strong><br>{"Missing values are visible. No measurements are invented." if eco else "GBP values. Credits separated. No profit claims without cost data."}<br>Source notes in Data & methods.</div>',unsafe_allow_html=True)


def metrics(labels,values,icons):
    for column,label,value,name in zip(st.columns(len(labels)),labels,values,icons):
        with column:
            st.markdown(f'<div class="metric-icon">{icon(name,20)}</div>',unsafe_allow_html=True)
            st.metric(label,value)


def section(title,name='chart'):
    st.markdown(f'<div class="section-title"><span>{icon(name,21)}</span>{escape(title)}</div>',unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight-strip">{icon("info",19)}<span>{escape(text)}</span></div>',unsafe_allow_html=True)
