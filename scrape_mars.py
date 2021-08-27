from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd


def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # Visit visitcostarica.herokuapp.com
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # add in a pause to allow site to fully load before creating html object
    time.sleep(3)

    # create html object
    html = browser.html

    # create a beautiful soup object
    soup = bs(html, 'html.parser')

    # collect the latest news title and paragraph text
    news_title = soup.find("div", class_='list_text').find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

    # visit Mars images url through splinter module
    image_url = "https://www.jpl.nasa.gov/spaceimages/"
    browser.visit(image_url)

    # navigate website by clicking on "full image"
    browser.click_link_by_id('full_image')

    # pause a second before second click of "more info" to get final large image
    time.sleep(1)
    browser.click_link_by_partial_text('more info')

    # add in a pause to allow site to fully load before creating html object
    time.sleep(3)

    # create html object
    html_image = browser.html

    # create a beautiful soup object
    soup = bs(html_image, 'html.parser')

    # find the image url
    image_url = soup.find('figure', class_='lede').a['href']

    # add in the home page to the featured image url to get full image url
    featured_image_url = f'https://www.jpl.nasa.gov{image_url}'
    #print(featured_image_url)

    # visit Mars weather Twitter url through splinter module
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)

    # add in a pause to allow site to fully load before creating html object
    time.sleep(3)

    # create html object
    html = browser.html

    # create a beautiful soup object
    soup = bs(html, 'html.parser')

    # find all tweets
    tweets = soup.find_all('div', lang='en')

    # loop through tweets to find first most recent weather tweet
    for tweet in tweets:
        tweet_text = tweet.text
        
        # if statement to find "insight" text identifying it as a weather tweet
        if 'InSight' in tweet_text:
            mars_weather = tweet_text
            break
        else:
            pass
    # print(mars_weather)

   # visit Mars facts url through splinter module
    facts_url = 'https://space-facts.com/mars/'

    # scrape table data using pandas
    mars_facts_df = pd.read_html(facts_url) 

    # return only first table
    mars_facts_df = mars_facts_df[0]

    # rename columns
    mars_facts_df = mars_facts_df.rename(columns = {0: "Description", 1: "Value"})

    # set index on description
    mars_facts_df.reset_index(inplace = True, drop=True)

    # convert the table to an html file
    mars_facts_html = mars_facts_df.to_html("mars_facts.html", index=False)
    
    # convert dataframe to html string
    mars_facts_html = mars_facts_df.to_html()

    # clean up html table
    mars_facts_html.replace('\n', '')
    
    # visit Mars hemisphere url through splinter module
    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemi_url)

    # add in a pause to allow site to fully load before creating html object
    time.sleep(3)

    # create html object
    html = browser.html

    # create a beautiful soup object
    soup = bs(html, 'html.parser')

    # create list to house img title and urls
    hemi_info = []

    # retrieve all elements that contain image information
    results = soup.find("div", class_ = "result-list")
    hemis = results.find_all("div", class_="item")

    # home url will serve as the first half of image links to click
    home_url = "https://astrogeology.usgs.gov/"

    # for loop to loop through items and append to list
    for hemi in hemis:
        title = hemi.find("h3").text
        title = title.replace(" Enhanced", "")
        
        # find the last part of the url to create a link to click
        part_url = hemi.find('a', class_='itemLink product-item')['href']
        image_link = home_url + part_url    
        browser.visit(image_link)
        
        # pause to allow page to load and get new page's html
        time.sleep(3)
        html = browser.html
        soup = bs(html, "html.parser")
        
        # find the end of the full size image url and combine with home_url
        image_url = home_url + soup.find('img', class_='wide-image')['src']
        
        # append title and image url to hemi_info
        hemi_info.append({"title": title, "image_url": image_url})

    mars_data = {
        "Mars_News_Title": news_title,
        "Mars_News_Paragraph": news_p,
        "Mars_Featured_Image": featured_image_url,
        "Mars_Weather_Data": mars_weather,
        "Mars_Facts": mars_facts_html,
        "Mars_Hemisphere_Images": hemi_info
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
