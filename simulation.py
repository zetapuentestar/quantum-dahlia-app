import numpy as np
import pandas as pd
from scipy.stats import poisson

def ejecutar_montecarlo(stats_local, stats_visita, n_simulaciones=100000):
    """
    [REFACTORIZADO AL MODELO ÚNICO ANALÍTICO]
    Se ha eliminado la naturaleza frecuentista (Montecarlo) para los goles.
    Ahora utiliza Matrices de Probabilidad de Poisson exactas, alineándose con
    el rigor matemático del motor Bayesiano/Termodinámico.
    (Mantenemos el nombre de la función para retrocompatibilidad con app.py)
    """
    # 1. Extraer Esperanzas Matemáticas (Lambdas)
    goles_hist_l = float(stats_local.get("goles_favor", 1.0))
    xg_rec_l = float(stats_local.get("xg", goles_hist_l))
    lambda_l = (goles_hist_l * 0.60) + (xg_rec_l * 0.40)
    
    goles_hist_v = float(stats_local.get("goles_contra", 1.0)) # Corregido al cruce defensivo
    xg_rec_v = float(stats_visita.get("xg", goles_hist_v))
    lambda_v = (goles_hist_v * 0.60) + (xg_rec_v * 0.40)
    
    # Goles Primera Mitad (HT) - Distribución temporal analítica
    lambda_1t_l = float(stats_local.get("goles_1t", lambda_l * 0.45))
    lambda_1t_v = float(stats_visita.get("goles_1t", lambda_v * 0.45))
    
    # Mercados Secundarios (Córners y Tarjetas)
    lambda_cor_l = float(stats_local.get("corners", 4.5))
    lambda_cor_v = float(stats_visita.get("corners", 4.5))
    lambda_cor_total = lambda_cor_l + lambda_cor_v
    
    lambda_tar_l = float(stats_local.get("tarjetas", 2.0))
    lambda_tar_v = float(stats_visita.get("tarjetas", 2.0))
    lambda_tar_total = lambda_tar_l + lambda_tar_v

    # 2. Reemplazo Analítico: Matriz Bivariada Base (Sin azar)
    matriz_ft = np.zeros((8, 8), dtype=float)
    matriz_ht = np.zeros((8, 8), dtype=float)
    
    for x in range(8):
        for y in range(8):
            matriz_ft[x, y] = poisson.pmf(x, lambda_l) * poisson.pmf(y, lambda_v)
            matriz_ht[x, y] = poisson.pmf(x, lambda_1t_l) * poisson.pmf(y, lambda_1t_v)

    # 3. Extracción de Probabilidades Exactas (Evita varianza frecuentista)
    gana_l = float(np.tril(matriz_ft, -1).sum())
    empate = float(np.trace(matriz_ft))
    gana_v = float(np.triu(matriz_ft, 1).sum())
    
    gana_1t_l = float(np.tril(matriz_ht, -1).sum())
    empate_1t = float(np.trace(matriz_ht))
    gana_1t_v = float(np.triu(matriz_ht, 1).sum())
    
    prob_u25 = float(sum(matriz_ft[x, y] for x in range(8) for y in range(8) if x + y < 2.5))
    under_2_5 = prob_u25
    over_2_5 = 1.0 - under_2_5
    
    prob_u15 = float(sum(matriz_ft[x, y] for x in range(8) for y in range(8) if x + y < 1.5))
    under_1_5 = prob_u15
    over_1_5 = 1.0 - under_1_5
    
    btts_no = float(matriz_ft[0, :].sum() + matriz_ft[:, 0].sum() - matriz_ft[0, 0])
    btts_si = 1.0 - btts_no

    # 4. Generación de Vectores Secundarios 
    # (Exclusivo para calcular Líneas Asiáticas personalizadas sin romper report.py)
    sim_corners_totales = np.random.poisson(lambda_cor_total, n_simulaciones)
    sim_tarjetas_totales = np.random.poisson(lambda_tar_total, n_simulaciones)

    # 5. Empaquetado final compatible con la UI
    resultados = {
        "prob_1x2": {"Local": gana_l, "Empate": empate, "Visita": gana_v},
        "prob_1x2_1t": {"Local": gana_1t_l, "Empate": empate_1t, "Visita": gana_1t_v},
        "goles": {
            "over_1_5": over_1_5, "under_1_5": under_1_5,
            "over_2_5": over_2_5, "under_2_5": under_2_5,
            "btts_si": btts_si, "btts_no": btts_no
        },
        "proyecciones_metricas": {
            "goles_promedio": lambda_l + lambda_v,
            "corners_promedio": lambda_cor_total,
            "tarjetas_promedio": lambda_tar_total
        },
        "vectores_raw": {
            "corners": sim_corners_totales,
            "tarjetas": sim_tarjetas_totales
        }
    }
    
    return resultados

def evaluar_lineas_especificas(vector_simulado, linea_mercado):
    """
    Compara un vector de eventos simulados (Córners/Tarjetas) contra una línea asiática.
    Mantiene la compatibilidad con el módulo de reportes.
    """
    over_prob = np.sum(vector_simulado > linea_mercado) / len(vector_simulado)
    under_prob = 1.0 - over_prob
    return {"Over": over_prob, "Under": under_prob}
