import streamlit as st
from modelo import resolver_modelo

st.set_page_config(
    page_title="Optimización de Paneles Solares",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ Optimización de Instalación de Paneles Solares")
st.markdown("**Modelo de Programación Lineal Entera** — Minimización de costos")

st.divider()

# ── Sidebar: parámetros editables ──────────────────────────────────────────
st.sidebar.header("Parámetros del modelo")
st.sidebar.markdown("**Lado derecho (RHS) de las restricciones**")

st.sidebar.markdown("*Restricciones ≥ (mínimos requeridos)*")
r1 = st.sidebar.number_input("R1 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=41.07, step=0.01, format="%.2f")
r2 = st.sidebar.number_input("R2 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=7.54,  step=0.01, format="%.2f")
r3 = st.sidebar.number_input("R3 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=8.32,  step=0.01, format="%.2f")

st.sidebar.markdown("*Restricciones ≤ (capacidades máximas)*")
r4 = st.sidebar.number_input("R4 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)",    value=280.0, step=1.0,  format="%.2f")
r5 = st.sidebar.number_input("R5 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)",    value=74.0,  step=1.0,  format="%.2f")
r6 = st.sidebar.number_input("R6 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)",    value=91.0,  step=1.0,  format="%.2f")

rhs = [r1, r2, r3, r4, r5, r6]

# ── Columnas: modelo y resultados ──────────────────────────────────────────
col_modelo, col_resultado = st.columns([1.2, 1])

with col_modelo:
    st.subheader("Modelo actual")
    st.latex(r"\text{Minimizar} \quad Z = 190x_1 + 205x_2 + 255x_3")
    st.markdown("**Sujeto a:**")
    st.latex(rf"1.80x_1 + 2.03x_2 + 2.48x_3 \geq {r1}")
    st.latex(rf"1.80x_1 + 2.03x_2 + 2.48x_3 \geq {r2}")
    st.latex(rf"1.80x_1 + 2.03x_2 + 2.48x_3 \geq {r3}")
    st.latex(rf"1.9x_1 + 2.1x_2 + 2.5x_3 \leq {r4}")
    st.latex(rf"1.9x_1 + 2.1x_2 + 2.5x_3 \leq {r5}")
    st.latex(rf"1.9x_1 + 2.1x_2 + 2.5x_3 \leq {r6}")
    st.latex(r"x_1, x_2, x_3 \geq 0 \quad \text{(enteras)}")

with col_resultado:
    st.subheader("Resultados")

    if st.button("Resolver", type="primary", use_container_width=True):
        with st.spinner("Resolviendo..."):
            res = resolver_modelo(rhs)

        if res["status"] == "Optimal":
            st.success("Solución óptima encontrada")

            c1, c2, c3 = st.columns(3)
            c1.metric("Panel A (x₁)", f"{res['x1']} uds.")
            c2.metric("Panel B (x₂)", f"{res['x2']} uds.")
            c3.metric("Panel C (x₃)", f"{res['x3']} uds.")

            st.metric("💰 Costo mínimo Z", f"${res['Z']:,}")

            st.info(
                f"**Verificación LHS:**\n\n"
                f"- Restricciones 1-3: "
                f"{1.80*res['x1'] + 2.03*res['x2'] + 2.48*res['x3']:.2f}\n"
                f"- Restricciones 4-6: "
                f"{1.9*res['x1'] + 2.1*res['x2'] + 2.5*res['x3']:.2f}"
            )

        elif res["status"] == "Infeasible":
            st.error("El modelo no tiene solución factible con estos valores de RHS. "
                     "Revisa que los límites ≤ sean alcanzables dado los mínimos ≥.")
        else:
            st.warning(f"⚠️ Estado del solver: {res['status']}")
