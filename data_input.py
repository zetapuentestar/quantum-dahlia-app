# data_input.py
import streamlit as st
import pandas as pd
import numpy as np

def render_db_uploader():
    """
    Renderiza el cargador de la base de datos en el sidebar.
    Soporta tus archivos de Excel (.xlsx) con tablas verticales por país.
    """
    st.sidebar.markdown("###  Base de Datos (Matriz)")
    archivo = st.sidebar.file_uploader("Sube tu Matriz Cuantitativa (Excel)", type=["xlsx", "xls"], key="db_uploader")
    
    if archivo:
        try:
            # Leemos el Excel sin asumir cabeceras fijas para poder procesar los bloques
            st.session_state.db_matriz = pd.read_excel(archivo, header=None)
            st.sidebar.success("✅ Matriz de bloques conectada con éxito.")
        except Exception as e:
            st.sidebar.error(f"Error al leer el Excel: {e}")
    else:
        st.session_state.db_matriz = None

def _extraer_métrica_bloque(df, fila_inicio, nombre_metrica, default_val):
    """
    Busca la métrica bajando desde la posición del país en la columna A,
    y extrae el valor calculado en la columna E (Ponderado).
    """
    # Buscamos en las siguientes 15 filas a partir de donde se encontró el país
    for i in range(fila_inicio + 1, min(fila_inicio + 16, len(df))):
        celda_A = str(df.iloc[i, 0]).strip().lower()
        if nombre_metrica in celda_A:
            valor_ponderado = df.iloc[i, 4] # Columna E es el índice 4 (A=0, B=1, C=2, D=3, E=4)
            
            # Validar que no sea un valor nulo o un error de Excel
            if pd.notna(valor_ponderado) and not isinstance(valor_ponderado, str):
                return float(valor_ponderado)
            try:
                return float(valor_ponderado)
            except (ValueError, TypeError):
                return default_val
    return default_val

def get_team_stats(team_name):
    # ... (código previo)
    
    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        idx_pais = None
        
        # LIMPIEZA: Convertimos el nombre buscado a un formato estándar
        target = str(team_name).strip().upper()
        
        # BUSQUEDA FLEXIBLE
        for idx, row in df.iterrows():
            # Buscamos en toda la fila, limpiando cada celda
            fila_texto = " ".join([str(c).strip().upper() for c in row if pd.notna(c)])
            if target == fila_texto: # Coincidencia exacta de fila
                idx_pais = idx
                break
        
        # Si no lo encuentra por fila completa, buscamos celda por celda
        if idx_pais is None:
            for idx, row in df.iterrows():
                if target in [str(c).strip().upper() for c in row if pd.notna(c)]:
                    idx_pais = idx
                    break
        
        if idx_pais is not None:
            # ... (resto del código de extracción)
    
    # Buscar e importar datos desde la estructura del Excel
    if "db_matriz" in st.session_state and st.session_state.db_matriz is not None:
        df = st.session_state.db_matriz
        idx_pais = None
        
        # 1. Buscar en qué fila se encuentra el nombre del país (Columnas A o B de tu cabecera)
        for idx, row in df.iterrows():
            val_A = str(row[0]).strip().upper() if pd.notna(row[0]) else ""
            val_B = str(row[1]).strip().upper() if pd.notna(row[1]) else ""
            
            if team_name.upper() in val_A or team_name.upper() in val_B:
                idx_pais = idx
                break
                
        if idx_pais is not None:
            st.caption(f" Datos automatizados extraídos de la columna 'Ponderado' para **{team_name}**")
            
            # 2. Mapeo exacto buscando la fila por palabra clave en la Columna A
            vals["posesion"] = _extraer_métrica_bloque(df, idx_pais, "posesion", vals["posesion"])
            vals["goles_favor"] = _extraer_métrica_bloque(df, idx_pais, "goles por partido", vals["goles_favor"])
            vals["goles_contra"] = _extraer_métrica_bloque(df, idx_pais, "encajados", vals["goles_contra"])
            vals["tiros"] = _extraer_métrica_bloque(df, idx_pais, "tiros totales", vals["tiros"])
            vals["puerta"] = _extraer_métrica_bloque(df, idx_pais, "tiros a puerta", vals["puerta"])
            vals["atajadas"] = _extraer_métrica_bloque(df, idx_pais, "atajadas", vals["atajadas"])
            vals["corners"] = _extraer_métrica_bloque(df, idx_pais, "corners", vals["corners"])
            vals["tarjetas"] = _extraer_métrica_bloque(df, idx_pais, "tarjetas", vals["tarjetas"])
            vals["xg"] = _extraer_métrica_bloque(df, idx_pais, "esperados", vals["xg"])
            vals["goles_1t"] = _extraer_métrica_bloque(df, idx_pais, "1 mitad", vals["goles_1t"])
        else:
            st.warning(f"⚠️ No se encontró el bloque para '{team_name}' en el Excel. Usando valores base.")

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
