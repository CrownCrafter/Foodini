
import numpy as np
np.float_ = np.float64
np.complex_ = np.complex128
import pyomo.environ as pyo
import pandas as pd
import shutil
# Define function to build model
def get_model(bounds = [(2200, 2300), (140, 180), (60, 90), (220, 300), (38, 999), (0.25, 0.75), (1500, 2300),
              (3400, 10000), (1000, 2500), (3400, 10000), (400, 10000), (8, 45), (0.9, 10), (55, 400), (11, 40), (900, 10000),
              (15, 1000), (1.2, 100), (1.3, 100), (1.3, 100), (2.4, 100), (16, 35), (400, 1000), (90, 2000)], min_weight = 30, max_weight = 1000) -> pyo.ConcreteModel:
    data = pd.read_excel('NEVO2023_v8.0.xlsx', sheet_name='NEVO2023')
    # Get columns of interest
    cols = ['Engelse naam/Food name', 'ENERCC (kcal)', 'PROT (g)', 'FAT (g)', 'CHO (g)', 'FIBT (g)', 'F22:6CN3 (g)', 'NA (mg)',
        'K (mg)', 'CA (mg)', 'P (mg)', 'MG (mg)', 'FE (mg)', 'CU (mg)', 'SE (µg)', 'ZN (mg)', 'VITA_RAE (µg)',
        'VITE (mg)', 'THIA (mg)', 'RIBF (mg)', 'VITB6 (mg)', 'VITB12 (µg)', 'NIA (mg)', 'FOL (µg)', 'VITC (mg)']

    # Define dataframe
    df = data[cols].dropna()
    df.set_index('Engelse naam/Food name', inplace=True)
    df = df / 100
    solver = pyo.SolverFactory('cbc')

    # Define big M and list of upper and lower nutrient bounds
    M = 999
    '''    bounds = [(2200, 2300), (140, 180), (60, 90), (220, 300), (38, 999), (0.25, 0.75), (1500, 2300),
              (3400, 10000), (1000, 2500), (3400, 10000), (400, 10000), (8, 45), (0.9, 10), (55, 400), (11, 40), (900, 10000),
              (15, 1000), (1.2, 100), (1.3, 100), (1.3, 100), (2.4, 100), (16, 35), (400, 1000), (90, 2000)]
    '''
    # Instantiate model
    model = pyo.ConcreteModel()

    # Define variables
    model.x = pyo.Var(df.index, within=pyo.NonNegativeIntegers)
    model.y = pyo.Var(df.index, within=pyo.Binary)

    # Define objective
    model.total_weight = pyo.Objective(expr=sum(model.x[i] for i in df.index),
                                       sense=pyo.minimize)

    # Define and add constraints
    model.requirements = pyo.ConstraintList()
    for i, bound in enumerate(bounds):
        lb, ub = bound
        nutrient = df.columns[i]
        model.requirements.add(expr=sum(df[nutrient][food]*model.x[food] for food in df.index) <= ub)
        model.requirements.add(expr=sum(df[nutrient][food]*model.x[food] for food in df.index) >= lb)

    # Add functionality constraints
    for food in df.index:
        model.requirements.add(expr=model.x[food] <= max_weight*model.y[food])
        model.requirements.add(expr=model.x[food] >= min_weight*model.y[food])

    # Solve and return model
    solver.solve(model)

    return model