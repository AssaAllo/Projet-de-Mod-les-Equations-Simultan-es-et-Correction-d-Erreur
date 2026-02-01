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
    initial_sidebar_state="expanded",
    theme="dark"
)

# Custom styling
st.markdown("""
<style>
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #1f77b4 0%, #1a5fa0 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #2ca02c 0%, #229620 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #ff7f0e 0%, #e67e0a 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .danger-box {
        background: linear-gradient(135deg, #d62728 0%, #b81f21 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2em;
        font-weight: bold;
    }
    
    .section-header {
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Projet MES/ARDL – Tchad (1995–2022)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Helpers
# -----------------------------
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

# -----------------------------
# Sidebar: data
# -----------------------------
st.sidebar.title("⚙️ Paramètres")
default_path = "base.xlsx"
use_default = st.sidebar.checkbox("Charger automatiquement base.xlsx (si présent)", value=True)
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
        st.sidebar.warning("⚠️ base.xlsx introuvable. Téléverse ton fichier.")
        df = None
else:
    st.sidebar.info("Téléverse un fichier pour démarrer.")

# -----------------------------
# Données attendues
# -----------------------------
expected_cols = ["year","GROWTH","REM","TC","FDI","OPEN","CREDIT","INV","INF","MIGSTOCK","HOSTGDP"]

# -----------------------------
# 3SLS RESULTS (modèle retenu) – tes tableaux
# -----------------------------
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

# -----------------------------
# ARDL/ECM RESULTS – coefficients réels (ARDL(1,2,2,1,3,3,1,3))
# -----------------------------
ardl_general = pd.DataFrame({
    "Variable": [
        "L(GROWTH,1)",
        "logREM","L(logREM,1)","L(logREM,2)",
        "logINV","L(logINV,1)","L(logINV,2)",
        "logOPEN","L(logOPEN,1)",
        "INF","L(INF,1)","L(INF,2)","L(INF,3)",
        "logCREDIT","L(logCREDIT,1)","L(logCREDIT,2)","L(logCREDIT,3)",
        "logTC","L(logTC,1)",
        "logFDI","L(logFDI,1)","L(logFDI,2)","L(logFDI,3)",
        "Constant"
    ],
    "Coefficient": [
        -0.139283,
        -14.065258, 0.814373, 3.478532,
        -1.494072, 12.180486, -4.376342,
        5.883577, 4.602755,
        -0.366516, -0.270084, 0.006172, 0.225961,
        -5.238680, -13.878765, 15.429603, 5.595321,
        9.669343, -40.599514,
        -0.045632, 0.586344, -0.029744, -0.443065,
        193.713570
    ],
    "p-value (summary)": [
        0.02416,
        0.00307, 0.05571, 0.00583,
        0.08327, 0.01421, 0.02008,
        0.00700, 0.00946,
        0.00346, 0.01617, 0.44050, 0.01498,
        0.01116, 0.00460, 0.00349, 0.00958,
        0.00917, 0.00235,
        0.05533, 0.00313, 0.09182, 0.00331,
        0.00425
    ]
})
ardl_general["Sig"] = ardl_general["p-value (summary)"].apply(format_sig)

ecm_short = pd.DataFrame({
    "Variable": [
        "d(logREM)", "d(L(logREM,1))",
        "d(logINV)", "d(L(logINV,1))",
        "d(logOPEN)",
        "d(INF)","d(L(INF,1))","d(L(INF,2))",
        "d(logCREDIT)","d(L(logCREDIT,1))","d(L(logCREDIT,2))",
        "d(logTC)",
        "d(logFDI)","d(L(logFDI,1))","d(L(logFDI,2))",
        "ect",
        "Constant"
    ],
    "Coefficient": [
        -14.065, -3.479,
        -1.494, 4.376,
        5.884,
        -0.367, -0.232, -0.226,
        -5.239, -21.025, -5.595,
        9.669,
        -0.046, 0.473, 0.443,
        -1.139,
        193.714
    ],
    "Std. Error": [
        0.005, 0.005,
        0.009, 0.010,
        0.014,
        0.0003, 0.0003, 0.0003,
        0.013, 0.017, 0.012,
        0.029,
        0.0004, 0.0004, 0.0004,
        0.001,
        0.095
    ],
    "Sig": ["***"]*17
})

long_run = pd.DataFrame({
    "Variable": ["logREM.1","logINV.1","logOPEN.1","INF.1","logCREDIT.1","logTC.1","logFDI.1"],
    "Coefficient (LR)": [-5.0981021, 10.4298151, 27.7491541, -1.3883375, -3.7688735, -36.4546632, 0.7089692]
})

bounds_test = pd.DataFrame({
    "Test": ["Pesaran Bounds (Case 2)"],
    "F-statistic": [5.3808169418405],
    "CV 10% I(0)": [2.277],
    "CV 10% I(1)": [3.498],
    "CV 5% I(0)": [2.73],
    "CV 5% I(1)": [4.163],
    "CV 1% I(0)": [3.864],
    "CV 1% I(1)": [5.694],
    "Conclusion": ["F > I(1) à 5% ⇒ cointégration (relation LT)"]
})

ardl_diag = pd.DataFrame({
    "Test": [
        "Wilcoxon (mu=0)",
        "t-test (mu=0)",
        "ARCH LM (lags=6)",
        "Box-Pierce (lag=6)",
        "Ljung-Box (lag=6)",
        "Lilliefors normalité",
        "Shapiro-Wilk normalité"
    ],
    "p-value": [0.9368, 1.0, 0.214, 0.4823, 0.3432, 0.8563, 0.6508],
    "Conclusion (5%)": [
        "moyenne nulle", "moyenne nulle",
        "pas d’ARCH", "pas d’autocorr", "pas d’autocorr",
        "normalité OK", "normalité OK"
    ]
})

# -----------------------------
# Granger (tableau)
# -----------------------------
granger = pd.DataFrame({
    "Variable": ["logREM","logINV","logOPEN","INF","logCREDIT","logTC","logFDI"],
    "F": [1.0089, 4.1263, 4.6084, 0.3763, 0.1844, 2.6538, 2.5814],
    "p-value": [0.4117, 0.02164, 0.01461, 0.7712, 0.9056, 0.07975, 0.0854]
})
granger["Sig"] = granger["p-value"].apply(format_sig)
granger["Conclusion (5%)"] = np.where(granger["p-value"]<=0.05, "Causalité (Granger)", "Non significatif")
granger.loc[(granger["p-value"]>0.05) & (granger["p-value"]<=0.1), "Conclusion (5%)"] = "Causalité marginale (10%)"

# -----------------------------
# App layout
# -----------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1f77b4 0%, #1a5fa0 100%); padding: 30px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0;">📊 Dashboard ARDL/ECM + MES (3SLS)</h1>
    <p style="font-size: 1.2em; color: #e8f4f8; margin: 10px 0 0 0;">Modèle de Transferts de Fonds et Croissance Économique | Tchad 1995–2022</p>
</div>
""", unsafe_allow_html=True)

st.caption("🔍 Analyse complète : Séries • KPIs • ARDL/ECM • Pesaran Bounds • Causalité Granger • Système 3SLS • Scénarios dynamiques")

tabs = st.tabs([
    "📁 Données",
    "📈 Séries & KPIs",
    "🧩 ARDL / ECM (résultats + tests)",
    "🔁 Granger",
    "🧠 MES 3SLS (4 équations)",
    "🎛️ Scénarios & simulation",
    "⬇️ Export"
])

# -----------------------------
# TAB Données
# -----------------------------
with tabs[0]:
    st.markdown('<div class="section-header"><h2>📊 Gestion des Données</h2></div>', unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ Aucune données chargées. Téléverse un fichier Excel ou place base.xlsx à côté de app.py.")
    else:
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            st.error(f"❌ Colonnes manquantes : {missing}")
            st.info("📝 Renomme les colonnes : year, GROWTH, REM, TC, FDI, OPEN, CREDIT, INV, INF, MIGSTOCK, HOSTGDP.")
        else:
            df = df.sort_values("year").reset_index(drop=True).copy()
            df["logREM"] = safe_log(df["REM"])
            df["logTC"]  = safe_log(df["TC"])
            df["logFDI"] = safe_log(df["FDI"])
            df["logOPEN"]= safe_log(df["OPEN"])
            df["logCREDIT"]= safe_log(df["CREDIT"])
            df["logINV"] = safe_log(df["INV"])

            # KPIs avec couleurs
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📅 Période", f"{int(df.year.min())}–{int(df.year.max())}", delta=f"{int(df.year.max()) - int(df.year.min())} ans")
            with col2:
                st.metric("📊 Observations", df.shape[0])
            with col3:
                st.metric("📈 Variables", df.shape[1])
            with col4:
                st.metric("🔲 Manquants", int(df.isna().sum().sum()), delta="0%" if int(df.isna().sum().sum()) == 0 else "⚠️")
            with col5:
                st.metric("✅ Complétude", f"{(1 - df.isna().sum().sum()/(df.shape[0]*df.shape[1]))*100:.1f}%")

            # Tabs pour données
            st.markdown("---")
            data_tabs = st.tabs(["📋 Aperçu", "📊 Statistiques", "📉 Distribution"])
            
            with data_tabs[0]:
                st.subheader("Données brutes")
                st.dataframe(df.head(25), use_container_width=True, height=500)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "⬇️ Télécharger en CSV",
                        df.to_csv(index=False),
                        "donnees_tchad.csv",
                        "text/csv"
                    )
                with col2:
                    st.download_button(
                        "⬇️ Télécharger en Excel",
                        to_excel_bytes({"Données": df}),
                        "donnees_tchad.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with data_tabs[1]:
                st.subheader("Statistiques descriptives")
                stats_df = df[expected_cols].describe().T
                st.dataframe(stats_df, use_container_width=True)
                
                # Heatmap de corrélations
                st.subheader("Matrice de corrélations")
                corr = df[[c for c in expected_cols if c != 'year']].corr(numeric_only=True)
                fig_corr = px.imshow(corr, color_continuous_scale="RdBu", zmin=-1, zmax=1, 
                                     labels=dict(color="Corrélation"))
                fig_corr.update_layout(height=600, title_text="Corrélations entre variables")
                st.plotly_chart(fig_corr, use_container_width=True)
            
            with data_tabs[2]:
                st.subheader("Distribution des variables")
                var_select = st.selectbox("Sélectionner une variable", 
                                         [c for c in expected_cols if c != 'year'], 
                                         key="dist_var")
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_hist = px.histogram(df, x=var_select, nbins=15, 
                                           title=f"Distribution - {var_select}",
                                           color_discrete_sequence=['#1f77b4'])
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    fig_box = px.box(df, y=var_select, title=f"Box plot - {var_select}",
                                    color_discrete_sequence=['#ff7f0e'])
                    st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------
# TAB Séries & KPIs
# -----------------------------
with tabs[1]:
    st.subheader("Séries temporelles & KPIs")
    if df is None:
        st.warning("Charge d’abord les données.")
    else:
        cols = [c for c in expected_cols if c != "year"]
        var = st.selectbox("Variable", cols, index=0)
        fig = px.line(df, x="year", y=var, markers=True, title=f"{var} (niveau)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### KPIs")
        s = pd.to_numeric(df[var], errors="coerce")
        a,b,c,d = st.columns(4)
        a.metric("Moyenne", f"{s.mean():.3f}")
        b.metric("Écart-type", f"{s.std():.3f}")
        c.metric("Min", f"{s.min():.3f}")
        d.metric("Max", f"{s.max():.3f}")

        st.markdown("### Corrélations (niveaux)")
        corr = df[cols].corr(numeric_only=True)
        st.dataframe(corr, use_container_width=True)

# -----------------------------
# TAB ARDL/ECM
# -----------------------------
with tabs[2]:
    st.subheader("ARDL / ECM – résultats, long terme, court terme, tests")

    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("### Modèle ARDL général (coefficients réels)")
        st.dataframe(ardl_general, use_container_width=True)
    with c2:
        st.markdown("### Test de cointégration (Pesaran Bounds)")
        st.dataframe(bounds_test, use_container_width=True)

    st.markdown("### Relation de long terme (coefficients long-run)")
    st.dataframe(long_run, use_container_width=True)

    st.markdown("### Relation de court terme (ECM / Δ + ECT)")
    st.dataframe(ecm_short, use_container_width=True)

    st.markdown("### Diagnostics (ARDL/ECM) – Résidus")
    st.dataframe(ardl_diag, use_container_width=True)

    st.info(
        "Lecture rapide : le test de Pesaran donne F=5.38, supérieur à la borne I(1) au seuil 5% ⇒ "
        "relation de long terme. Les tests ARCH et Box (lags=6) suggèrent des résidus proches du bruit blanc "
        "et une normalité acceptable (p-values élevées)."
    )

# -----------------------------
# TAB Granger
# -----------------------------
with tabs[3]:
    st.subheader("Causalité de Granger (ordre = 3)")
    st.dataframe(granger, use_container_width=True)

    st.markdown("### Synthèse automatique")
    sig5 = granger[granger["p-value"]<=0.05]["Variable"].tolist()
    sig10 = granger[(granger["p-value"]>0.05) & (granger["p-value"]<=0.1)]["Variable"].tolist()

    st.write(f"**Causalité au seuil 5%** : {', '.join(sig5) if sig5 else 'Aucune'}")
    st.write(f"**Causalité marginale au seuil 10%** : {', '.join(sig10) if sig10 else 'Aucune'}")

# -----------------------------
# TAB MES 3SLS
# -----------------------------
with tabs[4]:
    st.subheader("Système d’équations simultanées – 3SLS (4 équations)")

    st.markdown("""
**Système retenu :**
1) `logREM ~ GROWTH + MIGSTOCK + HOSTGDP + logTC`  
2) `GROWTH ~ logREM + logINV + OPEN + logFDI + logTC`  
3) `logINV ~ logREM + CREDIT + GROWTH + INF`  
4) `OPEN ~ logREM + GROWTH + logINV + HOSTGDP`
""")

    eq = st.radio("Équation", ["(1) logREM", "(2) GROWTH", "(3) logINV", "(4) OPEN"], horizontal=True)

    if eq.startswith("(1)"):
        st.dataframe(res_3sls_eq1, use_container_width=True)
        st.info(
            "Interprétation : GROWTH < 0 et très significatif ⇒ transferts contracycliques (motif d’assurance). "
            "HOSTGDP < 0 très significatif ⇒ la conjoncture des pays hôtes influence fortement les transferts. "
            "logTC < 0 très significatif ⇒ le taux de change affecte la valeur/choix de transfert. "
            "MIGSTOCK non significatif ⇒ effet structurel lent, peu détectable annuellement."
        )

    elif eq.startswith("(2)"):
        st.dataframe(res_3sls_eq2, use_container_width=True)
        st.warning(
            "Ici, **OPEN est la variable clé** (positive, très significative). "
            "Les remittances n’ont pas d’effet direct significatif sur la croissance dans cette spécification, "
            "ce qui est cohérent avec un rôle plutôt indirect (canaux) ou retardé."
        )

    elif eq.startswith("(3)"):
        st.dataframe(res_3sls_eq3, use_container_width=True)
        st.info(
            "L’investissement réagit positivement au CREDIT et à la croissance ⇒ canal financier + signal macro. "
            "REM n’est pas significatif ⇒ transferts plus orientés consommation ou contraintes d’allocation."
        )

    else:
        st.dataframe(res_3sls_eq4, use_container_width=True)
        st.info(
            "OPEN augmente avec la croissance (effet d’expansion des échanges). "
            "Les autres variables ne ressortent pas dans cette équation."
        )

# -----------------------------
# TAB Scénarios
# -----------------------------
with tabs[5]:
    st.subheader("Scénarios / Simulation (impact attendu sur la croissance – équation 3SLS)")

    st.markdown("""
On simule l’impact sur **GROWTH** en utilisant les coefficients de l’équation (2) 3SLS :

\[
\Delta GROWTH \approx \beta_{OPEN}\Delta OPEN + \beta_{logREM}\Delta logREM + \beta_{logINV}\Delta logINV + \beta_{logFDI}\Delta logFDI + \beta_{logTC}\Delta logTC
\]

> Ici, OPEN est en niveau (points), les autres en log (≈ %).
""")

    b_open = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="OPEN","Estimate"].iloc[0])
    b_logrem = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logREM","Estimate"].iloc[0])
    b_loginv = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logINV","Estimate"].iloc[0])
    b_logfdi = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logFDI","Estimate"].iloc[0])
    b_logtc = float(res_3sls_eq2.loc[res_3sls_eq2["Variable"]=="logTC","Estimate"].iloc[0])

    colA, colB = st.columns(2)
    with colA:
        d_open = st.slider("Choc sur OPEN (points)", -30.0, 30.0, 10.0, 1.0)
        d_rem_pct = st.slider("Choc sur REM (%)", -50.0, 50.0, 10.0, 1.0)
        d_inv_pct = st.slider("Choc sur INV (%)", -50.0, 50.0, 10.0, 1.0)
    with colB:
        d_fdi_pct = st.slider("Choc sur FDI (%)", -80.0, 80.0, 10.0, 1.0)
        d_tc_pct = st.slider("Choc sur TC (%)", -30.0, 30.0, 5.0, 1.0)

    # passer des % aux deltas de logs approximatifs: Δlog(x) ≈ log(1+g)
    dlog_rem = np.log(1 + d_rem_pct/100) if (1 + d_rem_pct/100) > 0 else np.nan
    dlog_inv = np.log(1 + d_inv_pct/100) if (1 + d_inv_pct/100) > 0 else np.nan
    dlog_fdi = np.log(1 + d_fdi_pct/100) if (1 + d_fdi_pct/100) > 0 else np.nan
    dlog_tc  = np.log(1 + d_tc_pct/100)  if (1 + d_tc_pct/100)  > 0 else np.nan

    if any(pd.isna(x) for x in [dlog_rem, dlog_inv, dlog_fdi, dlog_tc]):
        st.error("⚠️ Un des chocs en % donne un log non défini (1+g ≤ 0). Réduis l’amplitude.")
    else:
        delta_growth = (b_open*d_open) + (b_logrem*dlog_rem) + (b_loginv*dlog_inv) + (b_logfdi*dlog_fdi) + (b_logtc*dlog_tc)

        st.markdown("### Résultat")
        st.metric("Δ GROWTH attendu (points de %)", f"{delta_growth:.3f}")

        st.caption(
            "Attention : c’est une simulation mécanique basée sur l’équation (2) 3SLS. "
            "Elle ne remplace pas une prévision dynamique complète (ARDL/ECM), mais elle est très utile pour des scénarios rapides."
        )

# -----------------------------
# TAB Export
# -----------------------------
with tabs[6]:
    st.subheader("Exporter les tableaux (Excel)")

    sheets = {
        "3SLS_eq1_logREM": res_3sls_eq1,
        "3SLS_eq2_GROWTH": res_3sls_eq2,
        "3SLS_eq3_logINV": res_3sls_eq3,
        "3SLS_eq4_OPEN": res_3sls_eq4,
        "ARDL_general": ardl_general,
        "ECM_short": ecm_short,
        "Long_run": long_run,
        "Bounds_test": bounds_test,
        "ARDL_diagnostics": ardl_diag,
        "Granger": granger
    }

    st.download_button(
        "⬇️ Télécharger tous les tableaux (Excel)",
        data=to_excel_bytes(sheets),
        file_name="dashboard_resultats_Tchad_ARDL_MES.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.sidebar.markdown("---")
st.sidebar.caption("Version enrichie : ARDL/ECM + Granger + 3SLS + Scénarios.")
