# app.py
import streamlit as st
import pandas as pd
import data_input as di
import math_models as mm
import simulation as sim
import report as rep

# Configuración inicial de la página
st.set_page_config(
    page_title="Quantum Dahlia - Terminal de Inversión",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def aplicar_estilo_dinamico(modelo_seleccionado):
    """
    Inyecta CSS avanzado para controlar el fondo dinámico mediante enlaces web,
    establecer el modo oscuro absoluto y dar un acabado premium.
    """
    # Enlaces web directos en alta definición (Fútbol de Élite / Copa Mundial)
    imagenes_fondo = {
        "Simulación Montecarlo (100k)": "https://in.pinterest.com/pin/726979564881581700/",
        "Poisson Bivariado / Dixon-Coles": "https://in.pinterest.com/pin/726979564881581700/"
    }
    
    url_fondo = imagenes_fondo.get(modelo_seleccionado, imagenes_fondo["Simulación Montecarlo (100k)"])
    
    css = f"""
    <style>
    /* Fondo Dinámico con máscara de fusión negra profunda */
    .stApp {{
        background-image: url("{url_fondo}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: #0A0A0C !important;
        background-blend-mode: multiply;
    }}
    
    /* Contenedores de datos semi-transparentes elegantes */
    div[data-testid="stVerticalBlock"] > div {{
        background-color: rgba(15, 16, 20, 0.75);
        border-radius: 6px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }}
    
    /* Tipografía y Títulos Limpios sin emojis */
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
    
    /* Botón de Ejecución (Negro y Dorado Premium) */
    .stButton>button {{
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
    
    .stButton>button:hover {{
        background-color: #D4AF37 !important;
        color: #0A0A0C !important;
        box-shadow: 0px 0px 25px rgba(214, 175, 55, 0.4);
        border: 1px solid #D4AF37 !important;
    }}
    
    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def colorificar_ev(val):
    """
    Aplica estilos de color de forma segura a la columna EV (%).
    Retorna verde esmeralda si hay valor, o un tono neutro si no lo hay.
    """
    try:
        val_float = float(val)
        if val_float > 0.0:
            return 'background-color: rgba(0, 230, 118, 0.15); color: #00E676; font-weight: bold;'
        elif val_float < 0.0:
            return 'color: rgba(255, 255, 255, 0.4);'
    except ValueError:
        pass
    return ''

def main():
    st.title("QUANTUM DAHLIA SPORTS INVESTMENTS")
    
    # Selector de Modelo para cambiar el fondo dinámicamente
    modelo_activo = st.selectbox(
        "Arquitectura de Simulación Activa",
        ["Simulación Montecarlo (100k)", "Poisson Bivariado / Dixon-Coles"]
    )
    
    # Cargar el entorno visual personalizado según el modelo elegido
    aplicar_estilo_dinamico(modelo_activo)
    
    # Bloque de introducción de Datos de Equipos
    st.markdown("### Parámetros de Rendimiento")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        equipo_1 = st.text_input("Escuadra Local", value="Paris Saint-Germain")
        stats_e1 = di.get_team_stats(equipo_1)
        
    with col_t2:
        equipo_2 = st.text_input("Escuadra Visitante", value="Rival")
        stats_e2 = di.get_team_stats(equipo_2)
        # Cálculo automático de posesión inversa
        stats_e2["posesion"] = 100.0 - stats_e1["posesion"]
        st.caption(f"Distribución de Posesión Automática para {equipo_2}: {stats_e2['posesion']}%")
        
    st.markdown("---")
    
    # Bloque de introducción de Cuotas de Mercado
    cuotas_mercado = di.get_market_odds()
    
    st.markdown("---")
    
    # Botón de Procesamiento
    if st.button("Ejecutar Modelos Cuantitativos"):
        
        # 1. Ejecución del backend matemático
        analisis_analitico = mm.procesar_modelos_matematicos(stats_e1, stats_e2, cuotas_mercado)
        analisis_simulado = sim.ejecutar_montecarlo(stats_e1, stats_e2, n_simulaciones=100000)
        
        # 2. Generación de DataFrames estructurados desde report.py
        df_valores = rep.generar_reporte_valores(analisis_simulado, cuotas_mercado)
        df_lineas = rep.generar_reporte_lineas_asiaticas(analisis_simulado, cuotas_mercado)
        
        # 3. Renderizado de Reporte 1: Mercados Principales con Estilos Anti-KeyError
        st.markdown("### Proyección de Valor Esperado")
        
        if "EV (%)" in df_valores.columns:
            df_valores_estilado = df_valores.style.map(colorificar_ev, subset=["EV (%)"])
            st.dataframe(df_valores_estilado, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_valores, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        
        # 4. Renderizado de Reporte 2: Mercados Estadísticos Volátiles (Córners y Tarjetas)
        st.markdown("### Estimación de Líneas Cortas")
        st.dataframe(df_lineas, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
