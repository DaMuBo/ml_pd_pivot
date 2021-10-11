import sys
import os
import pandas as pd
import numpy as np
import pickle

class pivot_table:
    """
    Erzeugt ein Modell das eine Pivot Tabelle erzeugt und speichert und auch auf ein neues Datenset angewendet werden kann und dabei die gleiche Struktur als Output zurück gibt.
    """
    def __init__(self,df = None, columns = None, aggfunc = np.sum, c_group=None, c_pivot=None):
        """
        Initiale Parameter zuweisen für pivot_table klasse
        pivot = enthält das aggregierte dataframe
        columns = enthält die spaltenüberschriften in der richtigen reihenfolge
        aggfunc = enthält die Aggregationsfunktion. Standard = 'Sum'
        """
        self.df = df
        self.pivot = None
        self.columns = columns
        self.aggfunc = aggfunc
        self.c_group = c_group
        self.c_pivot = c_pivot
        
    def fit(self, df=None, c_group=None, c_pivot=None, aggrfunc=None):
        """
        Nimmt ein DF auf. c_group ist die spalte nach der gruppiert wird. aggfunc ist die funktion nach der Aggregiert wird.
        c_pivot ist die Spalte die pivotiert werden soll.
        """
        if df is not None:
            self.df = df
        if c_group is not None:
            self.c_group = c_group
        if c_pivot is not None:
            self.c_pivot = c_pivot
        if aggrfunc is not None:
            self.aggfunc = aggrfunc
        
        
        self.pivot = self.df.pivot_table(index=self.c_group, columns=self.c_pivot, aggfunc=self.aggfunc, fill_value=0)
        self.pivot.columns = [' '.join(col).strip() for col in self.pivot.columns.get_level_values(1)]
        self.pivot = self.pivot.reset_index(self.c_group)
        self.columns = self.pivot.columns
        return self.pivot
    
    def save_pivot(self,filename):
        """
        Speichert die Struktur der Pivot ab inkl. der Aggregat Funktion.
        """
        output = {
            'columns':self.columns
            , 'aggfunc':self.aggfunc
            , 'c_group':self.c_group
            , 'c_pivot':self.c_pivot
        }
        pickle.dump(output, open(filename, 'wb'))
        
    def load_pivot(self, link):
        """
        Lädt das Modell und baut das neue dataframe nach der geladenen Struktur um.
        """
        inputi = pickle.load(open(link, 'rb'))
        self.columns = inputi['columns']
        self.aggfunc = inputi['aggfunc']
        self.c_group = inputi['c_group']
        self.c_pivot = inputi['c_pivot']
        return self
    
    def transform(self, df):
        """
        Nimmt ein DF aufund transformiert es anhand der gelernten vorgaben
        """
        # erzeuge ein neues dataframe anhand der strukturen
        new_df = pd.DataFrame(columns=self.columns)
        
        # baue aus dem df ein pivot_table und spiele die daten nun zusammen
        df_pivot = df.pivot_table(index=self.c_group, columns=self.c_pivot, aggfunc=self.aggfunc, fill_value=0)
        df_pivot.columns = [' '.join(col).strip() for col in df_pivot.columns.get_level_values(1)]
        df_pivot = df_pivot.reset_index(self.c_group)
        
        # droppe falsche daten
        new_df = pd.concat([new_df, df_pivot], sort=False)
        columndrops = [x for x in df_pivot.columns if x not in self.columns]
        new_df = new_df.drop(columndrops, axis=1).fillna(0)
        
        self.pivot = new_df
        # Rückgabe des veränderten Objekts
        return self.pivot