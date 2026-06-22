import streamlit as st
import pandas as pd

def render_db_uploader():
    st.sidebar.markdown("### 📋 Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz (CSV/Excel)", type=["csv", "xlsx"], key="db_uploader")
    if archivo:
        try:
            if archivo.name.endswith('.csv'):
                st.session_state.db_matriz = pd.read_csv(archivo, header=None)
            else:
                st.session_state.db_matriz = pd.read_excel(archivo, header=None)
            st.sidebar.success("✅ Estructura plana cargada.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

def get_team_stats(team_name):
    stats = {"posesion": 50.0, "goles_favor": 1.5, "goles_contra": 1.0, "tiros": 10.0, 
             "puerta": 4.0, "atajadas": 0.0, "corners": 4.0, "tarjetas": 0.0, "xg": 1.3, "goles_1t": 0.5}

    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        found_idx = None
        for idx in range(len(df)):
            if any(team_name.upper() in str(cell).upper() for cell in df.iloc[idx]):
                found_idx = idx
                break
        
        if found_idx is not None:
            for i in range(found_idx + 1, found_idx + 15):
                if i >= len(df): break
                row = df.iloc[i]
                row_str = " ".join([str(c) for c in row if pd.notna(c)]).lower()
                val = row[4] 
                if pd.isna(val): continue
                
                try:
                    if "posesion" in row_str: stats["posesion"] = float(val)
                    elif "goles a favor" in row_str: stats["goles_favor"] = float(val)
                    elif "goles en contra" in row_str: stats["goles_contra"] = float(val)
                    elif "tiros totales" in row_str: stats["tiros"] = float(val)
                    elif "tiros a puerta" in row_str: stats["puerta"] = float(val)
                    elif "atajadas" in row_str: stats["atajadas"] = float(val)
                    elif "corners" in row_str: stats["corners"] = float(val)
                    elif "tarjetas" in row_str: stats["tarjetas"] = float(val)
                    elif "esperados" in row_str: stats["xg"] = float(val)
                    elif "goles 1t" in row_str: stats["goles_1t"] = float(val)
                except: continue

    st.subheader(f"📊 Estadísticas: {team_name}")
    col1, col2 = st.columns(2)
    
    vals = {}
    with col1:
        vals["gf"] = st.number_input("Goles Favor (Pond)", value=float(stats["goles_favor"]), step=0.1, key=f"gf_{team_name}")
        vals["gc"] = st.number_input("Goles Contra (Pond)", value=float(stats["goles_contra"]), step=0.1, key=f"gc_{team_name}")
        vals["xg"] = st.number_input("xG (Pond)", value=float(stats["xg"]), step=0.1, key=f"xg_{team_name}")
        vals["g1t"] = st.number_input("Goles 1T", value=float(stats["goles_1t"]), step=0.1, key=f"g1t_{team_name}")
        vals["pos"] = st.number_input("Posesión (%)", value=float(stats["posesion"]), step=1.0, key=f"pos_{team_name}")
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
    with col2:
        c4 = st.number_input("Más de 2.5", value=1.85, step=0.05)
        c5 = st.number_input("Menos de 2.5", value=1.95, step=0.05)
        c6 = st.number_input("Más de 1.5", value=1.25, step=0.05)
        c7 = st.number_input("Menos de 1.5", value=3.50, step=0.05)
    with col3:
        c8 = st.number_input("Ambos Anotan", value=1.75, step=0.05)
        c9 = st.number_input("Línea Córners", value=9.5, step=0.5)
        c10 = st.number_input("Línea Tarjetas", value=4.5, step=0.5)

    return {"1x2": [c1, c2, c3], "goles": [c4, c5, c6, c7], "btts": c8, "corners": c9, "tarjetas": c10}
