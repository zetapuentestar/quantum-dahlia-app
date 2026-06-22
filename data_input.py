import streamlit as st
import pandas as pd

def render_db_uploader():
    st.sidebar.markdown("### 📋 Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz (CSV/Excel)", type=["csv", "xlsx"], key="db_uploader")
    if archivo:
        try:
            # sep=None hace que Python detecte automáticamente si es coma o punto y coma
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo, sep=None, engine='python', encoding='utf-8-sig')
            else:
                df = pd.read_excel(archivo)
            
            # Limpiamos espacios y pasamos a minúsculas
            df.columns = [str(c).strip().lower() for c in df.columns]
            st.session_state.db_matriz = df
            st.sidebar.success("✅ Base de datos indexada correctamente.")
            
            # 👇 HERRAMIENTA DE DIAGNÓSTICO: Te mostrará los nombres de las columnas
            with st.sidebar.expander("🔍 Ver columnas detectadas"):
                st.write(df.columns.tolist())
                
        except Exception as e:
            st.sidebar.error(f"Error al cargar el archivo: {e}")

def get_team_stats(team_name):
    # Valores por defecto por si el equipo no está en el Excel
    stats = {
        "goles_favor": 1.5, "goles_contra": 1.0, "xg": 1.3, "goles_1t": 0.5,
        "posesion": 50.0, "corners": 4.0, "tarjetas": 1.5, "tiros": 10.0,
        "puerta": 4.0, "atajadas": 2.0
    }

    # Búsqueda automatizada en el DataFrame
    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        if "equipo" in df.columns:
            # Buscamos la fila que coincida con el nombre del equipo (sin importar mayúsculas/minúsculas)
            match = df[df["equipo"].astype(str).str.upper() == team_name.upper()]
            
            if not match.empty:
                row = match.iloc[0]
                # Mapeamos de forma segura cada columna al diccionario si existe en el Excel
                if "goles_favor" in df.columns: stats["goles_favor"] = float(row["goles_favor"])
                if "goles_contra" in df.columns: stats["goles_contra"] = float(row["goles_contra"])
                if "xg" in df.columns: stats["xg"] = float(row["xg"])
                if "goles_1t" in df.columns: stats["goles_1t"] = float(row["goles_1t"])
                if "posesion" in df.columns: stats["posesion"] = float(row["posesion"])
                if "corners" in df.columns: stats["corners"] = float(row["corners"])
                if "tarjetas" in df.columns: stats["tarjetas"] = float(row["tarjetas"])
                if "tiros" in df.columns: stats["tiros"] = float(row["tiros"])
                if "tiros_puerta" in df.columns: stats["puerta"] = float(row["tiros_puerta"])
                if "atajadas" in df.columns: stats["atajadas"] = float(row["atajadas"])

    # Renderizado en el panel central (se actualiza automáticamente al cambiar el equipo)
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
    c1, c2, c3 = st.columns(3)
    with c1:
        c_1 = st.number_input("Victoria Local (1)", value=2.10, step=0.05)
        c_x = st.number_input("Empate (X)", value=3.40, step=0.05)
        c_2 = st.number_input("Victoria Visita (2)", value=3.10, step=0.05)
        c_1t1 = st.number_input("Victoria Local 1T", value=2.60, step=0.05)
        c_1t2 = st.number_input("Victoria Visita 1T", value=3.50, step=0.05)
    with c2:
        c_o25 = st.number_input("Más 2.5 Goles", value=1.85, step=0.05)
        c_u25 = st.number_input("Menos 2.5 Goles", value=1.95, step=0.05)
        c_o15 = st.number_input("Más 1.5 Goles", value=1.25, step=0.05)
        c_u15 = st.number_input("Menos 1.5 Goles", value=3.80, step=0.05)
    with c3:
        linea_cor = st.number_input("Línea Corners", value=9.5, step=0.5)
        linea_tar = st.number_input("Línea Tarjetas", value=3.5, step=0.5)
        c_btts_si = st.number_input("Ambos Anotan (Sí)", value=1.80, step=0.05)
    
    # Retorno corregido con todas las llaves requeridas por report.py
    return {
        "1x2": [c_1, c_x, c_2],
        "goles_2_5": [c_o25, c_u25],
        "goles_1_5": [c_o15, c_u15],
        "victoria_1t": [c_1t1, c_1t2],
        "lineas": {"corners": linea_cor, "tarjetas": linea_tar},
        "btts_si": c_btts_si
    }
