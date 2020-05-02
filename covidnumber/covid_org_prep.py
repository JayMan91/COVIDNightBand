import pandas as pd
import numpy as np
import os
import glob
import urllib.request, json 
with urllib.request.urlopen("https://api.covid19india.org/v2/state_district_wise.json") as url:
    data = json.loads(url.read().decode())

def parse_covid(json_dict):
    n = len(json_dict)
    d = {}
    state_name = []
    state_code = []
    district_name = []
    active_list = []
    confirmed_list = []
    deceased_list = []
    recovered_list = []
    
    for i in range(n):
        #print(i,json_dict[i]['state'],len(json_dict[i]['districtData']))
        state_name = state_name + [json_dict[i]['state']]*len(json_dict[i]['districtData'])
        state_code = state_code + [json_dict[i]['statecode']]*len(json_dict[i]['districtData'])
        for j in range(len(json_dict[i]['districtData'])):
            district_json = json_dict[i]['districtData'][j]
            district_name.append(district_json['district'])
            active_list.append(district_json['active'])
            confirmed_list.append(district_json['confirmed'])
            deceased_list.append(district_json['deceased'])
            recovered_list.append(district_json['recovered'])
            
        
    d= {'state':state_name,'state_code':state_code,'district':district_name,
       'recovered':recovered_list,'deceased':deceased_list,'confirmed':confirmed_list,'active':active_list}
    return  pd.DataFrame.from_dict(d)
        
files = []
for file in glob.glob("../CensusData/slums/*.xlsx"):
    files.append(file)
print("number of states",len(files))
file_df =pd.DataFrame()
for file in files:
    sheet_name = 'Slum_'+ file[38:42]
    print("Sheet name {}, File name {}".format(sheet_name,file))
    df = pd.read_excel(open(file, 'rb'),
              sheet_name= sheet_name) 
    file_df = file_df.append(df,ignore_index=True)

file_df['Total Population of Town'] = file_df['Total Population of Town'].astype(float)
file_df_districtaggregated = file_df.groupby(['State Code', 
'District Code']).agg({'Slum Population (approximate)':'sum'}).reset_index(drop = False)
file_df_districtaggregated.columns = ['State Code', 'District Code', 
'Slum Population']

districts_df = pd.read_csv("../CensusData/Districts.csv")
state_code = pd.read_csv("../CensusData/statecode.csv")
districts_df = districts_df[['State Code', 'District Code','Name','Persons', 
       'Area In sq. km', 'Population per sq. km.']]
districts_df.rename(columns={'Persons':'District Population','Name':'District Name',}, inplace=True)
slum_df = districts_df.merge(file_df_districtaggregated,on=['State Code',
	'District Code'],how='left')

slum_df = slum_df.merge(state_code,on='State Code',how='left')

cols = list(slum_df.columns)
cols = cols[0:2] +cols[7:8]+cols[2:3]+cols[3:7]
slum_df = slum_df[cols]

slum_df['State Name'] = slum_df['State Name'].str.lower()
slum_df['District Name'] = slum_df['District Name'].str.lower()
slum_df['State Name'] =  slum_df['State Name'].str.strip()
slum_df['District Name'] =slum_df['District Name'].str.strip()

mapping = pd.read_csv("covid_mapping.csv")
mapping_state = mapping[mapping.level=="state"].drop(['level',
    'census_district','covid_district'], axis=1)
mapping_district = mapping[mapping.level=="district"].drop(['level'], axis=1)

covid_df = parse_covid(data)
covid_df['state'] = covid_df['state'].str.lower()
covid_df['district'] = covid_df['district'].str.lower()
covid_df['state'] =  covid_df['state'].str.strip()
covid_df['district'] = covid_df['district'].str.strip()
garbage_state = ['other state','unknown','other region','evacuees','italians']
covid_df = covid_df[~covid_df['district'].isin(garbage_state)]
covid_df = covid_df.merge(mapping_state,left_on='state',right_on='covid_state',
        how='left').rename(columns={'census_state':'State Name'}).drop(['covid_state'], axis=1)
covid_df['State Name'] = np.where(covid_df['State Name'].isnull(),
    covid_df['state'],covid_df['State Name'])
covid_df = covid_df.merge(mapping_district,left_on=['state',
    'district'],right_on=['covid_state','covid_district'],
        how='left').drop(['covid_state','census_state','covid_district'], 
        axis=1).rename(columns={'census_district':'District Name'})
covid_df['District Name'] = np.where(covid_df['District Name'].isnull(),
    covid_df['district'],covid_df['District Name'])



merged_df = slum_df.merge(covid_df,on=['State Name','District Name'],how='outer')
merged_df = merged_df.sort_values(by=['State Code',
    'District Code'])
merged_df.to_csv("jsoncovid.csv",index= False)