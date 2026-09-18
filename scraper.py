import os
import time
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def send_email(subject, body):
    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('APP_PASSWORD')
    receiver = os.environ.get('RECEIVER_EMAIL')
    
    if not sender or not password or not receiver:
        print("GitHub Secrets are missing. Cannot send email.")
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
    options.add_argument('--headless=new') # Uses Chrome's updated, stealthier headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080') # Adds a normal screen size
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36') # Pretends to be a normal Windows PC
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        driver.get("https://reservation.darbalwatan.com/")
        
        buy_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Buy tickets')]")))
        buy_btn.click()
        
        # Replace these IDs with the actual ones from the website
        origin = wait.until(EC.presence_of_element_located((By.ID, "origin_field_id")))
        origin.send_keys("Madinah Bus Station")
        
        destination = driver.find_element(By.ID, "destination_field_id")
        destination.send_keys("Makkah Bus Station (Jarwal)")
        
        date_input = driver.find_element(By.ID, "date_field_id")
        date_input.send_keys("22/09/2026") 
        
        driver.find_element(By.ID, "search_btn_id").click()
        
        time.sleep(5) 
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        if "book now" in page_text:
            send_email("🟢 ALERT: Bus Ticket Available!", "A ticket from Madinah to Makkah is open! 'BOOK NOW' button detected. Go book it immediately!")
        else:
            send_email("🔴 Status: No Bus Tickets Yet", "Checked Darb Al Watan. Still fully booked.")
            
    except Exception as e:
        send_email("🟡 Status: Scraper Error", f"The script failed to run properly. Error details:\n\n{e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    check_tickets()
