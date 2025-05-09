import pandas as pd
import os
source_file=r'C:\Users\Admin\OneDrive\Python\Problem 2 - Identify the team with the highest score foe each statistic.py'
destination_folder = r'C:\Users\Admin\OneDrive\Python\SourceCode'
destination_file = os.path.join(destination_folder, os.path.basename(source_file))
if os.path.exists(source_file):
    os.makedirs(destination_folder, exist_ok=True)
    os.rename(source_file, destination_file)

df = pd.read_csv('results2.csv')
df = df.rename(columns={df.columns[1]: 'Team'}) 
df = df[df['Team'] != 'all']  
results = []
team_counts = {} 

for stat in df.columns:
    if stat == 'Team':
        continue

    stat_parts = stat.split(' of ')
    stat_type = stat_parts[0] if len(stat_parts) > 1 else 'Value'
    stat_name = stat_parts[1] if len(stat_parts) > 1 else stat
    
    # Find top performers
    highest_val = df[stat].max()
    highest_teams = df[df[stat] == highest_val]['Team'].tolist()

    results.append({
        'Statistic': stat_name.strip(),
        'Type': stat_type.strip(),
        'Top Teams': ', '.join(highest_teams),
        'Score': highest_val    
    })
    
    # Update team counts 
    for team in highest_teams:
        team_counts[team] = team_counts.get(team, 0) + 1


max_count = max(team_counts.values())
best_teams = [team for team, count in team_counts.items() if count == max_count]

res = pd.DataFrame(results).sort_values(['Statistic', 'Type'])
res.to_csv('Best_teams_stats.csv', index=False)

print("STATISTICAL LEADERS:")
print(res.to_string(index=False))
print("\nTEAM DOMINANCE COUNT:")
print(pd.Series(team_counts).sort_values(ascending=False).to_string())
print(f"\nCONCLUSION: The best-performing team(s) is/are: {', '.join(best_teams)}")
print(f"Leading in {max_count} out of {len(df.columns)-1} statistics")
