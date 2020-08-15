from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import time
import pandas as pd
import pymongo

def scrape():
    ### NASA Mars News ###
    url_news = 'https://mars.nasa.gov/news/'
    response_news = requests.get(url_news)
    soup_news = bs(response_news.text, 'lxml')
    news_title = soup_news.find('div', class_='content_title').get_text().strip()
    news_p = soup_news.find('div', class_='rollover_description_inner').get_text().strip()

    ### JPL Mars Space Images - Featured Image ###
    browser = Browser('chrome', headless = False)
    url_image = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_image)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(2)
    browser.click_link_by_partial_text('more info')
    time.sleep(2)
    browser.click_link_by_partial_text('.jpg')
    html = browser.html
    soup_image = bs(html, 'html.parser')
    featured_image_url = soup_image.find('img').get('src')
    browser.quit()

    ### Mars Weather ###
    url_twitter = 'https://twitter.com/marswxreport?lang=en'
    browser = Browser('chrome', headless = False)
    browser.visit(url_twitter)
    browser.find_by_css('article').click()
    html_weather = browser.html
    soup_twitter = bs(html_weather, 'html.parser')
    browser.quit()
    mars_weather_data = soup_twitter.find_all('span', class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')
    mars_weather = mars_weather_data[9].text.replace('\n', ' ')

    ### Mars Facts ###
    url_facts = 'https://space-facts.com/mars/'
    table = pd.read_html(url_facts)
    facts_table = table[0]
    facts_table.columns = ['Description', 'Values']
    facts_table_html = facts_table.to_html(header=False, index=False)

    ### Mars Hemispheres ###
    browser_hem = Browser('chrome', headless = False)
    url_hem = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser_hem.visit(url_hem)
    response_hem = requests.get(url_hem)
    soup_hem = bs(response_hem.text, 'html.parser')
    links = []
    for link in soup_hem.find_all('a'):
        links.append(link.get('href'))
    
    astro = 'https://astrogeology.usgs.gov'
    link1 = astro+links[4]
    link2 = astro+links[5]
    link3 = astro+links[6]
    link4 = astro+links[7]

    browser_hem.visit(link1)
    response_1 = requests.get(link1)
    soup_1 = bs(response_1.text, 'html.parser')
    title_1 = soup_1.h2.text
    link_img_1 = soup_1.li.a['href']
    browser_hem.back()

    browser_hem.visit(link2)
    response_2 = requests.get(link2)
    soup_2 = bs(response_2.text, 'html.parser')
    title_2 = soup_2.h2.text
    link_img_2 = soup_2.li.a['href']
    browser_hem.back()

    browser_hem.visit(link3)
    response_3 = requests.get(link3)
    soup_3 = bs(response_3.text, 'html.parser')
    title_3 = soup_3.h2.text
    link_img_3 = soup_3.li.a['href']
    browser_hem.back()

    browser_hem.visit(link4)
    response_4 = requests.get(link4)
    soup_4 = bs(response_4.text, 'html.parser')
    title_4 = soup_4.h2.text
    link_img_4 = soup_4.li.a['href']
    browser_hem.quit()

    hemisphere_image_urls = [{"title":title_1, "img_url": link_img_1},
                        {"title":title_2, "img_url": link_img_2},
                        {"title":title_3, "img_url": link_img_3},
                        {"title":title_4, "img_url": link_img_4}]

    ### DB Setup ###
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mars_db"]
    collection = db["mars_data"]
    mars_data = {"news_title":news_title,
            "news_p":news_p,
            "featured_image_url":featured_image_url,
            "mars_weather":mars_weather,
            "hemisphere_image_urls":hemisphere_image_urls,
            "facts_table":facts_table_html}

    collection.insert_one(mars_dict)
    return mars_data