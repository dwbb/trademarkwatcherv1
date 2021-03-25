from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import mark_functions as trademark
import os
import sys
import json
import re
from datetime import date, datetime, timedelta

days_ago = 1

def tess_searcher():
    # Opens selenium, goes to tess, sets search options to reg date and 100 records per page
    global browser

    #Tells driver not to load images on webpages
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    path = os.getcwd()
    dir = "chromedriver"
    dir_path = os.path.join(path, dir)

    browser =  webdriver.Chrome(dir_path, port=0, chrome_options=chrome_options)
    browser.get("http://tmsearch.uspto.gov/")

    # Go to Tess database search by date
    tess_search_by_date = "/html/body/center/table[2]/tbody/tr[3]/td/font/font/a"
    browser.find_element_by_xpath(tess_search_by_date).click()

    # Changes Date search to Registration Date
    click_opp_date = '/html/body/form/font/table[4]/tbody/tr[1]/td[2]/select'
    browser.find_element_by_xpath(click_opp_date).click()

    # Selects IC as secondary search condition
    click_IC = '/html/body/form/font/table[4]/tbody/tr[2]/td[2]/select/option[20]'
    browser.find_element_by_xpath(click_IC).click()

    # Selects AND as search operator
    click_AND = '/html/body/form/font/table[4]/tbody/tr[1]/td[3]/select/option[1]'
    browser.find_element_by_xpath(click_AND).click()

    # Changes number of records returned to 500
    request_500_records = '/html/body/form/font/table[3]/tbody/tr/td[1]/select/option[5]'
    browser.find_element_by_xpath(request_500_records).click()

    return browser

def tess_search_date():
    # Uses date function to get wanted search date
    search_date = date.today() - timedelta(days = days_ago)
    search_date = search_date.strftime("%Y%m%d")

    return search_date

def run_tess_search():

    browser = tess_searcher()
    search_date = tess_search_date()

    # Inputs wanted date into date search field and removes the default entry
    og_date = browser.find_element_by_id("datefield")
    og_date.clear()
    og_date.send_keys(search_date)

    # Inputs IC search condition
    ic_search_term = browser.find_element_by_xpath('/html/body/form/font/table[4]/tbody/tr[2]/td[1]/input')
    ic_search_term.clear()
    ic_search_term.send_keys("009 OR 035 OR 042 OR 045")

    # Submits search
    submit_query = "/html/body/form/font/font/table[1]/tbody/tr[1]/td/input[2]"
    browser.find_element_by_xpath(submit_query).click()

    # Get text from search result page
    search_result_tag = "/html/body"
    search_result = browser.find_element_by_xpath(search_result_tag).get_attribute("innerText")

    # Check if there are any search results
    # If no results, creates file with current date and message about no found results then exits
    if re.search(r'No TESS records were found to match the criteria of your query.', search_result):
        no_results()
        browser.quit()
        return None

    # Checks number of pages and number of results per page to make sure it opens every entry
    else:
        # Number of total results
        tweet_dict = {}
        full_list = []

        tweet_counter = 1
        counter = 0

        next_page = "body > a:nth-child(44)" #"/html/body/a[27]"
        tsdr = "body > a:nth-child(26)"
        entry = "body > table:nth-child(28) > tbody > tr:nth-child(2) > td:nth-child(2) > a" #"/html/body/table[7]/tbody/tr[2]/td[2]/a"

        browser.find_element_by_css_selector(entry).click()


        while len(browser.find_elements_by_css_selector(next_page)) >= 0:

            # Goes through each entry on the page opens and runs functions to read and interpret tess records
            while len(browser.find_elements_by_css_selector("body > a:nth-child(47)")) > 0:

                url = get_url(browser, tsdr)

                #Checks through Tess registry and if it is a match for surveillance relation pulls the relevant "full" and tweet formatted entry
                tweet_content, full_content = tess_watcher(browser, url)
                counter += 1

                if tweet_content is not None:
                    tweet_dict[str(tweet_counter)] = tweet_content
                    tweet_counter += 1

                if full_content is not None:
                    full_list.append(full_content)

                entry = "body > a:nth-child(47)" #"/html/body/a[30]"
                browser.find_element_by_css_selector(entry).click()

            try:
                browser.find_element_by_css_selector(next_page).click()
                entry = "body > table:nth-child(28) > tbody > tr:nth-child(2) > td:nth-child(2) > a" #"/html/body/table[7]/tbody/tr[2]/td[2]/a"
                browser.find_element_by_css_selector(entry).click()
            except:
                print(str(counter) + " entries checked!")

            browser.quit()

            return tweet_dict, full_list

            # Reduced number by number of records on page that was checked and reduces page_number counter

    return print("Something went wrong!")

def get_url(browser, url):

    # Grab and save url and pass it to display_url
    url = url
    mark_url = browser.find_element_by_css_selector(url).get_attribute('href')

    return mark_url

def tess_to_string():
# Pulls the relevant data from teh Tess entry page
    content_tag = "/html/body/table[5]/tbody"
    content = browser.find_element_by_xpath(content_tag).get_attribute("innerText")

    return content

def tess_watcher(browser, url):

    tess_file = tess_to_string()
    tweet_content, full_content = trademark.trademark_watcher(tess_file, browser, url)

    return tweet_content, full_content
