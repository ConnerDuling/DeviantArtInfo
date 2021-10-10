from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import requests
from ContentFromPages import *

#Here we use Selenium to handle the dynamic parts of the webpage
#
#https://towardsdatascience.com/how-to-scrape-dynamic-web-pages-with-selenium-and-beautiful-soup-fa593235981
# Additional research material used in making this
# 
#https://mlvnt.com/blog/tech/2018/05/scraping-deviantart/

def getDriver():
    opts = Options()
    opts.add_argument(" --headless")

    opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    # Check that proper path is used. If not in Program Files, check Program Files (x86) 
    try:
        driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)
    except:
        opts.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

    return driver

def scrollThroughGalleryAndGetLinks(driver):

    SCROLL_PAUSE_TIME = 0.5
    
    last_height = driver.execute_script("return document.body.scrollHeight")

    pages = []

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        #Get links at current gap in scroll
        gallery = driver.find_element_by_id('sub-folder-gallery')
        links = gallery.find_elements_by_xpath('//a[@data-hook="deviation_link"]')
        for link in links:
            l = link.get_attribute('href')
            pages.append(l)

        unique_pages = list(set(pages))
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return unique_pages

def accessDriver(url, func):

    driver = getDriver()

    driver.get(url)

    list_of_links = func(driver)

    driver.close()

    return list_of_links

def getDeviationStats(url):
    pageLinks = accessDriver(url, scrollThroughGalleryAndGetLinks)
    listOfDeviations = getPageStats(pageLinks)

    n = len(listOfDeviations)
    for i in range(n-1):
    # Last i elements are already in place
        for j in range(0, n-1-i):
            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if listOfDeviations[j].getScore() > listOfDeviations[j + 1].getScore() :
                listOfDeviations[j], listOfDeviations[j + 1] = listOfDeviations[j + 1], listOfDeviations[j]
    
    return listOfDeviations


username = input("Input the username you want to scan: ")

url = "https://www.deviantart.com/"+username+"/gallery/all"

# If username URL is valid, run program
if usernameValidURL(url):
    while(1):
        userInput = str(input("Do you want to get statistics or save a gallery? (save/stat): ")).lower()

        if userInput == "save":
            pageLinks = accessDriver(url, scrollThroughGalleryAndGetLinks)

            print("User has",len(pageLinks),"deviations in their gallery.")
            getFilesFromDAPages(username, pageLinks)
            break
        elif userInput == "stat":
            listOfDeviations = getDeviationStats(url)

            for pages in listOfDeviations:
                print("Score:", pages.getScore(), "-- Views:", pages.getViewCount(),"-- Favorites:", pages.getFavCount(),"-- Comments:", pages.getCommentCount(),"--", pages.getUrl())
            break
        
        else:
            print("Invalid input. Please try again or Ctrl+C to abort.")
else:
    print("Bad username. Please run again and check spelling.")
