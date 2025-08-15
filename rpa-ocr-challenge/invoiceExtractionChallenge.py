# Import dependencies
import os
import time
from datetime import datetime
import re
import requests
import urllib.request
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Get environment variables for service connections
selenium_ip = os.getenv('HOST_IP', 'selenium-chrome')
tesseract_ip = os.getenv('TESSERACT_IP', 'tesseract-ocr')
selenium_port = os.getenv('SELENIUM_PORT', '4444')
tesseract_port = os.getenv('TESSERACT_PORT', '5000')

print(f"Connecting to Selenium at: {selenium_ip}")
print(f"Connecting to Tesseract at: {tesseract_ip}")


# Create a DataFrame to store the output results
df_output = pd.DataFrame(columns=['ID', 'DueDate', 'InvoiceNo', 'InvoiceDate', 'CompanyName', 'TotalDue'])


# Define parameters
# Set the download folder path
projectFolder = os.path.dirname(os.path.abspath(__file__))
projectDownloadFolder = os.path.join(projectFolder, "img")
# Create the 'img' folder if it doesn't already exist
if not os.path.exists(projectDownloadFolder):
    os.makedirs(projectDownloadFolder)


# Initialize the WebDriver using a remote Selenium server with retry logic
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        print(f"Attempting to connect to Selenium server (attempt {retry_count + 1}/{max_retries})")
        options = webdriver.ChromeOptions()
        driver = webdriver.Remote(
            command_executor=f'http://{selenium_ip}:{selenium_port}/wd/hub',
            options=options
        )
        print("Successfully connected to Selenium server")
        break
    except Exception as e:
        retry_count += 1
        print(f"Connection attempt {retry_count} failed: {e}")
        if retry_count >= max_retries:
            print("Failed to connect to Selenium server after all retry attempts")
            raise
        print(f"Retrying in 5 seconds...")
        time.sleep(5)

# Maximize the browser window
driver.maximize_window()
# Navigate to the RPA challenge page
driver.get("https://rpachallengeocr.azurewebsites.net/")


# Click on Start button
element = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#start'))
)
element.click()
time.sleep(0.5)


# List page numbers from the invoice table 
list_pages = list()
list_elements = driver.find_elements(By.CLASS_NAME,'paginate_button')
# Extract numeric page values and store them in list_pages
for i in list_elements:
    if i.get_attribute('innerHTML').isnumeric() == True:
        list_pages.append(i.get_attribute('innerHTML'))


# Loop through each page number in list_pages
for i in list_pages:
    # Navigate to the corresponding page
    element = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, f'//*[@id="tableSandbox_paginate"]/span/a['+ str(i) +']'))
    )
    element.click()

    # Locate and recreate the invoice table
    table_element = driver.find_element(By.XPATH,'//*[@id="tableSandbox"]')
    for i in table_element.find_elements(By.XPATH, '//tr'):
        # Extract table headers and initialize df_table
        if '</th>' in i.get_attribute('outerHTML'):
            items = re.findall(r'<th\b[^>]*>([^<]*)<\/th>',i.get_attribute('outerHTML'))
            df_table = pd.DataFrame(columns=items)
        else:
            # Extract data from table
            items = re.findall(r'<td\b[^>]*>([^<]*)<\/td>',i.get_attribute('outerHTML'))
            # Extract invoice href link
            href_invoice = re.findall(r'<a[\s\S]*?href="([^"]+)"[\s\S]*?>',i.get_attribute('outerHTML'))
            # Add invoice href link to items list
            items.append(href_invoice[0])
            # Add items list to the df_table
            df_table.loc[len(df_table)] = items


    # Convert the "Due Date" column to datetime format
    df_table["Due Date"] = pd.to_datetime(df_table["Due Date"], format="%d-%m-%Y")

    # Filter rows where the due date is today or earlier
    df_table = df_table[df_table["Due Date"] <= datetime.today()]
    # # Display the filtered table
    # print(df_table)


    # Loop through each row in the current df_table
    for i in range(0,len(df_table)):

        # Extract invoice details and link
        due_date_invoice = df_table.iloc[i,2]
        due_date_invoice = pd.to_datetime(due_date_invoice).strftime('%d-%m-%Y') # Mettre la date au bon format
        invoice_id = df_table.iloc[i,1]
        href_link = df_table.iloc[i,3]

        # Click the invoice link to open it in a new tab
        driver.find_element(By.XPATH, '//a[@href="'+ href_link +'"]').click()
        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[-1])

        # Wait until the image is loaded
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/img'))
        )

        # Download the invoice image and save it to the 'img' folder
        name_image = df_table.iloc[i,1]
        image_selector = driver.find_element(By.XPATH,'/html/body/img').get_attribute('src')
        file_name = os.path.join(projectDownloadFolder, str(name_image) + '.jpg')
        urllib.request.urlretrieve(image_selector, file_name)


        # Start the OCR procedure

        file_path = file_name  # define path to the img file to be processed

        with open(file_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f'http://{tesseract_ip}:{tesseract_port}/ocr', files=files)
        if response.ok:
            ocr_text = response.text
            # print("OCR text detected:") # Uncomment to display the full OCR result
            # print(ocr_text) # Uncomment to display the full OCR result
        else:
            print("OCR error:", response.status_code, response.text)


        # Preprocess the extracted data
        # Parse the JSON string into a Python dictionary
        data = json.loads(ocr_text)
        # Extract the raw OCR text from the 'text' field
        raw_text = data['text']
        # Replace newline characters with spaces for easier processing
        clean_text = raw_text.replace('\n', ' ')
        # Split the cleaned text into individual words
        data_text = clean_text.split()
        # Display the list of extracted words
        # print(data_text) # Uncomment to display the list of extracted words


        # Procedure to extract key information from the current invoice (from extracted OCR words)

        number_of_elements_in_data_text = len(data_text)
        # Loop through the extracted OCR words to identify relevant fields
        for i in range(int(number_of_elements_in_data_text)):
            # Extract company name (text before the word 'INVOICE')
            if data_text[i] == 'INVOICE':
                company_name = ' '.join([data_text[n] for n in range(0,i)])
            # Extract invoice number (e.g. 'Invoice #123456')
            if data_text[i] == 'Invoice' and ('#') in data_text[i+1]:
                invoiceNo = data_text[i+1]
                invoiceNo = str(invoiceNo).replace('#','')
            # Extract total amount (e.g. 'Total 6300.00')
            if data_text[i] == 'Total' and str(data_text[i+1]).replace('.','').isnumeric() == True:
                total = data_text[i+1]
            # Try to extract invoice date in 'YYYY-MM-DD' format
            try:
                invoiceDate = datetime.strptime(str(data_text[i]),'%Y-%m-%d').strftime('%d-%m-%Y')
            except:
                pass


        # Save extracted invoice data to the output DataFrame
        df_output.loc[len(df_output)] = [invoice_id,due_date_invoice,invoiceNo,invoiceDate,company_name,total]

        # Delete the downloaded image file
        try:
            path = file_name
            os.remove(path)
        except FileNotFoundError:
            pass


        # Close the current browser tab (invoice image)
        driver.close()


        # Switch back to the main RPA Challenge tab
        driver.switch_to.window(driver.window_handles[0])


# Create the output CSV file from df_output
# print(df_output)
output_file = os.path.join(projectFolder, 'output.csv')
df_output.to_csv(output_file, sep=',', index=False)


# Submit the CSV file via HTML form injection
driver.find_element(By.XPATH,'//*[@id="submit"]/div/div/div/form/input[1]').send_keys(output_file) 


# Delete the output CSV file
try:
    path = output_file
    os.remove(path)
except FileNotFoundError:
    pass


# Wait 3 seconds before closing the browser
time.sleep(3)
# Close the browser
driver.quit()