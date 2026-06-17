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
    
    /* Forzar iconos del header (GitHub, Ajustes, Desplegar) a Blanco Puro */
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
    
    /* Ocultar elementos innecesarios */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    div[data-testid="stAppDeployButton"] {{display: none !important;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- MODIFICACIÓN 1: AJUSTE DE COLORES EXPLICITOS PARA EVITAR TEXTO INVISIBLE ---
def colorificar_ev(val):
    try:
        val_float = float(val)
        if val_float > 0.0:
            # Fondo dorado oscuro opaco, texto dorado brillante
            return 'background-color: #2c2001; color: #D4AF37; font-weight: bold;'
        elif val_float < 0.0:
            return 'background-color: #18181b; color: #f07167;'
        else:
            return 'background-color: #18181b; color: #94a3b8;'
    except (ValueError, TypeError):
        return 'background-color: #18181b; color: #94a3b8;'

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
            st.sidebar.warning("¡Cuidado! El ticket includes selecciones con EV Negativo (Cuotas Trampa).")
            
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
        # 1. Ejecución en paralelo del backend matemático
        analisis_analitico = mm.procesar_modelos_matematicos(stats_e1, stats_e2, cuotas_mercado)
        analisis_simulado = sim.ejecutar_montecarlo(stats_e1, stats_e2, n_simulaciones=100000)
        
        # 2. Enrutamiento inteligente de datos para la Tabla 1
        if modelo_activo == "Poisson Bivariado / Dixon-Coles":
            if "prob_1x2_1t" not in analisis_analitico:
                analisis_analitico["prob_1x2_1t"] = {
                    "Local": 0.0, 
                    "Empate": 0.0, 
                    "Visita": 0.0, 
                    "Visitante": 0.0
                }
            df_valores = rep.generar_reporte_valores(analisis_analitico, cuotas_mercado)
        else:
            df_valores = rep.generar_reporte_valores(analisis_simulado, cuotas_mercado)
            
        # 3. La Tabla 2 SIEMPRE se alimenta de Montecarlo para Córners y Tarjetas
        df_lineas = rep.generar_reporte_lineas_asiaticas(analisis_simulado, cuotas_mercado)
        
        # Almacenar en el estado para persistencia entre clicks del formulario
        st.session_state.df_valores = df_valores
        st.session_state.df_lineas = df_lineas
        st.session_state.partido_activo = f"{equipo_1} vs {equipo_2}"

    # =========================================================
    # MODIFICACIÓN 2: RENDERIZADO DE LAS TABLAS MODO OSCURO TOTAL
    # =========================================================
    if st.session_state.df_valores is not None:
        st.markdown(f"## Análisis Actual: {st.session_state.partido_activo}")
        
        # Diccionario de propiedades CSS para forzar la tabla oscura premium
        propiedades_oscuras = {
            'background-color': '#121316',  # Fondo oscuro juego con los botones
            'color': '#FFFFFF',             # Texto blanco puro para lectura perfecta
            'border-color': '#27272a'       # Bordes sutiles oscuros
        }
        
        # Renderizado de Reporte 1: Mercados Principales
        st.markdown("### Proyección de Valor Esperado")
        if "EV (%)" in st.session_state.df_valores.columns:
            # Encadenamos la colorificación del EV y aplicamos el fondo oscuro al resto de celdas
            df_valores_estilado = st.session_state.df_valores.style \
                .map(colorificar_ev, subset=["EV (%)"]) \
                .set_properties(**propiedades_oscuras)
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
        else:
            df_valores_oscuro = st.session_state.df_valores.style.set_properties(**propiedades_oscuras)
            st.dataframe(df_valores_oscuro, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # Renderizado de Reporte 2: Mercados Estadísticos Volátiles (Córners y Tarjetas)
        st.markdown("### Estimación de Líneas Cortas")
        df_lineas_oscuro = st.session_state.df_lineas.style.set_properties(**propiedades_oscuras)
        st.dataframe(df_lineas_oscuro, use_container_width=True, hide_index=True)
        
        # ---------------------------------------------------------
        # ZONA 3: Constructor Dinámico de Combinadas
        # ---------------------------------------------------------
        st.markdown("### ➕ Panel de Carga al Ticket")
        with st.form("add_bet_form"):
            opciones_mercado = st.session_state.df_valores["Market" if "Market" in st.session_state.df_valores.columns else "Mercado"].tolist()
            mercado_elegido = st.selectbox("Selecciona el mercado validado para añadir a la combinada:", options=opciones_mercado)
            
            btn_agregar = st.form_submit_button("Asegurar Selección en el Ticket")
            
            if btn_agregar and mercado_elegido:
                col_filtro = "Market" if "Market" in st.session_state.df_valores.columns else "Mercado"
                fila = st.session_state.df_valores[st.session_state.df_valores[col_filtro] == mercado_elegido].iloc[0]
                
                # DETECTOR DINÁMICO DE COLUMNAS
                columnas_disponibles = st.session_state.df_valores.columns.tolist()
                
                col_prob = next((c for c in columnas_disponibles if "prob" in c.lower()), None)
                col_cuota = next((c for c in columnas_disponibles if "cuota" in c.lower() or "odd" in c.lower()), None)
                col_ev = next((c for c in columnas_disponibles if "ev" in c.lower()), None)
                
                if col_prob and col_cuota:
                    ya_existe = any(b["partido"] == st.session_state.partido_activo and b["mercado"] == mercado_elegido for b in st.session_state.combinada_actual)
                    
                    if not ya_existe:
                        st.session_state.combinada_actual.append({
                            "partido": st.session_state.partido_activo,
                            "mercado": mercado_elegido,
                            "cuota": float(fila[col_cuota]),
                            "prob_modelo": float(fila[col_prob]),
                            "ev_individual": float(fila[col_ev]) if col_ev else 0.0
                        })
                        st.success(f"Agregado con éxito: {mercado_elegido}")
                        st.rerun()
                    else:
                        st.warning("Esta selección ya se encuentra en el ticket.")
                else:
                    st.error(f"Error de Estructura: Columnas detectadas: {columnas_disponibles}")

if __name__ == "__main__":
    main()
