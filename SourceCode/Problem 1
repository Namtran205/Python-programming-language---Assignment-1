import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def setup_driver():
    try:
        chrome_options = Options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to setup driver: {e}")
        return None


def get_team_links(driver):
    try:
        print("Getting team links...")
        driver.get("https://fbref.com/en/")
        team_links=[]
        table=driver.find_element(By.ID,'results2024-202591_overall')
        teams=table.find_elements(By.TAG_NAME,'a')
        for team in teams:
            team_links.append(team.get_attribute('href'))
        return team_links
   
    except Exception as e:
        print(f"Error getting team links: {e}")
        return []

def get_stat(row, stat_name):
# Get_stat function can help get statistic faster and return 'N/a' if stat didnt exist when finding stats on each table
  try:
      element = row.find_element(By.CSS_SELECTOR, f"td[data-stat='{stat_name}']")
      text = element.text.strip()
      if not text:
          return 'N/a'
      return text
  except:
      return 'N/a'

def scrape_team_data(driver, team_url):
    try:
        team_name = team_url.split('/')[-1].replace('-Stats', '')
        print(f"\nScraping team: {team_name}:{team_url}")
        
        driver.get(team_url)
        time.sleep(2)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "stats_standard_9"))
            )
        except:
            print(f"Standard table not found for {team_name}")
            return []
        
        players = []# players will return player data 
        # Create a dictionary to store all tables
        tables = {
            'standard': driver.find_element(By.ID, "stats_standard_9") if driver.find_elements(By.ID, "stats_standard_9") else None,
            'keeper': driver.find_element(By.ID, "stats_keeper_9") if driver.find_elements(By.ID, "stats_keeper_9") else None,
            'shooting': driver.find_element(By.ID, "stats_shooting_9") if driver.find_elements(By.ID, "stats_shooting_9") else None,
            'passing': driver.find_element(By.ID, "stats_passing_9") if driver.find_elements(By.ID, "stats_passing_9") else None,
            'gca': driver.find_element(By.ID, "stats_gca_9") if driver.find_elements(By.ID, "stats_gca_9") else None,
            'defense': driver.find_element(By.ID, "stats_defense_9") if driver.find_elements(By.ID, "stats_defense_9") else None,
            'possession': driver.find_element(By.ID, "stats_possession_9") if driver.find_elements(By.ID, "stats_possession_9") else None,
            'misc': driver.find_element(By.ID, "stats_misc_9") if driver.find_elements(By.ID, "stats_misc_9") else None
        }
        
        # Firstly, Get player list from Standard Stats
        standard_table = tables['standard']
        if not standard_table:
            return []
        
        player_rows = {}
        for row in standard_table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)"):
            try:
                if not row.find_elements(By.CSS_SELECTOR, "th[data-stat='player']"):
                    continue
                
                mins_text = get_stat(row, "minutes")
                mins = int(mins_text.replace(",", "")) if mins_text.replace(",", "").isdigit() else 0
                if mins <= 90:
                    continue
                
                player_name = row.find_element(By.CSS_SELECTOR, "th[data-stat='player']").text
                player_rows[player_name] = {
                    'Name': player_name,
                    'Nation': get_stat(row, "nationality").split()[-1] if get_stat(row, "nationality") != "N/a" else "N/a",
                    'Team': team_name,
                    'Position': get_stat(row, "position"),
                    'Age': get_stat(row, "age"),
                    'Matches': get_stat(row, "games"),
                    'Starts': get_stat(row, "games_starts"),
                    'Minutes': mins_text,
                    'Goals': get_stat(row, "goals"),
                    'Assists': get_stat(row, "assists"),
                    'Yellow Cards': get_stat(row, "cards_yellow"),
                    'Red Cards': get_stat(row, "cards_red"),
                    'Expected: xG': get_stat(row, "xg"),
                    'Expected: xAG': get_stat(row, "xg_assist"),
                    'PrgC': get_stat(row, "progressive_carries"),
                    'Progression: PrgP': get_stat(row, "progressive_passes"),
                    'Progression: PrgR': get_stat(row, "progressive_passes_received"),
                    'Gls': get_stat(row, "goals_per90"),
                    'Ast': get_stat(row, "assists_per90"),
                    'xG per 90': get_stat(row, "xg_per90"),
                    'xGA per 90': get_stat(row, "xg_assist_per90"),
    #                 
                }
            except Exception as e:
                print(f"Error collecting standard stats for a player: {e}")
                continue
  
        for table_name, table in tables.items():
                if table_name == 'standard' or not table:
                    continue
                # Build mapping of players in this table
                try:
                    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)"):
                      try:
                          player_name = row.find_element(By.CSS_SELECTOR, "th[data-stat='player']").text.strip()
                          if player_name in player_rows:
                            # Process each table to take statistics 
                            if table_name == 'keeper':
                                player_rows[player_name].update({
                                    'GA90': get_stat(row, 'gk_goals_against_per90'),
                                    'Save%':get_stat(row, 'gk_save_pct'),
                                    'CS%': get_stat(row, 'gk_clean_sheets_pct'),
                                    'PK Save%': get_stat(row, 'gk_pens_save_pct'),
                                })
                            elif table_name == 'shooting':
                                player_rows[player_name].update({
                                    'SoT%': get_stat(row, "shots_on_target_pct"),
                                    'SoT/90': get_stat(row, "shots_on_target_per90"),
                                    'G/sh': get_stat(row, "goals_per_shot"),
                                    'Dist': get_stat(row, "average_shot_distance"),
                                })
                            elif table_name == 'passing':
                                player_rows[player_name].update({
                                    'Cmp': get_stat(row, "passes_completed"),
                                    'Cmp%': get_stat(row, "passes_pct"),
                                    'TotDist': get_stat(row, "passes_total_distance"),
                                    'Short Cmp%': get_stat(row, "passes_pct_short"),
                                    'Medium Cmp%': get_stat(row, "passes_pct_medium"),
                                    'Long Cmp%': get_stat(row, "passes_pct_long"),
                                    'KP': get_stat(row, "assisted_shots"),
                                    'Passing: 1/3': get_stat(row, "passes_into_final_third"),
                                    'PPA': get_stat(row, "passes_into_penalty_area"),
                                    'CrsPA': get_stat(row, "crosses_into_penalty_area"),
                                    'Passing: PrgP':get_stat(row,'progressive_passes'),
                                })
    
                            elif table_name == 'gca':
                                player_rows[player_name].update({
                                    'SCA': get_stat(row, "sca"),
                                    'SCA90': get_stat(row, "sca_per90"),
                                    'GCA': get_stat(row, "gca"),
                                    'GCA90': get_stat(row, "gca_per90"),
                                })
                            elif table_name == 'defense':
                                player_rows[player_name].update({
                                    'Tkl': get_stat(row, "tackles"),
                                    'TklW': get_stat(row, "tackles_won"),
                                    'Defensive: Att': get_stat(row, "challenges"),
                                    'Defensive: Lost': get_stat(row, "challenges_lost"),
                                    'Blocks': get_stat(row, "blocks"),
                                    'Sh': get_stat(row, "blocked_shots"),
                                    'Pass': get_stat(row, "blocked_passes"),
                                    'Int': get_stat(row, "interceptions"),
                                })
                            elif table_name == 'possession':
                                player_rows[player_name].update({
                                    'Touches':get_stat(row, "touches"),
                                    'Def Pen': get_stat(row, "touches_def_pen_area"),
                                    'Def 3rd': get_stat(row, "touches_def_3rd"),
                                    'Mid 3rd':get_stat(row, "touches_mid_3rd"),
                                    'Att 3rd': get_stat(row, "touches_att_3rd"),
                                    'Att Pen': get_stat(row, "touches_att_pen_area"),
                                    'Possession: Att':get_stat(row, "take_ons"),
                                    'Succ%': get_stat(row, "take_ons_won_pct"),
                                    'Tkld%': get_stat(row, "take_ons_tackled_pct"),
                                    'Carries': get_stat(row, "carries"),
                                    'ProDist': get_stat(row, "carries_progressive_distance"),
                                    'ProgC': get_stat(row,'progressive_carries'),
                                    'Possession: 1/3': get_stat(row, 'carries_into_final_third'),
                                    'CPA': get_stat(row, "carries_into_penalty_area"),
                                    'Mis': get_stat(row, "miscontrols"),
                                    'Dis': get_stat(row, "dispossessed"),
                                    'Rec': get_stat(row, "passes_received"),
                                    'Posession: PrgR': get_stat(row,'progressive_passes_received'),
                                })
                                
                            elif table_name == 'misc':
                                player_rows[player_name].update({
                                    'Fls': get_stat(row, "fouls"),
                                    'Fld': get_stat(row, "fouled"),
                                    'Off': get_stat(row, "offsides"),
                                    'Crs': get_stat(row, "crosses"),
                                    'Recov': get_stat(row, "ball_recoveries"),
                                    'Won': get_stat(row, "aerials_won"),
                                    'Mis: Lost': get_stat(row, "aerials_lost"),
                                    'Won%': get_stat(row, "aerials_won_pct"),
                                })
                      except Exception as e:
                        print(f"Error processing {table_name} stats for {player_name}: {e}")
                        # else:
                except Exception as e:
                    print(f"Error reading rows from {table_name} table: {e}")

            # Convert player_rows to list
        for player_data in player_rows.values():
            players.append(player_data)
        
        return players       
    except Exception as e:
            print(f"Error scraping {team_name}: {e}")
            return []
  
def main():
    print("Starting Premier League player data collection...")
    driver = setup_driver()
    
    if not driver:
        print("Failed to initialize WebDriver")
        return  
    try:
        team_links = get_team_links(driver)

        if not team_links:
            print("No team links found")
            return

        all_players = []
        for link in team_links: 
            team_players = scrape_team_data(driver, link)
            if team_players:
                all_players.extend(team_players)
            time.sleep(2)

        data_sorted = sorted(all_players, key=lambda x: x['Name'])
        df=pd.DataFrame(data_sorted,columns=[
        'Name', 'Nation', 'Team', 'Position', 'Age', 'Matches', 'Starts', 'Minutes',
        'Goals', 'Assists', 'Yellow Cards', 'Red Cards', 'Expected: xG', 'Expected: xAG', 'PrgC', 'Progression: PrgP', 'Progression: PrgR',
        'Gls', 'Ast', 'xG per 90', 'xGA per 90', 'GA90', 'Save%', 'CS%', 'PK Save%',
        'SoT%', 'SoT/90', 'G/sh', 'Dist', 'Cmp', 'Cmp%', 'TotDist',
        'Short Cmp%', 'Medium Cmp%', 'Long Cmp%', 'KP', 'Passing: 1/3', 'PPA', 'CrsPA','Passing: PrgP',
        'SCA', 'SCA90', 'GCA', 'GCA90', 'Tkl', 'TklW', 'Defensive: Att', 'Defensive: Lost', 'Blocks',
        'Sh', 'Pass', 'Int', 'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd',
        'Att Pen', 'Possession: Att', 'Succ%', 'Tkld%', 'Carries', 'ProDist', 'ProgC','Possession: 1/3',
        'CPA', 'Mis', 'Dis', 'Rec','Posession: PrgR', 'Fls', 'Fld', 'Off', 'Crs', 'Recov', 'Won', 'Mis: Lost', 'Won%'
    ])# Create Dataframe form player data with the above columns 
        df.fillna('N/a',inplace=True)
        df.to_csv('results.csv',index=True,encoding='utf-8')
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        driver.quit()
        print("\nData collection completed")

if __name__ == "__main__":
    main()
