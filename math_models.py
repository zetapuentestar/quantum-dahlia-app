# math_models.py
import numpy as np
import pandas as pd
from scipy.stats import poisson

def derivar_lambdas_del_mercado(cuota_mas_25, cuota_menos_25):
    """
    [Enfoque Bayesiano - Cálculo del Prior]
    Deriva el total de goles esperado implícito por las cuotas de la bookie.
    """
    if cuota_mas_25 <= 1.0 or cuota_menos_25 <= 1.0:
        return 2.5  
        
    prob_u25_raw = 1 / cuota_menos_25
    prob_o25_raw = 1 / cuota_mas_25
    prob_total = prob_u25_raw + prob_o25_raw
    prob_u25 = prob_u25_raw / prob_total
    
    for l_test in np.arange(0.5, 5.0, 0.05):
        p_calc = poisson.cdf(2, l_test)
        if p_calc <= prob_u25:
            return float(l_test)
            
    return 2.65

def actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado, alpha=0.60):
    """
    [Modelo Bayesiano Cruzado]
    Combina estadísticas ofensivas propias con las defensivas del rival,
    ponderadas con el xG reciente y cruzadas con el mercado.
    """
    c_g25 = cuotas_mercado.get("goles_2_5", [1.85, 1.85])
    lambda_mercado_total = derivar_lambdas_del_mercado(c_g25[0], c_g25[1])
    
    lambda_m_local = lambda_mercado_total * 0.55
    lambda_m_visita = lambda_mercado_total * 0.45
    
    # 1. Extracción de Métricas Ofensivas y Defensivas
    goles_hist_local = float(stats_local.get("goles_pp", 1.0))
    goles_contra_local = float(stats_local.get("goles_contra", 1.0)) # NUEVA MÉTRICA
    xg_rec_local = float(stats_local.get("xg_reciente", goles_hist_local))
    
    goles_hist_visita = float(stats_visita.get("goles_pp", 1.0))
    goles_contra_visita = float(stats_visita.get("goles_contra", 1.0)) # NUEVA MÉTRICA
    xg_rec_visita = float(stats_visita.get("xg_reciente", goles_hist_visita))
    
    # 2. Cruce Táctico: Tu ataque vs Su defensa (Peso 50/50)
    poder_ofensivo_l = (goles_hist_local * 0.5) + (goles_contra_visita * 0.5)
    poder_ofensivo_v = (goles_hist_visita * 0.5) + (goles_contra_local * 0.5)
    
    # 3. Ponderación Reciente: 60% Poder Histórico Cruzado vs 40% xG del último partido
    lambda_u_local = (poder_ofensivo_l * 0.60) + (xg_rec_local * 0.40)
    lambda_u_visita = (poder_ofensivo_v * 0.60) + (xg_rec_visita * 0.40)
    
    # 4. Fusión con el Mercado (Prior)
    lambda_final_local = (alpha * lambda_u_local) + ((1 - alpha) * lambda_m_local)
    lambda_final_visita = (alpha * lambda_u_visita) + ((1 - alpha) * lambda_m_visita)
    
    return round(lambda_final_local, 3), round(lambda_final_visita, 3)

def factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho):
    if rho == 0:
        return 1.0
        
    if x == 0 and y == 0:
        return float(1 - lambda_l * lambda_v * rho)
    elif x == 1 and y == 0:
        return float(1 + lambda_v * rho)
    elif x == 0 and y == 1:
        return float(1 + lambda_l * rho)
    elif x == 1 and y == 1:
        return float(1 - rho)
    else:
        return 1.0

def calcular_matriz_bivariada_dixon_coles(lambda_l, lambda_v, rho=-0.05, max_goles=8):
    matriz_prob = np.zeros((max_goles, max_goles), dtype=float)
    
    for x in range(max_goles):
        for y in range(max_goles):
            prob_p_local = poisson.pmf(x, lambda_l)
            prob_p_visita = poisson.pmf(y, lambda_v)
            indep_prob = prob_p_local * prob_p_visita
            
            tau = factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho)
            matriz_prob[x, y] = max(0.0, indep_prob * tau) 
            
    matriz_prob /= matriz_prob.sum()
    return matriz_prob

def extraer_mejores_marcadores(matriz_prob, top_n=3):
    """Extrae los N marcadores exactos con mayor probabilidad de la matriz."""
    marcadores = []
    max_goles = matriz_prob.shape[0]
    for x in range(max_goles):
        for y in range(max_goles):
            marcadores.append({"marcador": f"{x}-{y}", "prob": matriz_prob[x, y]})
            
    # Ordenar de mayor a menor probabilidad
    marcadores_ordenados = sorted(marcadores, key=lambda d: d['prob'], reverse=True)
    return marcadores_ordenados[:top_n]

def procesar_modelos_matematicos(stats_local, stats_visita, cuotas_mercado):
    # 1. Ejecutar actualización Bayesiana para estabilizar Lambdas
    lambda_l, lambda_v = actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado)
    
    # 2. Construir matriz con Poisson Bivariado y Dixon-Coles
    matriz_prob = calcular_matriz_bivariada_dixon_coles(lambda_l, lambda_v, rho=-0.06)
    
    # 3. Marcadores Exactos (NUEVO)
    top_marcadores = extraer_mejores_marcadores(matriz_prob, top_n=3)
    
    # 4. Extraer probabilidades de los mercados del partido completo
    prob_1 = float(np.tril(matriz_prob, -1).sum())
    prob_x = float(np.trace(matriz_prob))
    prob_2 = float(np.triu(matriz_prob, 1).sum())
    
    prob_u25 = float(sum(matriz_prob[x, y] for x in range(8) for y in range(8) if x + y < 2.5))
    prob_o25 = 1.0 - prob_u25
    
    prob_u15 = float(sum(matriz_prob[x, y] for x in range(8) for y in range(8) if x + y < 1.5))
    prob_o15 = 1.0 - prob_u15
    
    prob_btts_no = float(matriz_prob[0, :].sum() + matriz_prob[:, 0].sum() - matriz_prob[0, 0])
    prob_btts_si = 1.0 - prob_btts_no
    
    return {
        "lambdas_ajustados": {"lambda_l": lambda_l, "lambda_v": lambda_v},
        "marcadores_top": top_marcadores,  # <-- Se devuelve a app.py
        "prob_1x2": {"Local": prob_1, "Empate": prob_x, "Visita": prob_2},
        "goles": {
            "over_1_5": prob_o15, "under_1_5": prob_u15,
            "over_2_5": prob_o25, "under_2_5": prob_u25,
            "btts_si": prob_btts_si, "btts_no": prob_btts_no
        }
    }
