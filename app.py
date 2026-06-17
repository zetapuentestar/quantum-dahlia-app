import streamlit as st
import pandas as pd
import data_input as di
import math_models as mm
import simulation as sim
import report as rep

# Configuración inicial de la página (Panel expandido para control total)
st.set_page_config(
    page_title="Quantum Dahlia - Terminal de Inversión",
    layout="wide",
    initial_sidebar_state="expanded"
)

def calcular_stake_kelly(prob_combinada, cuota_total, banca_total, fraccion_kelly=0.25):
    """
    Calcula el dinero exacto a apostar basado en el Criterio de Kelly Fraccionado.
    """
    if cuota_total <= 1 or prob_combinada <= 0:
        return 0.0, 0.0
        
    b = cuota_total - 1  # Cuota neta
    p = prob_combinada
    q = 1.0 - p
    
    # Fórmula clásica de Kelly
    f_star = (b * p - q) / b
    
    if f_star <= 0:
        return 0.0, 0.0
        
    porcentaje_apuesta = f_star * fraccion_kelly
    dinero_a_apostar = banca_total * porcentaje_apuesta
    
    return porcentaje_apuesta * 100, dinero_a_apostar

def aplicar_estilo_dinamico(modelo_seleccionado):
    """
    Inyecta CSS avanzado apuntando al contenedor exacto de Streamlit
    y aplicando un overlay sutil para garantizar la visibilidad de la imagen.
    """
    imagenes_fondo = {
        "Simulación Montecarlo (100k)": "https://i.pinimg.com/736x/9d/2d/14/9d2d14b652fb4f21ab530ea256c37fcc.jpg",
        "Poisson Bivariado / Dixon-Coles": "https://i.pinimg.com/736x/9d/2d/14/9d2d14b652fb4f21ab530ea256c37fcc.jpg"
    }
    
    url_fondo = imagenes_fondo.get(modelo_seleccionado, imagenes_fondo["Simulación Montecarlo (100k)"])
    
    css = f"""
    <style>
    /* Forzar que el contenedor base y sus capas superiores sean transparentes */
    .stApp, div[data-testid="stAppViewBlockContainer"] {{
        background-color: transparent !important;
    }}
    
    /* Aplicar el fondo con un filtro oscuro del 85% directamente en el contenedor de la vista */
    div[data-testid="stAppViewContainer"] {{
        background: linear-gradient(rgba(10, 10, 12, 0.85), rgba(10, 10, 12, 0.85)), url("{url_fondo}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* ---------------------------------------------------------
    /* AJUSTE DEFINITIVO DE LA BARRA SUPERIOR (HEADER)
    /* --------------------------------------------------------- */
    header[data-testid="stHeader"], div[data-testid="stHeader"] {{
        background-color: #0A0A0C !important;
        background: #0A0A0C !important;
        height: 45px !important;
        border-bottom: 1px solid rgba(214, 175, 55, 0.15) !important;
    }}
    
    /* Forzar iconos del header a Blanco Puro */
    header[data-testid="stHeader"] svg, 
    div[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] button,
    div[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a,
    div[data-testid="stHeader"] a {{
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }}
    
    /* Forzar Negro Premium Absoluto en el Sidebar */
    div[data-testid="stSidebar"], 
    div[data-testid="stSidebarContent"], 
    div[data-testid="stSidebar"] > div {{
        background-color: #0A0A0C !important;
        background: #0A0A0C !important;
        border-right: 1px solid rgba(214, 175, 55, 0.25) !important;
    }}
    
    /* Forzar la lectura de textos en blanco dentro del Sidebar */
    div[data-testid="stSidebar"] h1, 
    div[data-testid="stSidebar"] h2, 
    div[data-testid="stSidebar"] h3, 
    div[data-testid="stSidebar"] p, 
    div[data-testid="stSidebar"] label, 
    div[data-testid="stSidebar"] span,
    div[data-testid="stSidebar"] small,
    div[data-testid="stSidebar"] div {{
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}
    
    /* Resaltar las métricas de cuotas y Kelly en Dorado Premium */
    div[data-testid="stSidebar"] div[data-testid="stMetricValue"] div,
    div[data-testid="stSidebar"] div[data-testid="stMetricValue"] span {{
        color: #D4AF37 !important;
        font-weight: 700 !important;
    }}
    
    /* Estilizar las cajas de entrada numéricas y sliders en el Sidebar */
    div[data-testid="stSidebar"] div.stNumberInput, 
    div[data-testid="stSidebar"] div.stSlider {{
        border: 1px solid rgba(214, 175, 55, 0.2) !important;
        background-color: rgba(18, 19, 22, 0.9) !important;
        padding: 12px !important;
        border-radius: 4px !important;
        margin-bottom: 10px;
    }}
    
    /* Tipografía y Títulos Limpios en Panel Central */
    h1, h2, h3, p, label, span {{
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}
    
    h1 {{
        font-weight: 700 !important;
        letter-spacing: -0.05em;
        border-bottom: 1px solid rgba(214, 175, 55, 0.3);
        padding-bottom: 10px;
    }}
    
    /* Botones Premium (Negro y Dorado de Quantum Dahlia) */
    .stButton>button, div[data-testid="stSidebar"] .stButton>button {{
        background-color: #121316 !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 4px !important;
        width: 100%;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 14px 0px;
        transition: all 0.4s ease;
    }}
    
    .stButton>button:hover, div[data-testid="stSidebar"] .stButton>button:hover {{
        background-color: #D4AF37 !important;
        color: #0A0A0C !important;
        box-shadow: 0px 0px 25px rgba(214, 175, 55, 0.4);
        border: 1px solid #D4AF37 !important;
    }}
    
    /* Inputs y Selectores del Panel Central */
    div.stSelectbox div[data-baseweb="select"] {{
        background-color: rgba(18, 19, 22, 0.9) !important;
        border: 1px solid rgba(214, 175, 55, 0.2) !important;
    }}
    
    div.stNumberInput input {{
        background-color: rgba(18, 19, 22, 0.9) !important;
        color: #FFFFFF !important;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    div[data-testid="stAppDeployButton"] {{display: none !important;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def colorificar_ev(val):
    try:
        val_float = float(val)
        if val_float > 0.0:
            return 'background-color: #2c2001; color: #D4AF37; font-weight: bold;'
        elif val_float < 0.0:
            return 'background-color: #121316; color: #f07167;'
        else:
            return 'background-color: #121316; color: #94a3b8;'
    except (ValueError, TypeError):
        return 'background-color: #121316; color: #94a3b8;'

def main():
    # ---------------------------------------------------------
    # ZONA 1: Inicialización del Estado de la Sesión
    # ---------------------------------------------------------
    if "combinada_actual" not in st.session_state:
        st.session_state.combinada_actual = []
    if "df_valores" not in st.session_state:
        st.session_state.df_valores = None
    if "df_lineas" not in st.session_state:
        st.session_state.df_lineas = None
    if "partido_activo" not in st.session_state:
        st.session_state.partido_activo = ""

    st.title("QUANTUM DAHLIA SPORTS INVESTMENTS")
    
    # Selector de Modelo para cambiar el fondo dinámicamente
    modelo_activo = st.selectbox(
        "Arquitectura de Simulación Activa",
        ["Simulación Montecarlo (100k)", "Poisson Bivariado / Dixon-Coles"]
    )
    
    # Cargar el entorno visual personalizado según el modelo elegido
    aplicar_estilo_dinamico(modelo_activo)
    
    # ---------------------------------------------------------
    # ZONA 2: Panel de Control del Ticket (Sidebar Estilizado)
    # ---------------------------------------------------------
    st.sidebar.markdown("## 📋 Ticket de la Sociedad")
    
    if st.sidebar.button("Vaciar Ticket"):
        st.session_state.combinada_actual = []
        st.rerun()
        
    cuota_acumulada = 1.0
    prob_acumulada = 1.0
    contiene_trampa = False
    
    if st.session_state.combinada_actual:
        for bet in st.session_state.combinada_actual:
            alerta = "⚠️" if bet['ev_individual'] < -3.0 else "🔹"
            if bet['ev_individual'] < -3.0:
                contiene_trampa = True
                
            st.sidebar.write(f"{alerta} **{bet['partido']}**")
            st.sidebar.write(f"   _{bet['mercado']}_")
            st.sidebar.write(f"   Cuota: {bet['cuota']:.2f} | EV: {bet['ev_individual']:.1f}%")
            st.sidebar.markdown("---")
            
            cuota_acumulada *= bet['cuota']
            prob_acumulada *= (bet['prob_modelo'] / 100.0)
            
        st.sidebar.metric(label="Cuota Total Combinada", value=f"{cuota_acumulada:.2f}x")
        
        # Valor Esperado del Ticket Completo
        ev_combinado = (prob_acumulada * cuota_acumulada) - 1
        
        if contiene_trampa:
            st.sidebar.warning("¡Cuidado! El ticket incluye selecciones con EV Negativo (Cuotas Trampa).")
            
        if ev_combinado > 0:
            st.sidebar.success(f"📈 EV Combinado: +{ev_combinado*100:.1f}% (VALOR)")
        else:
            st.sidebar.error(f"📉 EV Combinado: {ev_combinado*100:.1f}% (SIN VALOR)")
            
        # CALCULADORA DE KELLY INTEGRADA CON BASE AJUSTADA A $25
        st.sidebar.markdown("### 💰 Gestión de Banca (Kelly)")
        banca_total = st.sidebar.number_input("Banca Común ($)", min_value=1.0, value=25.0, step=1.0)
        fraccion_k = st.sidebar.slider("Fracción de Seguridad", min_value=0.05, max_value=1.0, value=0.25, step=0.05)
        
        pct_banca, dinero_stake = calcular_stake_kelly(prob_acumulada, cuota_acumulada, banca_total, fraccion_k)
        
        if dinero_stake > 0:
            st.sidebar.metric(label="Inversión Sugerida", value=f"${dinero_stake:.2f}", delta=f"{pct_banca:.1f}% de banca")
        else:
            st.sidebar.info("Kelly recomienda: No arriesgar capital en esta combinación.")
    else:
        st.sidebar.info("Analiza un partido en el panel central para comenzar a estructurar tu ticket.")

    # Bloque de introducción de Datos de Equipos
    st.markdown("### Parámetros de Rendimiento")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        equipo_1 = st.text_input("Escuadra Local", value="Paris Saint-Germain")
        stats_e1 = di.get_team_stats(equipo_1)
        
    with col_t2:
        equipo_2 = st.text_input("Escuadra Visitante", value="Barcelona")
        stats_e2 = di.get_team_stats(equipo_2)
        
    st.markdown("---")
    
    # Bloque de introducción de Cuotas de Mercado
    cuotas_mercado = di.get_market_odds()
    
    st.markdown("---")
    
    # Botón de Procesamiento
    if st.button("Ejecutar Modelos Cuantitativos"):
        analisis_analitico = mm.procesar_modelos_matematicos(stats_e1, stats_e2, cuotas_mercado)
        analisis_simulado = sim.ejecutar_montecarlo(stats_e1, stats_e2, n_simulaciones=100000)
        
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

    # =========================================================
    # RENDERIZADO DE LAS TABLAS
    # =========================================================
    if st.session_state.df_valores is not None:
        st.markdown(f"## Análisis Actual: {st.session_state.partido_activo}")
        
        propiedades_oscuras = {'background-color': '#121316', 'color': '#FFFFFF', 'border-color': '#27272a'}
        
        # TABLA 1: Mercados Principales
        st.markdown("### Proyección de Valor Esperado")
        col_ev_valores = next((c for c in st.session_state.df_valores.columns if "ev" in c.lower()), None)
        
        if col_ev_valores:
            df_valores_estilado = st.session_state.df_valores.style.set_properties(**propiedades_oscuras).map(colorificar_ev, subset=[col_ev_valores])
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(st.session_state.df_valores.style.set_properties(**propiedades_oscuras), use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # TABLA 2: Líneas Cortas (Córners y Tarjetas)
        st.markdown("### Estimación de Líneas Cortas")
        if st.session_state.df_lineas is not None:
            col_ev_lineas = next((c for c in st.session_state.df_lineas.columns if "ev" in c.lower()), None)
            if col_ev_lineas:
                df_lineas_estilado = st.session_state.df_lineas.style.set_properties(**propiedades_oscuras).map(colorificar_ev, subset=[col_ev_lineas])
                st.dataframe(df_lineas_estilado, use_container_width=True, hide_index=True)
            else:
                st.dataframe(st.session_state.df_lineas.style.set_properties(**propiedades_oscuras), use_container_width=True, hide_index=True)
            
        # ---------------------------------------------------------
        # ZONA 3: MODIFICADA - CALCULADORA DINÁMICA DE EV REAL
        # ---------------------------------------------------------
        st.markdown("### ➕ Panel de Carga al Ticket")
        
        origen_seleccionado = st.radio(
            "Selecciona la procedencia del mercado que deseas jugar:",
            ["Mercados Principales (Tabla 1)", "Líneas Cortas / Córners / Tarjetas (Tabla 2)"],
            horizontal=True
        )
        
        # Contenedor premium para la calculadora reactiva
        with st.container():
            if origen_seleccionado == "Mercados Principales (Tabla 1)" and st.session_state.df_valores is not None:
                df_origen = st.session_state.df_valores
                col_id = next((c for c in df_origen.columns if c.lower() in ["mercado", "market", "opción", "opcion"]), df_origen.columns[0])
                opciones = df_origen[col_id].dropna().unique().tolist()
                
                mercado_elegido = st.selectbox("Selecciona el mercado principal:", options=opciones)
                
                fila = df_origen[df_origen[col_id] == mercado_elegido].iloc[0]
                col_cuota_std = next((c for c in df_origen.columns if "cuota" in c.lower() or "odd" in c.lower()), df_origen.columns[0])
                col_prob_std = next((c for c in df_origen.columns if "prob" in c.lower() or "%" in c.lower()), df_origen.columns[1])
                
                try:
                    cuota_base = float(str(fila[col_cuota_std]).replace('%', '').strip())
                    prob_base = float(str(fila[col_prob_std]).replace('%', '').strip())
                    if 0.0 < prob_base <= 1.0: prob_base *= 100.0
                except:
                    cuota_base, prob_base = 1.85, 50.0
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    cuota_real_casa = st.number_input("Cuota Real Vigente en la Casa", min_value=1.01, value=cuota_base, step=0.01, key="input_cuota_p")
                with col_c2:
                    ev_dinamico = ((prob_base / 100.0) * cuota_real_casa - 1) * 100
                    st.metric("EV Real Calculado", f"{ev_dinamico:.2f}%", delta=f"{ev_dinamico:.1f}%", delta_color="normal")
                
                if st.button("Asegurar Selección en el Ticket", key="btn_add_p_fixed"):
                    st.session_state.combinada_actual.append({
                        "partido": st.session_state.partido_activo,
                        "mercado": str(mercado_elegido),
                        "cuota": cuota_real_casa,
                        "prob_modelo": prob_base,
                        "ev_individual": ev_dinamico
                    })
                    st.success(f"Agregado: {mercado_elegido} @{cuota_real_casa:.2f}")
                    st.rerun()
                    
            elif origen_seleccionado == "Líneas Cortas / Córners / Tarjetas (Tabla 2)" and st.session_state.df_lineas is not None:
                df_origen = st.session_state.df_lineas
                col_id = next((c for c in df_origen.columns if c.lower() in ["mercado", "market", "línea", "linea", "estadística", "estadistica"]), df_origen.columns[0])
                opciones = df_origen[col_id].dropna().unique().tolist()
                
                mercado_elegido = st.selectbox("Selecciona la línea base (Métrica/Línea):", options=opciones)
                direccion = st.radio("Pronóstico para esta línea:", ["Más / Over", "Menos / Under"], horizontal=True)
                
                # Extraer la probabilidad pura del modelo para la dirección elegida
                fila = df_origen[df_origen[col_id] == mercado_elegido].iloc[0]
                columnas_disponibles = df_origen.columns.tolist()
                variante_col = "más" if "más" in direccion.lower() or "over" in direccion.lower() else "menos"
                variante_alt = "over" if variante_col == "más" else "under"
                
                col_prob = next((c for c in columnas_disponibles if ("prob" in c.lower() or "%" in c.lower()) and (variante_col in c.lower() or variante_alt in c.lower())), None)
                col_cuota = next((c for c in columnas_disponibles if ("cuota" in c.lower() or "odd" in c.lower()) and (variante_col in c.lower() or variante_alt in c.lower())), None)
                
                try:
                    prob_base = float(str(fila[col_prob]).replace('%', '').strip()) if col_prob else 50.0
                    if 0.0 < prob_base <= 1.0: prob_base *= 100.0
                    cuota_base = float(str(fila[col_cuota]).replace('%', '').strip()) if col_cuota else 1.85
                except:
                    prob_base = 50.0
                    cuota_base = 1.85
                
                # Campos dinámicos para capturar cuotas reales de la casa de apuestas
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    cuota_real_casa = st.number_input(f"Cuota de la Casa para {direccion}", min_value=1.01, value=cuota_base, step=0.01, key="input_cuota_l")
                with col_l2:
                    # RECALCULO DE EV REAL EN TIEMPO REAL
                    ev_dinamico = ((prob_base / 100.0) * cuota_real_casa - 1) * 100
                    st.metric("EV Real Calculado", f"{ev_dinamico:.2f}%", delta=f"{ev_dinamico:.1f}%")
                
                nombre_mercado_final = f"{mercado_elegido} - {direccion}"
                
                if st.button("Asegurar Selección en el Ticket", key="btn_add_l_fixed"):
                    ya_existe = any(b["partido"] == st.session_state.partido_activo and b["mercado"] == nombre_mercado_final for b in st.session_state.combinada_actual)
                    if not ya_existe:
                        st.session_state.combinada_actual.append({
                            "partido": st.session_state.partido_activo,
                            "mercado": nombre_mercado_final,
                            "cuota": cuota_real_casa,
                            "prob_modelo": prob_base,
                            "ev_individual": ev_dinamico
                        })
                        st.success(f"Agregado al Ticket: {nombre_mercado_final} @{cuota_real_casa:.2f} (EV: {ev_dinamico:.1f}%)")
                        st.rerun()
                    else:
                        st.warning("Esta selección ya se encuentra guardada en el ticket.")
            else:
                st.info("Ejecuta los modelos matemáticos cuantitativos para habilitar el panel de carga.")

if __name__ == "__main__":
    main()
