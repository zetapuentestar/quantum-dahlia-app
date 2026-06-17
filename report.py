# report.py
import pandas as pd
import numpy as np
from simulation import evaluar_lineas_especificas

def calcular_ev(probabilidad_modelo, cuota_bookie):
    """
    Calcula el Valor Esperado (EV%).
    Si la cuota de la bookie es 0 o vacía, retorna 0.0
    """
    if cuota_bookie <= 1.0:
        return 0.0
    return float((probabilidad_modelo * cuota_bookie - 1) * 100)

def calcular_cuota_justa(probabilidad_modelo):
    """
    Calcula la cuota matemática pura basada en la probabilidad del modelo.
    """
    if probabilidad_modelo <= 0:
        return float('inf')
    return float(1 / probabilidad_modelo)

def generar_reporte_valores(resultados_montecarlo, cuotas_mercado):
    """
    Cruza las probabilidades simuladas con las cuotas para generar el DataFrame principal.
    Evita errores de tipos y asegura consistencia con decimales (floats).
    """
    # 1. Extraer probabilidades de la simulación
    p_1x2 = resultados_montecarlo["prob_1x2"]
    p_1x2_1t = resultados_montecarlo["prob_1x2_1t"]
    p_goles = resultados_montecarlo["goles"]
    
    # 2. Extraer cuotas ingresadas por el usuario
    c_1x2 = cuotas_mercado["1x2"]          # [Local, Empate, Visita]
    c_g25 = cuotas_mercado["goles_2_5"]     # [Over, Under]
    c_g15 = cuotas_mercado["goles_1_5"]     # [Over, Under]
    c_btts = cuotas_mercado["btts_si"]      # Solo Sí
    c_1t = cuotas_mercado["victoria_1t"]    # [Local 1T, Visita 1T]

    # 3. Definir la lista de mercados a evaluar
    datos_reporte = [
        # Mercado 1X2 Partido Completo
        {"Mercado": "1X2: Victoria Local", "Prob_Modelo": p_1x2["Local"], "Cuota_Bookie": c_1x2[0]},
        {"Mercado": "1X2: Empate", "Prob_Modelo": p_1x2["Empate"], "Cuota_Bookie": c_1x2[1]},
        {"Mercado": "1X2: Victoria Visitante", "Prob_Modelo": p_1x2["Visita"], "Cuota_Bookie": c_1x2[2]},
        
        # Mercado 1X2 Primera Mitad (NUEVO)
        {"Mercado": "1T 1X2: Victoria Local 1T", "Prob_Modelo": p_1x2_1t["Local"], "Cuota_Bookie": c_1t[0]},
        {"Mercado": "1T 1X2: Victoria Visitante 1T", "Prob_Modelo": p_1x2_1t["Visita"], "Cuota_Bookie": c_1t[1]},
        
        # Mercado Goles Totales (2.5)
        {"Mercado": "Goles: Más de 2.5", "Prob_Modelo": p_goles["over_2_5"], "Cuota_Bookie": c_g25[0]},
        {"Mercado": "Goles: Menos de 2.5", "Prob_Modelo": p_goles["under_2_5"], "Cuota_Bookie": c_g25[1]},
        
        # Mercado Goles Totales (1.5 NUEVO)
        {"Mercado": "Goles: Más de 1.5", "Prob_Modelo": p_goles["over_1_5"], "Cuota_Bookie": c_g15[0]},
        {"Mercado": "Goles: Menos de 1.5", "Prob_Modelo": p_goles["under_1_5"], "Cuota_Bookie": c_g15[1]},
        
        # Ambos Anotan
        {"Mercado": "Ambos Anotan: SÍ", "Prob_Modelo": p_goles["btts_si"], "Cuota_Bookie": c_btts}
    ]
    
    # 4. Construir el DataFrame y calcular las métricas derivadas con floats
    df = pd.DataFrame(datos_reporte)
    
    df["Prob_Modelo (%)"] = (df["Prob_Modelo"] * 100).round(2)
    df["Cuota_Justa"] = df["Prob_Modelo"].apply(calcular_cuota_justa).round(2)
    df["EV (%)"] = df.apply(lambda row: calcular_ev(row["Prob_Modelo"], row["Cuota_Bookie"]), axis=1).round(2)
    
    # Ordenar columnas para la visualización final
    columnas_finales = ["Mercado", "Prob_Modelo (%)", "Cuota_Justa", "Cuota_Bookie", "EV (%)"]
    return df[columnas_finales]

def generar_reporte_lineas_asiaticas(resultados_montecarlo, cuotas_mercado):
    """
    Genera un reporte especializado para las líneas de Córners y Tarjetas.
    Calcula la probabilidad exacta y la cuota justa para las líneas O/U configuradas de forma manual.
    """
    lineas = cuotas_mercado["lineas"]
    vectores = resultados_montecarlo["vectores_raw"]
    
    # Evaluar línea de córners simulada contra la línea manual
    res_corners = evaluar_lineas_especificas(vectores["corners"], lineas["corners"])
    # Evaluar línea de tarjetas simulada contra la línea manual
    res_tarjetas = evaluar_lineas_especificas(vectores["tarjetas"], lineas["tarjetas"])
    
    datos_lineas = [
        {
            "Métrica/Mercado": f"Córners: Más de {lineas['corners']}", 
            "Prob_Modelo (%)": round(res_corners["Over"] * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(res_corners["Over"]), 2),
            "Promedio_Proyectado": round(resultados_montecarlo["proyecciones_metricas"]["corners_promedio"], 2)
        },
        {
            "Métrica/Mercado": f"Córners: Menos de {lineas['corners']}", 
            "Prob_Modelo (%)": round(res_corners["Under"] * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(res_corners["Under"]), 2),
            "Promedio_Proyectado": round(resultados_montecarlo["proyecciones_metricas"]["corners_promedio"], 2)
        },
        {
            "Métrica/Mercado": f"Tarjetas: Más de {lineas['tarjetas']}", 
            "Prob_Modelo (%)": round(res_tarjetas["Over"] * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(res_tarjetas["Over"]), 2),
            "Promedio_Proyectado": round(resultados_montecarlo["proyecciones_metricas"]["tarjetas_promedio"], 2)
        },
        {
            "Métrica/Mercado": f"Tarjetas: Menos de {lineas['tarjetas']}", 
            "Prob_Modelo (%)": round(res_tarjetas["Under"] * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(res_tarjetas["Under"]), 2),
            "Promedio_Proyectado": round(resultados_montecarlo["proyecciones_metricas"]["tarjetas_promedio"], 2)
        }
    ]
    
    return pd.DataFrame(datos_lineas)
