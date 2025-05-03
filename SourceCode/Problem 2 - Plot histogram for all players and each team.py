import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
df = pd.read_csv("results.csv")
def convert_age(age):
    try:
        if '-' in age:
            y, d = map(int, age.split('-'))
            return y + d / 365
        return int(age)
    except:
        return np.nan

def dfclean(df):
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.replace("N/a", 0)
    return df_cleaned

# Clean DataFrame
df = dfclean(df)
df['Age'] = df['Age'].apply(convert_age)
df['Minutes']=df['Minutes'].str.replace(',','')
df['Minutes']=pd.to_numeric(df['Minutes'],errors='coerce')

if not os.path.exists('Statistics_for_all_players'):
    os.makedirs('Statistics_for_all_players')
if not os.path.exists('Statistics_for_each_team'):
    os.makedirs('Statistics_for_each_team')
atk_def=["SoT/90","G/sh","KP","Tkl","Blocks","Int"]

#===== Part 1: SAVE EACH HISTOGRAM FOR ALL PLAYERS =====

for stat in atk_def:
    stat_name=stat.replace("/", "_").replace(":", "_").replace(" ", "_")
    data = pd.to_numeric(df[stat], errors='coerce').dropna()
    unique_values = data.nunique()
    bins = min(30, unique_values) if unique_values > 1 else 10
    sns.histplot(data,kde=True,bins=bins)
    plt.title(f"Histogram of {stat} for all players")
    plt.ylabel('Frequency')
    plt.xlabel(stat)
    plt.grid(True, alpha=0.3)
    print(f"Histogram of {stat_name} for all players is saved")
    plt.savefig(os.path.join('Statistics_for_all_players',f"{stat_name}.png"))
    plt.show()
    plt.close()

#===== PART 2: SAVE 1 COMBINED HISTOGRAM FOR ALL PLAYERS =====

plt.figure(figsize=(15,10))
for i, stat in enumerate(atk_def,1):
    plt.subplot(2,3,i)
    data=pd.to_numeric(df[stat],errors='coerce').dropna()
    sns.histplot(data,bins=25,kde=True)
    plt.title(f"Histogram of {stat} for all players")
    plt.xlabel(stat)
    plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig(os.path.join('Statistics_for_all_players',f"A combined histogram for all stats.png"))
plt.show()
plt.close()


#===== PART 3: SAVE EACH HISTOGRAM FOR EACH TEAM =====

df_team=df['Team'].unique()
for team in df_team:
    daf=df[df['Team']==team]
    plt.figure(figsize=(15,10))
    for i,stat in enumerate(atk_def,1):
        stat_name=stat.replace("/", "_").replace(":", "_").replace(" ", "_")
        data=pd.to_numeric(daf[stat],errors='coerce').dropna()
        plt.subplot(2,3,i)
        sns.histplot(data,bins=20,kde=True)
        plt.title(f"{team}")
        plt.xlabel(stat)
        plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join('Statistics_for_each_team',f"Histogram for {team}.png"))
    plt.show()
