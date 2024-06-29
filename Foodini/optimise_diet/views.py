from django.shortcuts import render
from optimise_diet.optimiser import get_model
import pandas as pd
import numpy as np
# Create your views here.
def home(request):
    return render(request, 'index.html', )
def result(request):
    ENERCC_low = float(request.POST['ENERCC_low'])
    ENERCC_high = float(request.POST['ENERCC_high'])
    Protein_low = float(request.POST['Protein_low'])
    Protein_high = float(request.POST['Protein_high'])
    Fat_low = float(request.POST['Fat_low'])
    Fat_high = float(request.POST['Fat_high'])
    result = getPredictions([(ENERCC_low, ENERCC_high), (Protein_low, Protein_high), (Fat_low, Fat_high), (220, 300), (38, 999), (0.25, 0.75), (1500, 2300),
               (3400, 10000), (1000, 2500), (3400, 10000), (400, 10000), (8, 45), (0.9, 10), (55, 400), (11, 40), (900, 10000),
               (15, 1000), (1.2, 100), (1.3, 100), (1.3, 100), (2.4, 100), (16, 35), (400, 1000), (90, 2000)] )
    return render(request, 'result.html', {'result':result})
def getPredictions(bounds):
    # Get indices and values of non-zero weight food items
    model = get_model(bounds)
    indx = {i:j for i, j in enumerate(model.x[:]()) if j > 0}
    data = pd.read_excel('NEVO2023_v8.0.xlsx', sheet_name='NEVO2023')
    # Get columns of interest
    cols = ['Engelse naam/Food name', 'ENERCC (kcal)', 'PROT (g)', 'FAT (g)', 'CHO (g)', 'FIBT (g)', 'F22:6CN3 (g)', 'NA (mg)',
        'K (mg)', 'CA (mg)', 'P (mg)', 'MG (mg)', 'FE (mg)', 'CU (mg)', 'SE (µg)', 'ZN (mg)', 'VITA_RAE (µg)',
        'VITE (mg)', 'THIA (mg)', 'RIBF (mg)', 'VITB6 (mg)', 'VITB12 (µg)', 'NIA (mg)', 'FOL (µg)', 'VITC (mg)']

    # Define dataframe
    df = data[cols].dropna()
    df.set_index('Engelse naam/Food name', inplace=True)
    df = df / 10
    # Print food item name and amount to be consumes
    final_results = []
    # for food_inx, amount in indx.items():
    #     final_results.append(f'{df.index[food_inx].title()}:   {amount}g')
    # # Get indices and values of non-zero weight food items
    foods = [food for food in df.index if not np.isclose(pyo.value(model.x[food]()), 0.0)]

    # Print food item name and amount to be consumes
    for food_item in foods:
        final_results.append(f'{food_item.title()}:   {model.x[food_item]()}g')
    return final_results
import pyomo.environ as pyo
import pandas as pd
import shutil
# import pyomo.environ as pyo
# import pandas as pd
# import shutil
# # Define function to build model
# def get_model(bounds = [(2200, 2300), (140, 180), (60, 90), (220, 300), (38, 999), (0.25, 0.75), (1500, 2300),
#               (3400, 10000), (1000, 2500), (3400, 10000), (400, 10000), (8, 45), (0.9, 10), (55, 400), (11, 40), (900, 10000),
#               (15, 1000), (1.2, 100), (1.3, 100), (1.3, 100), (2.4, 100), (16, 35), (400, 1000), (90, 2000)] ) -> pyo.ConcreteModel:
#     data = pd.read_excel('NEVO2023_v8.0.xlsx', sheet_name='NEVO2023')
#     # Get columns of interest
#     cols = ['Engelse naam/Food name', 'ENERCC (kcal)', 'PROT (g)', 'FAT (g)', 'CHO (g)', 'FIBT (g)', 'F22:6CN3 (g)', 'NA (mg)',
#         'K (mg)', 'CA (mg)', 'P (mg)', 'MG (mg)', 'FE (mg)', 'CU (mg)', 'SE (µg)', 'ZN (mg)', 'VITA_RAE (µg)',
#         'VITE (mg)', 'THIA (mg)', 'RIBF (mg)', 'VITB6 (mg)', 'VITB12 (µg)', 'NIA (mg)', 'FOL (µg)', 'VITC (mg)']

#     # Define dataframe
#     df = data[cols].dropna()
#     df.set_index('Engelse naam/Food name', inplace=True)
#     df = df / 100
#     solver = pyo.SolverFactory('cbc')

#     # Define big M and list of upper and lower nutrient bounds
#     M = 999
#     '''    bounds = [(2200, 2300), (140, 180), (60, 90), (220, 300), (38, 999), (0.25, 0.75), (1500, 2300),
#               (3400, 10000), (1000, 2500), (3400, 10000), (400, 10000), (8, 45), (0.9, 10), (55, 400), (11, 40), (900, 10000),
#               (15, 1000), (1.2, 100), (1.3, 100), (1.3, 100), (2.4, 100), (16, 35), (400, 1000), (90, 2000)]
#     '''
#     # Instantiate model
#     model = pyo.ConcreteModel()

#     # Define variables
#     model.x = pyo.Var(df.index, within=pyo.NonNegativeIntegers)

#     # Define objective
#     model.total_weight = pyo.Objective(expr=sum(model.x[i] for i in df.index),
#                                        sense=pyo.minimize)

#     # Define and add constraints
#     model.requirements = pyo.ConstraintList()
#     for i, bound in enumerate(bounds):
#         lb, ub = bound
#         nutrient = df.columns[i]
#         model.requirements.add(expr=sum(df[nutrient][food]*model.x[food] for food in df.index) <= ub)
#         model.requirements.add(expr=sum(df[nutrient][food]*model.x[food] for food in df.index) >= lb)

#     # Solve and return model
#     solver.solve(model)

#     return model