# report.py
import pandas as pd
import numpy as np
from scipy.stats import poisson

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

def generar_reporte_valores(resultados_analiticos, cuotas_mercado):
    """
    Cruza las probabilidades simuladas con las cuotas para generar el DataFrame principal.
    Asegura consistencia convirtiendo porcentajes a probabilidades decimales puras.
    """
    p_1x2 = resultados_analiticos["prob_1x2"]
    p_1x2_1t = resultados_analiticos["prob_1x2_1t"]
    p_goles = resultados_analiticos["goles"]
    
    c_1x2 = cuotas_mercado.get("1x2", [0.0, 0.0, 0.0])         
    c_g25 = cuotas_mercado.get("goles_2_5", [0.0, 0.0])      
    c_g15 = cuotas_mercado.get("goles_1_5", [0.0, 0.0])      
    c_btts = cuotas_mercado.get("btts_si", 0.0)       
    c_1t = cuotas_mercado.get("victoria_1t", [0.0, 0.0])     

    datos_reporte = [
        {"Mercado": "1X2: Victoria Local", "Prob_Modelo": p_1x2["Local"] / 100.0, "Cuota_Bookie": c_1x2[0]},
        {"Mercado": "1X2: Empate", "Prob_Modelo": p_1x2["Empate"] / 100.0, "Cuota_Bookie": c_1x2[1]},
        {"Mercado": "1X2: Victoria Visitante", "Prob_Modelo": p_1x2["Visita"] / 100.0, "Cuota_Bookie": c_1x2[2]},
        
        {"Mercado": "1T 1X2: Victoria Local 1T", "Prob_Modelo": p_1x2_1t["Local"] / 100.0, "Cuota_Bookie": c_1t[0]},
        {"Mercado": "1T 1X2: Victoria Visitante 1T", "Prob_Modelo": p_1x2_1t["Visita"] / 100.0, "Cuota_Bookie": c_1t[1]},
        
        {"Mercado": "Goles: Más de 2.5", "Prob_Modelo": p_goles["over_2_5"] / 100.0, "Cuota_Bookie": c_g25[0]},
        {"Mercado": "Goles: Menos de 2.5", "Prob_Modelo": p_goles["under_2_5"] / 100.0, "Cuota_Bookie": c_g25[1]},
        
        {"Mercado": "Goles: Más de 1.5", "Prob_Modelo": p_goles["over_1_5"] / 100.0, "Cuota_Bookie": c_g15[0]},
        {"Mercado": "Goles: Menos de 1.5", "Prob_Modelo": p_goles["under_1_5"] / 100.0, "Cuota_Bookie": c_g15[1]},
        
        {"Mercado": "Ambos Anotan: SÍ", "Prob_Modelo": p_goles["btts_si"] / 100.0, "Cuota_Bookie": c_btts}
    ]
    
    df = pd.DataFrame(datos_reporte)
    
    df["Prob_Modelo (%)"] = (df["Prob_Modelo"] * 100).round(2)
    df["Cuota_Justa"] = df["Prob_Modelo"].apply(calcular_cuota_justa).round(2)
    df["EV (%)"] = df.apply(lambda row: calcular_ev(row["Prob_Modelo"], row["Cuota_Bookie"]), axis=1).round(2)
    
    columnas_finales = ["Mercado", "Prob_Modelo (%)", "Cuota_Justa", "Cuota_Bookie", "EV (%)"]
    return df[columnas_finales]

# ¡NUEVO!: Se agregaron stats_local y stats_visita como parámetros obligatorios
def generar_reporte_lineas_asiaticas(resultados_analiticos, cuotas_mercado, stats_local, stats_visita):
    """
    Genera un reporte especializado para Córners y Tarjetas utilizando cálculo de Poisson puro.
    Se elimina la simulación de Montecarlo y el uso de vectores (arrays).
    """
    lineas = cuotas_mercado.get("lineas", {"corners": 8.5, "tarjetas": 3.5})
    
    # 1. Reconstruir los promedios totales (Lambdas) desde las estadísticas base
    lambda_cor_total = float(stats_local.get("corners", stats_local.get("cor", 4.5))) + \
                       float(stats_visita.get("corners", stats_visita.get("cor", 4.5)))
                       
    lambda_tar_total = float(stats_local.get("tarjetas", stats_local.get("tar", 2.0))) + \
                       float(stats_visita.get("tarjetas", stats_visita.get("tar", 2.0)))

    # 2. Cálculo de probabilidad exacta (CDF y SF)
    linea_cor = float(lineas["corners"])
    k_cor = int(np.floor(linea_cor)) # Convierte la línea .5 al entero inferior (Ej: 8.5 -> 8)
    prob_cor_over = poisson.sf(k_cor, lambda_cor_total)
    prob_cor_under = poisson.cdf(k_cor, lambda_cor_total)

    linea_tar = float(lineas["tarjetas"])
    k_tar = int(np.floor(linea_tar)) # Convierte la línea .5 al entero inferior (Ej: 3.5 -> 3)
    prob_tar_over = poisson.sf(k_tar, lambda_tar_total)
    prob_tar_under = poisson.cdf(k_tar, lambda_tar_total)

    # 3. Ensamblaje del reporte
    datos_lineas = [
        {
            "Métrica/Mercado": f"Córners: Más de {linea_cor}", 
            "Prob_Modelo (%)": round(prob_cor_over * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(prob_cor_over), 2),
            "Promedio_Proyectado": round(lambda_cor_total, 2)
        },
        {
            "Métrica/Mercado": f"Córners: Menos de {linea_cor}", 
            "Prob_Modelo (%)": round(prob_cor_under * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(prob_cor_under), 2),
            "Promedio_Proyectado": round(lambda_cor_total, 2)
        },
        {
            "Métrica/Mercado": f"Tarjetas: Más de {linea_tar}", 
            "Prob_Modelo (%)": round(prob_tar_over * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(prob_tar_over), 2),
            "Promedio_Proyectado": round(lambda_tar_total, 2)
        },
        {
            "Métrica/Mercado": f"Tarjetas: Menos de {linea_tar}", 
            "Prob_Modelo (%)": round(prob_tar_under * 100, 2),
            "Cuota_Justa": round(calcular_cuota_justa(prob_tar_under), 2),
            "Promedio_Proyectado": round(lambda_tar_total, 2)
        }
    ]
    
    return pd.DataFrame(datos_lineas)
