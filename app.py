import os
try:
    import openpyxl
except ImportError:
    os.system('pip install openpyxl')
import streamlit as st
import pandas as pd
import data_input as di
import math_models as mm
import simulation as sim
import report as rep

st.set_page_config(
    page_title="Quantum Dahlia - Terminal de Inversión",
    layout="wide",
    initial_sidebar_state="expanded"
)

def calcular_stake_kelly_adaptado(prob_combinada, cuota_total, banca_total, fraccion_kelly=0.25, min_apuesta_casa=1.0):
    if cuota_total <= 1 or prob_combinada <= 0: return 0.0, 0.0, "Sin Valor"
    b = cuota_total - 1
    p = prob_combinada
    q = 1.0 - p
    f_star = (b * p - q) / b
    if f_star <= 0: return 0.0, 0.0, "EV Negativo"
    porcentaje_apuesta = f_star * fraccion_kelly
    dinero_sugerido_puro = banca_total * porcentaje_apuesta
    if dinero_sugerido_puro < min_apuesta_casa: return porcentaje_apuesta * 100, dinero_sugerido_puro, "Bajo Umbral"
    dinero_redondeado = round(dinero_sugerido_puro * 2) / 2
    porcentaje_ajustado = (dinero_redondeado / banca_total) * 100
    return porcentaje_ajustado, dinero_redondeado, "Óptimo"

def aplicar_estilo_dinamico(modelo_seleccionado):
    imagenes_fondo = {
        "Simulación Montecarlo (100k)": "https://i.pinimg.com/736x/9d/2d/14/9d2d14b652fb4f21ab530ea256c37fcc.jpg",
        "Poisson Bivariado / Dixon-Coles": "https://i.pinimg.com/736x/9d/2d/14/9d2d14b652fb4f21ab530ea256c37fcc.jpg"
    }
    url_fondo = imagenes_fondo.get(modelo_seleccionado, imagenes_fondo["Simulación Montecarlo (100k)"])
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

def main():
    if "combinada_actual" not in st.session_state: st.session_state.combinada_actual = []
    if "df_valores" not in st.session_state: st.session_state.df_valores = None
    if "df_lineas" not in st.session_state: st.session_state.df_lineas = None
    if "partido_activo" not in st.session_state: st.session_state.partido_activo = ""
    if "marcadores_top" not in st.session_state: st.session_state.marcadores_top = None

    st.title("QUANTUM DAHLIA SPORTS INVESTMENTS")
    
    modelo_activo = st.selectbox("Arquitectura de Simulación Activa", ["Simulación Montecarlo (100k)", "Poisson Bivariado / Dixon-Coles"])
    aplicar_estilo_dinamico(modelo_activo)
    
    st.sidebar.markdown("## 📋 Ticket de la Sociedad")
    
    # Renderizado del Cargador de Base de Datos
    di.render_db_uploader()
    
    if st.sidebar.button("Vaciar Todo el Ticket"):
        st.session_state.combinada_actual = []
        st.rerun()
        
    cuota_acumulada = 1.0
    prob_acumulada = 1.0
    contiene_trampa = False
    
    if st.session_state.combinada_actual:
        for i, bet in enumerate(st.session_state.combinada_actual):
            col_info, col_btn = st.sidebar.columns([4, 1])
            with col_info:
                alerta = "⚠️" if bet['ev_individual'] < -3.0 else "🔹"
                if bet['ev_individual'] < -3.0: contiene_trampa = True
                st.write(f"{alerta} **{bet['partido']}**")
                st.write(f"  _{bet['mercado']}_")
                st.write(f"  Cuota: {bet['cuota']:.2f} | EV: {bet['ev_individual']:.1f}%")
            with col_btn:
                if st.button("❌", key=f"remover_{i}"):
                    st.session_state.combinada_actual.pop(i)
                    st.rerun()
            st.sidebar.markdown("---")
            cuota_acumulada *= bet['cuota']
            prob_acumulada *= (bet['prob_modelo'] / 100.0)
            
        st.sidebar.metric(label="Cuota Total Combinada", value=f"{cuota_acumulada:.2f}x")
        ev_combinado = (prob_acumulada * cuota_acumulada) - 1
        
        if contiene_trampa: st.sidebar.warning("¡Cuidado! El ticket incluye selecciones con EV Negativo.")
        if ev_combinado > 0: st.sidebar.success(f"📈 EV Combinado: +{ev_combinado*100:.1f}%")
        else: st.sidebar.error(f"📉 EV Combinado: {ev_combinado*100:.1f}%")
            
        st.sidebar.markdown("### 💰 Gestión de Banca (Kelly)")
        banca_total = st.sidebar.number_input("Banca Común ($)", min_value=1.0, value=25.0, step=1.0)
        fraccion_k = st.sidebar.slider("Fracción de Seguridad", min_value=0.05, max_value=1.0, value=0.25, step=0.05)
        
        pct_banca, dinero_stake, estado_kelly = calcular_stake_kelly_adaptado(prob_acumulada, cuota_acumulada, banca_total, fraccion_k, min_apuesta_casa=1.0)
        
        if estado_kelly == "Óptimo":
            st.sidebar.metric(label="Monto Exacto a Apostar", value=f"${dinero_stake:.2f}", delta=f"{pct_banca:.1f}% de la banca")
        elif estado_kelly == "Bajo Umbral":
            st.sidebar.warning(f"Matemáticamente la inversión sugerida es de ${dinero_stake:.2f} (menor al límite).")
            pct_minimo = (1.0 / banca_total) * 100
            st.sidebar.info(f"Si deciden jugar el mínimo ($1.00), arriesgarán el **{pct_minimo:.1f}%** de la banca.")
        else:
            st.sidebar.info("El modelo recomienda NO arriesgar capital (Sin valor).")
    else:
        st.sidebar.info("Analiza un partido en el panel central.")

    # ---------------------------------------------------------
    # PARÁMETROS DE RENDIMIENTO AUTOMATIZADOS (Vía data_input)
    # ---------------------------------------------------------
    st.markdown("### Parámetros de Rendimiento Automáticos")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        equipo_1 = st.text_input("Escuadra Local", value="Argentina")
        # Todo el panel visual y lógica se maneja ahora desde data_input
        stats_e1 = di.get_team_stats(equipo_1)
        
    with col_t2:
        equipo_2 = st.text_input("Escuadra Visitante", value="Austria")
        stats_e2 = di.get_team_stats(equipo_2)
        
    st.markdown("---")
    cuotas_mercado = di.get_market_odds()
    st.markdown("---")
    
    if st.button("Ejecutar Modelos Cuantitativos"):
        analisis_analitico = mm.procesar_modelos_matematicos(stats_e1, stats_e2, cuotas_mercado)
        analisis_simulado = sim.ejecutar_montecarlo(stats_e1, stats_e2, n_simulaciones=100000)
        
        st.session_state.marcadores_top = analisis_analitico.get("marcadores_top", [])
        
        if modelo_activo == "Poisson Bivariado / Dixon-Coles":
            if "prob_1x2_1t" not in analisis_analitico or any(v == 0.0 for v in analisis_analitico.get("prob_1x2_1t", {}).values()):
                analisis_analitico["prob_1x2_1t"] = analisis_simulado.get("prob_1x2_1t", {"Local": 33.3, "Empate": 33.3, "Visita": 33.4})
            df_valores = rep.generar_reporte_valores(analisis_analitico, cuotas_mercado)
        else:
            df_valores = rep.generar_reporte_valores(analisis_simulado, cuotas_mercado)
            
        df_lineas = rep.generar_reporte_lineas_asiaticas(analisis_simulado, cuotas_mercado)
        
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
        if col_ev_valores:
            df_valores_estilado = st.session_state.df_valores.style.set_properties(**propiedades_oscuras).map(colorificar_ev, subset=[col_ev_valores])
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(st.session_state.df_valores.style.set_properties(**propiedades_oscuras), use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.markdown("### Estimación de Líneas Cortas")
        if st.session_state.df_lineas is not None:
            col_ev_lineas = next((c for c in st.session_state.df_lineas.columns if "ev" in c.lower()), None)
            if col_ev_lineas:
                df_lineas_estilado = st.session_state.df_lineas.style.set_properties(**propiedades_oscuras).map(colorificar_ev, subset=[col_ev_lineas])
                st.dataframe(df_lineas_estilado, use_container_width=True, hide_index=True)
            else:
                st.dataframe(st.session_state.df_lineas.style.set_properties(**propiedades_oscuras), use_container_width=True, hide_index=True)
            
        st.markdown("### ➕ Panel de Carga al Ticket")
        origen_seleccionado = st.radio("Selecciona la procedencia del mercado que deseas jugar:", ["Mercados Principales (Tabla 1)", "Líneas Cortas / Córners / Tarjetas (Tabla 2)"], horizontal=True)
        
        with st.form("add_bet_form_clean"):
            df_origen = None
            col_id = None
            es_linea_corta = False
            tiene_columnas_separadas = False
            direccion = ""
            
            if origen_seleccionado == "Mercados Principales (Tabla 1)" and st.session_state.df_valores is not None:
                df_origen = st.session_state.df_valores
                col_id = next((c for c in df_origen.columns if c.lower() in ["mercado", "market", "opción", "opcion"]), df_origen.columns[0])
                opciones = df_origen[col_id].dropna().unique().tolist()
                mercado_elegido = st.selectbox("Selecciona el mercado principal:", options=opciones)
                
            elif origen_seleccionado == "Líneas Cortas / Córners / Tarjetas (Tabla 2)" and st.session_state.df_lineas is not None:
                df_origen = st.session_state.df_lineas
                col_id = next((c for c in df_origen.columns if c.lower() in ["mercado", "market", "línea", "linea", "estadística", "estadistica"]), df_origen.columns[0])
                opciones = df_origen[col_id].dropna().unique().tolist()
                mercado_elegido = st.selectbox("Selecciona la línea o estadística:", options=opciones)
                
                columnas_minus = [c.lower() for c in df_origen.columns]
                tiene_columnas_separadas = any("más" in c or "over" in c or "menos" in c or "under" in c for c in columnas_minus)
                
                if tiene_columnas_separadas:
                    direccion = st.radio("Pronóstico para esta línea:", ["Más / Over", "Menos / Under"], horizontal=True)
                    es_linea_corta = True
            else:
                st.info("Ejecuta los modelos matemáticos cuantitativos para habilitar las opciones.")
                mercado_elegido = None
                
            btn_agregar = st.form_submit_button("Asegurar Selección en el Ticket")
            
            if btn_agregar and mercado_elegido and df_origen is not None:
                fila = df_origen[df_origen[col_id] == mercado_elegido].iloc[0]
                columnas_disponibles = df_origen.columns.tolist()
                
                cuota_f, prob_f, ev_f = 1.00, 0.0, 0.0
                nombre_mercado_final = str(mercado_elegido)
                
                if es_linea_corta and tiene_columnas_separadas:
                    variante_col = "más" if "más" in direccion.lower() or "over" in direccion.lower() else "menos"
                    variante_alt = "over" if variante_col == "más" else "under"
                    
                    col_cuota = next((c for c in columnas_disponibles if ("cuota" in c.lower() or "odd" in c.lower()) and (variante_col in c.lower() or variante_alt in c.lower())), None)
                    col_prob = next((c for c in columnas_disponibles if ("prob" in c.lower() or "%" in c.lower()) and (variante_col in c.lower() or variante_alt in c.lower())), None)
                    col_ev = next((c for c in columnas_disponibles if "ev" in c.lower() and (variante_col in c.lower() or variante_alt in c.lower())), None)
                    
                    nombre_mercado_final = f"{mercado_elegido} - {direccion}"
                else:
                    col_cuota = next((c for c in columnas_disponibles if "cuota" in c.lower() or "odd" in c.lower()), None)
                    col_prob = next((c for c in columnas_disponibles if "prob" in c.lower() or "%" in c.lower()), None)
                    col_ev = next((c for c in columnas_disponibles if "ev" in c.lower()), None)
                
                try:
                    if col_cuota and pd.notna(fila[col_cuota]): cuota_f = float(str(fila[col_cuota]).replace('%', '').strip())
                    if col_prob and pd.notna(fila[col_prob]): prob_f = float(str(fila[col_prob]).replace('%', '').strip())
                    if col_ev and pd.notna(fila[col_ev]): ev_f = float(str(fila[col_ev]).replace('%', '').strip())
                except (ValueError, TypeError):
                    pass
                
                if 0.0 < prob_f <= 1.0: prob_f *= 100.0
                    
                ya_existe = any(b["partido"] == st.session_state.partido_activo and b["mercado"] == nombre_mercado_final for b in st.session_state.combinada_actual)
                
                if not ya_existe:
                    st.session_state.combinada_actual.append({
                        "partido": st.session_state.partido_activo,
                        "mercado": nombre_mercado_final,
                        "cuota": cuota_f,
                        "prob_modelo": prob_f,
                        "ev_individual": ev_f
                    })
                    st.success(f"Agregado con éxito: {nombre_mercado_final} @{cuota_f:.2f} (EV: {ev_f:.1f}%)")
                    st.rerun()
                else:
                    st.warning("Esta selección ya se encuentra guardada en el ticket.")

if __name__ == "__main__":
    main()
