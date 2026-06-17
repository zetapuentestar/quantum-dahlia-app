# data_input.py
import streamlit as st

def get_team_stats(team_name):
    """
    Recolecta las estadísticas base de un equipo.
    Clave: Usar value=0.0 y step=0.1 para forzar el uso de decimales.
    """
    st.subheader(f"📊 Estadísticas: {team_name}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas Generales (Floats)
        goles_pp = st.number_input(f"Goles por partido", min_value=0.0, value=1.5, step=0.1, key=f"goles_{team_name}")
        tiros_totales = st.number_input(f"Tiros totales", min_value=0.0, value=10.0, step=0.5, key=f"tiros_{team_name}")
        tiros_puerta = st.number_input(f"Tiros a puerta", min_value=0.0, value=4.0, step=0.5, key=f"puerta_{team_name}")
        atajadas = st.number_input(f"Atajadas", min_value=0.0, value=3.0, step=0.5, key=f"atajadas_{team_name}")
        
    with col2:
        # Nuevos mercados y estadísticas expandidas
        posesion = st.number_input(f"Posesión (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.5, key=f"pos_{team_name}")
        corners = st.number_input(f"Córners por partido", min_value=0.0, value=4.5, step=0.5, key=f"corners_{team_name}")
        tarjetas = st.number_input(f"Tarjetas por partido", min_value=0.0, value=2.0, step=0.5, key=f"tarjetas_{team_name}")
        goles_1t = st.number_input(f"Goles 1ra Mitad (HT)", min_value=0.0, value=0.5, step=0.1, key=f"goles1t_{team_name}")

    return {
        "goles_pp": goles_pp,
        "tiros_totales": tiros_totales,
        "tiros_puerta": tiros_puerta,
        "atajadas": atajadas,
        "posesion": posesion,
        "corners": corners,
        "tarjetas": tarjetas,
        "goles_1t": goles_1t
    }

def get_market_odds():
    """
    Recolecta las cuotas de las casas de apuestas.
    """
    st.subheader("🏦 Cuotas del Mercado (Bookies)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Mercado 1X2**")
        cuota_local = st.number_input("Victoria Local (1)", min_value=1.0, value=2.10, step=0.05)
        cuota_empate = st.number_input("Empate (X)", min_value=1.0, value=3.40, step=0.05)
        cuota_visitante = st.number_input("Victoria Visita (2)", min_value=1.0, value=3.10, step=0.05)
        
    with col2:
        st.markdown("**Goles Totales**")
        cuota_mas_2_5 = st.number_input("Más de 2.5 goles", min_value=1.0, value=1.85, step=0.05)
        cuota_menos_2_5 = st.number_input("Menos de 2.5 goles", min_value=1.0, value=1.95, step=0.05)
        cuota_mas_1_5 = st.number_input("Más de 1.5 goles", min_value=1.0, value=1.25, step=0.05) # NUEVO
        cuota_menos_1_5 = st.number_input("Menos de 1.5 goles", min_value=1.0, value=3.50, step=0.05) # NUEVO
        btts_si = st.number_input("Ambos Anotan (Sí)", min_value=1.0, value=1.75, step=0.05)
        
    with col3:
        st.markdown("**Nuevos Mercados**")
        cuota_1t_local = st.number_input("Victoria 1T (Local)", min_value=1.0, value=2.70, step=0.05) # NUEVO
        cuota_1t_visita = st.number_input("Victoria 1T (Visita)", min_value=1.0, value=3.60, step=0.05) # NUEVO
        linea_corners = st.number_input("Línea Córners (Ej. O/U 9.5)", min_value=0.5, value=9.5, step=0.5) # NUEVO
        linea_tarjetas = st.number_input("Línea Tarjetas (Ej. O/U 4.5)", min_value=0.5, value=4.5, step=0.5) # NUEVO

    return {
        "1x2": [cuota_local, cuota_empate, cuota_visitante],
        "goles_2_5": [cuota_mas_2_5, cuota_menos_2_5],
        "goles_1_5": [cuota_mas_1_5, cuota_menos_1_5],
        "btts_si": btts_si,
        "victoria_1t": [cuota_1t_local, cuota_1t_visita],
        "lineas": {"corners": linea_corners, "tarjetas": linea_tarjetas}
    }
