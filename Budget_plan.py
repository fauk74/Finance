import pandas as pd
import numpy as np
import random



# Definition of useful functions to create and simulate a plan

def linear_trend_plan(start_year=2019, n_years=13, n_items=1, y0=1, increase=0.02, var=0.10, suff='Prod_', decimals=2,
                      tv=0, tv_method="avg"):
    """""
    creates and returns a dataframe with just one index row (unless diversely specified with parameter n_items ) , 
    with a linear trend , starting from "start_year", for "n_years"
    the bias is "y0" ,
    number of items is n_items 
    the yearly increase is "increase" on top of the previous year (e.g. 0.01 is +1% increase)
    every year is applied a random variation between + "var" and - "var" decided randomly with uniform distribution
    Default parameters are
    start_year=2019, n_years=13, n_items=1, y0=1, increase=0.02, var=0.10,suffix='Prod_', decimals=2,tv=0

    """""

    array1 = np.zeros((n_items, n_years + tv))
    lista = []
    list_columns = [str(b) for b in range(start_year, start_year + n_years)]
    for k in range(0, n_items):
        y = y0
        for i in range(0, n_years + tv):
            # Y.append(x)
            forecast = y + y * increase + y * random.uniform(-var, var)
            array1[k, i] = forecast
            y = forecast

        if k==0:
            b=""
        else:
            b=str(k)
        a = suff + b
        lista.append(a)
        
    if tv == 1:
            list_columns.append("TV")
            for k in range(0, n_items):
                if tv_method == "avg":
                    array1[k][-1] = np.mean(array1[k][-6:-1])
                else:
                    array1[k][-1] = array1[k][-2]
    

    df = pd.DataFrame(array1, columns=list_columns,index=lista)

    return df.round(decimals=decimals)


def random_costant_plan(start_year=2019, n_years=13, y0=100, var=0.05, suff='', decimals=2, tv=0,tv_method="avg"):
    """
    function that created and return a dataframe for one item
    the baseline is not changed all over the year , e.g. the reference is always y0 + y0 * uniform (-var, var)
    so no trend is manageable with this function
    default parameters are start_year=2019, n_years=13, y0=100, var=0.05, suff='Prod_'

    """
    X = list()
    Y = list()
    y = y0
    #   random.seed(seed)
    for i, x in enumerate(range(start_year, start_year + n_years )):
        Y.append(str(x))
        forecast = y0 + y0 * random.uniform(-var, var)
        X.append(forecast)
    Z = pd.DataFrame(X, index=Y).T
    Z.set_index([[suff]], inplace=True)
    if tv==1:
        if tv_method=="avg": 
            a=np.mean(Z.iloc[0][-6:-1])
        else: a=Z.iloc[0][-1]    
        Z["TV"]=a
    return Z.round(decimals=decimals)


def multiple_random_costant_plan(start_year=2019, n_years=13, n_items=10, suff="", ymax=500, ymin=200, var=0.05,
                                 decimals=2, tv=0, tv_method="avg"):
    """"
    creates and return a dataframe for multiple products, years, in a range between ymin and ymax.
    Useful to create a production plan with some random variation.
    To create the dataframe of products prices it is better to use a linear_trend_plan function to
    take into account the escalation factors

    Default parameters are :
    start_year=2019,n_items=10, n_years=13, suff="PROD", ymax=500, ymin=200, var=0.05

    """
    df = pd.DataFrame()
    rowlabels = []

    for i in range(0, n_items):
        x = str(suff) + str(i)
        df1 = random_costant_plan(start_year=start_year, n_years=n_years, y0=random.randint(ymin, ymax), suff=suff,
                                  tv=tv, tv_method=tv_method)
        df = pd.concat([df, df1])
        rowlabels.append(x)

    df.set_index([rowlabels], inplace=True)
    return df.round(decimals=decimals)


class Plan:
    def __init__(self, start_year=2019, n_years=13, current_year=2022, n_products=1, n_raw_materials=1, loss=0.02,
                 inflation=0.02, income_tax_rate=0.25, discount_rate=0.08, growth_rate=0.01, currency="€",
                 change_rate=1, turn_over=0.03, tv=0, tv_method="avg", decimals=2):

        # Rates and parameters
        self.loss = loss
        self.current_year = current_year
        self.n_raw_materials = n_raw_materials
        self.inflation = inflation
        self.income_tax_rate = income_tax_rate
        self.start_year = start_year
        self.n_years = n_years
        self.n_products = n_products
        self.growth_rate = growth_rate
        self.discount_rate = discount_rate
        self.currency = currency
        self.change_rate = change_rate
        self.turn_over = turn_over
        self.decimals = decimals
        self.tv=tv
        self.tv_method=tv_method
        if self.growth_rate >= self.discount_rate : raise "In the current model it is not foreseen that the Growth Rate is higher or equal to Discount Rate!"
        
        # internal functions to be applied to period of discoung and discounting factors
        list_years = [str(a) for a in range(start_year, start_year + n_years)]
        if tv == 1:
            list_years.append("TV")

        def func(n, cy):
            if n - cy < 0:
                return 0
            else:
                return n - cy + 0.5

        def disc_fact(rate, n):
            return 1 / ((1 + rate) ** n)

        self.Period_of_Discounting = pd.DataFrame(
            [[func(x, self.current_year) for x in range(self.start_year, self.start_year + self.n_years + tv)]],
            columns=list_years, index=['Period_of_Discounting'])
        self.Discounting_Factor = pd.DataFrame([[disc_fact(self.discount_rate, (func(x, self.current_year))) for x in
                                                 range(self.start_year, self.start_year + self.n_years + tv)]],
                                               columns=list_years, index=['Discounting_Factor'])
        self.Income_Tax_Rate = pd.DataFrame(self.income_tax_rate, columns=list_years, index=['Income_Tax_Rate%'])
        self.Inflation = pd.DataFrame(self.inflation, columns=list_years, index=['Inflation'])
        self.Change_Rate = pd.DataFrame(self.change_rate, columns=list_years,
                                        index=[f"Change_Rate {self.currency} / .."])
        self.Turnover = pd.DataFrame(self.turn_over, columns=list_years, index=['Turnover'])

        # self.period_of_discounting["TV"]=self.period_of_discounting[]

        # Tables creation
        self.Product_Table = pd.DataFrame(0, index=np.arange(self.n_products), columns=list_years)
        self.Product_Prices = pd.DataFrame(0, index=np.arange(self.n_products), columns=list_years)
        self.Revenues = pd.DataFrame(0, columns=list_years, index=['Revenues'])
        self.Raw_Materials_Quantities = pd.DataFrame(0, index=np.arange(self.n_raw_materials), columns=list_years)
        self.Raw_Materials_Costs = pd.DataFrame(0, columns=list_years, index=['Raw_Materials_Costs'])
        self.Raw_Materials_Prices = pd.DataFrame(0, index=np.arange(self.n_raw_materials), columns=list_years)
        self.Variable_Costs = pd.DataFrame(0, columns=list_years, index=['Variable_Costs'])
        self.HR_Costs = pd.DataFrame(0, columns=list_years, index=['HR_Costs'])
        self.Maintenance_Costs = pd.DataFrame(0, columns=list_years, index=['Maintenance_Costs'])
        self.Other_Fixed_Costs = pd.DataFrame(0, columns=list_years, index=['Other_Fixed_Costs'])
        self.Fixed_Costs = pd.DataFrame(0, columns=list_years, index=['Fixed_Costs'])
        self.Investments = pd.DataFrame(0, columns=list_years, index=['Investments'])
        self.Depreciations = pd.DataFrame(0, columns=list_years, index=['Depreciations'])
        self.FCF = pd.DataFrame(0, columns=list_years, index=['Free_Cash_Flow'])
        self.Net_Working_Capital = pd.DataFrame(0, columns=list_years, index=['Net_Working_Capital'])
        self.Changes_NWC = pd.DataFrame(0, columns=list_years, index=['Changes_In_Net_working_Capital'])
        self.DFCF = pd.DataFrame(0, columns=list_years, index=['Discounted_Cash_Flow'])

        self.update()  # it creates the PL tables.

    def update(self):
        self.update_fixed()
        self.update_variable()
        self.update_revenues()
        self.update_raw_materials()
        self.Operating = pd.concat([self.Revenues, self.Raw_Materials_Costs, self.Variable_Costs, self.Fixed_Costs])
        self.Ebitda = self.Operating.agg(['sum']).set_index([['EBITDA']])
        self.Ebit = self.operation_two_rows(self.Ebitda, self.Depreciations, "EBIT", "+")
        self.Income_Taxes = self.operation_two_rows(self.Ebit, self.income_tax_rate * (-1), "Income_Taxes", "*")
        self.Net_Income = self.operation_two_rows(self.Ebit, self.Income_Taxes, "Net_Income", "+")
        self.Net_Income.set_index([['Net_Income']])
        self.Net_Working_Capital = self.operation_two_rows(self.Revenues, self.Turnover, "Net_Working_Capital", "*")
        self.Changes_NWC = self.Net_Working_Capital - self.Net_Working_Capital.shift(1, axis=1)
        self.Changes_NWC.set_index([['Changes_NWC']])

        
        

        # table PL creation
        self.PL = pd.concat(
            [self.Revenues, self.Raw_Materials_Costs, self.Variable_Costs, self.Fixed_Costs, self.Ebitda,
             self.Depreciations, self.Ebit, self.Income_Taxes, self.Net_Income])
        self.PL_FCF = pd.concat(
            [self.Net_Income, self.Depreciations * (-1), self.Changes_NWC, self.Investments])
        self.FCF = self.PL_FCF.agg(['sum']).set_index([['FCF']]).round(decimals=self.decimals)

        self.DFCF = self.operation_two_rows(self.FCF, self.Discounting_Factor, "DFCF", "*")
        # other parameters
        self.Parameters = pd.concat(
            [self.Period_of_Discounting, self.Discounting_Factor, self.Income_Tax_Rate, self.Inflation, self.Turnover,
             self.Change_Rate])
        if self.tv==1:
            
            self.terminal_value_infinite=self.FCF['TV']/((self.discount_rate-self.growth_rate)*self.Discounting_Factor.iloc[0,-2])

    def update_fixed(self):
        self.Fixed_Costs = pd.concat([self.HR_Costs, self.Maintenance_Costs, self.Other_Fixed_Costs])
        self.Fixed_Costs_Sum = self.Fixed_Costs.agg(['sum']).set_index([['Fixed_Costs']])

    def update_raw_materials(self):
        self.Raw_Materials_Costs = (self.Raw_Materials_Quantities * self.Raw_Materials_Prices * (-1)).agg(
            ["sum"]).set_index([['Raw_Materials_Costs']])

    def update_variable(self):
        pass

    def update_revenues(self):
        self.Revenues = (self.Product_Prices * self.Product_Table).agg(["sum"]).set_index([['Revenues']])

    def compare(self, x, delta_params=True):
        # function to create a comparison (a difference) between two different plans
        y = copy.deepcopy(self)
        # callable= [a for a in dir(PL) if (not a.startswith("__") and not a.startswith("u"))]
        if self.n_years != x.n_years:
            raise "Error: the parameter n_years for the two Plans objects to be compared must have the same value!"
        # Tables
        y.Product_Table = self.Product_Table - x.Product_Table
        y.Product_Prices = self.Product_Prices - x.Product_Prices
        y.Revenues = self.Revenues - x.Revenues
        y.Raw_Material_Quantities = self.Raw_Materials_Quantities - x.Raw_Materials_Quantities
        y.Raw_Materials_Costs = self.Raw_Materials_Costs - x.Raw_Materials_Costs
        y.Raw_Materials_Prices = self.Raw_Materials_Prices - x.Raw_Materials_Prices
        y.Variable_Costs = self.Variable_Costs - x.Variable_Costs
        y.HR_Costs = self.HR_Costs - x.HR_Costs
        y.Maintenance_Costs = self.Maintenance_Costs - x.Maintenance_Costs
        y.Other_Fixed_Costs = self.Other_Fixed_Costs - x.Other_Fixed_Costs
        y.Fixed_Costs = self.Fixed_Costs - x.Fixed_Costs
        y.Investments = self.Investments - x.Investments
        y.Depreciations = self.Depreciations - x.Depreciations
        y.FCF = self.FCF - x.FCF
        y.Net_Working_Capital = self.Net_Working_Capital - x.Net_Working_Capital
        y.Changes_NWC = self.Changes_NWC - x.Changes_NWC
        y.DFCF = self.DFCF - x.DFCF
        y.PL = self.PL - x.PL

        # Other parameters and rates
        if delta_params==True:
            y.Period_of_Discounting = self.Period_of_Discounting - x.Period_of_Discounting
            y.Discounting_Factor = self.Discounting_Factor - x.Discounting_Factor
            y.Income_Tax_Rate = self.Income_Tax_Rate - x.Income_Tax_Rate
            y.Inflation = self.Inflation - x.Inflation
            y.Turnover = self.Turnover - x.Turnover
            y.Change_Rate=self.Change_Rate-x.Change_Rate
            if self.tv==1:
                y.terminal_value_infinite=self.terminal_value_infinite-x.terminal_value_infinite
            y.Parameters = pd.concat([y.Period_of_Discounting, y.Discounting_Factor, y.Income_Tax_Rate, y.Inflation, y.Turnover,
            y.Change_Rate])    
        else:
            y.Period_of_Discounting=x.Period_of_Discounting
            y.Discounting_Factor =  x.Discounting_Factor
            y.Income_Taxes =  x.Income_Taxes
            y.Inflation =  x.Inflation
            y.Turnover =  x.Turnover
            y.Change_Rate=x.Change_Rate
            y.update()
        #y.update  # this generates the calculation of the PL internally in y
        return y

    def operation_two_rows(self, x, y, index="sum", oper="+"):
        cols = x.columns
        data = np.array(x) + np.array(y)
        if oper == "+":
            data = np.array(x) + np.array(y)
            z = pd.DataFrame(data, columns=cols, index=[index])
        elif oper == "-":
            data = np.array(x) - np.array(y)
            z = pd.DataFrame(data, columns=cols, index=[index])
        elif oper == "*":
            data = np.array(x) * np.array(y)
            z = pd.DataFrame(data, columns=cols, index=[index])
        elif oper == "/":
            data = np.array(x) / np.array(y)
            z = pd.DataFrame(data, columns=cols, index=[index])
        else:
            raise f"Wrong operation : {oper} allowed only + - * / "
        return z

    def save(self, file):
        with pd.ExcelWriter(file) as writer:  
            self.PL.to_excel(writer, sheet_name='Profit_Loss')
            self.PL_FCF.to_excel(writer, sheet_name='Free_Cash_Flow')
            self.Parameters.to_excel(writer, sheet_name='Parameters')
            self.Product_Table.to_excel(writer, sheet_name='Product_Table')
            self.Product_Prices.to_excel(writer, sheet_name='Product_Prices')
            self.Raw_Materials_Quantities.to_excel(writer, sheet_name='Raw_Materials_Quantities')
            self.Raw_Materials_Prices.to_excel(writer, sheet_name='Raw_Materials_Prices')
    
    def load(self,file):        
 
        self.Product_Table=pd.read_excel(file,sheet_name='Product_Table',index_col=0,header=0)
        self.Product_Prices=pd.read_excel(file,sheet_name='Product_Prices',index_col=0,header=0)
        self.Raw_Materials_Quantities=pd.read_excel(file, sheet_name='Raw_Materials_Quantities',index_col=0,header=0)
        self.Raw_Materials_Prices=pd.read_excel(file, sheet_name='Raw_Materials_Prices',index_col=0,header=0)
        self.Parameters=pd.read_excel(file, sheet_name='Parameters',index_col=0,header=0)
    
