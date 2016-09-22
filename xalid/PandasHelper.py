
import csv
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join
import PandasHelper as pdh

def get_files(path):
	return [f for f in listdir(path) if isfile(join(path, f))]


def string_to_np_array(x):
    
    list_str = x.replace("]["," ").replace("]","").replace("[","").replace(", "," ")
    lista =  (map(int,list_str.split()))
    return np.unique(np.asarray(lista))