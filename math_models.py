import numpy as np

def bayesian_update(prior_rate, evidence_xg, evidence_shots_target, weight_xg=0.7, weight_shots=0.3):
    """
    Actualiza la tasa esperada de goles (lambda/mu) usando xG y tiros a puerta como evidencia.
    """
    expected_from_stats = (evidence_xg * weight_xg) + ((evidence_shots_target * 0.3) * weight_shots)
    # Actualización bayesiana simplificada (combinación lineal de prior y evidencia)
    posterior_rate = (prior_rate * 0.3) + (expected_from_stats * 0.7)
    return max(0.1, posterior_rate) # Evitar tasas negativas o nulas

def calculate_rates(home_team, away_team):
    """
    Calcula los parámetros lambda (goles esperados local) y mu (goles esperados visitante).
    """
    # Fuerza base usando posesión y tiros como "Prior"
    home_prior = (home_team.possession * 2) + (home_team.total_shots * 0.1) - (away_team.saves * 0.1)
    away_prior = (away_team.possession * 2) + (away_team.total_shots * 0.1) - (home_team.saves * 0.1)
    
    # Parámetros actualizados
    lambda_home = bayesian_update(home_prior, home_team.xg, home_team.shots_on_target)
    mu_away = bayesian_update(away_prior, away_team.xg, away_team.shots_on_target)
    
    return lambda_home, mu_away

def dixon_coles_adjustment(goals_h, goals_a, lambda_h, mu_a, rho=0.1):
    """
    Aplica el ajuste de Dixon-Coles a la matriz de probabilidades.
    """
    if goals_h == 0 and goals_a == 0:
        return max(0, 1 - lambda_h * mu_a * rho)
    elif goals_h == 0 and goals_a == 1:
        return max(0, 1 + lambda_h * rho)
    elif goals_h == 1 and goals_a == 0:
        return max(0, 1 + mu_a * rho)
    elif goals_h == 1 and goals_a == 1:
        return max(0, 1 - rho)
    return 1.0