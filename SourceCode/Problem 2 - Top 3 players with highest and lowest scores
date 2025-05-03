import pandas as pd
df = pd.read_csv('results.csv')

def dfclean(df, stats_col):
    df_cleaned = df.copy()
    for stats in stats_col:
        if stats in df_cleaned.columns:
            df_cleaned[stats] = pd.to_numeric(df_cleaned[stats], errors='coerce')
            df_cleaned[stats] = df_cleaned[stats].fillna(0)
    return df_cleaned

df = df.reset_index()

df = dfclean(df, df.columns[7:])

with open('top_3.txt', 'w', encoding='utf-8') as f:
    for stats in df.columns[7:]:
            
            other_colls=[ col for col in df.columns if col!=stats and col!='Name']
            display_colls=['Name', stats]+other_colls# create columns displayed in result like 'Name'-current stat-other cols( like 'Matches'-'Minutes'...)
            # Get top 3 highest and lowest
            top_high = df.nlargest(3, stats)[display_colls]
            top_low = df.nsmallest(3, stats)[display_colls]
            
            # Combine into one DataFrame
            combined = pd.concat([top_high.assign(Rank='Top'), top_low.assign(Rank='Bottom')])
            # Set columns width to prettify data when showing
            col_widths = {
                'Rank': 8,
                'Index': 10,
                'Name': 20,
                stats: 20, 
                'Nation': 12,
                'Team': 18,
                'Position': 15
            }
            # Create header to show in file txt
            header_parts = [
                f"{'Rank':<{col_widths['Rank']}}",
                f"{'Index':<{col_widths['Index']}}",
                f"{'Name':<{col_widths['Name']}}",
                f"{stats:<{col_widths[stats]}}",
                f"{'Nation':<{col_widths['Nation']}}",
                f"{'Team':<{col_widths['Team']}}",
                f"{'Position':<{col_widths['Position']}}"
            ]
            
            for col in other_colls[5:]:
                if col != stats:
                    col_widths[col] = 12 
                    header_parts.append(f"{col:<{col_widths[col]}}")
            
            headers = "".join(header_parts)
            f.write(headers + '\n')
            f.write('-' * len(headers) + '\n')
            print(headers)
            print('-' * len(headers))
            
            # Write rows
            for index, row in combined.iterrows():
                # Format stat value
                stat_value = f"{row[stats]:.1f}" if isinstance(row[stats], (int, float)) else str(row[stats])
                
                row_parts = [
                    f"{row['Rank']:<{col_widths['Rank']}}",
                    f"{row['index']:<{col_widths['Index']}}",
                    f"{str(row['Name'])[:col_widths['Name']]:<{col_widths['Name']}}",
                    f"{stat_value:<{col_widths[stats]}}",
                    f"{str(row['Nation'])[:col_widths['Nation']]:<{col_widths['Nation']}}",
                    f"{str(row['Team'])[:col_widths['Team']]:<{col_widths['Team']}}",
                    f"{str(row['Position'])[:col_widths['Position']]:<{col_widths['Position']}}"
                ]
                

                for col in other_colls[5:]:
                    if col != stats:
                        cell_value = str(row[col])[:col_widths[col]] 
                        row_parts.append(f"{cell_value:<{col_widths[col]}}")
                
                res = "".join(row_parts)
                f.write(res + '\n') 
                print(res)
            
            f.write('\n')
