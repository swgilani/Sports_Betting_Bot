import requests
from bs4 import BeautifulSoup


def imageSearch(word):
    url = f'https://www.google.com/search?q={word}&tbm=isch&ved=2ahUKEwis94D8ocDwAhUVHs0KHUE-CgUQ2-cCegQIABAA&oq=mma&gs_lcp=CgNpbWcQAzIECCMQJzIECCMQJzIFCAAQsQMyBQgAELEDMgUIABCxAzIICAAQsQMQgwEyAggAMggIABCxAxCDATICCAAyBQgAELEDULEcWOAdYKMeaABwAHgAgAFUiAFUkgEBMZgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=acGZYOyeL5W8tAbB_Kgo&bih=653&biw=1280&rlz=1C1CHBF_enCA948CA948'
    content = requests.get(url).content
    soup = BeautifulSoup(content,'lxml')
    images = soup.findAll('img')

    for image in images:    
        img_src = str(image.get('src'))
        img_height = image.get('height')
        img_width = image.get('height')

        if img_src.startswith("http"):
            return image.get('src')

    return None