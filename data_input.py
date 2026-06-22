import streamlit as st
import pandas as pd
import re

def render_db_uploader():
    st.sidebar.markdown("### 📋 Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz (CSV/Excel)", type=["csv", "xlsx"], key="db_uploader")
    if archivo:
        try:
            # Leemos sin cabecera predefinida para controlar todo manualmente
            if archivo.name.endswith('.csv'):
                st.session_state.db_matriz = pd.read_csv(archivo, header=None)
            else:
                st.session_state.db_matriz = pd.read_excel(archivo, header=None)
            st.sidebar.success("✅ Matriz cargada. Datos en Columna E (Índice 4).")
        except Exception as e:
            st.sidebar.error(f"Error al cargar: {e}")

def get_team_stats(team_name):
    # Valores por defecto
    stats = {"posesion": 50.0, "goles_favor": 1.5, "goles_contra": 1.0, "tiros": 10.0, 
             "puerta": 4.0, "atajadas": 0.0, "corners": 4.0, "tarjetas": 0.0, "xg": 1.3, "goles_1t": 0.5}

    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        
        # Buscar la fila donde aparece el nombre del equipo
        team_row_idx = None
        for idx in range(len(df)):
            if team_name.upper() in str(df.iloc[idx].values).upper():
                team_row_idx = idx
                break
        
        if team_row_idx is not None:
            # Escanear las filas siguientes buscando métricas
            # Se detiene al encontrar otra celda con texto que parece equipo o fin de matriz
            for i in range(team_row_idx + 2, min(team_row_idx + 20, len(df))):
                row = df.iloc[i]
                metric_name = str(row[0]).lower()
                
                # FORZAMOS la lectura de la columna índice 4 (Columna E)
                val_raw = row[4] 
                
                def to_float_safe(val):
                    try:
                        s = str(val).replace(',', '.')
                        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
                        return float(match.group()) if match else None
                    except: return None

                val = to_float_safe(val_raw)
                if val is None: continue
                
                if "posesion" in metric_name: stats["posesion"] = val
                elif "goles a favor" in metric_name: stats["goles_favor"] = val
                elif "goles en contra" in metric_name: stats["goles_contra"] = val
                elif "tiros totales" in metric_name: stats["tiros"] = val
                elif "tiros a puerta" in metric_name: stats["puerta"] = val
                elif "atajadas" in metric_name: stats["atajadas"] = val
                elif "corners" in metric_name: stats["corners"] = val
                elif "tarjetas" in metric_name: stats["tarjetas"] = val
                elif "esperados" in metric_name: stats["xg"] = val
                elif "goles 1t" in metric_name: stats["goles_1t"] = val

    st.subheader(f"📊 Estadísticas: {team_name}")
    col1, col2 = st.columns(2)
    vals = {}
    with col1:
        vals["gf"] = st.number_input("Goles Favor", value=float(stats["goles_favor"]), step=0.1, key=f"gf_{team_name}")
        vals["gc"] = st.number_input("Goles Contra", value=float(stats["goles_contra"]), step=0.1, key=f"gc_{team_name}")
        vals["xg"] = st.number_input("xG", value=float(stats["xg"]), step=0.1, key=f"xg_{team_name}")
        vals["g1t"] = st.number_input("Goles 1T", value=float(stats["goles_1t"]), step=0.1, key=f"g1t_{team_name}")
        vals["pos"] = st.number_input("Posesión %", value=float(stats["posesion"]), step=1.0, key=f"pos_{team_name}")
    with col2:
        vals["cor"] = st.number_input("Córners", value=float(stats["corners"]), step=0.5, key=f"cor_{team_name}")
        vals["tar"] = st.number_input("Tarjetas", value=float(stats["tarjetas"]), step=0.5, key=f"tar_{team_name}")
        vals["ti"] = st.number_input("Tiros Totales", value=float(stats["tiros"]), step=0.5, key=f"ti_{team_name}")
        vals["tp"] = st.number_input("Tiros a Puerta", value=float(stats["puerta"]), step=0.5, key=f"tp_{team_name}")
        vals["at"] = st.number_input("Atajadas", value=float(stats["atajadas"]), step=0.5, key=f"at_{team_name}")
    return vals

def get_market_odds():
    st.subheader("💰 Cuotas del Mercado")
    col1, col2, col3 = st.columns(3)
    with col1:
        c1 = st.number_input("Victoria Local (1)", value=2.10, step=0.05)
        c2 = st.number_input("Empate (X)", value=3.40, step=0.05)
        c3 = st.number_input("Victoria Visita (2)", value=3.10, step=0.05)
    return {"1x2": [c1, c2, c3]}
