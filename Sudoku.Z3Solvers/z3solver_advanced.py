from itertools import product, combinations
from z3 import Solver, Bool, And, Or, Not, sat
from timeit import default_timer

def solve_sudoku_bool_optimized(grid):
    """
    Encodage booléen rapide d'un Sudoku 9x9 avec Z3 en Python.
    grid: itérable 9x9, 0 pour case vide, sinon [1..9].

    Retourne la solution (liste 9x9) ou None si insatisfaisable.
    """

    # -- Création du solveur avec quelques paramètres autorisés --
    solver = Solver()
    solver.set(timeout=10_000)   # 10 secondes de timeout
    solver.set(threads=4)        # Exploiter 4 cœurs si possible

    # -- Déclaration des variables booléennes x[i][j][d] --
    # x[i][j][d] = True  <==>  la case (i,j) contient la valeur (d+1)
    x = [[[Bool(f"x_{i}_{j}_{d}")
            for d in range(9)]
          for j in range(9)]
         for i in range(9)]

    constraints = []

    # == 1) Contraintes "exactement une valeur par case" ==
    #    On décompose en:
    #    - "Au moins une" valeur
    #    - "Au plus une" valeur : paires incompatibles
    for i, j in product(range(9), range(9)):
        # Au moins une
        constraints.append(Or(*(x[i][j][d] for d in range(9))))

        # Au plus une (éliminer les paires d, d')
        for d1, d2 in combinations(range(9), 2):
            constraints.append(Not(And(x[i][j][d1], x[i][j][d2])))

    # == 2) Contraintes "chaque valeur apparaît une fois par ligne" ==
    for i in range(9):
        for d in range(9):
            # Au moins une colonne j
            constraints.append(Or(*(x[i][j][d] for j in range(9))))
            # Au plus une (pairwise)
            for j1, j2 in combinations(range(9), 2):
                constraints.append(Not(And(x[i][j1][d], x[i][j2][d])))

    # == 3) Contraintes "chaque valeur apparaît une fois par colonne" ==
    for j in range(9):
        for d in range(9):
            # Au moins une ligne i
            constraints.append(Or(*(x[i][j][d] for i in range(9))))
            # Au plus une
            for i1, i2 in combinations(range(9), 2):
                constraints.append(Not(And(x[i1][j][d], x[i2][j][d])))

    # == 4) Contraintes "chaque valeur apparaît une fois par bloc 3x3" ==
    for box_i in range(3):      # index du bloc ligne (0..2)
        for box_j in range(3):  # index du bloc colonne (0..2)
            for d in range(9):
                # Récupère les 9 cases du bloc
                block_vars = []
                for di in range(3):
                    for dj in range(3):
                        i_ = 3 * box_i + di
                        j_ = 3 * box_j + dj
                        block_vars.append(x[i_][j_][d])
                # Au moins une dans ce bloc
                constraints.append(Or(*block_vars))
                # Au plus une
                for (v1, v2) in combinations(block_vars, 2):
                    constraints.append(Not(And(v1, v2)))

    # == 5) Contraintes "indices donnés" (cases déjà remplies) ==
    for i, j in product(range(9), range(9)):
        val = grid[i][j]
        if val != 0:
            # val est dans [1..9], on force x[i][j][val-1] = True
            for d in range(9):
                if d == val - 1:
                    # doit être True
                    constraints.append(x[i][j][d])
                else:
                    # doit être False
                    constraints.append(Not(x[i][j][d]))

    # == AJOUT DE TOUTES LES CONTRAINTES EN UNE FOIS ==
    solver.add(*constraints)

    # == Mesure du temps de résolution ==
    start_time = default_timer()
    result = solver.check()
    end_time = default_timer()
    solve_duration = (end_time - start_time) * 1000.0  # en ms

    if result == sat:
        print(f"Solution trouvée en {solve_duration:.2f} ms")
        model = solver.model()

        # On reconstruit la grille solution en lisant le modèle
        solution = [[0]*9 for _ in range(9)]
        for i, j, d in product(range(9), range(9), range(9)):
            if model[x[i][j][d]]:
                solution[i][j] = d + 1
        return solution
    else:
        print("Aucune solution trouvée.")
        return None

# -------------------------------------------------------------------------
# Sudoku d'exemple
instance = (
    (0, 0, 0, 0, 9, 4, 0, 3, 0),
    (0, 0, 0, 5, 1, 0, 0, 0, 7),
    (0, 8, 9, 0, 0, 0, 0, 4, 0),
    (0, 0, 0, 0, 0, 0, 2, 0, 8),
    (0, 6, 0, 2, 0, 1, 0, 5, 0),
    (1, 0, 2, 0, 0, 0, 0, 0, 0),
    (0, 7, 0, 0, 0, 0, 5, 2, 0),
    (9, 0, 0, 0, 6, 5, 0, 0, 0),
    (0, 4, 0, 9, 7, 0, 0, 0, 0),
)

# Chrono global
t0 = default_timer()
result = solve_sudoku_bool_optimized(instance)
t1 = default_timer()
total_ms = (t1 - t0) * 1000

if result:
    print("Sudoku résolu :")
    for row in result:
        print(row)
    print(f"Temps total (construction + résolution + modélisation) = {total_ms:.2f} ms.")
else:
    print("Pas de solution.")