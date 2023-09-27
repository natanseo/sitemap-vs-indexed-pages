import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import bs4
from time import sleep
from datetime import date
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


#below script collect index pages number from Google results.

page_types = ["cat/", "p/"]
markets = ["gb/en/", "ca/en/", "ca/fr/", "us/en/", "fr/fr/", "es/es/", "es/ca/", "es/en/", "es/gl/", "es/eu/",
               "de/de/", "se/sv/", "jp/ja/", "jp/en/", "nl/nl/", "nl/en/", "pl/pl/", "it/it/", "au/en/", "at/de/", "be/fr/",
               "be/nl/", "ch/de/", "ch/fr/", "ch/it/", "ch/en/", "no/no/", "fi/fi/", "cz/cs/", "dk/da/", "hu/hu/", "pt/pt/",
               "pt/en/", "kr/ko/", "kr/en/", "ie/en/", "hr/hr/", "ro/ro/", "sk/sk/", "rs/sr/", "in/en/", "ua/uk/", "si/sl/",
               "my/en/", "my/ms/", "sa/ar/", "sa/en/", "sg/en/", "ma/fr/", "ma/en/", "th/th/", "th/en/", "ae/en/", "qa/en/", 
               "bh/en/", "jo/en/", "jo/ar/", "kw/en/", "kw/ar/", "eg/en/", "cz/en/", "il/he/", "cl/es/", "bh/ar/","eg/ar/", "ae/ar/",
               "ma/ar/", "om/ar/", "qa/ar/", "be/en/", "cn/en/", "mx/en/", "om/en/", "ph/en/", "mx/es/", "ru/ru/", "cn/zh/"]

placeholder_url = "https://www.ikea.com/{}{}"
urls = {}
final_index_list = {}

for a in markets:
    if a not in urls:
        urls[a] = []
    for b in page_types:
        url = placeholder_url.format(a, b)
        urls[a].append(url)
    
for x,y in urls.items():
    if x not in final_index_list:
        final_index_list[x] = []
    
    for url in y:
        total = 0
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        google_serp_url = f"https://www.google.com/search?q=site:{url}"
        google_request = requests.get(google_serp_url,headers={"User-Agent":ua})
        google_html = bs4.BeautifulSoup(google_request.text,"html.parser")
        indexed_pages = google_html.find(id="result-stats")
        serp_res = indexed_pages.text.split("Ungefär")[1].split(" resultat")[0]
        serp_res = serp_res.encode('ascii','ignore')
        total += int(serp_res)
        sleep(50)
        final_index_list[x].append(total)

newdf = pd.DataFrame.from_dict(final_index_list, orient='index')
newdf.reset_index(inplace=True)
final = newdf.rename(columns = {"index":"Market", 0:"Indexed_PLPs", 1:"Indexed_PIPs"})

#below script parses sitemaps and counts pages against page type.

df = pd.read_xml("https://www.ikea.com/sitemaps/sitemap.xml")    #enter index sitemap address here.

total_cat = {}
total_collections = {}
total_series = {}
total_filters = {}
total_veta = {}
total_editorial = {}
total_contentgallery = {}
total_planners = {}
total_events = {}
pips = {}

for a in df["loc"]:   #getting all product sitemaps for market in dictionary i.e. 'ae-AR':[sitemap1, sitemap2]
    if "/prod" in a:
        pips.setdefault(a[35:40], []).append(a)
    
for key, value in pips.items():   #counting all urls against a market sitemaps and returning to pips{} i.e. 'ae-AR': : 21172,
    total = 0
    #print(key,value)
    for url in value:

        df1 = pd.read_xml(url)
        all_urls = df1["loc"].count()
        total += all_urls

    pips[key] = total

for a in df["loc"]: #for sitemap urls
    
    if "/cat-" in a:   
        df1 = pd.read_xml(a)
        total_urls = df1["loc"].count()
        total_cat[a[34:39]] = total_urls   #extracting market name with index a[xx:yy]
    
    elif "/collection-" in a:   
        df2 = pd.read_xml(a)
        total_urls = df2["loc"].count()
        total_collections[a[41:46]] = total_urls
        
    elif "/series-" in a:   
        df3 = pd.read_xml(a)
        total_urls = df3["loc"].count()
        total_series[a[37:42]] = total_urls
        
    elif "/catalogfilter-" in a:   
        df4 = pd.read_xml(a)
        total_urls = df4["loc"].count()
        total_filters[a[44:49]] = total_urls
        
    elif "/veta-" in a:   
        df5 = pd.read_xml(a)
        total_urls = df5["loc"].count()
        total_veta[a[35:40]] = total_urls
        
    elif "/edit-" in a:   
        df6 = pd.read_xml(a)
        total_urls = df6["loc"].count()
        total_editorial[a[35:40]] = total_urls
        
    elif "/contentgallery-" in a:   
        df7 = pd.read_xml(a)
        total_urls = df7["loc"].count()
        total_contentgallery[a[45:50]] = total_urls
    
    elif "/planner-" in a:   
        df8 = pd.read_xml(a)
        total_urls = df8["loc"].count()
        total_planners[a[38:43]] = total_urls
        
    elif "/store-events" in a:   
        df9 = pd.read_xml(a)
        total_urls = df9["loc"].count()
        total_events[a[43:48]] = total_urls
        
def all_in_one(): #merging all dictionaries in one df and adding a Total column
    
    res = pd.DataFrame.from_dict([total_cat, total_collections, total_series, total_filters, total_veta, total_editorial, total_contentgallery, total_planners, total_events, pips], dtype=object).T
    res.reset_index(inplace=True)
    res.rename(columns = {"index":"Market", 0:"Categories", 1:"Collections", 2:"Series", 3:"Filters", 4:"Veta", 5:"Editorial", 6:"Insp. Feed", 7:"Planners", 8:"Events", 9:"Products"}, inplace = True)
    res.fillna(0, inplace=True)
    res["Total"] = res.iloc[:, 1:11].sum(axis=1)
    return res

sitemap = all_in_one()

def rearrangement():  #rearrnage both dataframes, indexed vs sitemaps for PLPs and PIPs.

    sitemap["Market"] = sitemap["Market"].str.lower()
    sitemap["Market"] = sitemap["Market"].str[3:]+"/"+sitemap["Market"].str[:2]+"/"
    df_merged = pd.merge(final, sitemap, on="Market", how="outer")
    df_merged["Total_Cats"] = df_merged.iloc[:, 3:7].sum(axis=1)  #total of categories, collections, series and filters 
    df_merged = df_merged[["Market", "Categories", "Collections", "Series", "Filters", "Total_Cats", "Indexed_PLPs", "Veta", "Editorial", "Insp. Feed", "Planners",
    "Events", "Products", "Indexed_PIPs", "Total"]]   #rearranging columns
    df_merged = df_merged.fillna(0)   #replacing NaN values with 0
    df_merged[["Indexed_PLPs", "Indexed_PIPs"]] = df_merged[["Indexed_PLPs", "Indexed_PIPs"]].astype(int)  #change float values to int in plp and pips
    return df_merged

#rearrangement() #call this function to print the data in a dataframe.
