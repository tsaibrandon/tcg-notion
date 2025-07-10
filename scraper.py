import undetected_chromedriver as uc
import pandas as pd
import time
import random
import json
import os
import csv

from numpy import empty
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_driver():
    driver = uc.Chrome()
    wait = WebDriverWait(driver, 10)
    return driver, wait

def restart_driver(driver):
    try:
        driver.quit()
    except:
        pass
    
    return start_driver()

driver, wait = start_driver()
cookies_file = 'cookies.json'

if os.path.exists(cookies_file):
    driver.get('https://seller.tcgplayer.com')

    time.sleep(2)

    with open(cookies_file, 'r') as f:
        cookies = json.load(f)

    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f'Failed to add cookie {cookie.get("name")} - {e}')

    driver.get(
        'https://sellerportal.tcgplayer.com/orders?searchRange=LastThreeMonths&page=1&size=25&sortBy=orderStatus,asc&sortBy=orderDate,asc&qfid=All'
    )
    
    input('If you have been logged in, press ENTER to continue.')

else:
    driver.get('https://seller.tcgplayer.com')

    time.sleep(2)

    cookie_buttons = driver.find_elements(By.ID, 'hs-eu-confirmation-button')
    if cookie_buttons:
        ActionChains(driver).move_to_element(cookie_buttons[0]).click().perform()

    login_button = driver.find_element(By.CLASS_NAME, 'navbar-interactive-dropdown')
    ActionChains(driver).move_to_element(login_button).click().perform()

    login_link = driver.find_element(By.CSS_SELECTOR, 'a[href="https://store.tcgplayer.com/admin/account/logon"]')
    ActionChains(driver).move_to_element(login_link).click().perform()

    time.sleep(2)

    input("Please log in and hit enter")

    with open('cookies.json', 'w') as f:
        json.dump(driver.get_cookies(), f)

    # wait = WebDriverWait(driver, 15)

    # order_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[.//span[text()="Orders"]]')))
    # ActionChains(driver).move_to_element(order_page).click().perform()

orders = driver.find_elements(
    By.CSS_SELECTOR, 
    'tbody.tcg-table-body tr.is-even, '
    'tbody.tcg-table-body tr.is-odd'
    )

order_urls = []

for order in orders:
    try:
        order_status = order.find_element(By.CSS_SELECTOR, 'span.tcg-status-badge__content').text

        if order_status in ['Shipped - In Transit', 'Completed - Paid', 'Completed - Payment Pending']:
            href = order.find_element(By.CSS_SELECTOR, '.color-surface-link').get_attribute('href')
            order_urls.append(href)

    except Exception as e:
        print("Skipping row", e)

csv_file = 'tcg_orders.csv'
existing_orders = set()

if os.path.exists(csv_file):
    try:
        df_existing = pd.read_csv(csv_file)
        existing_orders = set(df_existing['Order ID'].astype(str).str.strip().tolist())
    except Exception as e:
        print(f'Erro reading existing CSV: {e}')
    
all_orders = []

for url in order_urls:

    try:
        driver.get(url)

        time.sleep(random.uniform(1.2, 2.4))

        order_id = url.split("/")[-1].strip()
        if order_id in existing_orders:
            print(f'Skipping duplicate order: {order_id}')
            continue
    
        buyer_name = driver.find_element(By.CSS_SELECTOR, 'p.margin-0 > strong').text

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td')))

        transaction_info = driver.find_elements(
            By.CSS_SELECTOR, 
            'div[data-testid="OrderDetails_TransactionDetails_Table"] '
            'td.tcg-table-body__cell--align-right ' 
            'span'
        )
        if len(transaction_info) >= 4:
            product_amt = transaction_info[0].text.strip()
            shipping_amt = transaction_info[1].text.strip()
            fee_amt = transaction_info[2].text.strip()
            net_amt = transaction_info[3].text.strip()
        else:
            product_amt = 'N/A'
            shipping_amt = 'N/A'
            fee_amt = 'N/A'
            net_amt = 'N/A'
        
        order_amt = driver.find_element(
            By.CSS_SELECTOR, 
            'div[data-testid="OrderDetails_TransactionDetails_Table"] '
            'td.tcg-table-body__cell strong'
        ).text

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 
            'div[data-testid="OrderDetails_ProductList_Table"] tbody tr.is-even, '
            'div[data-testid="OrderDetails_ProductList_Table"] tbody tr.is-odd')
        ))

        products = driver.find_elements(
            By.CSS_SELECTOR,
            'div[data-testid="OrderDetails_ProductList_Table"] '
            'tbody tr.is-even, '
            'div[data-testid="OrderDetails_ProductList_Table"] '
            'tbody tr.is-odd'
        )

        product_list = []

        for p in products:
            try:
                tds = p.find_elements(By.CSS_SELECTOR, 'td')
                
                if len(tds) >= 4:
                    link_element = tds[0].find_element(By.TAG_NAME, 'a')
                    link = link_element.get_attribute('href')

                    mp_price = tds[1].text.strip()
                    quantity = tds[2].text.strip()
                    ext_price = tds[3].text.strip()

                    # original_window = driver.window_handles
                    # driver.execute_script('window.open(arguments[0]);', link)

                    # wait.until(lambda d: len(d.window_handles) > len(original_window))
                    # new_window = [w for w in driver.window_handles if w not in original_window][0]
                    # driver.switch_to.window(new_window)

                    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.product-details__name')))
                    # card_name = driver.find_element(By.CSS_SELECTOR, 'h1.product-details__name').text.strip()
                    
                    # if '-' in card_name:
                    #     part_name = card_name.split(' - ')
                    #     card_name_num = part_name[0].strip() if len(part_name) >=2 else card_name
                    # else:
                    #     card_name_num = card_name

                    # market_price = driver.find_element(By.CSS_SELECTOR, 'span.price-points__upper__price').text.strip()

                    # driver.close()
                    # driver.switch_to.window(original_window)

                if not mp_price and not quantity and not ext_price:
                    continue

                # print('Product Name:', card_name_num)
                # print('Market Price:', market_price)
                print('URL:', link)
                print('MP Price:', mp_price)
                print('Qty:', quantity)
                print('Ext Price:', ext_price)

                product_list.append({
                    'URL': link,
                    # 'Product Name': card_name_num,
                    # 'Market Price': market_price,
                    'MP Price': mp_price,
                    'Quantity': quantity,
                    'Exact Price': ext_price
                })   

            except Exception as e:
                print("Skipping product row:", e)
                continue

        all_orders.append({
            'Order ID': order_id,
            'Buyer': buyer_name,
            'Product Amount': product_amt,
            'Shipping Amount': shipping_amt,
            'Order Amount': order_amt,
            'Fee Amount': fee_amt,
            'Net Amount': net_amt,
            'Products': json.dumps(product_list)
        })

    except Exception as e:
        print(f'Diver crashed or invalid session: {e}')
        driver, wait = restart_driver(driver)
        continue

file_exists = os.path.exists(csv_file)

if all_orders:
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_orders[0].keys())
        
        if not file_exists:
            print(f'Writing {len(all_orders)} new orders to {csv_file}')
            writer.writeheader()
        writer.writerows(all_orders)
else:
    print('No orders were collected')

    


    

