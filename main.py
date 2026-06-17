import pandas as pd
from data_input import get_match_data
from math_models import calculate_rates
from simulation import run_monte_carlo
from report import generate_report

def main():
    print("Iniciando Sistema de Predicción de Fútbol (Monte Carlo + Bayes + Dixon-Coles)...\n")
    
    # 1. Obtener Datos
    home_team, away_team = get_match_data()
    
    # 2. Calcular parámetros del modelo matemático (Lambda y Mu)
    lambda_h, mu_a = calculate_rates(home_team, away_team)
    print(f"Parámetros Estimados -> Local (\u03BB): {lambda_h:.2f} | Visitante (\u03BC): {mu_a:.2f}")
    
    # 3. Simulación Monte Carlo (100,000 iteraciones)
    print("Ejecutando 100,000 iteraciones de Monte Carlo...")
    sim_results = run_monte_carlo(lambda_h, mu_a, home_team, away_team, iterations=100000)
    
    # Cuotas del mercado (Bookmakers) para cálculo de EV
    market_odds = {
        "Victoria Local (1)": 2.10,
        "Empate (X)": 3.40,
        "Victoria Visitante (2)": 3.60,
        "Más de 2.5 Goles": 1.85,
        "Menos de 2.5 Goles": 1.95,
        "Ambos Anotan (Sí)": 1.75
    }
    
    # 4. Generar Reporte
    report_data, exact_score = generate_report(sim_results, market_odds)
    
    # 5. Visualizar Resultados
    print("\n--- REPORTE DE PREDICCIONES ---")
    df_report = pd.DataFrame(report_data)
    print(df_report.to_string(index=False))
    
    print(f"\nResultado Exacto Más Probable: {exact_score[0]} - {exact_score[1]}")
    print("Nota: Un EV positivo (> 0.00) indica valor matemático a largo plazo según la cuota.")

if __name__ == "__main__":
    main()