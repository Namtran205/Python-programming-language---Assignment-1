import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import csv
import warnings
from tabulate import tabulate

pd.set_option('display.max_rows', None)   # Không giới hạn số dòng
pd.set_option('display.max_columns', None)  # Không giới hạn số cột
pd.set_option('display.width', None)       # Không giới hạn độ rộng
pd.set_option('display.max_colwidth', None)
warnings.filterwarnings("ignore")

def setup_driver():
    try:
        chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to setup driver: {e}")
        return None

def get_team_links(driver):
    try:
        print("Navigating to Premier League stats page...")
        driver.get("https://fbref.com/en/comps/9/Premier-League-Stats")
        
        print("Waiting for table to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.stats_table"))
        )
        
        print("Finding team links...")
        team_links = []
        table = driver.find_element(By.CSS_SELECTOR, "table.stats_table")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            try:
                team_cell = row.find_element(By.CSS_SELECTOR, "td[data-stat='team']")
                link = team_cell.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                if href and "squads" in href:
                    team_links.append(href)
                    print(f"Found team: {link.text} - {href}")
            except Exception:
                continue
        
        return team_links
    except Exception as e:
        print(f"Error getting team links: {e}")
        return []
# def get_team_links(driver):
#     driver.get('https://fbref.com/en/comps/9/Premier-League-Stats')
#     time.sleep(3)
#     table=driver.find_element(By.ID,'results2024-202591_overall')# Bnag chua doi bong
#     rows=table.find_elements(By.TAG_NAME,'tr')
#     team_links={}
#     for row in rows:
#             try:
#                 team_cell = row.find_element(By.XPATH, './/td[@data-stat="team"]/a')
#                 team_name = team_cell.text
#                 team_link = team_cell.get_attribute('href')
#                 team_links[team_name] = team_link
#             except:
#                 continue
#     print(f"Found {len(team_links)} team links")
#     return team_links

def safe_get_stat(row, stat_name, default="N/a"):
    selectors = [
        f"td[data-stat='{stat_name}']",  # Standard stat in <td>
        f"th[data-stat='{stat_name}']",  # Player name or header in <th>
        f"td.{stat_name}",               # Class-based fallback
        f"td[class*='{stat_name.lower()}']"  # Partial class match
    ]
    
    for selector in selectors:
        try:
            element = row.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            # Return default if text is empty, whitespace, or common null values
            if not text or text in ["", "-"]:
                return default
            return text
        except:
            continue
    
    return default

def scrape_team_data(driver, team_url):
    try:
        team_name = team_url.split('/')[-1].replace('-Stats', '')
        print(f"\nScraping team: {team_name}")
        
        driver.get(team_url)
        # time.sleep(3)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "stats_standard_9"))
            )
        except:
            print(f"Standard stats table not found for {team_name}")
            return []
        
        players = []
        # Dictionary to store all tables
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
        
        # Step 1: Get player list from Standard Stats
        standard_table = tables['standard']
        if not standard_table:
            return []
        
        player_rows = {}
        for row in standard_table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)"):
            try:
                if not row.find_elements(By.CSS_SELECTOR, "th[data-stat='player']"):
                    continue
                
                mins_text = safe_get_stat(row, "minutes", "0")
                mins = int(mins_text.replace(",", "")) if mins_text.replace(",", "").isdigit() else 0
                if mins <= 90:
                    continue
                
                player_name = row.find_element(By.CSS_SELECTOR, "th[data-stat='player']").text
                player_rows[player_name] = {
                    'Name': player_name,
                    'Nation': safe_get_stat(row, "nationality").split()[-1] if safe_get_stat(row, "nationality") != "N/a" else "N/a",
                    'Team': team_name,
                    'Position': safe_get_stat(row, "position"),
                    'Age': safe_get_stat(row, "age"),
                    'Matches': safe_get_stat(row, "games"),
                    'Starts': safe_get_stat(row, "games_starts"),
                    'Minutes': mins_text,
                    'Goals': safe_get_stat(row, "goals"),
                    'Assists': safe_get_stat(row, "assists"),
                    'Yellow Cards': safe_get_stat(row, "cards_yellow"),
                    'Red Cards': safe_get_stat(row, "cards_red"),
                    'Expected: xG': safe_get_stat(row, "xg"),
                    'Expected: xAG': safe_get_stat(row, "xg_assist"),
                    'PrgC': safe_get_stat(row, "progressive_carries"),
                    'Progression: PrgP': safe_get_stat(row, "progressive_passes"),
                    'Progression: PrgR': safe_get_stat(row, "progressive_passes_received"),
                    'Gls': safe_get_stat(row, "goals_per90"),
                    'Ast': safe_get_stat(row, "assists_per90"),
                    'xG per 90': safe_get_stat(row, "xg_per90"),
                    'xGA per 90': safe_get_stat(row, "xg_assist_per90"),
    #                 
                }
            except Exception as e:
                print(f"Error collecting standard stats for a player: {e}")
                continue
  
        for table_name, table in tables.items():
                if table_name == 'standard' or not table:
                    continue
                
                # Build mapping of players in this table
                table_players = {}
                try:
                    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)"):
                        try:
                            player_name = row.find_element(By.CSS_SELECTOR, "th[data-stat='player']").text.strip()
                            if player_name in player_rows:
                                table_players[player_name] = row
                        except:
                            continue
                except Exception as e:
                    print(f"Error reading rows from {table_name} table: {e}")
                
                # Assign stats for every player
                for player_name in player_rows:
                    try:
                        row = table_players.get(player_name)
                        if row:
                            if table_name == 'keeper':
                                player_rows[player_name].update({
                                    'GA90': safe_get_stat(row, 'gk_goals_against_per90'),
                                    'Save%': safe_get_stat(row, 'gk_save_pct'),
                                    'CS%': safe_get_stat(row, 'gk_clean_sheets_pct'),
                                    'PK Save%': safe_get_stat(row, 'gk_pens_save_pct'),
                                })
                            elif table_name == 'shooting':
                                player_rows[player_name].update({
                                    'SoT%': safe_get_stat(row, "shots_on_target_pct"),
                                    'SoT/90': safe_get_stat(row, "shots_on_target_per90"),
                                    'G/sh': safe_get_stat(row, "goals_per_shot"),
                                    'Dist': safe_get_stat(row, "average_shot_distance"),
                                })
                            elif table_name == 'passing':
                                player_rows[player_name].update({
                                    'Cmp': safe_get_stat(row, "passes_completed"),
                                    'Cmp%': safe_get_stat(row, "passes_pct"),
                                    'TotDist': safe_get_stat(row, "passes_total_distance"),
                                    'Short Cmp%': safe_get_stat(row, "passes_pct_short"),
                                    'Medium Cmp%': safe_get_stat(row, "passes_pct_medium"),
                                    'Long Cmp%': safe_get_stat(row, "passes_pct_long"),
                                    'KP': safe_get_stat(row, "assisted_shots"),
                                    'Passing: 1/3': safe_get_stat(row, "passes_into_final_third"),
                                    'PPA': safe_get_stat(row, "passes_into_penalty_area"),
                                    'CrsPA': safe_get_stat(row, "crosses_into_penalty_area"),
                                    'Passing: PrgP':safe_get_stat(row,'progressive_passes'),
                                })
                                
    
                            elif table_name == 'gca':
                                player_rows[player_name].update({
                                    'SCA': safe_get_stat(row, "sca"),
                                    'SCA90': safe_get_stat(row, "sca_per90"),
                                    'GCA': safe_get_stat(row, "gca"),
                                    'GCA90': safe_get_stat(row, "gca_per90"),
                                })
                            elif table_name == 'defense':
                                player_rows[player_name].update({
                                    'Tkl': safe_get_stat(row, "tackles"),
                                    'TklW': safe_get_stat(row, "tackles_won"),
                                    'Defensive: Att': safe_get_stat(row, "challenges"),
                                    'Defensive: Lost': safe_get_stat(row, "challenges_lost"),
                                    'Blocks': safe_get_stat(row, "blocks"),
                                    'Sh': safe_get_stat(row, "blocked_shots"),
                                    'Pass': safe_get_stat(row, "blocked_passes"),
                                    'Int': safe_get_stat(row, "interceptions"),
                                })
                            elif table_name == 'possession':
                                player_rows[player_name].update({
                                    'Touches': safe_get_stat(row, "touches"),
                                    'Def Pen': safe_get_stat(row, "touches_def_pen_area"),
                                    'Def 3rd': safe_get_stat(row, "touches_def_3rd"),
                                    'Mid 3rd': safe_get_stat(row, "touches_mid_3rd"),
                                    'Att 3rd': safe_get_stat(row, "touches_att_3rd"),
                                    'Att Pen': safe_get_stat(row, "touches_att_pen_area"),
                                    'Possession: Att': safe_get_stat(row, "take_ons"),
                                    'Succ%': safe_get_stat(row, "take_ons_won_pct"),
                                    'Tkld%': safe_get_stat(row, "take_ons_tackled_pct"),
                                    'Carries': safe_get_stat(row, "carries"),
                                    'ProDist': safe_get_stat(row, "carries_progressive_distance"),
                                    'ProgC': safe_get_stat(row,'progressive_carries'),
                                    'Possession: 1/3': safe_get_stat(row, 'carries_into_final_third'),
                                    'CPA': safe_get_stat(row, "carries_into_penalty_area"),
                                    'Mis': safe_get_stat(row, "miscontrols"),
                                    'Dis': safe_get_stat(row, "dispossessed"),
                                    'Rec': safe_get_stat(row, "passes_received"),
                                    'Posession: PrgR': safe_get_stat(row,'progressive_passes_received'),
                                })
                                
                            elif table_name == 'misc':
                                player_rows[player_name].update({
                                    'Fls': safe_get_stat(row, "fouls"),
                                    'Fld': safe_get_stat(row, "fouled"),
                                    'Off': safe_get_stat(row, "offsides"),
                                    'Crs': safe_get_stat(row, "crosses"),
                                    'Recov': safe_get_stat(row, "ball_recoveries"),
                                    'Won': safe_get_stat(row, "aerials_won"),
                                    'Mis: Lost': safe_get_stat(row, "aerials_lost"),
                                    'Won%': safe_get_stat(row, "aerials_won_pct"),
                                })
                        else:
                            
                            # Player not in table, assign N/a
                            if table_name == 'keeper':
                                player_rows[player_name].update({
                                    'GA90': "N/a",
                                    'Save%': "N/a",
                                    'CS%': "N/a",
                                    'PK Save%': "N/a",
                                })
                            elif table_name == 'shooting':
                                player_rows[player_name].update({
                                    'SoT%': "N/a",
                                    'SoT/90': "N/a",
                                    'G/sh': "N/a",
                                    'Dist': "N/a",
                                })
                            elif table_name == 'passing':
                                player_rows[player_name].update({
                                    'Cmp': "N/a",
                                    'Cmp%': "N/a",
                                    'TotDist': "N/a",
                                    'Short Cmp%': "N/a",
                                    'Medium Cmp%': "N/a",
                                    'Long Cmp%': "N/a",
                                    'KP': "N/a",
                                    'Passing: 1/3': "N/a",
                                    'PPA': "N/a",
                                    'CrsPA': "N/a",
                                    'Passing: PrgP': 'N/a',
                                })
                            elif table_name == 'gca':
                                player_rows[player_name].update({
                                    'SCA': "N/a",
                                    'SCA90': "N/a",
                                    'GCA': "N/a",
                                    'GCA90': "N/a",
                                })
                            elif table_name == 'defense':
                                player_rows[player_name].update({
                                    'Tkl': "N/a",
                                    'TklW': "N/a",
                                    'Defensive: Att': "N/a",
                                    'Defensive: Lost': "N/a",
                                    'Blocks': "N/a",
                                    'Sh': "N/a",
                                    'Pass': "N/a",
                                    'Int': "N/a",
                                })
                            elif table_name == 'possession':
                                player_rows[player_name].update({
                                    'Touches': "N/a",
                                    'Def Pen': "N/a",
                                    'Def 3rd': "N/a",
                                    'Mid 3rd': "N/a",
                                    'Att 3rd': "N/a",
                                    'Att Pen': "N/a",
                                    'Possession: Att': "N/a",
                                    'Succ%': "N/a",
                                    'Tkld%': "N/a",
                                    'Carries': "N/a",
                                    'ProDist': "N/a",
                                    'ProgC': 'N/aa',
                                    'Possession: 1/3': "N/a",
                                    'CPA': "N/a",
                                    'Mis': "N/a",
                                    'Dis': "N/a",
                                    'Rec': "N/a",
                                    'Posession: PrgR': 'N/a',
                                })
                                 
                            elif table_name == 'misc':
                                player_rows[player_name].update({
                                    'Fls': "N/a",
                                    'Fld': "N/a",
                                    'Off': "N/a",
                                    'Crs': "N/a",
                                    'Recov': "N/a",
                                    'Won': "N/a",
                                    'Mis: Lost': "N/a",
                                    'Won%': "N/a",
                                })
                    except Exception as e:
                        print(f"Error processing {table_name} stats for {player_name}: {e}")
            
            # Convert player_rows to list
        for player_data in player_rows.values():
            players.append(player_data)
        
        return players
        
    except Exception as e:
            print(f"Error scraping {team_name}: {e}")
            return []
    
def save_to_csv(data, filename="results.csv"):
    if not data:
        print("No data to save")
        return

    fields = [
        'Name', 'Nation', 'Team', 'Position', 'Age', 'Matches', 'Starts', 'Minutes',
        'Goals', 'Assists', 'Yellow Cards', 'Red Cards', 'Expected: xG', 'Expected: xAG', 'PrgC', 'Progression: PrgP', 'Progression: PrgR',
        'Gls', 'Ast', 'xG per 90', 'xGA per 90', 'GA90', 'Save%', 'CS%', 'PK Save%',
        'SoT%', 'SoT/90', 'G/sh', 'Dist', 'Cmp', 'Cmp%', 'TotDist',
        'Short Cmp%', 'Medium Cmp%', 'Long Cmp%', 'KP', 'Passing: 1/3', 'PPA', 'CrsPA','Passing: PrgP',
        'SCA', 'SCA90', 'GCA', 'GCA90', 'Tkl', 'TklW', 'Defensive: Att', 'Defensive: Lost', 'Blocks',
        'Sh', 'Pass', 'Int', 'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd',
        'Att Pen', 'Possession: Att', 'Succ%', 'Tkld%', 'Carries', 'ProDist', 'ProgC','Possession: 1/3',
        'CPA', 'Mis', 'Dis', 'Rec','Posession: PrgR', 'Fls', 'Fld', 'Off', 'Crs', 'Recov', 'Won', 'Mis: Lost', 'Won%'
    ]

    # Sort by first name (split by space and take first part)
    data_sorted = sorted(data, key=lambda x: x['Name'].split()[0])

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data_sorted)

    print(f"\nSuccessfully saved {len(data_sorted)} players to {filename}")

def main():
    print("Starting Premier League player data collection...")
    driver = setup_driver()
    
    if not driver:
        print("Failed to initialize WebDriver")
        return
    
    try:
        team_links = get_team_links(driver)
#         team_links= [
#     "https://fbref.com/en/squads/822bd0ba/2024-2025/Liverpool-Stats",
#     "https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats",
#     "https://fbref.com/en/squads/e4a775cb/2024-2025/Nottingham-Forest-Stats",
#     "https://fbref.com/en/squads/cff3d9bb/2024-2025/Chelsea-Stats",
#     "https://fbref.com/en/squads/b2b47a98/2024-2025/Newcastle-United-Stats",
#     "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats",
#     "https://fbref.com/en/squads/8602292d/2024-2025/Aston-Villa-Stats",
#     "https://fbref.com/en/squads/fd962109/2024-2025/Fulham-Stats",
#     "https://fbref.com/en/squads/d07537b9/2024-2025/Brighton-and-Hove-Albion-Stats",
#     "https://fbref.com/en/squads/4ba7cbea/2024-2025/Bournemouth-Stats",
#     "https://fbref.com/en/squads/47c64c55/2024-2025/Crystal-Palace-Stats",
#     "https://fbref.com/en/squads/cd051869/2024-2025/Brentford-Stats",
#     "https://fbref.com/en/squads/19538871/2024-2025/Manchester-United-Stats",
#     "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats",
#     "https://fbref.com/en/squads/d3fd31cc/2024-2025/Everton-Stats",
#     "https://fbref.com/en/squads/7c21e445/2024-2025/West-Ham-United-Stats",
#     "https://fbref.com/en/squads/8cec06e1/2024-2025/Wolverhampton-Wanderers-Stats",
#     'https://fbref.com/en/squads/b74092de/2024-2025/Ipswich-Town-Stats',
#     "https://fbref.com/en/squads/a2d435b3/2024-2025/Leicester-City-Stats",
#     "https://fbref.com/en/squads/33c895d4/2024-2025/Southampton-Stats"
# ]

        if not team_links:
            print("No team links found")
            return
        # all_players=scrape_team_data(driver,'https://fbref.com/en/squads/b74092de/2024-2025/Ipswich-Town-Stats')
        all_players = []
        for link in team_links:  # Process all teams
            team_players = scrape_team_data(driver, link)
            if team_players:
                all_players.extend(team_players)
            time.sleep(3)#5
        #  Delay to avoid rate limiting
       # Thay thế phần xử lý trống không hiệu quả bằng:
        for player in all_players:
            for key in player:
                if player[key] == '':
                    player[key] = 'N/a'
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
    ])

        # Cho phép in tất cả các cột
        pd.set_option('display.max_columns', None)

        # Không tự động xuống dòng khi in bảng rộng
        pd.set_option('display.width', 1000)

        # (Tùy chọn) Không rút gọn dữ liệu dài
        pd.set_option('display.max_colwidth', None)

        # In ra bảng đầy đủ
        if all_players:
            save_to_csv(all_players)
            print(df)

        
        #  df=pd.DataFrame(all_players)
        # Xem summary trước
        

        # Xem 10 dòng đầu với tất cả cột
        # Chia DataFrame thành các phần nhỏ
        

        # print(tabulate(df, headers='keys', tablefmt='pretty'))

        # if all_players:
        #     save_to_csv(all_players)
        #     print("\nSample data:")
        #     print(df)
        # else:
        #     print("No player data collected")
            
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        driver.quit()
        print("\nData collection completed")

if __name__ == "__main__":
    main()
