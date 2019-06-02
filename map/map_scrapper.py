from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import numpy as np

def cat_check(elem_lst):

    # check whether subcategories are present
    return True if 'bar2' in [elem.get_attribute('class') for elem in elem_lst] else False

def driver_wait(xpath, ie, time = 10):

    # wait for element to load in DOM
    WebDriverWait(driver, time, ignored_exceptions = ie)\
                    .until(expected_conditions.presence_of_element_located((By.XPATH, 
                                                                            xpath)))

def extract_address(cat_name, place, div):
    
    # get address 

    link = div.find_element_by_class_name('locationlink').get_attribute('href')
    driver.get(link)
    driver_wait('//*[@id="panel"]/div[2]/div[1]', ignored_exceptions)
    
    address = driver.find_element_by_class_name('locf').text.replace('\n',', ') 
    
    driver.get(f'{url}#q:{cat_name.replace(" ","%20")}')
    driver_wait('//div[@class="biz"]/div', ignored_exceptions)
    
    return address

### StaleElementReferenceException, element is no longer in the DOM
ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)

# opens website
driver = webdriver.Chrome()
url = 'http://maps.ntu.edu.sg/maps'
driver.get(url)

# click browse
driver.find_element_by_xpath('//*[@id="browse"]').click()

# extract all categories
catergories = driver.find_elements_by_xpath('//*[@id="browse_container"]/ul[3]/li/a')
cat_len = range(len(catergories))

cat_lst = []
for i in cat_len:
    
    # click on catergory
    place_xpath = f'//*[@id="browse_container"]/ul[3]/li[{i+1}]/a'
    driver_wait(place_xpath, ignored_exceptions)
    place = driver.find_element_by_xpath(place_xpath)
    
    cat_name = place.get_attribute('text')
    place.click()
    
    # load subcategory and places, classed under 'biz'
    driver_wait('//div[@class="biz"]/div', ignored_exceptions)
    divs = driver.find_elements_by_xpath('//div[@class="biz"]/div')
    divs_len = range(len(divs))
    
    # check for presence of category
    if cat_check(divs):
        
        for j in divs_len:
            
            div_xpath = f'//*[@class="biz"]/div[{j+1}]'
            driver_wait(div_xpath, ignored_exceptions)
            div = driver.find_element_by_xpath(div_xpath)
            
            # store subcategory name
            if div.get_attribute('class') == 'bar2':
                subcat_name = div.text
                
            # extract info
            elif 'place' in div.get_attribute('class'):
                place = div.text
                address = extract_address(cat_name, place, div)
                print((cat_name, subcat_name, place, address))
                cat_lst.append((cat_name, subcat_name, place, address))

    else:
        
        # no subcategory present
        subcat_name = np.nan
        
        for j in divs_len:
            
            div_xpath = f'//*[@class="biz"]/div[{j+1}]'
            driver_wait(div_xpath, ignored_exceptions)
            div = driver.find_element_by_xpath(div_xpath)
            
            # extract info
            if 'place' in div.get_attribute('class'):
                place = div.text
                address = extract_address(cat_name, place, div)
                print((cat_name, subcat_name, place, address))
                cat_lst.append((cat_name, subcat_name, place, address))
                
            else:
                pass
    
    # return to homepage and click on browse
    driver.get('http://maps.ntu.edu.sg/maps')
    driver.find_element_by_xpath('//*[@id="browse"]').click()

driver.close()

df = pd.DataFrame(cat_lst, columns = ['Category', 'Subcategory', 'Place', 'Address'])
df.set_index('Category', inplace=True)
df.to_csv('ntumap.csv')