#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 15:32:28 2020

@author: shyambhu.mukherjee
"""

from selenium import webdriver
import pandas as pd
import time
import requests
import json

login_header =  {"Host": "upvotocracy.com",
                 "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
                 "Accept": "*/*",
                 "Accept-Language": "en-US,en;q=0.5",
                 "Accept-Encoding": "gzip, deflate, br",
                 "Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7Imthcm1hIjoxMjE4LCJ1c2VybmFtZSI6InNoeWFtY29keTIwIiwibGlua3MiOlt7Il9pZCI6IjVlYTFmYjdmYjYzMGQ2MDAxZGQ5MjVlMCIsIm5hbWUiOiJzaHlhbWNvZHkiLCJ1cmwiOiJodHRwczovL3d3dy5zaHlhbWJodTIwLmJsb2dzcG90LmNvbSJ9XSwiY3JlYXRlZCI6IjIwMjAtMDQtMTlUMjI6MTU6NDcuNTc0WiIsImJpdGNvaW5BZGRyZXNzIjoiYmMxcTQ0a3Z0bGMzYWphYWN1NGZzOGVjNmpta2ZuaG1tNHl1Z2o4OW1oIiwiaWQiOiI1ZTljY2Q5M2QwZmYzMjAwMWM1ZmM3OGIifSwiaWF0IjoxNTg4Nzg3ODQ5LCJleHAiOjE1ODkzOTI2NDl9.KLz0L5oR7qD5WdguUz-MLmvImf9jOD0yXk7eFoR614k",
                 "Content-Type": "application/json; charset = utf-8",
                 "Origin": "https://upvotocracy.com",
                 "Referer": "https://upvotocracy.com/compose",
                 "Cookie": "_ga=GA1.2.525460825.1587334127; _gid=GA1.2.1420232059.1588693559",
                 "TE": "Trailers"}

def take_src(string):
    start_index = string.find('img src')
    end_index = start_index + 7
    endpoints = []
    for i in range(end_index,len(string)):
        if string[i] =='"':
            endpoints.append(i)
        if len(endpoints)>1:
            break
    if len(endpoints) == 0:
        return ''
    return string[endpoints[0]+1:endpoints[1]]

def Perform_rss_scrape(target_page):
    Item_list = []
    driver=webdriver.Firefox(executable_path="/home/shyambhu.mukherjee/Downloads/geckodriver.exe")
    try:
        driver.get(target_page)
    except:
        print("url error for ",target_page)
    AllItems = driver.find_elements_by_tag_name('item')
    for item in AllItems:
        curr_dict = {'type':'link','text':'null'}
        curr_dict['title'] = item.find_element_by_tag_name('title').get_attribute('textContent')
        curr_dict['url'] = item.find_element_by_tag_name('link').get_attribute('textContent')
        if 'onion' in target_page:
            curr_dict['thumb'] = take_src(item.find_element_by_tag_name('description').get_attribute('textContent'))
        elif 'cbn.com' in target_page:
            curr_dict['thumb'] = item.find_element_by_tag_name('thumbnail').get_attribute('textContent')
        else:
            curr_dict['thumb'] = ""
        for spec in ['title','url','thumb']:
            curr_dict[spec] = curr_dict[spec].strip('\n')
        Item_list.append(curr_dict)
    time.sleep(5)
    driver.close()
    return Item_list

def Perform_rss_scrape_thumb_definite(target_page):
    Item_list = []
    driver=webdriver.Firefox(executable_path="/home/shyambhu.mukherjee/Downloads/geckodriver.exe")
    try:
        driver.get(target_page)
    except:
        print("url error for ",target_page)
    AllItems = driver.find_elements_by_tag_name('item')
    for item in AllItems:
        curr_dict = {'type':'link','text':'null'}
        curr_dict['title'] = item.find_element_by_tag_name('title').get_attribute('textContent')
        curr_dict['url'] = item.find_element_by_tag_name('link').get_attribute('textContent')
        #send fetch request now:
        fetched_cont = requests.get(url = "https://upvotocracy.com/api/1/retrieve",
                                    headers = login_header,
                                    params = {"url":curr_dict['url']})
        fetched_dict = dict(fetched_cont.json())
        try:
            curr_dict['thumb'] = fetched_dict['thumb']
        except:
            curr_dict['thumb'] = ""
        Item_list.append(curr_dict)
    time.sleep(5)
    driver.close()
    return Item_list
def post_document(dict_lists,api_url,category):
    for basic_dict in dict_lists:
        
        basic_dict['category'] = category
        basic_dict['type'] = "link"
        basic_dict['text'] = "null"
        json_post = json.dumps(basic_dict)
        print(type(json_post))
        actual_json = json.loads(json_post)
        print(actual_json)
        req = requests.post(api_url,headers = login_header,json = actual_json)
        print(req)

def perform_scrape_post(target_page,api_url,category):
    Item_lists = Perform_rss_scrape_thumb_definite(target_page)
    print(len(Item_lists))
    post_document(Item_lists,api_url,category)

perform_scrape_post(target_page = 'https://www.theonion.com/rss',
                    api_url = "https://upvotocracy.com/api/1/posts",
                    category = '5e7bf4ec891cb9001cf00ddd')
    

market_urls = ["https://blog.hubspot.com/marketing/rss.xml"]
javascript_urls = ["https://www.echojs.com/rss"]
perform_scrape_post(target_page = market_urls[0],
                    api_url = "https://upvotocracy.com/api/1/posts",
                    category = '5e4e3a4d5a6930001d9badb0')
perform_scrape_post(target_page = javascript_urls[0],
                    api_url = "https://upvotocracy.com/api/1/posts",
                    category = '5e4dac375a6930001d9bad98')

"""
Next stop: work on search engine journal rss feed for marketing page.
"""