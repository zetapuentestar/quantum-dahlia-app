import numpy as np
from scipy.stats import poisson

def derivar_lambdas_del_mercado(cuota_mas_25, cuota_menos_25):
    """Deriva el total de goles esperado implícito por las cuotas de la bookie."""
    if cuota_mas_25 <= 1.0 or cuota_menos_25 <= 1.0: return 2.5  
        
    prob_u25 = (1 / cuota_menos_25) / ((1 / cuota_menos_25) + (1 / cuota_mas_25))
    
    for l_test in np.arange(0.5, 5.0, 0.05):
        if poisson.cdf(2, l_test) <= prob_u25:
            return float(l_test)
    return 2.65

def calcular_lambdas_estadisticos(stats_local, stats_visita):
    """
    Toma EXCLUSIVAMENTE los promedios ya calculados en tu Excel.
    Combina los Goles Reales con los Goles Esperados (xG) para un poder de ataque neto.
    """
    # Extracción segura de datos del Excel
    gf_l = float(stats_local.get("goles_favor", stats_local.get("gf", 1.0)))
    gc_l = float(stats_local.get("goles_contra", stats_local.get("gc", 1.0)))
    xg_l = float(stats_local.get("xg", gf_l))
    
    gf_v = float(stats_visita.get("goles_favor", stats_visita.get("gf", 1.0)))
    gc_v = float(stats_visita.get("goles_contra", stats_visita.get("gc", 1.0)))
    xg_v = float(stats_visita.get("xg", gf_v))

    # Poder ofensivo ponderado (60% Goles Reales, 40% xG del Excel)
    ataque_l = (gf_l * 0.6) + (xg_l * 0.4)
    ataque_v = (gf_v * 0.6) + (xg_v * 0.4)

    # El Lambda (expectativa de gol) cruza el ataque de uno con la defensa del otro
    lambda_u_local = (ataque_l + gc_v) / 2.0
    lambda_u_visita = (ataque_v + gc_l) / 2.0

    return lambda_u_local, lambda_u_visita

def actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado, alpha=0.65):
    """Fusiona nuestro análisis de Excel con las expectativas del mercado."""
    c_g25 = cuotas_mercado.get("goles_2_5", [1.85, 1.85])
    lambda_mercado_total = derivar_lambdas_del_mercado(c_g25[0], c_g25[1])
    
    lambda_m_local = lambda_mercado_total * 0.55 # Ligero sesgo localista del mercado
    lambda_m_visita = lambda_mercado_total * 0.45
    
    lambda_est_local, lambda_est_visita = calcular_lambdas_estadisticos(stats_local, stats_visita)
    
    # Fusión prior/posterior
    lambda_final_local = (alpha * lambda_est_local) + ((1 - alpha) * lambda_m_local)
    lambda_final_visita = (alpha * lambda_est_visita) + ((1 - alpha) * lambda_m_visita)
    
    return round(lambda_final_local, 3), round(lambda_final_visita, 3)

def factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho):
    if rho == 0: return 1.0
    if x == 0 and y == 0: return float(1 - lambda_l * lambda_v * rho)
    elif x == 1 and y == 0: return float(1 + lambda_v * rho)
    elif x == 0 and y == 1: return float(1 + lambda_l * rho)
    elif x == 1 and y == 1: return float(1 - rho)
    else: return 1.0

def calcular_matriz_zero_inflated_bivariada(lambda_l, lambda_v, rho=-0.05, zero_inf=0.03, max_goles=8):
    """
    [NUEVO] Aplica Poisson Bivariado + Dixon Coles + Zero-Inflation.
    Aumenta la precisión matemática al corregir la sobredimensión de empates 1-1.
    """
    matriz_prob = np.zeros((max_goles, max_goles), dtype=float)
    
    for x in range(max_goles):
        for y in range(max_goles):
            prob_p_local = poisson.pmf(x, lambda_l)
            prob_p_visita = poisson.pmf(y, lambda_v)
            indep_prob = prob_p_local * prob_p_visita
            
            # Aplicar Dixon-Coles
            tau = factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho)
            prob_final = max(0.0, indep_prob * tau)
            
            # Aplicar Zero-Inflation (Inflar 0-0 sutilmente para ajustar las colas)
            if x == 0 and y == 0:
                prob_final += zero_inf
                
            matriz_prob[x, y] = prob_final 
            
    # Normalizar la matriz para que sume exactamente 1.0
    matriz_prob /= matriz_prob.sum()
    return matriz_prob

def proyectar_marcador_unico(matriz_prob, lambda_l, lambda_v):
    """
    [NUEVO] Fuerza la predicción de un solo marcador exacto lógico (ej. 3-1), 
    analizando la tendencia ganadora en lugar de la campana de Gauss plana.
    """
    max_goles = matriz_prob.shape[0]
    prob_1 = float(np.tril(matriz_prob, -1).sum())
    prob_x = float(np.trace(matriz_prob))
    prob_2 = float(np.triu(matriz_prob, 1).sum())
    
    # Determinar el escenario base esperado
    tendencia = "Local" if prob_1 > prob_2 and prob_1 > prob_x else ("Visita" if prob_2 > prob_1 and prob_2 > prob_x else "Empate")
    
    mejor_marcador = "0-0"
    max_prob_condicionada = -1.0
    
    for x in range(max_goles):
        for y in range(max_goles):
            # Solo buscar marcadores que coincidan con la tendencia proyectada
            if tendencia == "Local" and x > y:
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"
            elif tendencia == "Visita" and y > x:
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"
            elif tendencia == "Empate" and x == y:
                # Evitar el 0-0 si los equipos tienen alto promedio de gol
                if x == 0 and (lambda_l + lambda_v) > 2.0: continue
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"

    # Retorna un formato de lista de un solo elemento para no romper app.py
    return [{"marcador": mejor_marcador, "prob": matriz_prob[int(mejor_marcador.split('-')[0]), int(mejor_marcador.split('-')[1])]}]

def procesar_modelos_matematicos(stats_local, stats_visita, cuotas_mercado):
    # 1. Ejecutar actualización Bayesiana con promedios puros de Excel
    lambda_l, lambda_v = actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado)
    
    # 2. Construir matriz con Poisson Bivariado, Dixon-Coles y Zero-Inflation
    matriz_prob = calcular_matriz_zero_inflated_bivariada(lambda_l, lambda_v, rho=-0.06)
    
    # 3. Marcador Único Proyectado (Reemplaza la lista genérica)
    marcador_unico = proyectar_marcador_unico(matriz_prob, lambda_l, lambda_v)
    
    # 4. Extraer probabilidades de los mercados
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
        "marcadores_top": marcador_unico,  # Ahora envía UN solo marcador fuerte
        "prob_1x2": {"Local": prob_1, "Empate": prob_x, "Visita": prob_2},
        "goles": {
            "over_1_5": prob_o15, "under_1_5": prob_u15,
            "over_2_5": prob_o25, "under_2_5": prob_u25,
            "btts_si": prob_btts_si, "btts_no": prob_btts_no
        }
    }
