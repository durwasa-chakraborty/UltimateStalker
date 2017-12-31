#!/usr/bin/env python3
from sys import argv
import datetime
import urllib
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import json

# Help Function
def Help():
    print ('Instagram Image Downloader')
    print ('-u [Instagram Handle] [Instagram Pages] ')
    print ('-h [help]')
    print ('Example')
    print ('python app.py -u @Handle 3')

# Download File
# URL -> Downloads an Image in the root folder

def download_file(handle, fileURL):
    print 'Downloading ' + fileURL
    f = urllib.urlopen(fileURL)
    page = f.read()
    soup = BeautifulSoup(page,'html.parser')
    metaTag = soup.find_all('meta',attrs={'property':'og:image'})
    img = metaTag[0]['content']
    cwd = os.path.join(os.getcwd(),handle)
    if not os.path.exists(cwd):
        os.makedirs(cwd)
    filename = handle[1:]+datetime.datetime.now().strftime("%Y-%b-%d_%H:%M:%S")+'.jpg'
    filename_cwd = os.path.join(cwd,filename)
    urllib.urlretrieve(img,filename_cwd)



# Given  : Page dictionary
# Returns : Boolean
def is_graph_image(d):
    return "__typename" in d \
        and d["__typename"] == "GraphImage" \
        and not d["is_video"]

# Given : Image List
# Returns : A code
def parse_images(img_list):
    codes = []
    for img in img_list:
        print("Found one: " + img["code"])
        codes.append(img["code"])
    return codes

# Given : Value from a key-value pair
# Returns : A list of Codes
def parse_profile_page(prof_page):
    if "user" in prof_page:
        prof_page = prof_page["user"] #Destructive Update
        if "media" in prof_page:
            prof_page = prof_page["media"]
            if "nodes" in prof_page:
                imgs = filter(is_graph_image, prof_page["nodes"])
                return parse_images(imgs)
    return []
        
# Extract URL from Handle
# Returns A List

def extract_image_URLs(url):

    f = urllib.urlopen(url)
    page = f.read()
    soup = BeautifulSoup(page,'html.parser')
    script = soup.find_all('script')
    display_src = script[2].text[21:-1].encode("utf-8")
    profile_data = json.loads(display_src)
    codes = []
    for key, val in profile_data["entry_data"].iteritems():
        if key == "ProfilePage":
            for item in val:
                codes += parse_profile_page(item)
    return map(lambda x: "https://instagram.com/p/"+x, codes)


# Given: User handle and page requests

def pages(handle, n):
    url = "https://www.instagram.com/"+handle[1:]
    driver = None
    for i in range(n):
        try:
            yield extract_image_URLs(url)
            if driver is None:
                driver = webdriver.PhantomJS()
                driver.implicitly_wait(10)
            driver.get(url)
            url = driver.find_element_by_css_selector("#react-root > section > main > article > div:nth-child(4) > a").get_attribute('href')
        except:
            print ("Failed on page: " + str(i + 1))
            break
    if driver is not None:
        driver.close()

if __name__ == "__main__":
    if len(argv) is not 4:
        Help()
        
    elif argv[1] == '-u':
        handle = argv[2]
        n = int(argv[3])
        gen = pages(handle, n)
        curPage = 0
        while True:
            print("Loading page: " + str(curPage))
            curPage+=1
            nextUrls = next(gen, None)
            if nextUrls is None:
                break
            for fileURL in nextUrls:
                download_file(handle, fileURL)
    else:
        Help()
                

