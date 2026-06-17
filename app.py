import streamlit as st
import pandas as pd

# Importamos tus módulos matemáticos
from data_input import TeamStats
from math_models import calculate_rates
from simulation import run_monte_carlo
from report import generate_report

st.set_page_config(page_title="Quantum Dahlia Sports", layout="wide")
st.title("⚽ Quantum Dahlia Sports Investments")
st.subheader("Motor de Análisis Predictivo (Monte Carlo & Bayes)")
st.markdown("---")

# 1. Ingreso de estadísticas
col1, col2 = st.columns(2)

with col1:
    st.header("🏠 Equipo Local")
    home_name = st.text_input("Nombre Local", "PSG")
    home_poss = st.slider("Posesión de Balón % (Local)", 0, 100, 65)
    # Permite decimales con step=0.1
    home_xg = st.number_input("Goles Esperados (xG)", 0.0, 10.0, 2.1, step=0.1)
    home_shots = st.number_input("Tiros Totales", 0, 100, 15, step=1)
    home_shots_target = st.number_input("Tiros a Puerta", 0, 50, 6, step=1)
    home_saves = st.number_input("Atajadas", 0.0, 20.0, 1.5, step=0.1) # Acepta decimales
    home_corners = st.number_input("Corners", 0, 50, 6, step=1)
    home_cards = st.number_input("Tarjetas", 0, 20, 2, step=1)

with col2:
    st.header("✈️ Equipo Visitante")
    away_name = st.text_input("Nombre Visitante", "Barcelona")
    away_poss = 100 - home_poss
    away_xg = st.number_input("Goles Esperados (xG) Visitante", 0.0, 10.0, 0.8, step=0.1)
    away_shots = st.number_input("Tiros Totales Visitante", 0, 100, 7, step=1)
    away_shots_target = st.number_input("Tiros a Puerta Visitante", 0, 50, 2, step=1)
    away_saves = st.number_input("Atajadas Visitante", 0.0, 20.0, 1.5, step=0.1) # Acepta decimales
    away_corners = st.number_input("Corners Visitante", 0, 50, 3, step=1)
    away_cards = st.number_input("Tarjetas Visitante", 0, 20, 3, step=1)

st.markdown("---")

# 2. NUEVA SECCIÓN: Cuotas de la casa de apuestas
st.header("💰 Cuotas del Mercado (Bookies)")
st.write("Ingresa las cuotas que ofrece tu casa de apuestas para calcular el Valor Esperado (EV).")

col_odds1, col_odds2, col_odds3 = st.columns(3)
with col_odds1:
    odd_1 = st.number_input("Victoria Local (1)", 1.0, 20.0, 1.95, step=0.05)
    odd_over = st.number_input("Más de 2.5 Goles", 1.0, 20.0, 1.85, step=0.05)
with col_odds2:
    odd_x = st.number_input("Empate (X)", 1.0, 20.0, 3.40, step=0.05)
    odd_under = st.number_input("Menos de 2.5 Goles", 1.0, 20.0, 1.95, step=0.05)
with col_odds3:
    odd_2 = st.number_input("Victoria Visitante (2)", 1.0, 20.0, 4.10, step=0.05)
    odd_btts = st.number_input("Ambos Anotan (Sí)", 1.0, 20.0, 1.75, step=0.05)

st.markdown("---")

# 3. Ejecución
if st.button("🚀 Ejecutar Simulación (100,000 iteraciones)", type="primary"):
    with st.spinner('Calculando fuerzas, ejecutando Monte Carlo y evaluando cuotas...'):
        
        home_team = TeamStats(
            name=home_name,
            possession=float(home_poss),
            xg=float(home_xg),
            total_shots=float(home_shots),
            shots_on_target=float(home_shots_target),
            saves=float(home_saves),
            corners=float(home_corners),
            cards=float(home_cards),
            ht_win_prob=0.40,
            ht_goal_prob=0.60
        )
            
        away_team = TeamStats(
            name=away_name,
            possession=float(away_poss),
            xg=float(away_xg),
            total_shots=float(away_shots),
            shots_on_target=float(away_shots_target),
            saves=float(away_saves),
            corners=float(away_corners),
            cards=float(away_cards),
            ht_win_prob=0.20,
            ht_goal_prob=0.35
        )
        
        lambda_h, mu_a = calculate_rates(home_team, away_team)
        sim_results = run_monte_carlo(lambda_h, mu_a, home_team, away_team)
        
        # Conectamos las cuotas de la interfaz con el reporte
        market_odds = {
            "Victoria Local (1)": odd_1,
            "Empate (X)": odd_x,
            "Victoria Visitante (2)": odd_2,
            "Más de 2.5 Goles": odd_over,
            "Menos de 2.5 Goles": odd_under,
            "Ambos Anotan (Sí)": odd_btts
        }
        
        report_data, exact_score = generate_report(sim_results, market_odds)
        
        st.success("¡Simulación completada con éxito!")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Resultado Exacto Más Probable", f"{exact_score[0]} - {exact_score[1]}")
        with col_res2:
            st.metric("Fuerza Ofensiva Base (λ / μ)", f"{lambda_h:.2f} / {mu_a:.2f}")
            
        st.subheader("📊 Tabla de Probabilidades y Valor Esperado (EV)")
        
        # Resaltamos las filas con EV positivo (una pequeña mejora visual)
        df = pd.DataFrame(report_data)
        st.subheader("📊 Tabla de Probabilidades y Valor Esperado (EV)")
df = pd.DataFrame(report_data)
st.dataframe(df, use_container_width=True)
