import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

st.set_page_config(
    page_title="Combustiveis Brasil | Flavio Paixao",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap');
:root {
    --bg: #0a0e17; --surface: #111827; --border: #1e2d45;
    --orange: #f97316; --blue: #38bdf8; --green: #22c55e;
    --text: #e2e8f0; --muted: #64748b;
}
html, body, [class*="css"] {
    font-family: 'Space Mono', monospace !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; color: var(--text) !important; }
.hero-label { font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: var(--orange); text-transform: uppercase; letter-spacing: 0.15em; }
.hero-title { font-family: 'Satoshi', sans-serif; font-size: clamp(28px, 4vw, 48px); font-weight: 800; color: var(--text); line-height: 1.1; margin: 8px 0 12px; }
.hero-sub { font-family: 'Space Mono', monospace; font-size: 14px; color: var(--muted); line-height: 1.7; }
.badge { display: inline-block; font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: var(--green); border: 1px solid var(--green); padding: 3px 10px; text-transform: uppercase; letter-spacing: 0.06em; margin-right: 8px; }
.badge-blue { color: var(--blue); border-color: var(--blue); }
.section-label { font-family: 'Space Mono', monospace; font-size: 11px; font-weight: 700; color: var(--orange); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }
.divider { height: 1px; background: var(--border); margin: 32px 0; }
.footer-text { font-family: 'Space Mono', monospace; font-size: 12px; color: var(--muted); text-align: center; padding: 24px 0; border-top: 1px solid var(--border); }
section[data-testid="stSidebar"] { background-color: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="metric-container"] { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--orange); padding: 16px !important; }
</style>
""", unsafe_allow_html=True)

BG = "#0a0e17"; SURFACE = "#111827"; BORDER = "#1e2d45"
ORANGE = "#f97316"; BLUE = "#38bdf8"; GREEN = "#22c55e"
TEXT = "#e2e8f0"; MUTED = "#64748b"

LAYOUT_BASE = dict(
    plot_bgcolor=BG, paper_bgcolor=BG,
    font=dict(color=MUTED, family="Space Mono, monospace", size=12),
    title=dict(font=dict(color=TEXT, family="Satoshi, sans-serif", size=18), x=0),
    xaxis=dict(showgrid=True, gridcolor=BORDER, title_font=dict(color=MUTED), tickfont=dict(color=MUTED)),
    yaxis=dict(showgrid=True, gridcolor=BORDER, title_font=dict(color=MUTED), tickfont=dict(color=MUTED)),
    margin=dict(l=40, r=40, t=60, b=40),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER, font=dict(color=TEXT, family="Space Mono")),
)

DATA_URL = "https://raw.githubusercontent.com/Flavio-Paixao/combustiveis-brasil-anp/main/dados_anp.csv"

@st.cache_data(show_spinner="Carregando dados da ANP...")
def carregar_dados():
    r = requests.get(DATA_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df["DATA_INICIAL"] = pd.to_datetime(df["DATA_INICIAL"], errors="coerce")
    df["ANO"] = df["DATA_INICIAL"].dt.year
    for col in ["PRECO_MEDIO", "PRECO_MINIMO", "PRECO_MAXIMO", "MARGEM_MEDIA"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = carregar_dados()

st.markdown("""
<div class="hero-label">Portfolio de Dados · Flavio Paixao</div>
<div class="hero-title">Painel de Combustiveis no Brasil</div>
<div class="hero-sub">Analise exploratoria dos precos de revenda de combustiveis com dados oficiais da ANP (2012-2026). Mais de 114 mil registros semanais por estado.</div>
<br>
<span class="badge">● Live</span>
<span class="badge badge-blue">ANP · Dados Abertos</span>
<span class="badge badge-blue">114k registros</span>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="section-label">Filtros</div>', unsafe_allow_html=True)
produtos = sorted(df["PRODUTO"].dropna().unique())
produto_sel = st.sidebar.selectbox("Combustivel", produtos, index=produtos.index("GASOLINA COMUM") if "GASOLINA COMUM" in produtos else 0)
anos = sorted(df["ANO"].dropna().unique().astype(int))
ano_range = st.sidebar.select_slider("Periodo", options=anos, value=(anos[0], anos[-1]))
regioes = ["Todas"] + sorted(df["REGIAO"].dropna().unique())
regiao_sel = st.sidebar.selectbox("Regiao", regioes)
st.sidebar.markdown("""<div class="hero-sub" style="font-size:12px;margin-top:16px;">Fonte: ANP — Agencia Nacional do Petroleo.<br><br>Desenvolvido por <b style="color:#f97316;">Flavio Paixao</b>.</div>""", unsafe_allow_html=True)

mask = (df["PRODUTO"] == produto_sel) & (df["ANO"] >= ano_range[0]) & (df["ANO"] <= ano_range[1])
if regiao_sel != "Todas":
    mask &= df["REGIAO"] == regiao_sel
df_f = df[mask].copy()

st.markdown('<div class="section-label">Visao Geral</div>', unsafe_allow_html=True)
st.markdown(f"### {produto_sel} — {ano_range[0]} a {ano_range[1]}")

preco_medio_geral = df_f["PRECO_MEDIO"].mean()
preco_min_geral = df_f["PRECO_MINIMO"].min()
preco_max_geral = df_f["PRECO_MAXIMO"].max()
registros = len(df_f)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Preco Medio (R$/L)", f"R$ {preco_medio_geral:.3f}" if pd.notna(preco_medio_geral) else "—")
c2.metric("Minimo Historico", f"R$ {preco_min_geral:.3f}" if pd.notna(preco_min_geral) else "—")
c3.metric("Maximo Historico", f"R$ {preco_max_geral:.3f}" if pd.notna(preco_max_geral) else "—")
c4.metric("Registros no Periodo", f"{registros:,}".replace(",", "."))

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Analise por Estado</div>', unsafe_allow_html=True)
st.markdown("### Preco Medio de Revenda por Estado")

preco_estado = df_f.groupby("ESTADO")["PRECO_MEDIO"].mean().reset_index().sort_values("PRECO_MEDIO").dropna()
fig_estado = px.bar(preco_estado, x="ESTADO", y="PRECO_MEDIO", text=preco_estado["PRECO_MEDIO"].map(lambda x: f"R$ {x:.3f}"), labels={"PRECO_MEDIO": "Preco Medio (R$/L)", "ESTADO": "Estado"})
fig_estado.update_traces(marker_color=ORANGE, marker_line_color=BLUE, marker_line_width=1, textposition="outside", textfont=dict(color=MUTED, size=10), opacity=0.9)
fig_estado.update_layout(**LAYOUT_BASE)
st.plotly_chart(fig_estado, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Serie Historica</div>', unsafe_allow_html=True)
st.markdown("### Evolucao do Preco Medio Nacional")

evolucao = df_f.groupby("DATA_INICIAL")["PRECO_MEDIO"].mean().reset_index().dropna().sort_values("DATA_INICIAL")
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=evolucao["DATA_INICIAL"], y=evolucao["PRECO_MEDIO"], mode="lines", line=dict(color=ORANGE, width=2), fill="tozeroy", fillcolor="rgba(249,115,22,0.08)", hovertemplate="<b>%{x|%d/%m/%Y}</b><br>R$ %{y:.3f}/L<extra></extra>"))
fig_hist.update_layout(**LAYOUT_BASE, showlegend=False)
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Analise Economica</div>', unsafe_allow_html=True)
st.markdown("### Regra dos 70% — Etanol vs Gasolina Comum")
st.markdown("""<div class="hero-sub">Se a razao <b style="color:#38bdf8;">Etanol / Gasolina</b> for menor que <b style="color:#f97316;">70%</b>, o etanol e economicamente mais vantajoso. Acima de 70%, a gasolina compensa.</div><br>""", unsafe_allow_html=True)

mask_70 = df["PRODUTO"].isin(["GASOLINA COMUM", "ETANOL HIDRATADO"]) & (df["ANO"] >= ano_range[0]) & (df["ANO"] <= ano_range[1])
df_70 = df[mask_70].copy()
paridade = df_70.groupby(["ESTADO", "PRODUTO"])["PRECO_MEDIO"].mean().unstack().reset_index().dropna(subset=["GASOLINA COMUM", "ETANOL HIDRATADO"])
paridade["Paridade (%)"] = paridade["ETANOL HIDRATADO"] / paridade["GASOLINA COMUM"] * 100
paridade["Recomendacao"] = paridade["Paridade (%)"].apply(lambda x: "Etanol vale a pena" if x <= 70 else "Gasolina vale a pena")
paridade = paridade.sort_values("Paridade (%)")

if not paridade.empty:
    fig_par = px.bar(paridade, x="ESTADO", y="Paridade (%)", color="Recomendacao", color_discrete_map={"Etanol vale a pena": GREEN, "Gasolina vale a pena": ORANGE}, text=paridade["Paridade (%)"].map(lambda x: f"{x:.1f}%"), labels={"Paridade (%)": "Etanol / Gasolina (%)", "ESTADO": "Estado"})
    fig_par.add_hline(y=70, line_dash="dash", line_color=BLUE, line_width=1.5, annotation_text="Limite 70%", annotation_font_color=BLUE, annotation_font_size=11)
    fig_par.update_traces(textposition="outside", textfont=dict(color=MUTED, size=10), opacity=0.9, marker_line_width=0)
    fig_par.update_layout(**LAYOUT_BASE, legend=dict(title=dict(text="Recomendacao", font=dict(color=TEXT)), bgcolor=SURFACE, bordercolor=BORDER, font=dict(color=MUTED)))
    st.plotly_chart(fig_par, use_container_width=True)
    etanol_ok = (paridade["Recomendacao"] == "Etanol vale a pena").sum()
    gasolina_ok = (paridade["Recomendacao"] == "Gasolina vale a pena").sum()
    c1, c2 = st.columns(2)
    c1.metric("Estados onde Etanol compensa", etanol_ok)
    c2.metric("Estados onde Gasolina compensa", gasolina_ok)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Comparativo Regional</div>', unsafe_allow_html=True)
st.markdown("### Preco Medio por Regiao ao Longo dos Anos")

evolucao_regiao = df_f.groupby(["ANO", "REGIAO"])["PRECO_MEDIO"].mean().reset_index().dropna()
fig_regiao = px.line(evolucao_regiao, x="ANO", y="PRECO_MEDIO", color="REGIAO", color_discrete_sequence=[ORANGE, BLUE, GREEN, "#a855f7", "#ec4899"], markers=True, labels={"PRECO_MEDIO": "Preco Medio (R$/L)", "ANO": "Ano", "REGIAO": "Regiao"})
fig_regiao.update_traces(line_width=2, marker_size=5)
fig_regiao.update_layout(**LAYOUT_BASE, legend=dict(title=dict(text="Regiao", font=dict(color=TEXT)), bgcolor=SURFACE, bordercolor=BORDER, font=dict(color=MUTED)))
st.plotly_chart(fig_regiao, use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Ranking</div>', unsafe_allow_html=True)
st.markdown("### Top 5 — Estados Mais Caros e Mais Baratos")

preco_rank = df_f.groupby("ESTADO")["PRECO_MEDIO"].mean().reset_index().sort_values("PRECO_MEDIO").dropna()
col_bar, col_car = st.columns(2)

with col_bar:
    st.markdown('<div class="section-label" style="color:#22c55e;">Mais Baratos</div>', unsafe_allow_html=True)
    top_bar = preco_rank.head(5)
    fig_bar = px.bar(top_bar, x="PRECO_MEDIO", y="ESTADO", orientation="h", text=top_bar["PRECO_MEDIO"].map(lambda x: f"R$ {x:.3f}"))
    fig_bar.update_traces(marker_color=GREEN, textposition="outside", textfont=dict(color=MUTED, size=10))
    fig_bar.update_layout(**LAYOUT_BASE, showlegend=False, yaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_car:
    st.markdown('<div class="section-label" style="color:#f97316;">Mais Caros</div>', unsafe_allow_html=True)
    fig_car.update_layout(**LAYOUT_BASE, showlegend=False, yaxis_title="")
    fig_car = px.bar(top_car, x="PRECO_MEDIO", y="ESTADO", orientation="h", text=top_car["PRECO_MEDIO"].map(lambda x: f"R$ {x:.3f}"))
    fig_car.update_traces(marker_color=ORANGE, textposition="outside", textfont=dict(color=MUTED, size=10))
    fig_car.update_layout(**LAYOUT_BASE, showlegend=False, yaxis_title="")
    st.plotly_chart(fig_car, use_container_width=True)

st.markdown("""<div class="footer-text">Dados: ANP — Agencia Nacional do Petroleo · Serie Historica Semanal por Estado (2012–2026)<br>Desenvolvido por <b style="color:#f97316;">Flavio Paixao</b> · <a href="https://github.com/Flavio-Paixao" style="color:#38bdf8;">GitHub</a> · <a href="https://linkedin.com/in/flaviopx" style="color:#38bdf8;">LinkedIn</a></div>""", unsafe_allow_html=True)
