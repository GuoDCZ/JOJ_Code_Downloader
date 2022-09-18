import os
import requests
from bs4 import BeautifulSoup
import wget
import zipfile
import csv
import shutil


# py -m py_compile trial.py

def main():
    global interval, cookie, url
    config_file = open('./config.csv')
    config = csv.reader(config_file)
    for line in config:
        if line[0] == "sid":
            cookie = {"save": "1", "sid": line[1]}
        elif line[0] == "url":
            url = line[1]
        elif line[0] == "dir":
            dir_ = line[1]

    dir_ = './' + dir_
    if os.path.exists(dir_):
        shutil.rmtree(dir_)
    if os.path.exists('./zips/'):
        shutil.rmtree('./zips/')
    os.mkdir(dir_)
    os.mkdir(r'./zips')

    page = requests.get(url, cookies=cookie).text
    soup = BeautifulSoup(page, 'html.parser')

    post_list = soup.find_all("tr")
    for post in post_list:
        if not post.find_all("td"):
            continue
        if not post.find("td", class_="col--problem_detail").find("a"):
            continue
        rank = post.find("td", class_="col--rank").get_text().replace("\n", "").replace(" ", "")
        uid = post.find("td", class_="col--uid").get_text().replace("\n", "").replace(" ", "")
        score = post.find("td", class_="col--total_score").get_text().replace("\n", "").replace(" ", "")
        name = post.find('a').get_text().replace("\n", "").replace(" ", "")
        link = post.find("td", class_="col--problem_detail").find("a").get("href")
        print('\n', rank, uid, score, name)
        url = "https://joj.sjtu.edu.cn" + link + "/code"
        r = requests.get(url, cookies=cookie)
        info = rank + '-' + score + '-' + name + '-' + uid

        wget.download(r.url, out='./zips/' + info + ".zip")
        os.mkdir(dir_ + info + '/')

        if not zipfile.is_zipfile('./zips/' + info + ".zip"):
            print(info + " is not a zip file")
            continue

        f = zipfile.ZipFile('./zips/' + info + ".zip", 'r')
        f.extractall(dir_ + info + '/')


if __name__ == '__main__':
    main()
