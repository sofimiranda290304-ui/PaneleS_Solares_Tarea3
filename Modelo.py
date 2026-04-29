from pulp import *

def resolver_modelo(rhs):
    prob = LpProblem("Minimizar_Costo_Paneles_Solares", LpMinimize)

    x1 = LpVariable("x1_Panel_A", lowBound=0, cat='Integer')
    x2 = LpVariable("x2_Panel_B", lowBound=0, cat='Integer')
    x3 = LpVariable("x3_Panel_C", lowBound=0, cat='Integer')

    # Función objetivo
    prob += 190*x1 + 205*x2 + 255*x3, "Costo_Total"

    # Restricciones con RHS dinámico
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
