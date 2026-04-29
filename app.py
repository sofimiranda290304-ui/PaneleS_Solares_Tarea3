import streamlit as st
from pulp import *

def resolver_modelo(rhs_min, rhs_max):
    prob = LpProblem("Minimizar_Costo_Paneles_Solares", LpMinimize)

    x1 = LpVariable("x1_Panel_A", lowBound=0, cat='Integer')
    x2 = LpVariable("x2_Panel_B", lowBound=0, cat='Integer')
    x3 = LpVariable("x3_Panel_C", lowBound=0, cat='Integer')

    prob += 190*x1 + 205*x2 + 255*x3, "Costo_Total"

    # Solo 2 restricciones estructurales
    prob += 1.80*x1 + 2.03*x2 + 2.48*x3 >= rhs_min, "R_minimo"
    prob += 1.9*x1  + 2.1*x2  + 2.5*x3  <= rhs_max, "R_maximo"

    prob.solve(PULP_CBC_CMD(msg=0))

    return {
        "status": LpStatus[prob.status],
        "x1": int(value(x1)) if value(x1) is not None else None,
        "x2": int(value(x2)) if value(x2) is not None else None,
        "x3": int(value(x3)) if value(x3) is not None else None,
        "Z":  int(value(prob.objective)) if value(prob.objective) is not None else None
    }

# ── Interfaz ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Optimización de Paneles Solares",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ Optimización de Instalación de Paneles Solares")
st.markdown("**Modelo de Programación Lineal Entera** — Minimización de costos")
st.divider()

# ── Sidebar: selección de caso ───────────────────────────────────────────────
st.sidebar.header("⚙️ Parámetros del modelo")

# Casos predefinidos (los 3 pares de RHS de la imagen)
casos = {
    "Caso 1 (RHS: 41.07 / 280)": (41.07, 280.0),
    "Caso 2 (RHS: 7.54  / 74)":  (7.54,  74.0),
    "Caso 3 (RHS: 8.32  / 91)":  (8.32,  91.0),
    "Caso personalizado":         None,
}

caso_seleccionado = st.sidebar.selectbox("Selecciona un caso", list(casos.keys()))

if casos[caso_seleccionado] is not None:
    rhs_min_default, rhs_max_default = casos[caso_seleccionado]
else:
    rhs_min_default, rhs_max_default = 41.07, 280.0

st.sidebar.divider()
st.sidebar.markdown("**Lado derecho (RHS)**")

rhs_min = st.sidebar.number_input(
    "RHS mínimo  ≥  (1.80x₁ + 2.03x₂ + 2.48x₃)",
    value=rhs_min_default,
    step=0.01,
    format="%.2f",
    disabled=(casos[caso_seleccionado] is not None)
)

rhs_max = st.sidebar.number_input(
    "RHS máximo  ≤  (1.9x₁ + 2.1x₂ + 2.5x₃)",
    value=rhs_max_default,
    step=0.01,
    format="%.2f",
    disabled=(casos[caso_seleccionado] is not None)
)

# Si es caso predefinido, usar los valores fijos
if casos[caso_seleccionado] is not None:
    rhs_min, rhs_max = casos[caso_seleccionado]

# ── Layout principal ─────────────────────────────────────────────────────────
col_modelo, col_resultado = st.columns([1.2, 1])

with col_modelo:
    st.subheader("📐 Modelo actual")
    st.latex(r"\text{Minimizar} \quad Z = 190x_1 + 205x_2 + 255x_3")
    st.markdown("**Sujeto a:**")
    st.latex(rf"1.80x_1 + 2.03x_2 + 2.48x_3 \geq {rhs_min}")
    st.latex(rf"1.9x_1 + 2.1x_2 + 2.5x_3 \leq {rhs_max}")
    st.latex(r"x_1, x_2, x_3 \geq 0 \quad \text{(enteras)}")

    st.divider()
    st.markdown("**📋 Casos del problema original**")
    st.table({
        "Caso": ["Caso 1", "Caso 2", "Caso 3"],
        "RHS  ≥": [41.07, 7.54, 8.32],
        "RHS  ≤": [280, 74, 91],
    })

with col_resultado:
    st.subheader("📊 Resultados")

    if st.button("⚡ Resolver", type="primary", use_container_width=True):
        with st.spinner("Resolviendo..."):
            res = resolver_modelo(rhs_min, rhs_max)

        if res["status"] == "Optimal":
            st.success("✅ Solución óptima encontrada")

            c1, c2, c3 = st.columns(3)
            c1.metric("Panel A (x₁)", f"{res['x1']} uds.")
            c2.metric("Panel B (x₂)", f"{res['x2']} uds.")
            c3.metric("Panel C (x₃)", f"{res['x3']} uds.")

            st.metric("💰 Costo mínimo Z", f"${res['Z']:,}")

            lhs1 = 1.80*res['x1'] + 2.03*res['x2'] + 2.48*res['x3']
            lhs2 = 1.9*res['x1']  + 2.1*res['x2']  + 2.5*res['x3']

            st.info(
                f"**Verificación:**\n\n"
                f"- 1.80x₁ + 2.03x₂ + 2.48x₃ = **{lhs1:.2f}** ≥ {rhs_min} "
                f"{'✅' if lhs1 >= rhs_min else '❌'}\n"
                f"- 1.9x₁ + 2.1x₂ + 2.5x₃ = **{lhs2:.2f}** ≤ {rhs_max} "
                f"{'✅' if lhs2 <= rhs_max else '❌'}"
            )

        elif res["status"] == "Infeasible":
            st.error("❌ Sin solución factible. El RHS mínimo podría ser mayor al permitido por el RHS máximo.")
        else:
            st.warning(f"⚠️ Estado del solver: {res['status']}")
