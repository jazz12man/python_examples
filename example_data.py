
#import packages
import pandas as pd
import matplotlib.pyplot as plt

#read file in as data frame 
#path = 'J:/Data/HRE/SHARED/BI&A Team/TWDS ROI SECOND GENERATION Q1FY12/Automation/Python/'
path = 'C:/Users/vauga026/Desktop/'
file = 'example_data.csv'

csvReader = csv.DictReader(open(path+file), delimiter=',', quotechar='"')
data_in = [row for row in csvReader]
tv_camp = [c['value'].strip() for c in data_in if c['Media'].strip() != 'TV'
            and c['Type'].strip() != 'Camp']



df = pd.read_csv(path+file)
print df


#extract relevant data (use '.ix' to index a DataFrame)
tv_camp = df.ix[(df['Media']=='TV')&(df['Type']=='Camp'),'value']
print tv_camp

tv_sim = df.ix[(df['Media']=='TV')&(df['Type']=='Sim'),'value']
print tv_camp

dig_camp = df.ix[(df['Media']=='Dig') & (df['Type']=='Camp'),'value']
print dig_camp

dig_sim = df.ix[(df['Media']=='Dig') & (df['Type']=='Sim'),'value']
print dig_sim

#plot 
plt.plot(range(len(tv_camp)),tv_camp,color='red',linestyle='-')
plt.plot(range(len(tv_sim)),tv_sim,color='red',linestyle=':')
plt.plot(range(len(dig_camp)),dig_camp,color='blue',linestyle='-')
plt.plot(range(len(dig_sim)),dig_sim,color='blue',linestyle=':')

#write data
tv_camp.to_csv(path+'tv_camp.csv')
tv_camp.to_csv(path+'tv_sim.csv')
tv_camp.to_csv(path+'dig_camp.csv')
tv_camp.to_csv(path+'dig_camp.csv')

