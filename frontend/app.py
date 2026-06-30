"""
Startup Simulator — Frontend
Run: streamlit run frontend/app.py
"""
import re, time, threading
import requests
import plotly.graph_objects as go
import streamlit as st

import os
API = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Startup Simulator",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
.stApp{background:#09090b}
[data-testid="stSidebar"]{background:#0d0d10;border-right:1px solid #1c1c21}
.block-container{padding:28px 36px 48px 36px;max-width:1280px}

.rc{background:#111115;border:1px solid #1c1c21;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-blue{background:#0a0e1f;border:1px solid #312e81;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-green{background:#031a0e;border:1px solid #14532d;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-amber{background:#150c00;border:1px solid #78350f;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-red{background:#150000;border:1px solid #7f1d1d;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-orange{background:#160900;border:1px solid #9a3412;border-radius:10px;padding:16px 18px;margin-bottom:10px}
.rc-purple{background:#0f0a1e;border:1px solid #4c1d95;border-radius:10px;padding:16px 18px;margin-bottom:10px}

.rl{font-size:11px;font-weight:800;letter-spacing:1.8px;color:#9ca3af;text-transform:uppercase;margin-bottom:7px}
.rl-blue{font-size:11px;font-weight:800;letter-spacing:1.8px;color:#a5b4fc;text-transform:uppercase;margin-bottom:7px}
.rl-green{font-size:11px;font-weight:800;letter-spacing:1.8px;color:#6ee7b7;text-transform:uppercase;margin-bottom:7px}
.rl-orange{font-size:11px;font-weight:800;letter-spacing:1.8px;color:#fdba74;text-transform:uppercase;margin-bottom:7px}
.rl-purple{font-size:11px;font-weight:800;letter-spacing:1.8px;color:#d8b4fe;text-transform:uppercase;margin-bottom:7px}
.rv{font-size:13px;color:#f3f4f6;line-height:1.75}

.rb-p{display:inline-block;background:#064e3b;color:#6ee7b7;border:1px solid #059669;padding:4px 16px;border-radius:5px;font-size:11px;font-weight:700;letter-spacing:1px}
.rb-v{display:inline-block;background:#451a03;color:#fcd34d;border:1px solid #d97706;padding:4px 16px;border-radius:5px;font-size:11px;font-weight:700;letter-spacing:1px}
.rb-a{display:inline-block;background:#450a0a;color:#fca5a5;border:1px solid #dc2626;padding:4px 16px;border-radius:5px;font-size:11px;font-weight:700;letter-spacing:1px}

.rx{border-left:3px solid #6366f1;padding:10px 14px;background:#0d0d10;border-radius:0 6px 6px 0;font-size:12px;color:#6b7280;line-height:1.65;margin:6px 0 18px 0}

.rg{display:inline-block;background:#1e1b4b;color:#a5b4fc;border-radius:4px;padding:2px 8px;font-size:11px;font-family:monospace;margin-right:4px;font-weight:600}

[data-testid="stSidebar"] .stButton>button{background:transparent;color:#9ca3af;border:1px solid transparent;border-radius:6px;font-size:12px;font-weight:500;padding:8px 12px;width:100%;margin-bottom:2px}
[data-testid="stSidebar"] .stButton>button:hover{background:#18181b;color:#f3f4f6;border-color:#374151}

.stButton>button{background:#18181b;color:#e5e7eb;border:1px solid #374151;border-radius:7px;font-size:12px;font-weight:500;padding:8px 14px}
.stButton>button:hover{background:#374151;color:#f9fafb;border-color:#818cf8}

[data-testid="stDownloadButton"]>button{background:#064e3b;color:#6ee7b7;border:1px solid #059669;border-radius:7px;font-size:12px;font-weight:500}
[data-testid="stDownloadButton"]>button:hover{background:#065f46}

[data-testid="metric-container"]{background:#111115;border:1px solid #1c1c21;border-radius:10px;padding:14px 16px}

.stTextInput input,.stTextArea textarea{background:#111115;border:1px solid #374151;color:#f9fafb;border-radius:8px;font-size:13px}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#818cf8;box-shadow:0 0 0 3px rgba(129,140,248,0.15)}

.stTabs [data-baseweb="tab-list"]{background:transparent;border-bottom:1px solid #1c1c21;gap:0}
.stTabs [data-baseweb="tab"]{color:#6b7280;font-size:12px;font-weight:500;padding:10px 16px;background:transparent}
.stTabs [aria-selected="true"]{color:#f3f4f6;border-bottom:2px solid #818cf8;background:transparent}

[data-testid="stExpander"]{background:#111115;border:1px solid #1c1c21;border-radius:10px}

.stProgress>div>div>div{background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:4px}

#MainMenu,footer,header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{visibility:hidden;height:0;overflow:hidden}
</style>""", unsafe_allow_html=True)

# ── Session ────────────────────────────────────────────────────────────────────
for k, v in [("page","dashboard"),("sim_id",None),("chat",[]),("chat_loaded",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── API ────────────────────────────────────────────────────────────────────────
def _get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=300)
        r.raise_for_status()
        return r.json()
    except requests.ConnectionError:
        st.error("Backend offline — run:  uvicorn backend.main:app --reload")
        return None
    except requests.HTTPError as e:
        try:   detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def _post(path, data):
    try:
        r = requests.post(f"{API}{path}", json=data, timeout=300)
        r.raise_for_status()
        return r.json()
    except requests.ConnectionError:
        st.error("Backend offline — run:  uvicorn backend.main:app --reload")
        return None
    except requests.HTTPError as e:
        try:   detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        st.error(f"API error: {detail}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def _delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def _pdf(sid):
    try:
        r = requests.get(f"{API}/report/{sid}/pdf", timeout=60)
        r.raise_for_status()
        return r.content
    except Exception as e:
        st.warning(f"PDF unavailable: {e}")
        return None

def _load_chat(sid):
    d = _get(f"/chat/{sid}")
    if d:
        st.session_state.chat = d.get("messages", [])

def _save_chat(sid):
    if st.session_state.chat:
        _post(f"/chat/{sid}", {"messages": st.session_state.chat})

# ── Colour utils ───────────────────────────────────────────────────────────────
_VC  = {"Proceed":"rb-p","Pivot":"rb-v","Abandon":"rb-a"}
_VLB = {"Proceed":"PROCEED","Pivot":"PIVOT","Abandon":"ABANDON"}

def sc(s): return "#6ee7b7" if s>=65 else ("#fcd34d" if s>=40 else "#fca5a5")

# ── UI helpers ────────────────────────────────────────────────────────────────
def _card_cls(style):
    return {"blue":"rc-blue","green":"rc-green","amber":"rc-amber",
            "red":"rc-red","orange":"rc-orange","purple":"rc-purple"}.get(style,"rc")

def _lbl_cls(style):
    return {"blue":"rl-blue","green":"rl-green","orange":"rl-orange",
            "purple":"rl-purple"}.get(style,"rl")

def card(label, text, style=""):
    if not text: return
    st.markdown(
        f'<div class="{_card_cls(style)}">'
        f'<div class="{_lbl_cls(style)}">{label}</div>'
        f'<div class="rv">{text}</div></div>',
        unsafe_allow_html=True)

def bullets(label, items, style=""):
    if not items: return
    dot = {"green":"#34d399","amber":"#fcd34d","red":"#fca5a5",
           "orange":"#fb923c","blue":"#818cf8","purple":"#c084fc"}.get(style,"#818cf8")
    rows = "".join(
        f'<div style="display:flex;gap:10px;padding:8px 0;border-top:1px solid #1c1c21;align-items:flex-start">'
        f'<div style="width:5px;height:5px;border-radius:50%;background:{dot};flex-shrink:0;margin-top:7px"></div>'
        f'<div style="font-size:13px;color:#d1d5db;line-height:1.65">{i}</div></div>'
        for i in items
    )
    st.markdown(
        f'<div class="{_card_cls(style)}">'
        f'<div class="{_lbl_cls(style)}">{label}</div>'
        f'{rows}</div>',
        unsafe_allow_html=True)

def sec(title, color="#9ca3af"):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 14px 0">'
        f'<span style="font-size:11px;font-weight:800;letter-spacing:2px;color:{color};'
        f'text-transform:uppercase;white-space:nowrap">{title}</span>'
        f'<div style="flex:1;height:1px;background:#1c1c21"></div></div>',
        unsafe_allow_html=True)

def explain(text):
    st.markdown(
        f'<div class="rx"><span style="color:#818cf8;font-weight:700;font-size:11px">'
        f'HOW TO READ: </span>{text}</div>',
        unsafe_allow_html=True)

def sub(text):
    st.markdown(
        f'<p style="color:#9ca3af;font-size:13px;line-height:1.7;margin-bottom:16px">{text}</p>',
        unsafe_allow_html=True)

def divider():
    st.markdown("<hr style='border-color:#1c1c21;margin:16px 0'>", unsafe_allow_html=True)

# ── Plotly ─────────────────────────────────────────────────────────────────────
_T = dict(
    paper_bgcolor="#111115", plot_bgcolor="#111115",
    font=dict(color="#9ca3af", family="ui-sans-serif,system-ui,sans-serif", size=12),
    margin=dict(l=20,r=20,t=44,b=20),
    hoverlabel=dict(bgcolor="#1f2937",bordercolor="#374151",font=dict(color="#f9fafb",size=12)),
)
_G  = dict(gridcolor="#1c1c21", zerolinecolor="#374151")
_CF = dict(displayModeBar=True,scrollZoom=False,displaylogo=False,
           modeBarButtonsToRemove=["lasso2d","select2d","autoScale2d"],
           responsive=True,toImageButtonOptions=dict(format="png",scale=2))

def show(fig):
    if fig: st.plotly_chart(fig, use_container_width=True, config=_CF)

def chart_radar(bd):
    cats = ["Problem","Market","Competition","Team","Financials"]
    vals = [bd.get("problem_strength",0),bd.get("market_opportunity",0),
            bd.get("competitive_position",0),bd.get("team_execution",0),
            bd.get("financial_viability",0)]
    if not any(vals): return None
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(129,140,248,0.12)",
        line=dict(color="#818cf8",width=2),
        hovertemplate="<b>%{theta}</b><br>%{r}/20<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Score Breakdown", font=dict(size=12,color="#6b7280"), x=0.5),
        polar=dict(radialaxis=dict(visible=True,range=[0,20],gridcolor="#1c1c21",
                                   color="#4b5563",tickfont=dict(size=9)),
                   angularaxis=dict(gridcolor="#1c1c21",tickfont=dict(size=11,color="#9ca3af")),
                   bgcolor="#111115"),
        showlegend=False, height=310, **_T)
    return fig

def chart_market(ms):
    parts = re.findall(r'\$([0-9.]+)\s*([BMKbmk])', ms or "")
    if not parts: return None
    names = ["TAM","SAM","SOM"]
    vals, lbls = [], []
    for i,(n,u) in enumerate(parts[:3]):
        vals.append(float(n)*{"B":1000,"M":1,"K":0.001}[u.upper()])
        lbls.append(f"{names[i]}: ${n}{u.upper()}")
    if not vals: return None
    fig = go.Figure(go.Bar(
        x=lbls, y=vals,
        marker=dict(color=["#6366f1","#8b5cf6","#a78bfa"][:len(vals)],line=dict(width=0)),
        text=[f"${v:,.0f}M" for v in vals], textposition="outside",
        textfont=dict(color="#e5e7eb",size=12),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}M<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Market Size (USD Millions)", font=dict(size=12,color="#6b7280"), x=0.5),
        yaxis=dict(title="USD Millions",**_G,color="#6b7280"),
        xaxis=dict(**_G,color="#6b7280"),
        height=320, **_T)
    return fig

def chart_competitors(details):
    if not details: return None
    names, funds = [], []
    for d in details[:6]:
        m = re.search(r'\$([0-9.]+)\s*([BMKbmk])', d.get("funding",""))
        if m:
            names.append(d.get("name","?"))
            funds.append(float(m.group(1))*{"B":1000,"M":1,"K":0.001}[m.group(2).upper()])
    if not funds: return None
    colors = ["#6366f1","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe","#ede9fe"]
    fig = go.Figure(go.Bar(
        y=names, x=funds, orientation="h",
        marker=dict(color=colors[:len(funds)],line=dict(width=0)),
        text=[f"${f:,.0f}M" for f in funds], textposition="outside",
        textfont=dict(color="#e5e7eb",size=11),
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}M raised<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Competitor Funding (USD Millions)", font=dict(size=12,color="#6b7280"), x=0.5),
        xaxis=dict(title="Total Raised ($M)",**_G,color="#6b7280"),
        yaxis=dict(**_G,color="#9ca3af",automargin=True),
        height=max(260,len(names)*54), **_T)
    return fig

def chart_gauge(score):
    clr = "#34d399" if score>=7 else ("#fcd34d" if score>=4 else "#fca5a5")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        title={"text":"Investor Confidence","font":{"color":"#6b7280","size":11}},
        gauge={"axis":{"range":[1,10],"tickcolor":"#4b5563","tickfont":{"color":"#6b7280","size":9}},
               "bar":{"color":clr,"thickness":0.22},
               "bgcolor":"#1c1c21","bordercolor":"#374151",
               "steps":[{"range":[1,4],"color":"rgba(252,165,165,0.1)"},
                        {"range":[4,7],"color":"rgba(252,211,77,0.1)"},
                        {"range":[7,10],"color":"rgba(52,211,153,0.1)"}],
               "threshold":{"line":{"color":clr,"width":2},"thickness":0.75,"value":score}},
        number={"font":{"color":clr,"size":40},"suffix":"/10"},
    ))
    fig.update_layout(height=270, **_T)
    return fig

def chart_timeline(plan):
    if not plan: return None
    clrs = ["#6366f1","#10b981","#f59e0b"]
    lbls = ["Days 1-30","Days 31-60","Days 61-90"]
    fig  = go.Figure()
    for i, step in enumerate(plan[:3]):
        short = (step[:65]+"...") if len(step)>65 else step
        fig.add_trace(go.Bar(
            x=[30], y=[lbls[i]], orientation="h", base=i*30,
            marker=dict(color=clrs[i],line=dict(width=0),opacity=0.85),
            name=lbls[i], text=short, textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#09090b",size=10),
            hovertemplate=f"<b>{lbls[i]}</b><br>{step}<extra></extra>",
        ))
    fig.update_layout(
        title=dict(text="90-Day Execution Timeline", font=dict(size=12,color="#6b7280"), x=0.5),
        barmode="overlay", showlegend=False,
        xaxis=dict(title="Day",range=[0,92],tickvals=[0,30,60,90],
                   ticktext=["Day 0","Day 30","Day 60","Day 90"],**_G,color="#6b7280"),
        yaxis=dict(**_G,color="#9ca3af",automargin=True),
        height=220, **_T)
    return fig

def chart_score_bar(bd, total):
    if not bd: return None
    cats = ["Problem","Market","Competition","Team","Financials"]
    keys = ["problem_strength","market_opportunity","competitive_position",
            "team_execution","financial_viability"]
    vals = [bd.get(k,0) for k in keys]
    clrs = [("#34d399" if v>=14 else "#fcd34d" if v>=8 else "#fca5a5") for v in vals]
    fig  = go.Figure(go.Bar(
        x=cats, y=vals, marker=dict(color=clrs,line=dict(width=0),opacity=0.85),
        text=[f"{v}/20" for v in vals], textposition="outside",
        textfont=dict(color="#e5e7eb",size=11),
        hovertemplate="<b>%{x}</b><br>Score: %{y}/20<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"Dimension Scores — Total: {total}/100",
                   font=dict(size=12,color="#6b7280"), x=0.5),
        yaxis=dict(range=[0,23],**_G,color="#6b7280",title="Score / 20"),
        xaxis=dict(**_G,color="#9ca3af"),
        height=300, **_T)
    return fig

# ── Glossary ───────────────────────────────────────────────────────────────────
_GL = {"TAM":"Total Addressable Market — full global opportunity at 100% share",
       "SAM":"Serviceable Addressable Market — portion your product can target",
       "SOM":"Serviceable Obtainable Market — realistic near-term share",
       "CAGR":"Compound Annual Growth Rate — year-on-year market growth",
       "MVP":"Minimum Viable Product — simplest version delivering real value",
       "UVP":"Unique Value Proposition — what makes you different from competitors",
       "CAC":"Customer Acquisition Cost — cost to win one paying customer",
       "LTV":"Lifetime Value — total revenue expected from one customer",
       "MRR":"Monthly Recurring Revenue — predictable subscription revenue",
       "PMF":"Product-Market Fit — evidence customers love your product",
       "VC":"Venture Capital — investors who fund high-growth startups",
       "DPIIT":"Dept for Promotion of Industry and Internal Trade (India)",
       "80-IAC":"Indian tax section — 3-year tax holiday for startups",
       "ESOP":"Employee Stock Option Plan — equity for employees",
       "Moat":"Durable competitive advantage that takes 18+ months to copy",
       "GTM":"Go-To-Market — strategy for reaching paying customers",
       "ARR":"Annual Recurring Revenue — MRR multiplied by 12",
       "MoM":"Month-over-Month growth comparison"}

def glossary():
    with st.expander("Glossary — expand if any abbreviation is unfamiliar"):
        items = list(_GL.items())
        c1, c2 = st.columns(2)
        for col, chunk in zip([c1,c2],[items[:len(items)//2],items[len(items)//2:]]):
            with col:
                for k, v in chunk:
                    st.markdown(
                        f'<div style="margin-bottom:8px;display:flex;gap:8px;align-items:flex-start">'
                        f'<span class="rg">{k}</span>'
                        f'<span style="font-size:12px;color:#6b7280;line-height:1.5">{v}</span></div>',
                        unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:4px 0 20px 0">'
        '<div style="font-size:15px;font-weight:700;color:#f9fafb;letter-spacing:-0.3px">'
        'Startup Simulator</div>'
        '<div style="font-size:11px;color:#4b5563;margin-top:3px">'
        'AI-powered startup analysis</div></div>',
        unsafe_allow_html=True)

    for k, lbl in [("dashboard","Dashboard"),("new_sim","New Simulation"),
                   ("results","View Report"),("qa","Report Q&A")]:
        if st.button(lbl, key=f"nav_{k}", use_container_width=True):
            st.session_state.page = k
            if k in ("results","qa"):
                st.session_state.chat_loaded = False
            st.rerun()

    st.markdown("<hr style='border-color:#1c1c21;margin:16px 0'>", unsafe_allow_html=True)

    h   = _get("/health")
    dot = "#34d399" if h else "#fca5a5"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:10px">'
        f'<div style="width:7px;height:7px;border-radius:50%;background:{dot}"></div>'
        f'<span style="font-size:11px;color:#6b7280">'
        f'Backend {"Online" if h else "Offline"}</span></div>',
        unsafe_allow_html=True)

    if h and st.button("Test LLM", use_container_width=True):
        with st.spinner("Testing..."):
            t = _get("/test-llm")
        if t and t.get("llm_ok"): st.success("LLM working")
        else:                      st.error("LLM failed — check .env")

    st.markdown("<hr style='border-color:#1c1c21;margin:16px 0'>", unsafe_allow_html=True)

    hist = _get("/history")
    if hist and hist.get("simulations"):
        st.markdown(
            '<div style="font-size:10px;letter-spacing:1.5px;color:#374151;'
            'text-transform:uppercase;margin-bottom:8px">Recent</div>',
            unsafe_allow_html=True)
        for s in hist["simulations"][:7]:
            lbl = (s["idea"][:30]+"...") if len(s["idea"])>30 else s["idea"]
            st.button(lbl, key=f"sb_{s['id']}", use_container_width=True,
                      on_click=lambda sid=s["id"]: (
                          st.session_state.update(
                              sim_id=sid, page="results", chat_loaded=False)))

    st.markdown(
        '<div style="font-size:10px;color:#1f2937;margin-top:20px;line-height:1.6">'
        'LangGraph · FastAPI · ChromaDB</div>',
        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.title("Dashboard")
    sub("Overview of all startup simulations run on this system.")
    data = _get("/history")
    if not data: return
    sims = data.get("simulations", [])
    if not sims:
        st.markdown(
            '<div class="rc" style="text-align:center;padding:40px;color:#4b5563">'
            'No simulations yet. Go to <b style="color:#818cf8">New Simulation</b>'
            ' to run your first analysis.</div>',
            unsafe_allow_html=True)
        return

    scores = [s["final_score"] for s in sims]
    vs     = [s["verdict"]     for s in sims]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Simulations", len(sims))
    c2.metric("Average Score",     f"{sum(scores)//len(scores)}/100")
    c3.metric("Proceed",           vs.count("Proceed"))
    c4.metric("Pivot / Abandon",   vs.count("Pivot")+vs.count("Abandon"))

    if len(sims) >= 2:
        fig = go.Figure(go.Bar(
            x=[(s["idea"][:22]+"...") if len(s["idea"])>22 else s["idea"] for s in sims],
            y=scores,
            marker=dict(color=[sc(s) for s in scores],line=dict(width=0),opacity=0.85),
            text=scores, textposition="outside",
            textfont=dict(color="#e5e7eb",size=11),
            hovertemplate="<b>%{x}</b><br>%{y}/100<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text="Viability Scores", font=dict(size=12,color="#6b7280"), x=0.5),
            yaxis=dict(range=[0,115],**_G,color="#6b7280",title="Score /100"),
            xaxis=dict(**_G,color="#9ca3af"),
            height=280, **_T)
        show(fig)

    divider()
    for s in sims:
        vc = _VC.get(s["verdict"],"rb-v")
        ca, cb, cc = st.columns([6,1,1])
        with ca:
            st.markdown(
                f'<div class="rc">'
                f'<div style="font-size:14px;font-weight:600;color:#f9fafb">{s["idea"]}</div>'
                f'<div style="margin-top:7px;display:flex;align-items:center;gap:14px;flex-wrap:wrap">'
                f'<code style="font-size:11px;color:#4b5563;background:#18181b;'
                f'padding:2px 8px;border-radius:4px">{s["id"]}</code>'
                f'<span style="font-size:11px;color:#4b5563">'
                f'{s["timestamp"][:16].replace("T"," ")}</span>'
                f'<span style="font-size:12px;font-weight:700;color:{sc(s["final_score"])}">'
                f'{s["final_score"]}/100</span>'
                f'<span class="{vc}">{_VLB.get(s["verdict"],"")}</span>'
                f'</div></div>',
                unsafe_allow_html=True)
        with cb:
            st.write("")
            if st.button("Open", key=f"v_{s['id']}"):
                st.session_state.sim_id=s["id"]; st.session_state.page="results"
                st.session_state.chat_loaded=False; st.rerun()
        with cc:
            st.write("")
            if st.button("Delete", key=f"d_{s['id']}"):
                _delete(f"/report/{s['id']}"); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# NEW SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
def page_new_sim():
    st.title("New Simulation")
    sub("Eight AI agents analyse your idea with live web search: Founder, Market, Competitor, "
        "Customer, Investor, Failure, India Policy, and Judge. Expected time: 3 to 5 minutes.")

    with st.expander("System check"):
        if st.button("Test LLM Connection"):
            with st.spinner("Testing..."):
                r = _get("/test-llm")
            if r and r.get("llm_ok"): st.success("LLM working — ready.")
            else: st.error("LLM failed. Check OPENROUTER_MODEL and OPENROUTER_API_KEY in .env.")

    with st.form("simform"):
        idea = st.text_area("Startup Idea",
            placeholder="Be specific. Example: An AI platform for Indian kirana stores that "
                        "photographs the shelf, auto-tracks inventory, predicts restocking in "
                        "48 hours, and connects directly to FMCG distributors — replacing the "
                        "manual notebook system used by 12 million stores.",
            height=140,
            help="More detail = better analysis. Include: the problem, who it is for, how it solves it.")
        run = st.form_submit_button("Run Simulation", use_container_width=True)

    if run:
        if not idea or len(idea.strip()) < 10:
            st.error("Please describe your idea in more detail."); return

        steps = [(10,"Founder agent — researching existing solutions..."),
                 (22,"Market agent — finding market size and CAGR data..."),
                 (35,"Competitor agent — mapping the competitive landscape..."),
                 (48,"Customer agent — researching real user pain points..."),
                 (56,"India Policy agent — finding schemes and VCs..."),
                 (68,"Investor agent — evaluating investability..."),
                 (81,"Failure agent — researching failed similar startups..."),
                 (93,"Judge agent — computing final verdict...")]
        prog = st.progress(0,"Initialising...")
        result = {"d": None, "done": False, "error": None}

        def _run():
            # Must NOT call st.error() from a background thread — Streamlit is
            # not thread-safe.  Use raw requests here; show errors in main thread.
            try:
                r = requests.post(
                    f"{API}/simulate",
                    json={"idea": idea.strip()},
                    timeout=360,
                )
                r.raise_for_status()
                result["d"] = r.json()
            except requests.ConnectionError:
                result["error"] = "Backend offline. Make sure uvicorn is running."
            except requests.HTTPError as e:
                try:
                    result["error"] = e.response.json().get("detail", str(e))
                except Exception:
                    result["error"] = str(e)
            except Exception as e:
                result["error"] = str(e)
            finally:
                result["done"] = True

        threading.Thread(target=_run, daemon=True).start()

        # Keep looping until backend thread finishes.
        # 5s sleep = more responsive than 15s, and we never exit early.
        idx = 0
        while not result["done"]:
            if idx < len(steps):
                p, msg = steps[idx]
                prog.progress(p, msg)
                idx += 1
            else:
                prog.progress(96, "Saving report and building Q&A index...")
            time.sleep(5)

        prog.progress(100, "Complete.")
        time.sleep(0.8)

        r = result["d"]
        if r and r.get("simulation_id"):
            sid = r["simulation_id"]
            st.session_state.sim_id      = sid
            st.session_state.page        = "results"
            st.session_state.chat_loaded = False
            st.rerun()
        else:
            err = result.get("error") or "No report was returned."
            st.error(f"Simulation failed: {err}")


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def page_results():
    st.title("Simulation Report")
    sid = st.session_state.get("sim_id")
    if not sid: st.warning("No simulation selected — pick one from the sidebar."); return

    data = _get(f"/report/{sid}")
    if not data: return

    f=data.get("founder",{}); m=data.get("market",{}); c=data.get("competitor",{})
    cu=data.get("customer",{}); inv=data.get("investor",{}); fl=data.get("failure",{})
    ip=data.get("india_policy",{}); j=data.get("judge",{})
    score=j.get("final_score",0); v=j.get("verdict","Pivot")
    sclr=sc(score); vc=_VC.get(v,"rb-v")

    # Header
    st.markdown(
        f'<div class="rc" style="margin-bottom:16px;border-left:4px solid #6366f1">'
        f'<div style="font-size:11px;letter-spacing:1.5px;color:#4b5563;'
        f'text-transform:uppercase;margin-bottom:6px">ID: {sid} | '
        f'{data.get("timestamp","")[:16].replace("T"," ")}</div>'
        f'<div style="font-size:17px;font-weight:700;color:#f9fafb;line-height:1.4">'
        f'{data.get("idea","")}</div></div>',
        unsafe_allow_html=True)

    # Actions
    a1,a2,a3 = st.columns(3)
    with a1:
        safe = data.get("idea","report")[:30].replace(" ","_").replace("/","")
        st.markdown(
            f'<a href="{API}/report/{sid}/pdf" download="startup_report_{safe}.pdf" '
            f'style="display:block;background:#064e3b;color:#6ee7b7;border:1px solid #059669;'
            f'border-radius:7px;font-size:12px;font-weight:600;padding:9px 14px;'
            f'text-align:center;text-decoration:none;width:100%;box-sizing:border-box">'
            f'Download PDF Report</a>',
            unsafe_allow_html=True)
    with a2:
        if st.button("Open Q&A",use_container_width=True):
            st.session_state.page="qa"; st.session_state.chat_loaded=False; st.rerun()
    with a3:
        if st.button("Delete Report",use_container_width=True):
            _delete(f"/report/{sid}")
            st.session_state.sim_id=None; st.session_state.page="dashboard"; st.rerun()

    divider()

    # Score row
    cs,cr,cv = st.columns([1,1,2])
    with cs:
        st.markdown(
            f'<div class="rc" style="padding:24px;text-align:center;border-top:3px solid {sclr}">'
            f'<div class="rl">Viability Score</div>'
            f'<div style="font-size:72px;font-weight:900;line-height:1;letter-spacing:-4px;'
            f'color:{sclr}">{score}</div>'
            f'<div style="font-size:18px;color:#374151;margin:4px 0 12px">/ 100</div>'
            f'<span class="{vc}">{_VLB.get(v,"")}</span></div>',
            unsafe_allow_html=True)
        st.metric("Investor Score",f"{inv.get('investment_score',0)}/10",
                  help="1-3=Pass. 4-6=Interested. 7-8=Ready to fund. 9-10=Exceptional.")
    with cr:
        show(chart_radar(j.get("scoring_breakdown",{})))
    with cv:
        if j.get("one_line_verdict"):
            st.markdown(
                f'<div class="rc-purple" style="margin-bottom:10px">'
                f'<div class="rl-purple">Bottom Line</div>'
                f'<div style="font-size:14px;color:#d8b4fe;font-style:italic;line-height:1.7">'
                f'"{j["one_line_verdict"]}"</div></div>',
                unsafe_allow_html=True)
        card("Judge Summary", j.get("summary",""))

    explain("Radar chart scores five dimensions out of 20 each. Wider = stronger all-round viability. "
            "Pointed gaps show where you need the most work before raising investment.")

    divider(); glossary(); divider()

    tabs = st.tabs(["Founder","Market","Competitor","Customer",
                    "Investor","Failure","India Policy","Action Plan","Conclusion"])

    with tabs[0]:
        sub("Defines the problem, who you solve it for, and what the first version of your product looks like.")
        r1,r2 = st.columns(2)
        with r1:
            card("Problem Being Solved",f.get("problem",""))
            card("Target Market",f.get("target_market",""))
            card("Unique Value Proposition",f.get("unique_value_proposition",""),style="blue")
        with r2:
            card("Minimum Viable Product (MVP)",f.get("mvp",""))
            card("Problem Evidence",f.get("problem_evidence",""))
            card("Founder-Market Fit Required",f.get("founder_market_fit",""))
        bullets("Similar Companies Found",f.get("similar_companies",[]))
        bullets("Critical Success Factors",f.get("success_factors",[]),style="green")

    with tabs[1]:
        sub("Estimates the size of the opportunity and whether it is growing fast enough to justify building a startup.")
        show(chart_market(m.get("market_size","")))
        explain("TAM = total global market. SAM = the portion your product can serve. "
                "SOM = what you can realistically win in 3 years. "
                "Hover bars for exact values. SOM above $50M + CAGR above 15% is investor-grade.")
        r1,r2 = st.columns(2)
        with r1:
            card("Market Size — TAM / SAM / SOM",m.get("market_size",""))
            card("Growth Rate (CAGR)",m.get("growth_rate",""))
            card("Why Now",m.get("why_now",""))
        with r2:
            bullets("Market Statistics (Research-backed)",m.get("market_statistics",[]))
            bullets("Revenue Models",m.get("revenue_models",[]),style="blue")
        divider()
        r3,r4 = st.columns(2)
        with r3: bullets("Key Opportunities",m.get("opportunities",[]))
        with r4: bullets("Market Trends",m.get("trends",[]),style="purple")
        bullets("Target Segments",m.get("target_segments",[]))

    with tabs[2]:
        sub("Maps who already exists in your market to find gaps and define positioning. A moat is a durable advantage.")
        show(chart_competitors(c.get("competitor_details",[])))
        explain("Each bar shows how much funding a competitor has raised. "
                "More funding = more resources. Your goal is to find the gap they all ignore. "
                "Hover bars for names and amounts.")
        card("Market Map",c.get("market_map",""))
        card("Competitive Advantage / Moat",c.get("competitive_advantage",""),style="blue")
        card("Positioning Strategy",c.get("positioning_strategy",""))
        divider()
        for d in c.get("competitor_details",[]):
            with st.expander(f"{d.get('name','Competitor')} — {d.get('funding','unknown funding')}"):
                dc1,dc2 = st.columns(2)
                with dc1: bullets("Strengths",d.get("strengths",[]),style="green")
                with dc2: bullets("Weaknesses",d.get("weaknesses",[]),style="red")
                card("Strategy to Win",d.get("how_to_beat",""))
        if not c.get("competitor_details"): bullets("Competitors",c.get("competitors",[]))
        bullets("Market Gaps — Underserved Needs",c.get("gaps",[]),style="amber")

    with tabs[3]:
        sub("Personas are realistic representations of your ideal customers built from research.")
        for p in cu.get("personas",[]):
            st.markdown(
                f'<div class="rc" style="border-left:3px solid #818cf8;margin-bottom:8px">'
                f'<div class="rl-blue">User Persona</div>'
                f'<div class="rv">{p}</div></div>',
                unsafe_allow_html=True)
        divider()
        r1,r2 = st.columns(2)
        with r1:
            bullets("Pain Points — In User's Own Words",cu.get("pain_points",[]),style="amber")
            card("Willingness to Pay",cu.get("willingness_to_pay",""),style="green")
        with r2:
            bullets("Acquisition Channels and CAC",cu.get("acquisition_channels",[]))
            card("Early Adopter Profile",cu.get("early_adopter_profile",""),style="blue")
        bullets("Community Insights — From Online Research",cu.get("community_insights",[]))
        card("Customer Journey — 7 Steps from Problem to Paid",cu.get("customer_journey",""))

    with tabs[4]:
        sub("Evaluates fundability from a VC perspective — which investors to target and what traction to hit first.")
        r1,r2 = st.columns([1,2])
        with r1:
            show(chart_gauge(inv.get("investment_score",0)))
            explain("1-3=Pass. 4-6=Interested but needs proof. 7-8=Ready to fund. 9-10=Exceptional.")
        with r2:
            card("Funding Stage Recommendation",inv.get("funding_stage",""))
            card("Suggested Raise Structure",inv.get("suggested_raise",""),style="blue")
            card("Exit Potential",inv.get("exit_potential",""))
            card("Investor Concerns",inv.get("concerns",""),style="amber")
        divider()
        r3,r4 = st.columns(2)
        with r3:
            bullets("Investment Strengths",inv.get("strengths",[]),style="green")
            bullets("Key Investor Metrics",inv.get("key_metrics_for_investors",[]),style="blue")
        with r4:
            bullets("Key Risks",inv.get("risks",[]),style="red")
        divider()
        bullets("Relevant VCs — From Web Research",inv.get("relevant_investors",[]),style="purple")
        bullets("Real Funding Examples",inv.get("funding_examples",[]),style="amber")

    with tabs[5]:
        sub("Identifies the specific ways this startup could fail with full causal chains.")
        card("Biggest Single Risk",fl.get("biggest_single_risk",""),style="red")
        card("Runway Analysis",fl.get("runway_analysis",""))
        divider()
        r1,r2 = st.columns(2)
        with r1: bullets("Failure Modes — Causal Chains",fl.get("failure_modes",[]),style="red")
        with r2: bullets("Mitigation Strategies",fl.get("mitigation_strategies",[]),style="green")
        divider()
        bullets("Real Companies That Failed Here",fl.get("failed_companies",[]),style="amber")
        r3,r4 = st.columns(2)
        with r3: bullets("Critical Success Factors",fl.get("critical_success_factors",[]),style="green")
        with r4: bullets("Pivot Options",fl.get("pivot_options",[]))

    with tabs[6]:
        sub("India has significant government support for startups. DPIIT recognition unlocks "
            "tax holidays, angel tax exemption, and fast-track patents.")
        card("DPIIT / Startup India Eligibility",ip.get("startup_india_eligibility",""),style="orange")
        divider()
        i1,i2 = st.columns(2)
        with i1:
            bullets("DPIIT Benefits",ip.get("dpiit_benefits",[]),style="orange")
            bullets("Tax Benefits",ip.get("tax_benefits",[]),style="green")
            bullets("Key Indian Markets",ip.get("key_indian_markets",[]))
        with i2:
            bullets("Government Schemes — With Amounts",ip.get("government_schemes",[]),style="orange")
            bullets("Grants and Subsidies",ip.get("grants_and_subsidies",[]),style="amber")
        divider()
        bullets("Indian VCs Active in This Space",ip.get("indian_vcs",[]),style="purple")
        divider()
        i3,i4 = st.columns(2)
        with i3:
            bullets("Accelerators and Incubators",ip.get("accelerators_incubators",[]),style="blue")
            bullets("Regulatory Requirements",ip.get("regulatory_requirements",[]),style="red")
        with i4:
            bullets("State-Level Incentives",ip.get("state_incentives",[]),style="amber")
        divider()
        sec("Compliance Checklist","#fb923c")
        for i,item in enumerate(ip.get("compliance_checklist",[])):
            st.markdown(
                f'<div style="display:flex;gap:14px;padding:9px 0;'
                f'border-bottom:1px solid #1c1c21;align-items:flex-start">'
                f'<div style="color:#fb923c;font-size:10px;font-weight:700;'
                f'flex-shrink:0;margin-top:2px;font-family:monospace">0{i+1}</div>'
                f'<div style="font-size:13px;color:#d1d5db;line-height:1.65">{item}</div></div>',
                unsafe_allow_html=True)

    with tabs[7]:
        sub("A concrete 90-day plan — what to build, who to talk to, what metrics prove traction.")
        r1,r2 = st.columns(2)
        with r1: show(chart_score_bar(j.get("scoring_breakdown",{}),score))
        with r2: show(chart_timeline(j.get("action_plan_90_days",[])))
        explain("Left: dimension scores out of 20. Green=strong (14+), amber=needs work (8-13), "
                "red=critical gap (below 8). Right: 90-day phases — hover for full milestone details.")
        divider()
        bullets("Top Recommendations",j.get("recommendations",[]),style="blue")
        divider()
        card("Go-To-Market Strategy",j.get("go_to_market",""),style="blue")
        divider()
        sec("90-Day Plan — Detailed","#818cf8")
        for i,step in enumerate(j.get("action_plan_90_days",[])):
            pc = ["#6366f1","#10b981","#f59e0b"][i%3]
            lb = ["Days 1-30","Days 31-60","Days 61-90"][i%3]
            st.markdown(
                f'<div style="display:flex;gap:14px;margin-bottom:10px;align-items:flex-start">'
                f'<div style="background:{pc};color:#09090b;font-size:10px;font-weight:700;'
                f'padding:3px 10px;border-radius:4px;flex-shrink:0;margin-top:3px;'
                f'white-space:nowrap">{lb}</div>'
                f'<div style="font-size:13px;color:#d1d5db;line-height:1.7">{step}</div></div>',
                unsafe_allow_html=True)
        divider()
        bullets("Key Metrics to Track Weekly",j.get("key_metrics",[]),style="green")

    with tabs[8]:
        sub("Consolidated summary for anyone who wants the bottom line without reading the full report.")

        st.markdown(
            f'<div class="rc" style="border-top:3px solid {sclr};padding:28px;margin-bottom:16px">'
            f'<div class="rl">Overall Verdict</div>'
            f'<div style="display:flex;align-items:flex-end;gap:16px;margin:10px 0 14px">'
            f'<span style="font-size:72px;font-weight:900;line-height:1;letter-spacing:-4px;'
            f'color:{sclr}">{score}</span>'
            f'<span style="font-size:20px;color:#374151;margin-bottom:10px">/ 100</span>'
            f'<span class="{vc}" style="font-size:13px;padding:6px 18px;margin-bottom:6px">'
            f'{_VLB.get(v,"")}</span></div>'
            f'<div style="font-size:14px;color:#9ca3af;font-style:italic;line-height:1.7;'
            f'border-left:3px solid {sclr}40;padding-left:14px">'
            f'"{j.get("one_line_verdict","")}"</div></div>',
            unsafe_allow_html=True)

        card("Summary",j.get("summary",""))
        divider()
        cc1,cc2 = st.columns(2)
        with cc1: bullets("Top Strengths",inv.get("strengths",[])[:3],style="green")
        with cc2: bullets("Top Risks",    inv.get("risks",[])[:3],    style="red")

        divider()
        recs = j.get("recommendations",[])
        if recs:
            st.markdown(
                f'<div class="rc-blue">'
                f'<div class="rl-blue">Most Important Action Right Now</div>'
                f'<div style="font-size:14px;color:#e0e7ff;line-height:1.75">{recs[0]}</div></div>',
                unsafe_allow_html=True)
        if len(recs)>1: bullets("All Recommendations",recs,style="blue")

        divider()
        if ip.get("startup_india_eligibility"):
            st.markdown(
                f'<div class="rc-orange">'
                f'<div class="rl-orange">India Opportunity</div>'
                f'<div class="rv">{ip["startup_india_eligibility"]}</div>'
                f'<div style="font-size:12px;color:#6b7280;margin-top:8px">'
                f'Key scheme: {(ip.get("government_schemes") or [""])[0][:200]}</div></div>',
                unsafe_allow_html=True)

        divider()
        sec("Investment Readiness Checklist","#818cf8")
        checks = [
            ("Problem validated with 20+ customer interviews",  bool(f.get("problem_evidence"))),
            ("Market size quantified with data sources",        bool(m.get("market_size") and "$" in m.get("market_size",""))),
            ("Competitive moat clearly defined",                bool(c.get("competitive_advantage"))),
            ("Willingness-to-pay validated with real users",    bool(cu.get("willingness_to_pay"))),
            ("MVP scoped and buildable within 60 days",         bool(f.get("mvp"))),
            ("DPIIT recognition obtained",                      "yes" in ip.get("startup_india_eligibility","").lower()),
            ("90-day plan with measurable milestones",          bool(j.get("action_plan_90_days"))),
            ("Target investors identified",                     bool(inv.get("relevant_investors"))),
        ]
        for item, done in checks:
            clr = "#34d399" if done else "#374151"
            sym = "+" if done else "-"
            tc  = "#f3f4f6" if done else "#4b5563"
            st.markdown(
                f'<div style="display:flex;gap:10px;padding:8px 0;'
                f'border-bottom:1px solid #1c1c21;align-items:center">'
                f'<div style="width:18px;height:18px;border:1px solid {clr};border-radius:4px;'
                f'display:flex;align-items:center;justify-content:center;flex-shrink:0;'
                f'font-size:11px;font-weight:700;color:{clr}">{sym}</div>'
                f'<span style="font-size:13px;color:{tc}">{item}</span></div>',
                unsafe_allow_html=True)

        divider()
        st.markdown(
            '<div style="font-size:11px;color:#374151;line-height:1.7">'
            'Disclaimer: AI-generated for informational purposes only. '
            'Verify all market figures, funding data, and company information independently '
            'before making any business or investment decisions.</div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Q&A
# ══════════════════════════════════════════════════════════════════════════════
def page_qa():
    st.title("Report Q&A")
    sid = st.session_state.get("sim_id")
    if not sid: st.warning("No simulation selected — pick one from the sidebar."); return

    if not st.session_state.chat_loaded:
        _load_chat(sid); st.session_state.chat_loaded = True

    data = _get(f"/report/{sid}")
    if data:
        j    = data.get("judge",{})
        sclr2 = sc(j.get("final_score",0))
        st.markdown(
            f'<div class="rc" style="margin-bottom:16px;border-left:4px solid #6366f1">'
            f'<div class="rl">Discussing</div>'
            f'<div style="font-size:14px;font-weight:600;color:#f9fafb;margin:4px 0">'
            f'{data.get("idea","")}</div>'
            f'<div style="font-size:11px;color:#4b5563">'
            f'Score: <b style="color:{sclr2}">{j.get("final_score",0)}/100</b>'
            f'&nbsp;|&nbsp;<code style="color:#374151">{sid}</code></div></div>',
            unsafe_allow_html=True)

    sub("Ask any question about this startup analysis. The system retrieves relevant sections and answers with specific data.")

    sec("Suggested Questions","#818cf8")
    sugg = ["What government schemes apply?",
            "Which Indian VCs should we target?",
            "What are the top three risks?",
            "How do we get the first 100 customers?",
            "How much should we raise and at what valuation?",
            "Which failed startups are most similar?"]
    cols = st.columns(3)
    for i,s in enumerate(sugg):
        with cols[i%3]:
            if st.button(s, key=f"sq_{i}", use_container_width=True):
                st.session_state.chat.append({"role":"user","content":s})
                with st.spinner("Searching report..."):
                    r = _post("/ask",{"simulation_id":sid,"question":s})
                if r:
                    st.session_state.chat.append({"role":"assistant","content":r.get("answer","")})
                    _save_chat(sid)
                st.rerun()

    divider()
    for msg in st.session_state.chat:
        with st.chat_message(msg.get("role","user")):
            st.markdown(msg.get("content",""))

    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("chatform", clear_on_submit=True):
        ci,cb = st.columns([6,1])
        with ci: q = st.text_input("Question", label_visibility="collapsed",
                                   placeholder="Ask anything about this startup analysis...")
        with cb: send = st.form_submit_button("Send", use_container_width=True)

    if send and q.strip():
        st.session_state.chat.append({"role":"user","content":q.strip()})
        with st.spinner("Thinking..."):
            r = _post("/ask",{"simulation_id":sid,"question":q.strip()})
        if r:
            st.session_state.chat.append({"role":"assistant","content":r.get("answer","")})
            _save_chat(sid)
        st.rerun()

    divider()
    cl1,cl2 = st.columns(2)
    with cl1:
        if st.session_state.chat and st.button("Clear Chat History",use_container_width=True):
            _delete(f"/chat/{sid}")
            st.session_state.chat=[]; st.session_state.chat_loaded=False; st.rerun()
    with cl2:
        if st.button("Back to Report",use_container_width=True):
            st.session_state.page="results"; st.rerun()


# ── Router ─────────────────────────────────────────────────────────────────────
p = st.session_state.get("page","dashboard")
if   p=="dashboard": page_dashboard()
elif p=="new_sim":   page_new_sim()
elif p=="results":   page_results()
elif p=="qa":        page_qa()