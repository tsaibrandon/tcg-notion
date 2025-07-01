import undetected_chromedriver as uc
import time
import json
import os

from numpy import empty
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = uc.Chrome()
wait = WebDriverWait(driver, 10)
cookies_file = "cookies.json"

if os.path.exists(cookies_file):
    driver.get("https://seller.tcgplayer.com")

    time.sleep(2)

    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if isinstance(cookie.get("expiry"), float):
            cookie["expiry"] = int(cookie["expiry"])
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Failed to add cookie {cookie.get('name')} - {e}")

    driver.get("https://sellerportal.tcgplayer.com/orders?searchRange=LastThreeMonths&page=1&size=25&sortBy=orderStatus,asc&sortBy=orderDate,asc&qfid=All")
    input("Check if you were logged in. Press ENTER to continue.")

else:
    cookie_buttons = driver.find_elements(By.ID, 'hs-eu-confirmation-button')
    if cookie_buttons:
        ActionChains(driver).move_to_element(cookie_buttons[0]).click().perform()

    login_button = driver.find_element(By.CLASS_NAME, 'navbar-interactive-dropdown')
    ActionChains(driver).move_to_element(login_button).click().perform()

    login_link = driver.find_element(By.CSS_SELECTOR, 'a[href="https://store.tcgplayer.com/admin/account/logon"]')
    ActionChains(driver).move_to_element(login_link).click().perform()

    time.sleep(2)

    input("Please log in and hit enter")

    with open("cookies.json", "w") as f:
        json.dump(driver.get_cookies(), f)

    # wait = WebDriverWait(driver, 15)

    # order_page = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[.//span[text()="Orders"]]')))
    # ActionChains(driver).move_to_element(order_page).click().perform()

orders = driver.find_elements(By.CSS_SELECTOR, '.color-surface-link')
order_urls = [
    link.get_attribute("href") for link in orders
]

order_data = []

for url in order_urls:
    driver.get(url)

    time.sleep(1)

    order_id = url.split("/")[-1]
    buyer_name = driver.find_element(By.CSS_SELECTOR, 'p.margin-0 > strong').text

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

    products = driver.find_elements(
        By.CSS_SELECTOR,
        'div[data-testid="OrderDetails_ProductDetails_Table] tbody tr'
    )

    for product in products:
        product_info = product.find_elements(By.CSS_SELECTOR, 'td')

        if len(product) == 4:
            listed_price = product_info[1].text.strip()
            qty_sold = product_info[2].text.strip()
            total_price = product_info[3].text.strip()
   

    # product_urls = [
    #     link.get_attribute("href") for link in products
    # ]
    


    print(order_id)
    print(buyer_name)
    print(product_amt)
    print(shipping_amt)
    print(order_amt)
    print(fee_amt)
    print(net_amt)

    print(listed_price)
    print(qty_sold)
    print(total_price)





