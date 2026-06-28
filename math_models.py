import numpy as np
from scipy.stats import poisson
import math

def derivar_lambdas_del_mercado(cuota_mas_25, cuota_menos_25):
    """
    [PRIOR BAYESIANO]
    Deriva la creencia inicial del mercado (casas de apuestas) sobre la cantidad de goles.
    """
    if cuota_mas_25 <= 1.0 or cuota_menos_25 <= 1.0: return 2.5  
        
    prob_u25 = (1 / cuota_menos_25) / ((1 / cuota_menos_25) + (1 / cuota_mas_25))
    
    for l_test in np.arange(0.5, 5.0, 0.05):
        if poisson.cdf(2, l_test) <= prob_u25:
            return float(l_test)
    return 2.65

def termodinamica_futbolistica(stats_local, stats_visita):
    """
    [NUEVO: MODELO FÍSICO ESTADÍSTICO]
    Aplica la Ley de los Gases Ideales (PV = nRT) y Entropía para medir la Presión Ofensiva y el Caos.
    """
    # --- 1. Extracción de variables ---
    gf_l = float(stats_local.get("goles_favor", stats_local.get("gf", 1.0)))
    gc_l = float(stats_local.get("goles_contra", stats_local.get("gc", 1.0)))
    xg_l = float(stats_local.get("xg", gf_l))
    pos_l = float(stats_local.get("posesion", stats_local.get("pos", 50.0)))
    cor_l = float(stats_local.get("corners", stats_local.get("cor", 4.0)))
    tp_l = float(stats_local.get("puerta", stats_local.get("tp", 4.0)))
    ti_l = float(stats_local.get("tiros", stats_local.get("ti", 10.0)))
    tar_l = float(stats_local.get("tarjetas", stats_local.get("tar", 2.0)))
    atj_l = float(stats_local.get("atajadas", stats_local.get("at", 2.0)))

    gf_v = float(stats_visita.get("goles_favor", stats_visita.get("gf", 1.0)))
    gc_v = float(stats_visita.get("goles_contra", stats_visita.get("gc", 1.0)))
    xg_v = float(stats_visita.get("xg", gf_v))
    pos_v = float(stats_visita.get("posesion", stats_visita.get("pos", 50.0)))
    cor_v = float(stats_visita.get("corners", stats_visita.get("cor", 4.0)))
    tp_v = float(stats_visita.get("puerta", stats_visita.get("tp", 4.0)))
    ti_v = float(stats_visita.get("tiros", stats_visita.get("ti", 10.0)))
    tar_v = float(stats_visita.get("tarjetas", stats_visita.get("tar", 2.0)))
    atj_v = float(stats_visita.get("atajadas", stats_visita.get("at", 2.0)))

    # --- 2. LEY DE GASES IDEALES (P = nRT / V) ---
    # n (Moles): Eficiencia goleadora (Goles Reales / Goles Esperados)
    n_l = gf_l / max(0.1, xg_l)
    n_v = gf_v / max(0.1, xg_v)
    
    # R (Constante Universal Adaptada): Dominio de balón
    r_l = pos_l / 50.0
    r_v = pos_v / 50.0
    
    # T (Temperatura): Intensidad del ataque (Tiros a puerta + Córners)
    t_l = tp_l + (cor_l * 0.5)
    t_v = tp_v + (cor_v * 0.5)
    
    # V (Volumen Defensivo Rival): Espacio o "densidad" defensiva. 
    # Un equipo que recibe muchos goles y ataja mucho, tiene un volumen grande (fácil de penetrar).
    v_def_visita = max(1.0, 10.0 - (gc_v + atj_v))
    v_def_local = max(1.0, 10.0 - (gc_l + atj_l))
    
    # P (Presión Ofensiva) -> Equivalente al Lambda Puro
    presion_l = (n_l * r_l * t_l) / v_def_visita
    presion_v = (n_v * r_v * t_v) / v_def_local

    # Ajuste de escala a Goles Esperados Físicos (normalización suave)
    lambda_fisico_l = (presion_l * 0.25) + (xg_l * 0.75)
    lambda_fisico_v = (presion_v * 0.25) + (xg_v * 0.75)

    # --- 3. CÁLCULO DE ENTROPÍA (Caos / Incertidumbre) ---
    # Entropía S = ln(W). W = Desperdicio (tiros fuera) + Infracciones (Tarjetas)
    microestados_l = max(1.0, (ti_l - tp_l) + tar_l)
    microestados_v = max(1.0, (ti_v - tp_v) + tar_v)
    
    entropia_sistema = math.log(microestados_l + microestados_v)
    
    # Factor de Caos (0.0 a 1.0)
    caos = min(1.0, entropia_sistema / 4.0)

    return lambda_fisico_l, lambda_fisico_v, caos

def actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado):
    """
    [FILTRO BAYESIANO MAESTRO]
    Combina el Prior del mercado con el Likelihood (nuestra Termodinámica).
    La entropía decide a quién creerle más.
    """
    c_g25 = cuotas_mercado.get("goles_2_5", [1.85, 1.85])
    lambda_mercado_total = derivar_lambdas_del_mercado(c_g25[0], c_g25[1])
    
    # El mercado suele dar un ~55% de peso al local históricamente
    lambda_m_local = lambda_mercado_total * 0.55 
    lambda_m_visita = lambda_mercado_total * 0.45
    
    # Likelihood Termodinámico y Nivel de Caos
    lambda_fisico_l, lambda_fisico_v, caos = termodinamica_futbolistica(stats_local, stats_visita)
    
    # Si hay MUCHO CAOS, el modelo desconfía de la física exacta y confía más en el Prior del Mercado (que aplana probabilidades)
    # Si hay POCO CAOS, el partido es predecible y mandan nuestros cálculos físicos (Alpha alto).
    alpha_base = 0.70
    alpha_ajustado = alpha_base * (1.0 - (caos * 0.3)) # A más caos, menor alpha
    
    # Fusión Bayesiana (Posterior)
    lambda_final_local = (alpha_ajustado * lambda_fisico_l) + ((1 - alpha_ajustado) * lambda_m_local)
    lambda_final_visita = (alpha_ajustado * lambda_fisico_v) + ((1 - alpha_ajustado) * lambda_m_visita)
    
    return round(lambda_final_local, 3), round(lambda_final_visita, 3), caos

def factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho):
    if rho == 0: return 1.0
    if x == 0 and y == 0: return float(1 - lambda_l * lambda_v * rho)
    elif x == 1 and y == 0: return float(1 + lambda_v * rho)
    elif x == 0 and y == 1: return float(1 + lambda_l * rho)
    elif x == 1 and y == 1: return float(1 - rho)
    else: return 1.0

def calcular_matriz_zero_inflated_bivariada(lambda_l, lambda_v, caos, rho=-0.05, zero_inf_base=0.03, max_goles=8):
    """
    [POISSON BIVARIADO ESTOCÁSTICO]
    La entropía (caos) afecta dinámicamente la cantidad de 0-0 y empates sorpresa.
    """
    matriz_prob = np.zeros((max_goles, max_goles), dtype=float)
    
    # El Caos (Entropía) modifica directamente a Rho (dependencia) y al Zero-Inflation
    rho_ajustado = rho - (caos * 0.05) # Aumenta la probabilidad de empates bajos en partidos caóticos
    zero_inf_ajustado = zero_inf_base + (caos * 0.04) # Más caos = Más riesgo de partido cerrado/trabado 0-0

    for x in range(max_goles):
        for y in range(max_goles):
            prob_p_local = poisson.pmf(x, lambda_l)
            prob_p_visita = poisson.pmf(y, lambda_v)
            indep_prob = prob_p_local * prob_p_visita
            
            # Dixon-Coles
            tau = factor_ajuste_dixon_coles(x, y, lambda_l, lambda_v, rho_ajustado)
            prob_final = max(0.0, indep_prob * tau)
            
            # Zero-Inflation Termodinámico
            if x == 0 and y == 0:
                prob_final += zero_inf_ajustado
            elif x == 1 and y == 1:
                # Partidos con alta entropía tienden a atascarse en 1-1 si se rompe el 0-0
                prob_final += (zero_inf_ajustado * 0.5) 
                
            matriz_prob[x, y] = prob_final 
            
    # Normalización estricta
    matriz_prob /= matriz_prob.sum()
    return matriz_prob

def proyectar_marcador_unico(matriz_prob, lambda_l, lambda_v):
    """
    [MAXIMUM A POSTERIORI (MAP)]
    Encuentra el escenario lógico más denso en probabilidad.
    """
    max_goles = matriz_prob.shape[0]
    prob_1 = float(np.tril(matriz_prob, -1).sum())
    prob_x = float(np.trace(matriz_prob))
    prob_2 = float(np.triu(matriz_prob, 1).sum())
    
    tendencia = "Local" if prob_1 > prob_2 and prob_1 > prob_x else ("Visita" if prob_2 > prob_1 and prob_2 > prob_x else "Empate")
    
    mejor_marcador = "0-0"
    max_prob_condicionada = -1.0
    
    for x in range(max_goles):
        for y in range(max_goles):
            if tendencia == "Local" and x > y:
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"
            elif tendencia == "Visita" and y > x:
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"
            elif tendencia == "Empate" and x == y:
                if x == 0 and (lambda_l + lambda_v) > 2.2: continue # Si son goleadores, ignorar el 0-0 lógico
                if matriz_prob[x, y] > max_prob_condicionada:
                    max_prob_condicionada = matriz_prob[x, y]
                    mejor_marcador = f"{x}-{y}"

    return [{"marcador": mejor_marcador, "prob": matriz_prob[int(mejor_marcador.split('-')[0]), int(mejor_marcador.split('-')[1])]}]

def procesar_modelos_matematicos(stats_local, stats_visita, cuotas_mercado):
    """
    Orquestador Principal. Reemplaza por completo a Montecarlo.
    """
    # 1. Filtro Bayesiano y Termodinámico
    lambda_l, lambda_v, nivel_caos = actualizar_lambdas_bayesiano(stats_local, stats_visita, cuotas_mercado)
    
    # 2. Matriz Bivariada Dixon-Coles Ajustada por Caos
    matriz_prob = calcular_matriz_zero_inflated_bivariada(lambda_l, lambda_v, nivel_caos, rho=-0.06)
    
    # 3. Predicción MAP (Marcador Único)
    marcador_unico = proyectar_marcador_unico(matriz_prob, lambda_l, lambda_v)
    
    # 4. Cálculo Analítico Exacto de Mercados (Frecuentismo Eliminado)
    prob_1 = float(np.tril(matriz_prob, -1).sum())
    prob_x = float(np.trace(matriz_prob))
    prob_2 = float(np.triu(matriz_prob, 1).sum())
    
    # Probs 1er Tiempo (Asumiendo distribución temporal del 45% de los goles en el 1T)
    ratio_1t = 0.45
    matriz_1t = calcular_matriz_zero_inflated_bivariada(lambda_l * ratio_1t, lambda_v * ratio_1t, nivel_caos)
    prob_1_1t = float(np.tril(matriz_1t, -1).sum())
    prob_x_1t = float(np.trace(matriz_1t))
    prob_2_1t = float(np.triu(matriz_1t, 1).sum())
    
    prob_u25 = float(sum(matriz_prob[x, y] for x in range(8) for y in range(8) if x + y < 2.5))
    prob_o25 = 1.0 - prob_u25
    prob_u15 = float(sum(matriz_prob[x, y] for x in range(8) for y in range(8) if x + y < 1.5))
    prob_o15 = 1.0 - prob_u15
    
    prob_btts_no = float(matriz_prob[0, :].sum() + matriz_prob[:, 0].sum() - matriz_prob[0, 0])
    prob_btts_si = 1.0 - prob_btts_no
    
    return {
        "lambdas_ajustados": {"lambda_l": lambda_l, "lambda_v": lambda_v, "caos": nivel_caos},
        "marcadores_top": marcador_unico,  
        "prob_1x2": {"Local": prob_1 * 100, "Empate": prob_x * 100, "Visita": prob_2 * 100},
        "prob_1x2_1t": {"Local": prob_1_1t * 100, "Empate": prob_x_1t * 100, "Visita": prob_2_1t * 100},
        "goles": {
            "over_1_5": prob_o15 * 100, "under_1_5": prob_u15 * 100,
            "over_2_5": prob_o25 * 100, "under_2_5": prob_u25 * 100,
            "btts_si": prob_btts_si * 100, "btts_no": prob_btts_no * 100
        }
    }
