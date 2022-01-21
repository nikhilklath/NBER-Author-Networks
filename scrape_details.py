import pandas as pd
import os
import numpy as np
import re
import string
import math
import time
import json
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import math
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import lxml
from pprint import pprint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import winsound


def solve_captcha():
    Freq = 1500  # Set Frequency To 2500 Hertz
    Dur = 500  # Set Duration To 1000 ms == 1 second
    winsound.Beep(Freq, Dur)
    input('Please, solve the CAPTCHA and press ENTER: ')


def scrape_data_for_paper(paper_title, out):
    EXE_PATH = r"C:\Users\nik596\Downloads\chromedriver_win32\chromedriver.exe"
    browser = webdriver.Chrome(executable_path=EXE_PATH)
    browser.maximize_window()
    base = "https://scholar.google.com"
    browser.get(base)
    browser.implicitly_wait(10)

    browser.find_element(By.ID, "gs_hdr_tsi").send_keys(paper_title)
    browser.find_element(By.ID, "gs_hdr_tsb").click()
    html = browser.page_source
    """try:
        cap=browser.find_element(By.ID, "gs_captcha_ccl").text
        print(cap, " 1", type(cap))
        if cap.find("robot") > 0:
            print("Captcha Found")
            solve_captcha()
    except: 
        print("No Captcha")"""
    soup = BeautifulSoup(html, 'html.parser')
    a_dicts = {}

    for item in soup.find_all('div', class_="gs_r gs_or gs_scl"):
        if paper_title.lower() in item.text.lower():
            if "nber.org" in item.text:
                print("Found on NBER")
            for link in item.find('div', class_='gs_a').find_all('a'):
                a_dict = {}
                a_link = base + link.get('href')
                a_dict['abb_name'] = link.get_text()
                print(a_dict)
                browser.get(a_link)
                """try:
                    cap=browser.find_element(By.ID, "gs_captcha_ccl").text
                    print(cap, " 2")
                    if cap.find("Please show you're not a robot") > 0:
                        print("Captcha Found")
                        solve_captcha()
                except: 
                    print("No Captcha")"""
                temp1 = ''
                temp2 = BeautifulSoup(browser.page_source, 'html.parser').find('span', id="gsc_bpf_more")
                attempt = 1
                while str(temp1) != str(temp2) or attempt < 5:
                    if str(temp1) != str(temp2):
                        attempt = 1
                    temp1 = BeautifulSoup(browser.page_source, 'html.parser').find('button', id="gsc_bpf_more")
                    print("page extended")
                    browser.find_element(By.ID, "gsc_bpf_more").click()
                    print(browser.find_element(By.ID, "gsc_a_nn").text)
                    temp2 = BeautifulSoup(browser.page_source, 'html.parser').find('button', id="gsc_bpf_more")
                    attempt += 1
                a_html = browser.page_source
                a_soup = BeautifulSoup(a_html, 'html.parser')
                a_dict['name'] = a_soup.find('div', id='gsc_prf').find('div', id='gsc_prf_in').get_text()
                i = 0
                for paper in a_soup.find('tbody', id='gsc_a_b').find_all('tr', class_='gsc_a_tr'):
                    paper_dict = {'name': paper.find('td', class_='gsc_a_t').find('a').get_text()}
                    print(paper_dict)
                    proxies = {
                        'http': os.getenv('HTTP_PROXY')  # or just type proxy here without os.getenv()
                    }
                    headers = {
                        'User-agent':
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edge/18.19582"
                    }
                    #browser.get(base + paper.find('td', class_='gsc_a_t').find('a').get('href'))
                    paper_html = requests.get(base + paper.find('td', class_='gsc_a_t').find('a').get('href'),
                                              headers=headers, proxies=proxies)
                    """try:
                        cap=browser.find_element(By.ID, "gs_captcha_ccl").text
                        print(cap, " 3")
                        if cap.find("Please show you're not a robot") > 0:
                            print("Captcha Found")
                            solve_captcha()
                    except: 
                        print("No Captcha")"""
                    #paper_html = browser.page_source
                    paper_soup = BeautifulSoup(paper_html.text, 'html.parser')
                    table = paper_soup.find('div', id='gsc_oci_table')
                    for row in table.find_all('div', class_='gs_scl'):
                        field = row.find('div', class_='gsc_oci_field').text
                        value = row.find('div', class_='gsc_oci_value')
                        if field == 'Total citations':
                            if len(row.find_all('div', id='gsc_oci_graph_bars')) < 1:
                                paper_dict['total_citations'] = value.find('a').text
                                continue
                            years = [x.get_text() for x in row.find_all('div', id='gsc_oci_graph_bars')[0].find_all('span',class_='gsc_oci_g_t')]
                            num = [x.get_text() for x in row.find_all('div', id='gsc_oci_graph_bars')[0].find_all('a', class_='gsc_oci_g_a')]
                            paper_dict['Citations'] = {years[i]: num[i] for i in range(len(num))}
                            paper_dict['total_citations'] = value.find('a').text
                        elif field == 'Scholar articles':
                            continue
                        else:
                            paper_dict[field] = value.text
                    a_dict['paper_' + str(i)] = paper_dict
                    i += 1
                if a_soup.find_all('div', class_='gsc_md_hist_b') is not None:
                    years = [x.get_text() for x in a_soup.find_all('div', class_='gsc_md_hist_b')[0].find_all('span', class_='gsc_g_t')]
                    num = [x.get_text() for x in a_soup.find_all('div', class_='gsc_md_hist_b')[0].find_all('a', class_='gsc_g_a')]
                    a_dict['citations'] = {years[i]: num[i] for i in range(len(num))}
                a_dicts[a_dict['abb_name']] = a_dict
            break
        else:
            continue

    if os.path.exists(out + r'/data.json'):
        with open(out + '/data.json', mode='r', encoding='utf-8') as feedsjson:
            feeds = json.load(feedsjson)
        feeds[paper_title] = a_dicts
    else:
        feeds = {paper_title: a_dicts}

    with open(out + r'/data.json', 'w', encoding='utf-8') as feedsjson:
        print("dumping data for ", paper_title)
        json.dump(feeds, feedsjson, indent=4)
    browser.close()
    return a_dicts

path = r"D:\Winter 2020\NBER Analysis/"
out = r"D:\Spring 2022"

df1 = pd.read_excel(path + "NBER_detailed.xlsx")
new = df1["paper month"].str.split(" ", n=1, expand=True)
df1["month"] = new[0]
df1["year"] = new[1]
df1.drop(columns=["paper month"], inplace=True)
df1 = df1[df1['year'].apply(lambda x: 1981 <= int(x) <= 2020)]
papers_list = list(df1['paper'])

if os.path.exists(out + r'/data.json'):
    with open(out + '/data.json', mode='r', encoding='utf-8') as feedsjson:
        feeds = json.load(feedsjson)
    print(len(feeds))
    #feeds = {paper:feeds[paper] for paper in feeds if len(feeds[paper]) > 0}
    #print(len(feeds))
    found_papers = set(feeds.keys())
    papers_not_found = [paper for paper in papers_list if paper not in found_papers ]
else:
    papers_not_found = papers_list

new_dict = {}
for paper in papers_not_found:
    print(paper)
    new_dict[paper] = scrape_data_for_paper(paper, out)
    #if len(new_dict[paper]) > 0:
    #    break
