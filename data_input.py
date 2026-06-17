class TeamStats:
    def __init__(self, name, possession, xg, total_shots, shots_on_target, 
                 saves, corners, cards, ht_win_prob, ht_goal_prob):
        self.name = name
        self.possession = possession / 100.0  # Convertir a decimal
        self.xg = xg
        self.total_shots = total_shots
        self.shots_on_target = shots_on_target
        self.saves = saves
        self.corners = corners
        self.cards = cards
        self.ht_win_prob = ht_win_prob
        self.ht_goal_prob = ht_goal_prob

def get_match_data():
    # En una app real, esto vendría de una API, base de datos o input del usuario por consola/UI
    home = TeamStats(
        name="Equipo Local", possession=55, xg=1.8, total_shots=14, shots_on_target=5,
        saves=3, corners=6, cards=2, ht_win_prob=0.35, ht_goal_prob=0.60
    )
    away = TeamStats(
        name="Equipo Visitante", possession=45, xg=1.1, total_shots=9, shots_on_target=3,
        saves=4, corners=4, cards=3, ht_win_prob=0.20, ht_goal_prob=0.45
    )
    return home, away