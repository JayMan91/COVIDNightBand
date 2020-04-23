import pandas as pd
import numpy as np
import os
import glob

files = []
for file in glob.glob("CensusData/slums/*.xlsx"):
    files.append(file)

file_df =pd.DataFrame()
for file in files:
    sheet_name = 'Slum_'+ file[35:39]
    print("Sheet name {}, File name {}".format(sheet_name,file))
    df = pd.read_excel(open(file, 'rb'),
              sheet_name= sheet_name) 
    file_df = file_df.append(df,ignore_index=True)

file_df['Total Population of Town'] = file_df['Total Population of Town'].astype(float)

file_df_townaggregated = file_df.groupby(['State Code', 'State Name', 'District Code', 'District Name',
                'Sub District Code','Sub District Name',
                'Town Code','Town Name']).agg({'Total Population of Town':'mean',
                'Slum Population (approximate)':'sum'}).reset_index(drop = False)
file_df_districtaggregated = file_df_townaggregated.groupby(['State Code', 'State Name', 
	'District Code', 'District Name']).agg({'Total Population of Town':'sum',
         'Slum Population (approximate)':'sum'}).reset_index(drop = False)
file_df_districtaggregated.columns = ['State Code', 'State Name', 'District Code', 
'District Name','Population of Town','Slum Population']

districts_df = pd.read_csv("CensusData/Districts.csv")
districts_df = districts_df[['State Code', 'District Code','Name','Persons', 'Males', 'Females',
       'Area In sq. km', 'Population per sq. km.']]

slum_population = file_df_districtaggregated.merge(districts_df,on=['State Code',
	'District Code'])
slum_population.to_csv("DistrictwiseSlumandTotalPopulation.csv",index=False)
