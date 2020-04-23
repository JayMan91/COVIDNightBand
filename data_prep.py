import argparse
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from shapely import wkt
from fiona.crs import from_epsg
import numpy as np
import fiona
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon

parser = argparse.ArgumentParser(description='input folder')
parser.add_argument('--input', metavar='S',type=str, 
                    help='folder name with /')


args = parser.parse_args()

input_file = args.input+"India_alldata.pickle"
df = pd.read_pickle(input_file)
print(df.shape)
## WB
df_wb = df[(df.latitude >21.5) & (df.latitude <27.3) &(df.longitude>85.7) &(df.longitude <89.8)]
del df
print(df_wb.shape)

## 1st approach
# df['geometry'] = "POINT("+df.longitude.map(str) + " " + df.latitude.map(str)+")"
# df['geometry'] = df['geometry'].apply(wkt.loads)
# gdf = gpd.GeoDataFrame(df, geometry='geometry')
## 2nd approach
gdf = gpd.GeoDataFrame(
    df_wb, geometry=gpd.points_from_xy(df_wb.longitude, df_wb.latitude))
gdf.crs = "epsg:4326"
## 3rd approach  
# geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
# df = df.drop(['longitude', 'latitude'], axis=1)
# crs = {'init': 'epsg:4326'}
# gdf = GeoDataFrame(df, crs=crs, geometry=geometry)
# df = df.drop(['longitude', 'latitude'], axis=1)
# crs = {'init': 'epsg:4326'}
# gdf = GeoDataFrame(df, crs=crs, geometry=geometry)
# 4th approch
# gdf_nodes = gpd.GeoDataFrame(df)
# gdf_nodes.crs ="epsg:4326"
# gdf_nodes['geometry'] = gdf_nodes.apply(lambda row: Point((row['longitude'], row['latitude'])), axis=1)


namp = gpd.read_file("maps-master/Districts/Census_2011/2011_Dist.shp")

# f, ax = plt.subplots(figsize=(30,30))
# namp.plot(ax=ax,color= "black")
# gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
# ax.set_axis_off()
# lims = plt.axis('equal')
# plt.savefig("wb.jpg")
# plt.show()
# points = gdf.iloc[0:10,:]
# cnt = 0
# for row in points.itertuples(index=True, name='Pandas'):
#     point = getattr(row, "geometry")
#     for row in namp.itertuples(index=True, name='Pandas'):
#         cnt+=1
#         geom = getattr(row, "geometry")
#         if point.within(shape(geom)):
#             print("OK",getattr(row, "NAME_1"))
#             break

gdf=  gpd.sjoin( gdf,namp, how="left", op='intersects')
gdf = gdf[gdf['DISTRICT'].notnull()]
gdf = gdf[gdf['ST_NM']=='West Bengal']
table_df = gdf.groupby(["DISTRICT"]).agg({"NB":['count',np.sum, 
	np.mean,np.std]}).reset_index()
table_df.columns = ['DISTRICT','count','sum','mean','std']
op_file = args.input+ "WB_table.pickle"
table_df.to_pickle(op_file)