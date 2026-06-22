# data_input.py
import streamlit as st
import pandas as pd
import numpy as np

import streamlit as st
import pandas as pd

def render_db_uploader():
    st.sidebar.markdown("### 📋 Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz Cuantitativa (Excel/CSV)", type=["xlsx", "csv"], key="db_uploader")
    if archivo:
        try:
            if archivo.name.endswith('.csv'):
                st.session_state.db_matriz = pd.read_csv(archivo, header=None)
            else:
                st.session_state.db_matriz = pd.read_excel(archivo, header=None)
            st.sidebar.success("✅ Datos cargados.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

def get_team_stats(team_name):
    # Valores base por defecto
    stats = {"posesion": 50.0, "goles_favor": 1.5, "goles_contra": 1.0, "tiros": 10.0, 
             "puerta": 4.0, "atajadas": 0.0, "corners": 4.0, "tarjetas": 0.0, "xg": 1.3, "goles_1t": 0.5}

    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        # Buscar la fila del país
        found_idx = None
        for idx in range(len(df)):
            if team_name.upper() in str(df.iloc[idx, 0]).upper():
                found_idx = idx
                break
        
        if found_idx is not None:
            # Escanear filas debajo del país
            for i in range(found_idx + 1, found_idx + 12):
                if i >= len(df): break
                row = df.iloc[i]
                key = str(row[0]).lower()
                val = row[4] # Columna E (Ponderado)
                if pd.isna(val): continue
                
                try:
                    if "posesion" in key: stats["posesion"] = float(val)
                    elif "goles a favor" in key: stats["goles_favor"] = float(val)
                    elif "goles en contra" in key: stats["goles_contra"] = float(val)
                    elif "tiros totales" in key: stats["tiros"] = float(val)
                    elif "tiros a puerta" in key: stats["puerta"] = float(val)
                    elif "atajadas" in key: stats["atajadas"] = float(val)
                    elif "corners" in key: stats["corners"] = float(val)
                    elif "tarjetas" in key: stats["tarjetas"] = float(val)
                    elif "esperados" in key: stats["xg"] = float(val)
                    elif "goles 1t" in key: stats["goles_1t"] = float(val)
                except: continue

    # Renderizado UI unificado
    col1, col2 = st.columns(2)
    with col1:
        out_g_f = st.number_input("Goles Favor (Pond)", value=stats["goles_favor"], step=0.1, key=f"gf_{team_name}")
        out_g_c = st.number_input("Goles Contra (Pond)", value=stats["goles_contra"], step=0.1, key=f"gc_{team_name}")
        out_xg = st.number_input("xG (Pond)", value=stats["xg"], step=0.1, key=f"xg_{team_name}")
        out_g1t = st.number_input("Goles 1T", value=stats["goles_1t"], step=0.1, key=f"g1t_{team_name}")
        out_pos = st.number_input("Posesión (%)", value=stats["posesion"], step=1.0, key=f"pos_{team_name}")
    with col2:
        out_cor = st.number_input("Córners", value=stats["corners"], step=0.5, key=f"cor_{team_name}")
        out_tar = st.number_input("Tarjetas", value=stats["tarjetas"], step=0.5, key=f"tar_{team_name}")
        out_tir = st.number_input("Tiros Totales", value=stats["tiros"], step=0.5, key=f"ti_{team_name}")
        out_pue = st.number_input("Tiros a Puerta", value=stats["puerta"], step=0.5, key=f"tp_{team_name}")
        out_ata = st.number_input("Atajadas", value=stats["atajadas"], step=0.5, key=f"at_{team_name}")

    return {
        "goles_favor": out_g_f, "goles_contra": out_g_c, "xg": out_xg, "goles_1t": out_g1t,
        "posesion": out_pos, "corners": out_cor, "tarjetas": out_tar, "tiros": out_tir,
        "puerta": out_pue, "atajadas": out_ata
    }

def get_market_odds():
    # Mantenemos tu lógica de mercado intacta
    return {"1x2": [2.10, 3.40, 3.10], "goles_2_5": [1.85, 1.95], "goles_1_5": [1.25, 3.50], "btts_si": 1.75, "victoria_1t": [2.70, 3.60], "lineas": {"corners": 9.5, "tarjetas": 4.5}}

    # 3. Renderizado simétrico e interactivo en la interfaz de Streamlit
    col1, col2 = st.columns(2)
    
    with col1:
        goles_pp = st.number_input("Goles a Favor (Ponderado)", min_value=0.0, value=float(vals["goles_favor"]), step=0.1, key=f"gf_{team_name}")
        goles_contra = st.number_input("Goles en Contra (Ponderado)", min_value=0.0, value=float(vals["goles_contra"]), step=0.1, key=f"gc_{team_name}")
        xg_reciente = st.number_input("Goles esperados (xG Ponderado)", min_value=0.0, value=float(vals["xg"]), step=0.1, key=f"xg_{team_name}")
        goles_1t = st.number_input("Goles 1ra Mitad (HT)", min_value=0.0, value=float(vals["goles_1t"]), step=0.1, key=f"g1t_{team_name}")
        posesion = st.number_input("Posesión Balón (%)", min_value=0.0, max_value=100.0, value=float(vals["posesion"]), step=0.5, key=f"pos_{team_name}")
        
    with col2:
        corners = st.number_input("Córners Totales", min_value=0.0, value=float(vals["corners"]), step=0.5, key=f"cor_{team_name}")
        tarjetas = st.number_input("Tarjetas Totales", min_value=0.0, value=float(vals["tarjetas"]), step=0.5, key=f"tarj_{team_name}")
        tiros_totales = st.number_input("Tiros totales", min_value=0.0, value=float(vals["tiros"]), step=0.5, key=f"ti_{team_name}")
        tiros_puerta = st.number_input("Tiros a puerta", min_value=0.0, value=float(vals["puerta"]), step=0.5, key=f"tp_{team_name}")
        atajadas = st.number_input("Atajadas del Portero", min_value=0.0, value=float(vals["atajadas"]), step=0.5, key=f"ataj_{team_name}")

    return {
        "goles_pp": goles_pp,
        "goles_contra": goles_contra,
        "xg_reciente": xg_reciente,
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
    Mantiene la recolección manual de las cuotas de las bookies.
    """
    st.subheader(" Cuotas del Mercado (Bookies)")
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
        linea_corners = st.number_input("Línea Córners", min_value=0.5, value=9.5, step=0.5)
        linea_tarjetas = st.number_input("Línea Tarjetas", min_value=0.5, value=4.5, step=0.5)

    return {
        "1x2": [cuota_local, cuota_empate, cuota_visitante],
        "goles_2_5": [cuota_mas_2_5, cuota_menos_2_5],
        "goles_1_5": [cuota_mas_1_5, cuota_menos_1_5],
        "btts_si": btts_si,
        "victoria_1t": [cuota_1t_local, cuota_1t_visita],
        "lineas": {"corners": linea_corners, "tarjetas": linea_tarjetas}
    }
