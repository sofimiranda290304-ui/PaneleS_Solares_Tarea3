import streamlit as st
from pulp import *

# ── Función del modelo ──────────────────────────────────────────────────────
def resolver_modelo(rhs):
    prob = LpProblem("Minimizar_Costo_Paneles_Solares", LpMinimize)

    x1 = LpVariable("x1_Panel_A", lowBound=0, cat='Integer')
    x2 = LpVariable("x2_Panel_B", lowBound=0, cat='Integer')
    x3 = LpVariable("x3_Panel_C", lowBound=0, cat='Integer')

    prob += 190*x1 + 205*x2 + 255*x3, "Costo_Total"

    prob += 1.80*x1 + 2.03*x2 + 2.48*x3 >= rhs[0], "R1"
    prob += 1.80*x1 + 2.03*x2 + 2.48*x3 >= rhs[1], "R2"
    prob += 1.80*x1 + 2.03*x2 + 2.48*x3 >= rhs[2], "R3"
    prob += 1.9*x1  + 2.1*x2  + 2.5*x3  <= rhs[3], "R4"
    prob += 1.9*x1  + 2.1*x2  + 2.5*x3  <= rhs[4], "R5"
    prob += 1.9*x1  + 2.1*x2  + 2.5*x3  <= rhs[5], "R6"

    prob.solve(PULP_CBC_CMD(msg=0))

    return {
        "status": LpStatus[prob.status],
        "x1": int(value(x1)) if value(x1) is not None else None,
        "x2": int(value(x2)) if value(x2) is not None else None,
        "x3": int(value(x3)) if value(x3) is not None else None,
        "Z":  int(value(prob.objective)) if value(prob.objective) is not None else None
    }

# ── Interfaz Streamlit ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Optimización de Paneles Solares",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ Optimización de Instalación de Paneles Solares")
st.markdown("**Modelo de Programación Lineal Entera** — Minimización de costos")
st.divider()

# Sidebar
st.sidebar.header("⚙️ Parámetros del modelo")
st.sidebar.markdown("**Lado derecho (RHS) de las restricciones**")

st.sidebar.markdown("*Restricciones ≥ (mínimos requeridos)*")
r1 = st.sidebar.number_input("R1 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=41.07, step=0.01, format="%.2f")
r2 = st.sidebar.number_input("R2 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=7.54,  step=0.01, format="%.2f")
r3 = st.sidebar.number_input("R3 ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)", value=8.32,  step=0.01, format="%.2f")

st.sidebar.markdown("*Restricciones ≤ (capacidades máximas)*")
r4 = st.sidebar.number_input("R4 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)", value=280.0, step=1.0, format="%.2f")
r5 = st.sidebar.number_input("R5 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)", value=74.0,  step=1.0, format="%.2f")
r6 = st.sidebar.number_input("R6 ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)", value=91.0,  step=1.0, format="%.2f")

rhs = [r1, r2, r3, r4, r5, r6]

# Layout principal
col_modelo, col_resultado = st.columns([1.2, 1])

with col_modelo:
    st.subheader("📐 Modelo actual")
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
    st.subheader("📊 Resultados")

    if st.button("⚡ Resolver", type="primary", use_container_width=True):
        with st.spinner("Resolviendo..."):
            res = resolver_modelo(rhs)

        if res["status"] == "Optimal":
            st.success("✅ Solución óptima encontrada")
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
            st.error("❌ No tiene solución factible. Revisa que los límites ≤ sean mayores que los mínimos ≥.")
        else:
            st.warning(f"⚠️ Estado del solver: {res['status']}")
