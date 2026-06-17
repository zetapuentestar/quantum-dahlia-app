import numpy as np

def calculate_ev(probability, odds):
    if odds <= 0: return 0
    return (probability * odds) - 1

def generate_report(sim_data, market_odds):
    weights = sim_data['weights']
    total_weight = np.sum(weights)
    
    # Funciones auxiliares para calcular probabilidad pesada
    def calc_prob(condition):
        return np.sum(weights[condition]) / total_weight

    # Condiciones de Mercado
    h_win = sim_data['goals_h'] > sim_data['goals_a']
    draw = sim_data['goals_h'] == sim_data['goals_a']
    a_win = sim_data['goals_h'] < sim_data['goals_a']
    total_goals = sim_data['goals_h'] + sim_data['goals_a']
    btts = (sim_data['goals_h'] > 0) & (sim_data['goals_a'] > 0)
    
    ht_h_win = sim_data['ht_goals_h'] > sim_data['ht_goals_a']
    ht_goal = (sim_data['ht_goals_h'] + sim_data['ht_goals_a']) > 0

    # Diccionario de resultados
    results = {
        "Victoria Local (1)": calc_prob(h_win),
        "Empate (X)": calc_prob(draw),
        "Victoria Visitante (2)": calc_prob(a_win),
        "Más de 2.5 Goles": calc_prob(total_goals > 2.5),
        "Menos de 2.5 Goles": calc_prob(total_goals <= 2.5),
        "Ambos Anotan (Sí)": calc_prob(btts),
        "Más de 8.5 Corners": calc_prob(sim_data['corners'] > 8.5),
        "Más de 4.5 Tarjetas": calc_prob(sim_data['cards'] > 4.5),
        "Victoria Local 1ra Mitad": calc_prob(ht_h_win),
        "Gol en 1ra Mitad (Sí)": calc_prob(ht_goal)
    }

    # Estructurar reporte con Confianza y EV
    report = []
    for market, prob in results.items():
        odds = market_odds.get(market, 2.0) # Cuota por defecto 2.0 si no se provee
        ev = calculate_ev(prob, odds)
        
        # Ranking de confianza basado en la probabilidad
        if prob > 0.65: confidence = "⭐⭐⭐ Alta"
        elif prob > 0.45: confidence = "⭐⭐ Media"
        else: confidence = "⭐ Baja"
        
        report.append({
            "Mercado": market,
            "Probabilidad": f"{prob * 100:.2f}%",
            "Confianza": confidence,
            "EV (Valor Esperado)": f"{ev:+.2f}"
        })
        
    # Resultado exacto más probable
    score_pairs = list(zip(sim_data['goals_h'], sim_data['goals_a']))
    from collections import Counter
    most_common_score = Counter(score_pairs).most_common(1)[0][0]
    
    return report, most_common_score