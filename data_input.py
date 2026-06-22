# data_input.py
import streamlit as st
import pandas as pd

def render_db_uploader():
    """
    Renderiza el cargador de la base de datos en el sidebar.
    Se conecta con el CSV de la Matriz Cuantitativa descargado de Google Sheets.
    """
    st.sidebar.markdown("### 🗄️ Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz Cuantitativa (CSV)", type=["csv"], key="db_uploader")
    
    if archivo:
        try:
            st.session_state.db_matriz = pd.read_csv(archivo)
            st.sidebar.success("✅ Matriz conectada. Datos automatizados.")
        except Exception as e:
            st.sidebar.error("Error al leer el CSV.")
    else:
        st.session_state.db_matriz = None

def get_team_stats(team_name):
    """
    Recolecta las estadísticas base de un equipo.
    Si la matriz está cargada, busca al país y autocompleta con ponderaciones 60/40.
    """
    st.subheader(f"📊 Estadísticas: {team_name}")
    
    # 1. Valores por defecto (se usarán si el país no está en el Excel)
    val_goles_pp = 1.5
    val_goles_contra = 1.0
    val_xg = 1.5
    val_corners = 4.5
    val_tarjetas = 2.0
    val_goles_1t = 0.5
    val_tiros = 10.0
    val_puerta = 4.0
    
    # 2. Extracción y cálculo automatizado desde la Matriz de Excel
    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        if 'Pais' in df.columns:
            # Buscar el equipo en la columna 'Pais' ignorando mayúsculas/minúsculas
            match = df[df['Pais'].str.contains(team_name, case=False, na=False, regex=False)]
            if not match.empty:
                row = match.iloc[0]
                st.caption("✨ Datos importados desde la Matriz (60% Clasificación / 40% Mundial)")
                
                try:
                    # Cálculo al vuelo: (Historico * 0.60) + (Reciente * 0.40)
                    g_clas = float(row.get('Clas_Goles_Favor_Prom', val_goles_pp))
                    g_mund = float(row.get('Mundial_Ult_Goles_Favor', g_clas))
                    val_goles_pp = (g_clas * 0.6) + (g_mund * 0.4)
                    
                    gc_clas = float(row.get('Clas_Goles_Contra_Prom', val_goles_contra))
                    gc_mund = float(row.get('Mundial_Ult_Goles_Contra', gc_clas))
                    val_goles_contra = (gc_clas * 0.6) + (gc_mund * 0.4)
                    
                    c_clas = float(row.get('Clas_Corners_Prom', val_corners))
                    c_mund = float(row.get('Mundial_Ult_Corners', c_clas))
                    val_corners = (c_clas * 0.6) + (c_mund * 0.4)
                    
                    t_clas = float(row.get('Clas_Tarjetas_Prom', val_tarjetas))
                    t_mund = float(row.get('Mundial_Ult_Tarjetas', t_clas))
                    val_tarjetas = (t_clas * 0.6) + (t_mund * 0.4)
                    
                    g1_clas = float(row.get('Goles_1T_Ult10_Favor_Prom', val_goles_1t))
                    g1_mund = float(row.get('Goles_1T_Ult_Mundial_Favor', g1_clas))
                    val_goles_1t = (g1_clas * 0.6) + (g1_mund * 0.4)
                    
                    # El xG esperado inicialmente lo atamos a la proyección,
                    # tú puedes sobreescribirlo a mano en la interfaz si lo deseas.
                    val_xg = val_goles_pp 
                except ValueError:
                    pass

    # 3. Renderizado de los campos en la Terminal
    col1, col2 = st.columns(2)
    
    with col1:
        goles_pp = st.number_input(f"Goles a Favor (Ponderado)", min_value=0.0, value=float(val_goles_pp), step=0.1, key=f"gf_{team_name}")
        goles_contra = st.number_input(f"Goles en Contra (Ponderado)", min_value=0.0, value=float(val_goles_contra), step=0.1, key=f"gc_{team_name}")
        xg_reciente = st.number_input(f"xG Último Partido", min_value=0.0, value=float(val_xg), step=0.1, key=f"xg_{team_name}")
        goles_1t = st.number_input(f"Goles 1ra Mitad (HT)", min_value=0.0, value=float(val_goles_1t), step=0.1, key=f"g1t_{team_name}")
        
    with col2:
        corners = st.number_input(f"Córners Totales", min_value=0.0, value=float(val_corners), step=0.5, key=f"cor_{team_name}")
        tarjetas = st.number_input(f"Tarjetas Totales", min_value=0.0, value=float(val_tarjetas), step=0.5, key=f"tarj_{team_name}")
        tiros_totales = st.number_input(f"Tiros totales", min_value=0.0, value=float(val_tiros), step=0.5, key=f"ti_{team_name}")
        tiros_puerta = st.number_input(f"Tiros a puerta", min_value=0.0, value=float(val_puerta), step=0.5, key=f"tp_{team_name}")

    return {
        "goles_pp": goles_pp,
        "goles_contra": goles_contra,
        "xg_reciente": xg_reciente,
        "tiros_totales": tiros_totales,
        "tiros_puerta": tiros_puerta,
        "atajadas": 3.0, 
        "posesion": 50.0,
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
        cuota_mas_1_5 = st.number_input("Más de 1.5 goles", min_value=1.0, value=1.25, step=0.05)
        cuota_menos_1_5 = st.number_input("Menos de 1.5 goles", min_value=1.0, value=3.50, step=0.05)
        btts_si = st.number_input("Ambos Anotan (Sí)", min_value=1.0, value=1.75, step=0.05)
        
    with col3:
        st.markdown("**Nuevos Mercados**")
        cuota_1t_local = st.number_input("Victoria 1T (Local)", min_value=1.0, value=2.70, step=0.05)
        cuota_1t_visita = st.number_input("Victoria 1T (Visita)", min_value=1.0, value=3.60, step=0.05)
        linea_corners = st.number_input("Línea Córners (Ej. O/U 9.5)", min_value=0.5, value=9.5, step=0.5)
        linea_tarjetas = st.number_input("Línea Tarjetas (Ej. O/U 4.5)", min_value=0.5, value=4.5, step=0.5)

    return {
        "1x2": [cuota_local, cuota_empate, cuota_visitante],
        "goles_2_5": [cuota_mas_2_5, cuota_menos_2_5],
        "goles_1_5": [cuota_mas_1_5, cuota_menos_1_5],
        "btts_si": btts_si,
        "victoria_1t": [cuota_1t_local, cuota_1t_visita],
        "lineas": {"corners": linea_corners, "tarjetas": linea_tarjetas}
    }
