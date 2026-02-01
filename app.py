import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Projet MES/ARDL – Tchad (1995–2022)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PROFESSIONAL STYLING ====================
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --accent-color: #9467bd;
    }
    
    /* Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Cards and boxes */
    .metric-box {
        background: linear-gradient(135deg, #1f77b4 0%, #1a5fa0 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .highlight-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
        border-left: 5px solid #1f77b4;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .result-box {
        background: rgba(31, 119, 180, 0.05);
        border-left: 4px solid #1f77b4;
        padding: 12px;
        border-radius: 4px;
    }
    
    /* Headers */
    .section-header {
        border-left: 5px solid #1f77b4;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    
    .table-title {
        font-size: 1.3em;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def safe_log(s: pd.Series):
    s = pd.to_numeric(s, errors="coerce")
    s = s.where(s > 0)
    return np.log(s)

def format_sig(p):
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""

def to_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df_ in sheets.items():
            df_.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()

def format_results_table(df, title=""):
    """Format a results table with professional styling"""
    st.markdown(f'<div class="table-title">{title}</div>', unsafe_allow_html=True)
    
    styled_df = df.style
    
    # Color coefficients
    coef_cols = [c for c in df.columns if 'Coefficient' in c or 'Estimate' in c]
    if coef_cols:
        def color_coef(val):
            try:
                v = float(val)
                max_val = max(abs(df[coef_cols[0]]).max(), 1)
                intensity = min(abs(v)/max_val, 0.4)
                if v > 0:
                    return f'background-color: rgba(44, 160, 44, {intensity})'
                else:
                    return f'background-color: rgba(214, 39, 40, {intensity})'
            except:
                return ''
        styled_df = styled_df.applymap(color_coef, subset=coef_cols)
    
    # Color p-values
    pval_cols = [c for c in df.columns if 'p-value' in c or 'Pr(>|t|)' in c]
    if pval_cols:
        def color_pval(val):
            try:
                v = float(val)
                if v < 0.01:
                    return 'background-color: rgba(214, 39, 40, 0.4); color: white; font-weight: bold'
                elif v < 0.05:
                    return 'background-color: rgba(214, 39, 40, 0.3); font-weight: bold'
                elif v < 0.1:
                    return 'background-color: rgba(255, 127, 14, 0.2)'
                else:
                    return 'background-color: rgba(200, 200, 200, 0.1)'
            except:
                return ''
        styled_df = styled_df.applymap(color_pval, subset=pval_cols)
    
    styled_df = styled_df.format(precision=4)
    st.dataframe(styled_df, use_container_width=True)

def create_coefficient_chart(df, title=""):
    """Create a professional chart showing coefficients"""
    coef_col = None
    var_col = 'Variable'
    
    if 'Coefficient' in df.columns:
        coef_col = 'Coefficient'
    elif 'Estimate' in df.columns:
        coef_col = 'Estimate'
    else:
        return
    
    # Filter out intercept/constant
    df_plot = df[~df[var_col].str.contains('Intercept|Constant', na=False)].copy()
    if df_plot.empty:
        return
    
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in df_plot[coef_col]]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_plot[var_col],
            x=df_plot[coef_col],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            hovertemplate='<b>%{y}</b><br>Coef: %{x:.4f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="Coefficient",
        yaxis_title="Variable",
        height=400,
        showlegend=False,
        template="plotly_white",
        margin=dict(l=150, r=50, t=50, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==================== DATA LOADING ====================

st.sidebar.title("⚙️ Paramètres")
default_path = "base.xlsx"
use_default = st.sidebar.checkbox("Charger automatiquement base.xlsx", value=True)
uploaded = st.sidebar.file_uploader("Ou téléverse ton fichier Excel", type=["xlsx"])

@st.cache_data(show_spinner=False)
def load_data_from_excel(file_like) -> pd.DataFrame:
    return pd.read_excel(file_like)

df = None
if uploaded is not None:
    df = load_data_from_excel(uploaded)
    st.sidebar.success("✅ Données chargées (upload).")
elif use_default:
    try:
        df = load_data_from_excel(default_path)
        st.sidebar.success("✅ Données chargées (base.xlsx).")
    except Exception:
        st.sidebar.warning("⚠️ base.xlsx introuvable.")
        df = None
else:
    st.sidebar.info("📁 Téléverse un fichier.")

expected_cols = ["year","GROWTH","REM","TC","FDI","OPEN","CREDIT","INV","INF","MIGSTOCK","HOSTGDP"]

# ==================== RESULTS DATA ====================

res_3sls_eq1 = pd.DataFrame({
    "Variable": ["(Intercept)", "GROWTH", "MIGSTOCK", "HOSTGDP", "logTC"],
    "Estimate": [19.867206200, -0.049708380, 0.000853106, -0.450865283, -1.998338922],
    "Std. Error": [0.337291584, 0.001640530, 0.005728275, 0.012902207, 0.049374055],
    "t value": [58.90217, -30.30019, 0.14893, -34.94482, -40.47346],
    "Pr(>|t|)": [0.0, 0.0, 0.88291, 0.0, 0.0],
})
res_3sls_eq1["Sig"] = res_3sls_eq1["Pr(>|t|)"].apply(format_sig)

res_3sls_eq2 = pd.DataFrame({
    "Variable": ["(Intercept)", "logREM", "logINV", "OPEN", "logFDI", "logTC"],
    "Estimate": [-64.0286419, 6.9329983, 0.3976088, 0.4263826, -0.0071939, 0.6139383],
    "Std. Error": [130.7465478, 7.8687708, 6.1718758, 0.0879557, 0.0568619, 14.4947751],
    "t value": [-0.48972, 0.88108, 0.06442, 4.84770, -0.12652, 0.04236],
    "Pr(>|t|)": [0.62918, 0.38780, 0.94922, 7.6231e-05, 0.90047, 0.96660],
})
res_3sls_eq2["Sig"] = res_3sls_eq2["Pr(>|t|)"].apply(format_sig)

res_3sls_eq3 = pd.DataFrame({
    "Variable": ["(Intercept)", "logREM", "CREDIT", "GROWTH", "INF"],
    "Estimate": [4.6102489, -0.4648178, 0.1363536, 0.0740374, 0.0168264],
    "Std. Error": [2.1739193, 0.3688956, 0.0602302, 0.0334644, 0.0167276],
    "t value": [2.12071, -1.26003, 2.26387, 2.21242, 1.00590],
    "Pr(>|t|)": [0.044943, 0.220296, 0.033323, 0.037141, 0.324928],
})
res_3sls_eq3["Sig"] = res_3sls_eq3["Pr(>|t|)"].apply(format_sig)

res_3sls_eq4 = pd.DataFrame({
    "Variable": ["(Intercept)", "logREM", "GROWTH", "logINV", "HOSTGDP"],
    "Estimate": [131.589512, -15.134111, 2.395862, -0.589054, 0.595468],
    "Std. Error": [123.522193, 15.736289, 0.789872, 13.955603, 7.280021],
    "t value": [1.06531, -0.96173, 3.03323, -0.04221, 0.08179],
    "Pr(>|t|)": [0.29779, 0.34619, 0.00591, 0.96670, 0.93552],
})
res_3sls_eq4["Sig"] = res_3sls_eq4["Pr(>|t|)"].apply(format_sig)

ardl_general = pd.DataFrame({
    "Variable": ["L(GROWTH,1)", "logREM","L(logREM,1)","L(logREM,2)", "logINV","L(logINV,1)","L(logINV,2)",
                 "logOPEN","L(logOPEN,1)", "INF","L(INF,1)","L(INF,2)","L(INF,3)",
                 "logCREDIT","L(logCREDIT,1)","L(logCREDIT,2)","L(logCREDIT,3)",
                 "logTC","L(logTC,1)", "logFDI","L(logFDI,1)","L(logFDI,2)","L(logFDI,3)", "Constant"],
    "Coefficient": [-0.139283, -14.065258, 0.814373, 3.478532, -1.494072, 12.180486, -4.376342,
                    5.883577, 4.602755, -0.366516, -0.270084, 0.006172, 0.225961,
                    -5.238680, -13.878765, 15.429603, 5.595321, 9.669343, -40.599514,
                    -0.045632, 0.586344, -0.029744, -0.443065, 193.713570],
    "p-value": [0.02416, 0.00307, 0.05571, 0.00583, 0.08327, 0.01421, 0.02008,
                0.00700, 0.00946, 0.00346, 0.01617, 0.44050, 0.01498,
                0.01116, 0.00460, 0.00349, 0.00958, 0.00917, 0.00235,
                0.05533, 0.00313, 0.09182, 0.00331, 0.00425]
})
ardl_general["Sig"] = ardl_general["p-value"].apply(format_sig)

ecm_short = pd.DataFrame({
    "Variable": ["d(logREM)", "d(L(logREM,1))", "d(logINV)", "d(L(logINV,1))", "d(logOPEN)",
                 "d(INF)","d(L(INF,1))","d(L(INF,2))", "d(logCREDIT)","d(L(logCREDIT,1))","d(L(logCREDIT,2))",
                 "d(logTC)", "d(logFDI)","d(L(logFDI,1))","d(L(logFDI,2))", "ect", "Constant"],
    "Coefficient": [-14.065, -3.479, -1.494, 4.376, 5.884, -0.367, -0.232, -0.226,
                    -5.239, -21.025, -5.595, 9.669, -0.046, 0.473, 0.443, -1.139, 193.714],
})

long_run = pd.DataFrame({
    "Variable": ["logREM","logINV","logOPEN","INF","logCREDIT","logTC","logFDI"],
    "Coefficient (LR)": [-5.0981021, 10.4298151, 27.7491541, -1.3883375, -3.7688735, -36.4546632, 0.7089692]
})

bounds_test = pd.DataFrame({
    "Test": ["Pesaran Bounds"],
    "F-stat": [5.3808],
    "CV 5% I(0)": [2.73],
    "CV 5% I(1)": [4.163],
    "Result": ["✅ Cointégration"]
})

ardl_diag = pd.DataFrame({
    "Test": ["Wilcoxon", "t-test", "ARCH LM", "Box-Pierce", "Ljung-Box", "Lilliefors", "Shapiro-Wilk"],
    "p-value": [0.9368, 1.0, 0.214, 0.4823, 0.3432, 0.8563, 0.6508],
    "Status": ["✅", "✅", "✅", "✅", "✅", "✅", "✅"]
})

granger = pd.DataFrame({
    "Variable": ["logREM","logINV","logOPEN","INF","logCREDIT","logTC","logFDI"],
    "F": [1.0089, 4.1263, 4.6084, 0.3763, 0.1844, 2.6538, 2.5814],
    "p-value": [0.4117, 0.02164, 0.01461, 0.7712, 0.9056, 0.07975, 0.0854]
})

# ==================== PAGE HEADER ====================

st.markdown("""
<div style="background: linear-gradient(135deg, #1f77b4 0%, #1a5fa0 100%); padding: 40px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0; font-size: 2.8em;">📊 Dashboard Professionnel ARDL/ECM</h1>
    <h2 style="color: #e8f4f8; margin: 15px 0 0 0; font-weight: 400; font-size: 1.4em;">Modèle de Transferts de Fonds & Croissance | Tchad 1995–2022</h2>
</div>
""", unsafe_allow_html=True)

st.caption("🔬 Analyse: Données • Séries • ARDL/ECM • Pesaran Bounds • Causalité Granger • Système 3SLS • Scénarios | Visualization enrichie avec couleurs professionnelles")

tabs = st.tabs([
    "📁 Données",
    "📈 Séries & KPIs",
    "🧩 ARDL/ECM",
    "🔁 Granger",
    "🧠 3SLS",
    "🎛️ Scénarios",
    "⬇️ Export"
])

# ==================== TAB 0: DONNÉES ====================

with tabs[0]:
    st.markdown('<div class="section-header"><h2>📊 Gestion des Données</h2></div>', unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ Aucune donnée chargée.")
    else:
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            st.error(f"❌ Colonnes manquantes : {missing}")
        else:
            df = df.sort_values("year").reset_index(drop=True).copy()
            df["logREM"] = safe_log(df["REM"])
            df["logTC"]  = safe_log(df["TC"])
            df["logFDI"] = safe_log(df["FDI"])
            df["logOPEN"]= safe_log(df["OPEN"])
            df["logCREDIT"]= safe_log(df["CREDIT"])
            df["logINV"] = safe_log(df["INV"])

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📅 Période", f"{int(df.year.min())}–{int(df.year.max())}")
            with col2:
                st.metric("📊 Obs", df.shape[0])
            with col3:
                st.metric("📈 Vars", df.shape[1])
            with col4:
                st.metric("🔲 Manquants", int(df.isna().sum().sum()))
            with col5:
                completeness = (1 - df.isna().sum().sum()/(df.shape[0]*df.shape[1]))*100
                st.metric("✅ Complétude", f"{completeness:.1f}%")

            st.markdown("---")
            data_tabs = st.tabs(["📋 Aperçu", "📊 Stats", "📉 Distribs"])
            
            with data_tabs[0]:
                st.dataframe(df.head(20), use_container_width=True)
            
            with data_tabs[1]:
                st.dataframe(df[expected_cols].describe().T.style.format(precision=3), use_container_width=True)
            
            with data_tabs[2]:
                col1, col2 = st.columns(2)
                with col1:
                    var = st.selectbox("Distribution", [c for c in expected_cols if c != 'year'])
                    fig = px.histogram(df, x=var, nbins=15, color_discrete_sequence=['#1f77b4'])
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    corr = df[[c for c in expected_cols if c != 'year']].corr()
                    fig_corr = px.imshow(corr, color_continuous_scale="RdBu", zmin=-1, zmax=1)
                    st.plotly_chart(fig_corr, use_container_width=True)

# ==================== TAB 1: SÉRIES & KPIs ====================

with tabs[1]:
    st.markdown('<div class="section-header"><h2>📈 Séries Temporelles</h2></div>', unsafe_allow_html=True)
    
    if df is not None:
        cols = [c for c in expected_cols if c != "year"]
        var = st.selectbox("Sélectionner une variable", cols)
        
        fig = px.line(df, x="year", y=var, markers=True, color_discrete_sequence=['#1f77b4'],
                     title=f"<b>{var}</b> - Évolution 1995-2022")
        fig.update_layout(hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        s = pd.to_numeric(df[var], errors="coerce")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Moyenne", f"{s.mean():.3f}")
        col2.metric("📈 Écart-type", f"{s.std():.3f}")
        col3.metric("📉 Min", f"{s.min():.3f}")
        col4.metric("📈 Max", f"{s.max():.3f}")

# ==================== TAB 2: ARDL/ECM ====================

with tabs[2]:
    st.markdown('<div class="section-header"><h2>🧩 ARDL/ECM – Résultats Complets</h2></div>', unsafe_allow_html=True)
    
    ardl_tabs = st.tabs(["📊 Général", "📈 Long Terme", "📉 Court Terme", "🔬 Bounds", "📋 Diagnostics"])
    
    with ardl_tabs[0]:
        format_results_table(ardl_general, "Modèle ARDL(1,2,2,1,3,3,1,3)")
        create_coefficient_chart(ardl_general, "Coefficients ARDL")
        st.info("🟢 Vert = positif  |  🔴 Rouge = négatif  |  Intensité = magnitude")
    
    with ardl_tabs[1]:
        format_results_table(long_run.style.format(precision=6), "Relation de Long Terme")
        create_coefficient_chart(long_run, "Effets à Long Terme")
        st.markdown("**Équilibre structurel** entre les variables")
    
    with ardl_tabs[2]:
        st.markdown(f'<div class="table-title">Dynamique Court Terme (ECM)</div>', unsafe_allow_html=True)
        st.dataframe(ecm_short.style.format(precision=4), use_container_width=True)
    
    with ardl_tabs[3]:
        st.dataframe(bounds_test, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("F-statistic", "5.3808", delta="Pesaran Test")
        with col2:
            st.success("✅ **F-stat > I(1) 5%** → Cointégration détectée")
    
    with ardl_tabs[4]:
        def color_diag_pval(val):
            try:
                v = float(val)
                if v > 0.05:
                    return 'background-color: rgba(44, 160, 44, 0.3); font-weight: bold'
                else:
                    return 'background-color: rgba(214, 39, 40, 0.2)'
            except:
                return ''
        
        diag_styled = ardl_diag.style.applymap(color_diag_pval, subset=['p-value'])
        st.dataframe(diag_styled, use_container_width=True)
        st.success("✅ **Tous les diagnostics OK** - Résidus proches du bruit blanc")

# ==================== TAB 3: GRANGER ====================

with tabs[3]:
    st.markdown('<div class="section-header"><h2>🔁 Causalité de Granger</h2></div>', unsafe_allow_html=True)
    
    gr_styled = granger.copy()
    gr_styled['Status'] = gr_styled['p-value'].apply(lambda x: '✅ Causalité' if x < 0.05 else ('⚠️ Marginale' if x < 0.1 else '❌ Non-sig'))
    st.dataframe(gr_styled, use_container_width=True)
    
    sig5 = granger[granger['p-value']<=0.05]['Variable'].tolist()
    st.info(f"**Variables causales au seuil 5%**: {', '.join(sig5) if sig5 else 'Aucune'}")

# ==================== TAB 4: 3SLS ====================

with tabs[4]:
    st.markdown('<div class="section-header"><h2>🧠 Système 3SLS (4 Équations)</h2></div>', unsafe_allow_html=True)
    
    eq = st.radio("Sélectionner l'équation", ["(1) logREM", "(2) GROWTH", "(3) logINV", "(4) OPEN"], horizontal=True)
    
    if eq.startswith("(1)"):
        st.markdown('**Équation 1: Remittances (logREM)** 🔴', unsafe_allow_html=True)
        format_results_table(res_3sls_eq1, "Coefficients 3SLS - Équation 1")
        create_coefficient_chart(res_3sls_eq1, "Effets sur les Remittances")
        st.markdown("💡 **GROWTH < 0 (très sig.)** → Transferts contracycliques (motif d'assurance)")

    elif eq.startswith("(2)"):
        st.markdown('**Équation 2: Croissance (GROWTH)** 🟠', unsafe_allow_html=True)
        format_results_table(res_3sls_eq2, "Coefficients 3SLS - Équation 2")
        create_coefficient_chart(res_3sls_eq2, "Effets sur la Croissance")
        st.markdown("💡 **OPEN > 0 (très sig.)** → Libéralisation commerciale est crucial!")

    elif eq.startswith("(3)"):
        st.markdown('**Équation 3: Investissement (logINV)** 🟢', unsafe_allow_html=True)
        format_results_table(res_3sls_eq3, "Coefficients 3SLS - Équation 3")
        create_coefficient_chart(res_3sls_eq3, "Effets sur l'Investissement")
        st.markdown("💡 **CREDIT > 0 (sig.)** → Canal financier stimule l'investissement")

    else:
        st.markdown('**Équation 4: Ouverture Commerciale (OPEN)** 🟣', unsafe_allow_html=True)
        format_results_table(res_3sls_eq4, "Coefficients 3SLS - Équation 4")
        create_coefficient_chart(res_3sls_eq4, "Déterminants de l'Ouverture")
        st.markdown("💡 **GROWTH > 0 (sig.)** → Expansion économique élargit le commerce")

# ==================== TAB 5: SCÉNARIOS ====================

with tabs[5]:
    st.markdown('<div class="section-header"><h2>🎛️ Simulation de Scénarios</h2></div>', unsafe_allow_html=True)
    
    b_open = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="OPEN","Estimate"].iloc[0])
    b_logrem = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logREM","Estimate"].iloc[0])
    b_loginv = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logINV","Estimate"].iloc[0])
    b_logfdi = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logFDI","Estimate"].iloc[0])
    b_logtc = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logTC","Estimate"].iloc[0])

    col1, col2, col3 = st.columns(3)
    with col1:
        d_open = st.slider("OPEN (points)", -30.0, 30.0, 10.0, 1.0)
        d_rem_pct = st.slider("REM (%)", -50.0, 50.0, 10.0, 1.0)
    with col2:
        d_inv_pct = st.slider("INV (%)", -50.0, 50.0, 10.0, 1.0)
        d_fdi_pct = st.slider("FDI (%)", -80.0, 80.0, 10.0, 1.0)
    with col3:
        d_tc_pct = st.slider("TC (%)", -30.0, 30.0, 5.0, 1.0)

    dlog_rem = np.log(1 + d_rem_pct/100) if (1 + d_rem_pct/100) > 0 else np.nan
    dlog_inv = np.log(1 + d_inv_pct/100) if (1 + d_inv_pct/100) > 0 else np.nan
    dlog_fdi = np.log(1 + d_fdi_pct/100) if (1 + d_fdi_pct/100) > 0 else np.nan
    dlog_tc  = np.log(1 + d_tc_pct/100)  if (1 + d_tc_pct/100)  > 0 else np.nan

    if any(pd.isna(x) for x in [dlog_rem, dlog_inv, dlog_fdi, dlog_tc]):
        st.error("⚠️ Erreur de calcul")
    else:
        delta_growth = (b_open*d_open) + (b_logrem*dlog_rem) + (b_loginv*dlog_inv) + (b_logfdi*dlog_fdi) + (b_logtc*dlog_tc)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if delta_growth > 0:
                st.success(f"📈 **Δ GROWTH = {delta_growth:.3f}%**")
            else:
                st.error(f"📉 **Δ GROWTH = {delta_growth:.3f}%**")

# ==================== TAB 6: EXPORT ====================

with tabs[6]:
    st.markdown('<div class="section-header"><h2>⬇️ Exporter les Résultats</h2></div>', unsafe_allow_html=True)
    
    sheets = {
        "3SLS_eq1": res_3sls_eq1,
        "3SLS_eq2": res_3sls_eq2,
        "3SLS_eq3": res_3sls_eq3,
        "3SLS_eq4": res_3sls_eq4,
        "ARDL_general": ardl_general,
        "ECM_short": ecm_short,
        "Long_run": long_run,
        "Bounds_test": bounds_test,
        "Diagnostics": ardl_diag,
        "Granger": granger
    }

    st.download_button(
        "⬇️ Excel - Tous les résultats",
        to_excel_bytes(sheets),
        f"ARDL_3SLS_Resultats_{datetime.now().strftime('%Y%m%d')}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.sidebar.markdown("---")
st.sidebar.caption("✨ Dashboard Professional v3.0 | ARDL/ECM + Granger + 3SLS | Couleurs & Visualisations enrichies")
