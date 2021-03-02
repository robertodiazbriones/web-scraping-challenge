# Dependencies
import pandas as pd
from sqlalchemy import create_engine
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time

def init_browser():
    # Execute Chromedriver (add in again in case you close the browser)
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)


# Define scrape function
def scrape():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    #Create Dictonary
    mars_library = {}

    #############################
    ####    NASA Mars News   ####
    #############################
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    #Visit url
    browser.visit(url)
    #assign html content
    html=browser.html
    soup = BeautifulSoup(html, 'html.parser')

    try:
        #Get latest news paragraph
        results_p = soup.find_all('div', class_="image_and_description_container")
        result_p=results_p[0].find('div', class_="rollover_description_inner").text.strip() 

    except AttributeError:
        result_p="Error scrapping paragraph"

    try:
        #Get latest news title
        results_t = soup.find_all('div', class_="content_title")
        result_t=results_t[0].find('a').text.strip()
    except AttributeError:
        result_t="Error scrapping title"

    #Save title and paragraph into mars_library dictionary
    mars_library['news_title'] = result_t
    mars_library['news_p'] = result_p

    #############################
    ####JPL Mars Space Images####
    #############################
    # URL of page to be scraped
    url_pic = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_pic)
    # assign html content
    html = browser.html
    # Create a Beautiful Soup object
    soup2 = BeautifulSoup(html, "html5lib")
    #Scrape Path for the Feature Image. got the partial path of the url
    picture_address = soup2.find_all('div', class_='sm:object-cover object-cover')[9].find('img').attrs['src'].strip()
    #Save picture_address into mars_library dictionary
    mars_library['featured_image_url'] = picture_address

    #############################
    ####      Mars Facts     ####
    #############################
    # URL of page to be scraped
    url_facts = 'https://space-facts.com/mars/'
    # use Pandas to get the url table
    tables = pd.read_html(url_facts)
    #Creating df for mars facts
    mars_facts = tables[0]
    mars_facts.columns=['Description','Value']
    #Set Description as new index
    mars_facts.set_index('Description', inplace=True)
    # Export df as html file
    mars_facts_html=mars_facts.to_html(justify='left')
    # Save info into Library
    mars_library['mars_facts'] = mars_facts_html

    #############################
    ####    Mars Hemisperes  ####
    #############################

    # URL of page to be scraped
    url_hemis = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    #Visit the page using the browser
    browser.visit(url_hemis)
    # assign html content
    html = browser.html
    # scrape to find links to pictures
    soup = BeautifulSoup(html,"html5lib")
    results = soup.find_all('h3')
    #Create list and dictionary
    hemis_image_urls = []
    hemis_dict = {}
    # Loop results
    for result in results:
        #get link to pictures
        link = result.text
        time.sleep(1)    
        browser.click_link_by_partial_text(link)
        time.sleep(1)
        #visit link picture
        link_html= browser.html 
        #Scrape to find picture ref
        soup_link = BeautifulSoup(link_html,"html5lib")
        link_pic = soup_link.find_all('div', class_="downloads")[0].find_all('a')[0].get("href")
        #build dict with link and link_html
        hemis_dict["title"]=link
        hemis_dict["img_url"]=link_pic
        # Append Dict to the hemis_dict
        hemis_image_urls.append(hemis_dict)
        #erased dict for next link
        hemis_dict = {}
        #go back to main page
        browser.visit(url_hemis)
        time.sleep(1)
    # Put infos into Library
    mars_library['hemisphere_image_urls']=hemis_image_urls
    
    # Return Library
    return mars_library

    




