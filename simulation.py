# simulation.py
import numpy as np
import pandas as pd

def ejecutar_montecarlo(stats_local, stats_visita, n_simulaciones=100000):
    """
    Ejecuta una simulación de Montecarlo basada en las esperanzas matemáticas (lambdas)
    de cada equipo para predecir goles, goles en el 1T, córners y tarjetas.
    """
    # 1. Extraer los Lambdas (valores esperados con decimales)
    # Goles Partido Completo
    lambda_goles_l = float(stats_local["goles_pp"])
    lambda_goles_v = float(stats_visita["goles_pp"])
    
    # Goles Primera Mitad (HT)
    lambda_goles_1t_l = float(stats_local["goles_1t"])
    lambda_goles_1t_v = float(stats_visita["goles_1t"])
    
    # Córners
    lambda_corners_l = float(stats_local["corners"])
    lambda_corners_v = float(stats_visita["corners"])
    
    # Tarjetas
    lambda_tarjetas_l = float(stats_local["tarjetas"])
    lambda_tarjetas_v = float(stats_visita["tarjetas"])

    # 2. Generar muestreos aleatorios masivos (Vectores de Poisson)
    # Goles en el partido completo
    sim_goles_l = np.random.poisson(lambda_goles_l, n_simulaciones)
    sim_goles_v = np.random.poisson(lambda_goles_v, n_simulaciones)
    
    # Goles en el Primer Tiempo
    sim_goles_1t_l = np.random.poisson(lambda_goles_1t_l, n_simulaciones)
    sim_goles_1t_v = np.random.poisson(lambda_goles_1t_v, n_simulaciones)
    
    # Córners Totales (Suma de ambos equipos)
    sim_corners_l = np.random.poisson(lambda_corners_l, n_simulaciones)
    sim_corners_v = np.random.poisson(lambda_corners_v, n_simulaciones)
    sim_corners_totales = sim_corners_l + sim_corners_v
    
    # Tarjetas Totales (Suma de ambos equipos)
    sim_tarjetas_l = np.random.poisson(lambda_tarjetas_l, n_simulaciones)
    sim_tarjetas_v = np.random.poisson(lambda_tarjetas_v, n_simulaciones)
    sim_tarjetas_totales = sim_tarjetas_l + sim_tarjetas_v

    # 3. Procesamiento de Probabilidades (Resultados con floats de alta precisión)
    
    # Mercado 1X2 Partido Completo
    gana_l = np.sum(sim_goles_l > sim_goles_v) / n_simulaciones
    empate = np.sum(sim_goles_l == sim_goles_v) / n_simulaciones
    gana_v = np.sum(sim_goles_l < sim_goles_v) / n_simulaciones
    
    # Mercado 1X2 Primera Mitad (HT)
    gana_1t_l = np.sum(sim_goles_1t_l > sim_goles_1t_v) / n_simulaciones
    empate_1t = np.sum(sim_goles_1t_l == sim_goles_1t_v) / n_simulaciones
    gana_1t_v = np.sum(sim_goles_1t_l < sim_goles_1t_v) / n_simulaciones
    
    # Mercado Goles (Over / Under)
    goles_totales_sim = sim_goles_l + sim_goles_v
    over_1_5 = np.sum(goles_totales_sim > 1.5) / n_simulaciones
    under_1_5 = 1.0 - over_1_5
    over_2_5 = np.sum(goles_totales_sim > 2.5) / n_simulaciones
    under_2_5 = 1.0 - over_2_5
    
    # Ambos Anotan (BTTS)
    btts_si = np.sum((sim_goles_l > 0) & (sim_goles_v > 0)) / n_simulaciones
    btts_no = 1.0 - btts_si

    # Promedios proyectados finales (Métricas clave para contrastar líneas asiáticas)
    promedio_corners = float(np.mean(sim_corners_totales))
    promedio_tarjetas = float(np.mean(sim_tarjetas_totales))
    promedio_goles_totales = float(np.mean(goles_totales_sim))

    # 4. Empaquetado de resultados en un diccionario limpio
    resultados = {
        "prob_1x2": {"Local": gana_l, "Empate": empate, "Visita": gana_v},
        "prob_1x2_1t": {"Local": gana_1t_l, "Empate": empate_1t, "Visita": gana_1t_v},
        "goles": {
            "over_1_5": over_1_5, "under_1_5": under_1_5,
            "over_2_5": over_2_5, "under_2_5": under_2_5,
            "btts_si": btts_si, "btts_no": btts_no
        },
        "proyecciones_metricas": {
            "goles_promedio": promedio_goles_totales,
            "corners_promedio": promedio_corners,
            "tarjetas_promedio": promedio_tarjetas
        },
        "vectores_raw": {
            "corners": sim_corners_totales,
            "tarjetas": sim_tarjetas_totales
        }
    }
    
    return resultados

def evaluar_lineas_especificas(vector_simulado, linea_mercado):
    """
    Compara un vector de eventos simulados contra una línea específica de la casa de apuestas.
    Útil para calcular Over/Under exactos personalizados de Córners o Tarjetas.
    """
    over_prob = np.sum(vector_simulado > linea_mercado) / len(vector_simulado)
    under_prob = 1.0 - over_prob
    return {"Over": over_prob, "Under": under_prob}
