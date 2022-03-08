import pandas as pd
import numpy as np

class Budget_plan:
    def __init__(self, start_year, n_years, n_products=1, n_raw_materials=1):
        self.start_year = start_year
        self.n_years = n_years
        self.n_products=n_products
        list_years = [a for a in range(start_year, start_year + n_years)]
        self.Product_table=pd.DataFrame(0,index=np.arange(self.n_products),columns=list_years)
        self.Product_prices = pd.DataFrame(0, index=np.arange(self.n_products), columns=list_years)
        self.Revenues = pd.DataFrame(0, columns=list_years, index=['Revenues'])
        self.Raw_materials_costs = pd.DataFrame(0, columns=list_years, index=['Raw_Materials_Costs'])
        self.Variable_costs = pd.DataFrame(0, columns=list_years, index=['Variable_Costs'])
        self.HR_costs = pd.DataFrame(0, columns=list_years, index=['HR_Costs'])
        self.Maintenance_costs = pd.DataFrame(0, columns=list_years, index=['Maintenance_Costs'])
        self.Other_fixed_costs = pd.DataFrame(0, columns=list_years, index=['Other_Fixed_Costs'])
        self.Fixed_costs = pd.DataFrame(0, columns=list_years, index=['Fixed_Costs'])
        self.PL = pd.concat([self.Revenues, self.Raw_materials_costs, self.Variable_costs, self.Fixed_costs])

    def update(self):
        self.update_fixed()
        self.update_variable()
        self.update_revenues()

    def update_variable(self):
        pass

    def update_revenues(self):
        self.Revenues=(self.Product_Prices*self.Product_Table).agg(["sum"])
