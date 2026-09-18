import os
import time
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def send_email(subject, body):
    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('APP_PASSWORD')
    receiver = os.environ.get('RECEIVER_EMAIL')
    
    if not sender or not password or not receiver:
        print("GitHub Secrets missing.")
        return
        
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def check_tickets():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Loading Darb Al Watan...")
        driver.get("https://reservation.darbalwatan.com/")
        
        # 1. Click '+ Buy tickets'
        buy_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Buy tickets') or contains(text(), 'Buy ticket')]")))
        buy_btn.click()
        time.sleep(2) # Wait for popup to animate
        
        # 2. Origin (First 'id=from' input)
        print("Entering Origin...")
        origin_input = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@id='from']//input)[1]")))
        origin_input.send_keys("Madinah Bus Station")
        time.sleep(1)
        origin_input.send_keys(Keys.RETURN)
        
        # 3. Destination (Second 'id=from' input)
        print("Entering Destination...")
        dest_input = driver.find_element(By.XPATH, "(//div[@id='from']//input)[2]")
        dest_input.send_keys("Makkah Bus Station (Jarwal)")
        time.sleep(1)
        dest_input.send_keys(Keys.RETURN)
        
        # 4. Date (Requires exact format DD.MM.YYYY)
        print("Entering Date...")
        date_input = driver.find_element(By.XPATH, "//input[@placeholder='Select Departure Date']")
        # Clear the field using backspaces, then send the date
        date_input.send_keys(Keys.CONTROL + "a")
        date_input.send_keys(Keys.BACKSPACE)
        date_input.send_keys("22.09.2026")
        date_input.send_keys(Keys.ESCAPE) # Closes the calendar popup
        
        # 5. Click Search (Finds the main button at the bottom of the popup)
        print("Clicking Search...")
        search_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'search') or contains(., 'Search') or contains(., 'SEARCH')]")
        search_btn.click()
        
        # 6. Verify Results
        print("Checking results...")
        time.sleep(6) # Wait for search results to load completely
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        if "book now" in page_text:
            send_email("🟢 ALERT: Bus Ticket Available!", "A ticket from Madinah to Makkah is open for Sept 22/23! 'BOOK NOW' button detected. Go book it immediately!")
            print("Ticket found! Email sent.")
        else:
            send_email("🔴 Status: No Bus Tickets Yet", "Checked Darb Al Watan. Still fully booked.")
            print("No tickets found. Status email sent.")
            
    except Exception as e:
        send_email("🟡 Status: Scraper Error", f"The script encountered an error:\n\n{e}")
        print(f"Error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    check_tickets()
