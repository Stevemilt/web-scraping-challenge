from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()

    #Page to be scraped
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    time.sleep(5)

    # Scrape page into Soup

    #html object
    html = browser.html
    #Parse html
    soup = bs(html, "html.parser")

    # Retrieve the latest news title
    mars = soup.find('ul', class_='item_list').find('li', class_='slide')
    news_title = mars.find("div", class_="content_title").get_text()
    # Retrieve the news paragraph
    news_body = mars.find("div", class_= "article_teaser_body").get_text()

    #JPL Mars Space Images - Featured Image
    jpl_url = "https://www.jpl.nasa.gov"
    url_jpl_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_jpl_image)

    #html object
    html = browser.html
    #parse html
    soup = bs(html, "html.parser")

    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)
    html = browser.html
    soup = bs(html, "html.parser")
    browser.is_element_present_by_text('more info', wait_time=1)
    jpl_image = soup.find("img", class_="fancybox-image")["src"]
    image_url = f"{jpl_url}{jpl_image}"

    #Mars Facts
    mars_url = "https://space-facts.com/mars/"
    tables = pd.read_html(mars_url)

    mars_fact = tables[0]
    mars_fact = mars_fact.rename(columns={0: "Description", 1: "Mars"}, errors="raise")
    mars_fact.set_index("Description", inplace=True)
    mars_fact

    mars_table = mars_fact.to_html()
    mars_table = mars_table.replace('\n', '')

    #Mars Hemispheres

    astro_url = "https://astrogeology.usgs.gov/"
    hemis_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemis_url)
    html = browser.html
    soup = bs(html, "html.parser")

    #Extract Item elements
    mars_hems = soup.find("div", class_="collapsible results")
    mars_item = mars_hems.find_all("div", class_="item")
    image_urls = []

    #looping through hemisphere item
    for item in mars_item:
        # Error handling
        try:
            #Extract title
            hem = item.find("div", class_="description")
            hem_title = hem.h3.text
            #Image url
            hem_image_url = hem.a["href"]
            browser.visit(astro_url+hem_image_url)
            html = browser.html
            soup = bs(html, "html.parser")
            image_src = soup.find('li').a['href']
            hem_dict = {
                "Title" : hem_title,
                "Image_Url" : image_src}
                
            image_urls.append(hem_dict)
        except Exception as e:
            print(e)
    
    #Create dictionary for all the record

    mars_dict = {
        "news_title" : news_title,
        "news_body" : news_body,
        "jpl_image" : image_url,
        "table" : mars_table,
        "hemisphere" : image_urls
    }

    #close the browser
    browser.quit()

    return mars_dict