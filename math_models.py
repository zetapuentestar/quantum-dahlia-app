# math_models.py
import numpy as np
import pandas as pd
from scipy.stats import poisson

def calcular_probabilidades_poisson(goles_esperados_local, goles_esperados_visita, max_goles=7):
    """
    Genera una matriz de probabilidades de marcadores exactos usando Poisson.
    """
    # Generar distribuciones individuales
    prob_local = [poisson.pmf(i, goles_esperados_local) for i in range(max_goles)]
    prob_visita = [poisson.pmf(i, goles_esperados_visita) for i in range(max_goles)]
    
    # Crear matriz bivariada (asumiendo independencia inicial antes de Dixon-Coles)
    matriz_prob = np.outer(prob_local, prob_visita)
    return matriz_prob

def analizar_mercados_base(matriz_prob):
    """
    Extrae las probabilidades de los mercados tradicionales y los nuevos (1.5 goles)
    a partir de la matriz de marcadores exactos.
    """
    # Mercado 1X2
    prob_1 = np.tril(matriz_prob, -1).sum()  # Triángulo inferior (Gana Local)
    prob_x = np.trace(matriz_prob)           # Diagonal (Empate)
    prob_2 = np.triu(matriz_prob, 1).sum()   # Triángulo superior (Gana Visita)
    
    # Mercado Goles Totales (Over/Under 2.5)
    prob_under_2_5 = matriz_prob[0:3, 0:3]
    mask_under_2_5 = np.array([[i+j < 2.5 for j in range(3)] for i in range(3)])
    prob_u25 = np.sum(prob_under_2_5[mask_under_2_5])
    prob_o25 = 1 - prob_u25
    
    # NUEVO: Mercado Goles Totales (Over/Under 1.5)
    prob_under_1_5 = matriz_prob[0:2, 0:2]
    mask_under_1_5 = np.array([[i+j < 1.5 for j in range(2)] for i in range(2)])
    prob_u15 = np.sum(prob_under_1_5[mask_under_1_5])
    prob_o15 = 1 - prob_u15

    # Ambos Anotan (BTTS)
    prob_btts_no = matriz_prob[0, :].sum() + matriz_prob[:, 0].sum() - matriz_prob[0, 0]
    prob_btts_si = 1 - prob_btts_no
    
    return {
        "1X2": {"Local": prob_1, "Empate": prob_x, "Visita": prob_2},
        "O/U 2.5": {"Over": prob_o25, "Under": prob_u25},
        "O/U 1.5": {"Over": prob_o15, "Under": prob_u15},
        "BTTS": {"Si": prob_btts_si, "No": prob_btts_no}
    }

def estimar_primera_mitad(goles_esperados_total, factor_1t=0.45):
    """
    Estima el lambda (goles esperados) para la primera mitad.
    El fútbol históricamente ve el 45% de los goles en el 1T y 55% en el 2T.
    """
    return goles_esperados_total * factor_1t
