# main.py (Fragmento de integración)
import streamlit as st
import data_input as di

def main():
    st.title("⚽ Simulador de Pronósticos Cuantitativos")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        equipo_1 = st.text_input("Nombre Equipo Local", value="PSG")
        stats_e1 = di.get_team_stats(equipo_1)
        
    with col_t2:
        equipo_2 = st.text_input("Nombre Equipo Visitante", value="Rival")
        stats_e2 = di.get_team_stats(equipo_2)
        # Cálculo automático de posesión inversa
        stats_e2["posesion"] = 100.0 - stats_e1["posesion"]
        st.info(f"Posesión automática calculada para {equipo_2}: {stats_e2['posesion']}%")
        
    st.divider()
    
    mercado = di.get_market_odds()
    
    if st.button("Ejecutar Modelos"):
        # Aquí enviaríamos 'stats_e1', 'stats_e2' y 'mercado' a math_models.py
        st.success("Datos recolectados exitosamente (con decimales). Listos para modelar.")

if __name__ == "__main__":
    main()
    
    print(f"\nResultado Exacto Más Probable: {exact_score[0]} - {exact_score[1]}")
    print("Nota: Un EV positivo (> 0.00) indica valor matemático a largo plazo según la cuota.")

if __name__ == "__main__":
    main()
