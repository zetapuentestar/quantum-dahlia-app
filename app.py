# app.py
import os
try:
    import openpyxl
except ImportError:
    os.system('pip install openpyxl')
import streamlit as st
import pandas as pd
import data_input as di
import math_models as mm
import report as rep

st.set_page_config(
    page_title="Quantum Dahlia - Terminal de Inversión",
    layout="wide",
    initial_sidebar_state="expanded"
)

def aplicar_estilo_dinamico():
    url_fondo = "https://i.pinimg.com/736x/9d/2d/14/9d2d14b652fb4f21ab530ea256c37fcc.jpg"
    css = f"""
    <style>
    .stApp, div[data-testid="stAppViewBlockContainer"] {{ background-color: transparent !important; }}
    div[data-testid="stAppViewContainer"] {{
        background: linear-gradient(rgba(10, 10, 12, 0.85), rgba(10, 10, 12, 0.85)), url("{url_fondo}") !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }}
    header[data-testid="stHeader"], div[data-testid="stHeader"] {{
        background-color: #0A0A0C !important; background: #0A0A0C !important; height: 45px !important; border-bottom: 1px solid rgba(214, 175, 55, 0.15) !important;
    }}
    header[data-testid="stHeader"] svg, div[data-testid="stHeader"] svg, header[data-testid="stHeader"] button, div[data-testid="stHeader"] button, header[data-testid="stHeader"] a, div[data-testid="stHeader"] a {{
        fill: #FFFFFF !important; color: #FFFFFF !important;
    }}
    div[data-testid="stSidebar"], div[data-testid="stSidebarContent"], div[data-testid="stSidebar"] > div {{
        background-color: #0A0A0C !important; background: #0A0A0C !important; border-right: 1px solid rgba(214, 175, 55, 0.25) !important;
    }}
    div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3, div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] label, div[data-testid="stSidebar"] span, div[data-testid="stSidebar"] small, div[data-testid="stSidebar"] div {{
        color: #FFFFFF !important; font-family: 'Inter', -apple-system, sans-serif !important;
    }}
    div[data-testid="stSidebar"] div[data-testid="stMetricValue"] div, div[data-testid="stSidebar"] div[data-testid="stMetricValue"] span {{
        color: #D4AF37 !important; font-weight: 700 !important;
    }}
    div[data-testid="stSidebar"] div.stNumberInput, div[data-testid="stSidebar"] div.stSlider {{
        border: 1px solid rgba(214, 175, 55, 0.2) !important; background-color: rgba(18, 19, 22, 0.9) !important; padding: 12px !important; border-radius: 4px !important; margin-bottom: 10px;
    }}
    h1, h2, h3, p, label, span {{ color: #FFFFFF !important; font-family: 'Inter', -apple-system, sans-serif !important; }}
    h1 {{ font-weight: 700 !important; letter-spacing: -0.05em; border-bottom: 1px solid rgba(214, 175, 55, 0.3); padding-bottom: 10px; }}
    .stButton>button, div[data-testid="stSidebar"] .stButton>button {{
        background-color: #121316 !important; color: #D4AF37 !important; border: 1px solid #D4AF37 !important; border-radius: 4px !important; width: 100%; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; padding: 14px 0px; transition: all 0.4s ease;
    }}
    .stButton>button:hover, div[data-testid="stSidebar"] .stButton>button:hover {{
        background-color: #D4AF37 !important; color: #0A0A0C !important; box-shadow: 0px 0px 25px rgba(214, 175, 55, 0.4); border: 1px solid #D4AF37 !important;
    }}
    div.stSelectbox div[data-baseweb="select"] {{ background-color: rgba(18, 19, 22, 0.9) !important; border: 1px solid rgba(214, 175, 55, 0.2) !important; }}
    div.stNumberInput input {{ background-color: rgba(18, 19, 22, 0.9) !important; color: #FFFFFF !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} div[data-testid="stAppDeployButton"] {{display: none !important;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def colorificar_ev(val):
    try:
        val_float = float(val)
        if val_float > 0.0: return 'background-color: #2c2001; color: #D4AF37; font-weight: bold;'
        elif val_float < 0.0: return 'background-color: #121316; color: #f07167;'
        else: return 'background-color: #121316; color: #94a3b8;'
    except (ValueError, TypeError):
        return 'background-color: #121316; color: #94a3b8;'

def resaltar_ganador(data):
    """
    Agrupa los mercados (separando por ':') y resalta en verde 
    la opción con mayor probabilidad dentro de ese grupo.
    """
    styles = pd.DataFrame('', index=data.index, columns=data.columns)
    col_mercado = "Mercado" if "Mercado" in data.columns else "Métrica/Mercado"
    col_prob = "Prob_Modelo (%)"

    if col_mercado in data.columns and col_prob in data.columns:
        # Extraer prefijo (ej: "1X2" de "1X2: Victoria Local")
        prefijos = [str(x).split(":")[0] for x in data[col_mercado]]
        grupos = {}
        for i, p in enumerate(prefijos):
            if p not in grupos:
                grupos[p] = []
            grupos[p].append(data.index[i])
        
        # Iterar sobre cada mercado y buscar el ganador
        for p, indices in grupos.items():
            max_val = max([data.loc[idx, col_prob] for idx in indices])
            for idx in indices:
                if data.loc[idx, col_prob] == max_val:
                    styles.loc[idx, col_prob] = 'background-color: #064e3b; color: #4ade80; font-weight: bold; border-left: 3px solid #22c55e;'
    return styles

def main():
    if "df_valores" not in st.session_state: st.session_state.df_valores = None
    if "df_lineas" not in st.session_state: st.session_state.df_lineas = None
    if "partido_activo" not in st.session_state: st.session_state.partido_activo = ""
    if "marcadores_top" not in st.session_state: st.session_state.marcadores_top = None

    st.title("QUANTUM DAHLIA SPORTS INVESTMENTS")
    aplicar_estilo_dinamico()
    
    # Renderizado del Cargador de Base de Datos en el panel izquierdo
    di.render_db_uploader()
    
    # ---------------------------------------------------------
    # PARÁMETROS DE RENDIMIENTO AUTOMATIZADOS (Vía data_input)
    # ---------------------------------------------------------
    st.markdown("### Parámetros de Rendimiento Automáticos")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        equipo_1 = st.text_input("Escuadra Local", value="Argentina")
        stats_e1 = di.get_team_stats(equipo_1)
        
    with col_t2:
        equipo_2 = st.text_input("Escuadra Visitante", value="Austria")
        stats_e2 = di.get_team_stats(equipo_2)
        
    st.markdown("---")
    cuotas_mercado = di.get_market_odds()
    st.markdown("---")
    
    if st.button("Ejecutar Modelos Cuantitativos"):
        # Modelo unificado analítico (Poisson / Dixon-Coles)
        analisis_analitico = mm.procesar_modelos_matematicos(stats_e1, stats_e2, cuotas_mercado)
        
        st.session_state.marcadores_top = analisis_analitico.get("marcadores_top", [])
        
        # Generación de DataFrames. (Se incluyeron stats_e1 y stats_e2 para evitar errores con las líneas asiáticas)
        df_valores = rep.generar_reporte_valores(analisis_analitico, cuotas_mercado)
        df_lineas = rep.generar_reporte_lineas_asiaticas(analisis_analitico, cuotas_mercado, stats_e1, stats_e2)
        
        st.session_state.df_valores = df_valores
        st.session_state.df_lineas = df_lineas
        st.session_state.partido_activo = f"{equipo_1} vs {equipo_2}"

    if st.session_state.df_valores is not None:
        st.markdown(f"## Análisis Actual: {st.session_state.partido_activo}")
        propiedades_oscuras = {'background-color': '#121316', 'color': '#FFFFFF', 'border-color': '#27272a'}
        
        if st.session_state.marcadores_top:
            st.markdown("### 🎯 Proyección de Marcador Exacto (Poisson / Dixon-Coles)")
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.metric("1° Más Probable", st.session_state.marcadores_top[0]['marcador'], f"{st.session_state.marcadores_top[0]['prob']*100:.1f}%")
            if len(st.session_state.marcadores_top) > 1:
                with col_m2:
                    st.metric("2° Más Probable", st.session_state.marcadores_top[1]['marcador'], f"{st.session_state.marcadores_top[1]['prob']*100:.1f}%", delta_color="off")
            if len(st.session_state.marcadores_top) > 2:
                with col_m3:
                    st.metric("3° Más Probable", st.session_state.marcadores_top[2]['marcador'], f"{st.session_state.marcadores_top[2]['prob']*100:.1f}%", delta_color="off")
            st.markdown("---")
        
        st.markdown("### Proyección de Valor Esperado")
        col_ev_valores = next((c for c in st.session_state.df_valores.columns if "ev" in c.lower()), None)
        
        # Aplicamos la cadena de estilos: Tema oscuro -> Color EV -> Resaltado Verde del Ganador
        if col_ev_valores:
            df_valores_estilado = st.session_state.df_valores.style\
                .set_properties(**propiedades_oscuras)\
                .map(colorificar_ev, subset=[col_ev_valores])\
                .apply(resaltar_ganador, axis=None)
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
        else:
            df_valores_estilado = st.session_state.df_valores.style\
                .set_properties(**propiedades_oscuras)\
                .apply(resaltar_ganador, axis=None)
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.markdown("### Estimación de Líneas Cortas")
        if st.session_state.df_lineas is not None:
            col_ev_lineas = next((c for c in st.session_state.df_lineas.columns if "ev" in c.lower()), None)
            
            if col_ev_lineas:
                df_lineas_estilado = st.session_state.df_lineas.style\
                    .set_properties(**propiedades_oscuras)\
                    .map(colorificar_ev, subset=[col_ev_lineas])\
                    .apply(resaltar_ganador, axis=None)
                st.dataframe(df_lineas_estilado, use_container_width=True, hide_index=True)
            else:
                df_lineas_estilado = st.session_state.df_lineas.style\
                    .set_properties(**propiedades_oscuras)\
                    .apply(resaltar_ganador, axis=None)
                st.dataframe(df_lineas_estilado, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
