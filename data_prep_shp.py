import argparse
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from shapely import wkt
from fiona.crs import from_epsg
import numpy as np
import fiona
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.colors as colors
namp = gpd.read_file("maps-master/Districts/Census_2011/2011_Dist.shp")
namp['ST_NM'] = namp['ST_NM'].str.lower()
namp['DISTRICT'] = namp['DISTRICT'].str.lower()
namp['ST_NM'] =  namp['ST_NM'].str.strip()
namp['ST_NM'] = namp['ST_NM'].str.strip()

urban_df = pd.read_csv("Covid_Bayer_Urbanization.csv")
slum_df = pd.read_csv("DistrictwiseSlumandTotalPopulation.csv")
urban_df['State Name'] =  urban_df['State Name'].str.strip()
urban_df['District Name'] = urban_df['District Name'].str.strip()
urban_df['State Name'] = urban_df['State Name'].str.lower()
urban_df['District Name'] = urban_df['District Name'].str.lower()
slum_df['State Name'] = slum_df['State Name'].str.lower()
slum_df['District Name'] = slum_df['District Name'].str.lower()
slum_df['State Name'] =  slum_df['State Name'].str.strip()
slum_df['District Name'] =slum_df['District Name'].str.strip()
slum_df= slum_df[['State Code', 'State Name', 'District Code',
'District Name','Population of Town',
       'Slum Population','Population per sq. km.']]
covid = urban_df.merge(slum_df,on=['State Name','District Name'],how='left')
covid = covid.iloc[:,[33,34,35,36,37,38,39,17,21,22,23,24,25]]
#covid.to_csv("preshpmerge.csv",index=False)
#covid['density rank' ] = covid['Population per sq. km.'].rank(ascending=False,method = 'max')
covid = pd.read_csv("preshpmerge.csv")
name_change= pd.read_csv("shp_namechange.csv")
covid['District Name'].replace(name_change.old.tolist(),
name_change.new.tolist(),inplace=True)
covid['District Name'] = covid['District Name'].str.strip()
covid['District Name'] = covid['District Name'].str.lower()
covid_shp = covid.merge(namp,left_on=['State Code', 'District Name'],
                                  right_on=['ST_CEN_CD','DISTRICT'],how='outer')

covid_shp['Slum Proportion'] = covid_shp['Slum Population']/covid_shp['Total Population']
covid_shp.to_csv("shp_districts.csv")
covid_shp = gpd.GeoDataFrame(covid_shp)

# bins = [0.0, 0.25, 0.5, 0.75, 1.0]
# covid_shp[['covidcount','Population per sq. km.',
#           "Slum Population","Urban_Proportion"]] = covid_shp[['covidcount','Population per sq. km.',
#           "Slum Population","Urban_Proportion"]].apply(lambda s:pd.qcut(s, bins, bins[1:]).astype(float))

# cmap = colors.ListedColormap([ "rosybrown", "indianred","orangered","firebrick", "red"],N=5)
# norm = BoundaryNorm([0, 0.2, 0.4, 0.6,0.8,1], cmap.N)

# f, ax = plt.subplots(figsize=(30,30))
# covid_shp.plot(ax=ax,column="covidcount",legend=True,#cmap = GnRd,
#                #cmap=plt.cm.get_cmap(GnRd, 4),
#                cmap=cmap,norm=norm,
#                missing_kwds={'color': 'lightgrey',"label": "Missing values"})

# #gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
# ax.set_axis_off()
# lims = plt.axis('equal')
# plt.title('Covid Number',fontsize=36)
# plt.savefig("COVID.jpg")
# plt.show()

# f, ax = plt.subplots(figsize=(30,30))
# covid_shp.plot(ax=ax,column="Slum Population",legend=True,cmap=cmap,norm=norm,
#                missing_kwds={'color': 'lightgrey'})
# #gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
# ax.set_axis_off()
# lims = plt.axis('equal')
# plt.title('Slum Population',fontsize=36)
# plt.savefig("slum.jpg")
# plt.show()

# f, ax = plt.subplots(figsize=(30,30))
# covid_shp.plot(ax=ax,column="Urban_Proportion",legend=True,cmap=cmap,norm=norm,
#                missing_kwds={'color': 'lightgrey'})
# #gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
# ax.set_axis_off()
# lims = plt.axis('equal')
# plt.title('Urbanization',fontsize=36)
# plt.savefig("Urbanization.jpg")
# plt.show()
#covid_shp['covidcount'] = covid_shp['covidcount'].astype('Int64')

print(np.nanquantile(covid_shp.covidcount, [0.2,0.4,0.6,0.8]))
print(np.nanquantile(covid_shp['Slum Proportion'] ,[0.2,0.4,0.6,0.8]))
cmap = colors.ListedColormap(["darkorange", "rosybrown", "lightcoral",
	"maroon", "red"],N=5)
f, ax = plt.subplots(figsize=(30,30))
covid_shp.plot(ax=ax,column="covidcount",legend=True,scheme="Quantiles",
               #cmap=plt.cm.get_cmap(GnRd, 4),
               #cmap=cmap,norm=norm,
               cmap=cmap,
               missing_kwds={'color': 'lightgrey',"label": "Insignificant COVID"})

#gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
ax.set_axis_off()
lims = plt.axis('equal')
plt.title('Covid Number',fontsize=36)
plt.savefig("COVID.jpg")
plt.show()

f, ax = plt.subplots(figsize=(30,30))
covid_shp.plot(ax=ax,column="Slum Proportion",legend=True,scheme="quantiles",
               #cmap=plt.cm.get_cmap(GnRd, 4),
               #cmap=cmap,norm=norm,
               cmap=cmap,
               missing_kwds={'color': 'lightgrey',"label": "Insignificant COVID"})

#gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
ax.set_axis_off()
lims = plt.axis('equal')
plt.title('Slum Population',fontsize=36)
plt.savefig("slum.jpg")
plt.show()

f, ax = plt.subplots(figsize=(30,30))
covid_shp.plot(ax=ax,column="Urban_Proportion",legend=True,scheme="quantiles",
               #cmap=plt.cm.get_cmap(GnRd, 4),
               #cmap=cmap,norm=norm,
               cmap=cmap,
               missing_kwds={'color': 'lightgrey',"label": "Insignificant COVID"})

#gdf.plot(ax=ax, column= "NB",legend=True,cmap = 'Wistia')
ax.set_axis_off()
lims = plt.axis('equal')
plt.title('Urbanization',fontsize=36)
plt.savefig("Urbanization.jpg")
plt.show()

