import numpy as np
from math_models import dixon_coles_adjustment

def run_monte_carlo(lambda_h, mu_a, home_team, away_team, iterations=100000):
    # Generar muestras base de Poisson
    raw_goals_h = np.random.poisson(lambda_h, iterations)
    raw_goals_a = np.random.poisson(mu_a, iterations)
    
    # Aplicar ajuste de dependencia (Dixon-Coles) en tiempo de simulación mediante filtrado probabilístico
    # Para mayor rendimiento en Python, aproximamos el peso del ajuste
    adjustment_weights = np.array([
        dixon_coles_adjustment(h, a, lambda_h, mu_a) for h, a in zip(raw_goals_h, raw_goals_a)
    ])
    
    # Simulación de otros mercados basados en las estadísticas base
    sim_corners_h = np.random.poisson(home_team.corners, iterations)
    sim_corners_a = np.random.poisson(away_team.corners, iterations)
    
    sim_cards_h = np.random.poisson(home_team.cards, iterations)
    sim_cards_a = np.random.poisson(away_team.cards, iterations)
    
    # Simulación Primera Mitad (Aprox. 45% de los goles ocurren en el 1T)
    ht_goals_h = np.random.binomial(raw_goals_h, 0.45)
    ht_goals_a = np.random.binomial(raw_goals_a, 0.45)
    
    return {
        'iterations': iterations,
        'goals_h': raw_goals_h,
        'goals_a': raw_goals_a,
        'weights': adjustment_weights,
        'corners': sim_corners_h + sim_corners_a,
        'cards': sim_cards_h + sim_cards_a,
        'ht_goals_h': ht_goals_h,
        'ht_goals_a': ht_goals_a
    }