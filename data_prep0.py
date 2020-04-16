import argparse
import matplotlib.pyplot as plt
import geopandas as gpd
from geopandas.tools import sjoin
import pandas as pd
from shapely import wkt
from fiona.crs import from_epsg
from geopandas import GeoDataFrame
from shapely.geometry import Point
import fiona
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon
import numpy as np
import rasterio
from affine import Affine

parser = argparse.ArgumentParser(description='input file and output folder')
parser.add_argument('--input', metavar='S',type=str, 
                    help='tif file')
parser.add_argument('--output',metavar='S', type=str, 
                    help='output folder lcoation')

args = parser.parse_args()


#file_in = './SVDNB/2017/SVDNB_npp_20171101-20171130_75N060E_vcmcfg_v10_c201712040930/SVDNB_npp_20171101-20171130_75N060E_vcmcfg_v10_c201712040930.avg_rade9h.tif'
dataset = rasterio.open(args.input)
band1 = dataset.read(1)
print("shape of file",band1.shape)


column_list = []
longitude_list = []
latitude_list= []
for i in range(dataset.height):
    l1 =(dataset.transform * (0,i))[1]

    if l1<=36 and l1>= 8:
        column_list.append(i)
        latitude_list.append(l1)
row_list = []      
for j in range(dataset.height):
    l2 =(dataset.transform * (j,0))[0]
    if l2 <=96 and l2 >=68:
        row_list.append(j)
        longitude_list.append(l2)
                
longitude_list = np.array(longitude_list)
latitude_list = np.array(latitude_list)
print(len(column_list),len(row_list), len(longitude_list),len(latitude_list))

light = band1[row_list,:][:,column_list]
df = np.transpose([np.repeat(longitude_list, len(latitude_list)), 
              np.tile(latitude_list, len(longitude_list)),light.flatten()])
print(df.shape)

df = pd.DataFrame(df)
df.columns = ['longitude','latitude','NB']
op_name = args.output + "India_alldata.pickle"
df.to_pickle(op_name)

