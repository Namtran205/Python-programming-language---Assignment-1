from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
Base_url = 'https://www.footballtransfers.com/us'
def load_players():
    try:
        df = pd.read_csv('results.csv')
        df['Minutes'] = df['Minutes'].str.replace(',', '')
        df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce')
        df = df[df['Minutes'] > 900].reset_index(drop=True)
        df = df.drop(columns=['Unnamed: 0'], errors='ignore')
        return list(df['Name'])
    except Exception as e:
        print(f"Error loading players: {e}")
        return []

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

def get_premier_league_link(driver):
    try:
        pl_tag=driver.find_element(By.CSS_SELECTOR,"a[title='Premier League']")
        if not pl_tag:
            raise Exception("Premier League link not found.")
        
        return f"{pl_tag.get_attribute('href')}/2024-2025"
    except Exception as e:
        print(f"Error getting Premier League link:{e}")

def get_valued_players_link(driver, pl_link):
    try:
        driver.get(pl_link)
        time.sleep(3)
        valued_tag=driver.find_element(By.CSS_SELECTOR,"a[title='View all valued players']")
        if not valued_tag:
            raise Exception("All valued players link not found.")
        
        return valued_tag.get_attribute('href')
    except Exception as e:
        print(f"Error getting valued players link: {e}")


def scrape_player_values(driver, all_players, all_valued_players_link):
    matched_players = []
    
    for page in range(1, 23):
            try:
                url = f"{all_valued_players_link}/{page}"
                driver.get(url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover.no-cursor.table-striped.leaguetable.mvp-table.mb-0"))
                )
                rows = driver.find_elements(By.CSS_SELECTOR, "table.table-hover.no-cursor.table-striped.leaguetable.mvp-table.mb-0 tbody#player-table-body tr")

                print(f"Found {len(rows)} rows on page {page}")
                time.sleep(2)
                for row in rows:
                    try:
                        td_player = row.find_element(By.CSS_SELECTOR,"td[class='td-player']")
                        if not td_player:
                            continue
                        
                        name_tag = td_player.find_element(By.TAG_NAME,'a') 
                        if not name_tag:
                            continue
                        
                        player_name = name_tag.text.strip()
                        
                        if player_name in all_players:
                            value_tag = row.find_element(By.CSS_SELECTOR,"span[class='player-tag']")
                            transfer_value = value_tag.text.strip() if value_tag else "N/A"
                            
                            print(f"Found {player_name}: {transfer_value}")
                            matched_players.append({"Name": player_name, "Value": transfer_value})
                        else:
                            print(f" {player_name} not found in list")
                    
                    except Exception as e:
                        print(f"Error processing row: {e}")

            except Exception as e:
                print(f"Error on page {page}: {e}")

    return matched_players

def search_missing_players(driver, player_name):
    try:
        # Wait for seach box to find and search player name
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']"))
        )
        search_box.clear()

        for char in player_name:
            search_box.send_keys(char)
            time.sleep(0.2)

        time.sleep(3)
        results = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.searchResults a.newItem.player"))
        )
        # After getting result table, I'll find value by getting value of the first player in the result table
        if results:
            value = results[0].find_element(By.CSS_SELECTOR, "div.pl_value").text
            print(f"Found {player_name} with {value}")
            return value
        else:
            print(f"Not found {player_name} in the result")
            return "Not found"
    
    except Exception as e:
        print(f"Error when searching {player_name}: {e}")
        return 'Not found'
def normalize_value(value):
    if not isinstance(value, str):
        return 0.0
    try:
        value = value.replace('€', '').replace('M', '').replace(',', '').strip()
        return float(value) if value else 0.0
    except:
        return 0.0

def main():
    driver = None
    try:
        all_players = load_players()
        driver = setup_driver()
        driver.get(Base_url)
        WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='Premier League']"))
)
    # Get Premier League valued players page
        pl_link = get_premier_league_link(driver)
        all_valued_players_link = get_valued_players_link(driver, pl_link)
        print(f"Valued players link: {all_valued_players_link}")
        
    # Scrape player values
        matched_players = scrape_player_values(driver, all_players, all_valued_players_link)
        
    # Go back to link 'https://www.footballtransfers.com/us' to find values of missing players 
        driver.get(Base_url)
        time.sleep(3)
    # List of missing players
        matched_names = [p['Name'] for p in matched_players]
        missing_players = [p for p in all_players if p not in matched_names]
        
        for player in missing_players:
            value = search_missing_players(driver, player)
            matched_players.append({"Name": player, "Value": value})

        df = pd.DataFrame(matched_players)
        df['NumericValue'] = df['Value'].apply(normalize_value)
        df = df.sort_values('NumericValue', ascending=False).drop('NumericValue', axis=1)
        df.to_csv('Transfer_value.csv', index=True) 
        print(f"\nSaved results to {'Transfer_value.csv'}")

        for _, row in df.iterrows():
            print(f"{row['Name']}: {row['Value']}")
    
    except Exception as e:
        print(f"Main function error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
