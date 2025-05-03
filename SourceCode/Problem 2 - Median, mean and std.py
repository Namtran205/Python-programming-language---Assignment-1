import pandas as pd
import numpy as np
df = pd.read_csv('results.csv')
def convert_age(age):
    try:
        if '-' in age:
            y, d = map(int, age.split('-'))
            return y + d / 365
        return int(age)
    except:
        return np.nan
df['Age'] = df['Age'].apply(convert_age)
def dfclean(df, stats_col):
    df_cleaned = df.copy()
    for stats in stats_col:
        if stats in df_cleaned.columns:
            df_cleaned[stats] = pd.to_numeric(df_cleaned[stats], errors='coerce')
            df_cleaned[stats] = df_cleaned[stats].fillna(0)
    return df_cleaned
# Keep index as column
df = df.reset_index()

df = dfclean(df, df.columns[6:])
team_names=[]
for  name in df['Team']:
    if not name in team_names:
        team_names.append(name)
team_names.sort()

results = []
# All players
all_stats = {
    '': 'all'
}

for stat in df.columns[6:]:

    all_stats[f'Median of {stat}'] = df[stat].median()
    all_stats[f'Mean of {stat}'] = df[stat].mean()
    all_stats[f'Std of {stat}'] = df[stat].std()
results.append(all_stats)

for team in team_names:
    df_team=df[df['Team']==team]
    data={'':f"{team}"}
    for stat in df.columns[6:]:
        data[f'Median of {stat}'] = df_team[stat].median()
        data[f'Mean of {stat}'] = df_team[stat].mean()
        data[f'Std of {stat}'] = df_team[stat].std()
    results.append(data)

m=pd.DataFrame(results,columns=[i for i in all_stats.keys()])
m.to_csv('results2.csv',index=True,encoding='utf-8-sig')


           



