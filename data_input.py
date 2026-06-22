# data_input.py
# data_input.py
import streamlit as st
import pandas as pd

def render_db_uploader():
    """
    Renderiza el cargador de la base de datos en el sidebar.
    Permite subir tanto archivos CSV como archivos Excel (.xlsx).
    """
    st.sidebar.markdown("### 🗄️ Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz Cuantitativa (Excel o CSV)", type=["csv", "xlsx"], key="db_uploader")
    
    if archivo:
        try:
            if archivo.name.endswith('.csv'):
                st.session_state.db_matriz = pd.read_csv(archivo)
            else:
                st.session_state.db_matriz = pd.read_excel(archivo)
            st.sidebar.success("✅ Matriz conectada. Datos automatizados.")
        except Exception as e:
            st.sidebar.error(f"Error al leer el archivo: {e}")
    else:
        st.session_state.db_matriz = None

def _buscar_columna(df, keywords):
    """Función interna para buscar columnas de forma flexible e insensible a mayúsculas/minúsculas."""
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if all(kw in col_lower for kw in keywords):
            return col
    return None

def _extraer_métrica(row, df, keywords_pond, keywords_ult8, keywords_clas, keywords_mundial, default):
    """
    Extrae el valor ponderado. Prioriza la columna precalculada 'Ponderado/Promedio'.
    Si no existe, aplica la fórmula condicional exacta de tu Excel:
    =SI(O(Mundial="";Mundial=0); (Ult8*0.3)+(Clas*0.7); (Ult8*0.3)+(Clas*0.3)+(Mundial*0.4))
    """
    # 1. Intentar leer directo la columna Ponderada o Promedio
    col_pond = _buscar_columna(df, keywords_pond) or _buscar_columna(df, [keywords_pond[0], 'promedio'])
    if col_pond and pd.notna(row[col_pond]):
        try: return float(row[col_pond])
        except ValueError: pass
        
    # 2. Si no existe, aplicar tu fórmula condicional usando los componentes individuales
    col_ult8 = _buscar_columna(df, keywords_ult8)
    col_clas = _buscar_columna(df, keywords_clas)
    col_mund = _buscar_columna(df, keywords_mundial)
    
    if col_ult8 and col_clas:
        try:
            val_ult8 = float(row[col_ult8]) if pd.notna(row[col_ult8]) else default
            val_clas = float(row[col_clas]) if pd.notna(row[col_clas]) else default
            val_mund = float(row[col_mund]) if (col_mund and pd.notna(row[col_mund])) else 0.0
            
            if val_mund == 0.0:
                return (val_ult8 * 0.3) + (val_clas * 0.7)
            else:
                return (val_ult8 * 0.3) + (val_clas * 0.3) + (val_mund * 0.4)
        except ValueError:
            pass
            
    return default

def get_team_stats(team_name):
    """
    Recolecta las estadísticas base de un equipo de forma limpia.
    Elimina duplicaciones e integra Posesión y Atajadas desde el Excel o valores base.
    """
    st.subheader(f"📊 Estadísticas: {team_name}")
    
    # 1. Valores por defecto (se usarán si el país no está en la matriz)
    val_goles_pp = 1.5
    val_goles_contra = 1.0
    val_xg = 1.3
    val_goles_1t = 0.5
    val_posesion = 50.0
    
    val_corners = 4.5
    val_tarjetas = 2.0
    val_tiros = 10.0
    val_puerta = 4.0
    val_atajadas = 3.0
    
    # 2. Extracción automatizada inteligente
    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        
        # Buscar la columna que contiene los nombres de los países
        col_pais = next((c for c in df.columns if str(c).lower().strip() in ['pais', 'país', 'equipo', 'team']), None)
        
        if col_pais:
            match = df[df[col_pais].astype(str).str.contains(team_name, case=False, na=False, regex=False)]
            if not match.empty:
                row = match.iloc[0]
                st.caption("✨ Datos automatizados extraídos de la Matriz Cuantitativa")
                
                # --- GOLES A FAVOR ---
                val_goles_pp = _extraer_métrica(row, df, ['favor', 'ponderado'], ['goles', 'ult8'], ['clas_goles_favor'], ['mundial_ult_goles_favor'], val_goles_pp)
                
                # --- GOLES EN CONTRA ---
                val_goles_contra = _extraer_métrica(row, df, ['contra', 'ponderado'], ['contra', 'ult8'], ['clas_goles_contra'], ['mundial_ult_goles_contra'], val_goles_contra)
                
                # --- GOLES ESPERADOS (xG): Solo Mundial para evitar pérdida de tiempo ---
                col_xg_mundial = _buscar_columna(df, ['xg', 'mundial']) or _buscar_columna(df, ['esperados', 'mundial'])
                if col_xg_mundial and pd.notna(row[col_xg_mundial]):
                    try: val_xg = float(row[col_xg_mundial])
                    except ValueError: pass
                else:
                    col_xg_gen = _buscar_columna(df, ['xg']) or _buscar_columna(df, ['esperados'])
                    if col_xg_gen and pd.notna(row[col_xg_gen]):
                        try: val_xg = float(row[col_xg_gen])
                        except ValueError: pass

                # --- GOLES 1T ---
                val_goles_1t = _extraer_métrica(row, df, ['1t', 'ponderado'], ['goles_1t', 'ult8'], ['goles_1t_ult10'], ['goles_1t_ult_mundial'], val_goles_1t)
                
                # --- POSESIÓN ---
                val_posesion = _extraer_métrica(row, df, ['posesion', 'ponderado'], ['posesion', 'ult8'], ['clas_posesion'], ['mundial_ult_posesion'], val_posesion)
                
                # --- CÓRNERS ---
                val_corners = _extraer_métrica(row, df, ['corners', 'ponderado'], ['corners', 'ult8'], ['clas_corners_prom'], ['mundial_ult_corners'], val_corners)
                
                # --- TARJETAS ---
                val_tarjetas = _extraer_métrica(row, df, ['tarjetas', 'ponderado'], ['tarjetas', 'ult8'], ['clas_tarjetas_prom'], ['mundial_ult_tarjetas'], val_tarjetas)
                
                # --- TIROS TOTALES ---
                val_tiros = _extraer_métrica(row, df, ['tiros', 'ponderado'], ['tiros', 'ult8'], ['clas_tiros'], ['mundial_ult_tiros'], val_tiros)
                
                # --- TIROS A PUERTA ---
                val_puerta = _extraer_métrica(row, df, ['puerta', 'ponderado'], ['puerta', 'ult8'], ['clas_puerta'], ['mundial_ult_puerta'], val_puerta)
                
                # --- ATAJADAS ---
                val_atajadas = _extraer_métrica(row, df, ['atajadas', 'ponderado'], ['atajadas', 'ult8'], ['clas_atajadas'], ['mundial_ult_atajadas'], val_atajadas)

    # 3. Renderizado simétrico en la interfaz (5 inputs por columna)
    col1, col2 = st.columns(2)
    
    with col1:
        goles_pp = st.number_input("Goles a Favor (Ponderado)", min_value=0.0, value=float(val_goles_pp), step=0.1, key=f"gf_{team_name}")
        goles_contra = st.number_input("Goles en Contra (Ponderado)", min_value=0.0, value=float(val_goles_contra), step=0.1, key=f"gc_{team_name}")
        xg_reciente = st.number_input("Goles esperados (xG Mundial)", min_value=0.0, value=float(val_xg), step=0.1, key=f"xg_{team_name}")
        goles_1t = st.number_input("Goles 1ra Mitad (HT)", min_value=0.0, value=float(val_goles_1t), step=0.1, key=f"g1t_{team_name}")
        posesion = st.number_input("Posesión Balón (%)", min_value=0.0, max_value=100.0, value=float(val_posesion), step=0.5, key=f"pos_{team_name}")
        
    with col2:
        corners = st.number_input("Córners Totales", min_value=0.0, value=float(val_corners), step=0.5, key=f"cor_{team_name}")
        tarjetas = st.number_input("Tarjetas Totales", min_value=0.0, value=float(val_tarjetas), step=0.5, key=f"tarj_{team_name}")
        tiros_totales = st.number_input("Tiros totales", min_value=0.0, value=float(val_tiros), step=0.5, key=f"ti_{team_name}")
        tiros_puerta = st.number_input("Tiros a puerta", min_value=0.0, value=float(val_puerta), step=0.5, key=f"tp_{team_name}")
        atajadas = st.number_input("Atajadas del Portero", min_value=0.0, value=float(val_atajadas), step=0.5, key=f"ataj_{team_name}")

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
    Recolecta las cuotas de las casas de apuestas (llenado manual obligatorio).
    """
    st.subheader("🎲 Cuotas del Mercado (Bookies)")
    
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
