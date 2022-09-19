import os
import requests
from bs4 import BeautifulSoup
import wget
import zipfile
import rarfile
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

    pre_page = requests.get(url, cookies=cookie).text
    pre_soup = BeautifulSoup(pre_page, 'html.parser')
    dir_ = './' + pre_soup.find("h1", class_="location-current").get_text().replace("\n", "").replace(" ", "").replace(":", "").replace("'", "") + '/'
    
    if os.path.exists(dir_):
        shutil.rmtree(dir_)
    if os.path.exists('./zips/'):
        shutil.rmtree('./zips/')
    os.mkdir(dir_)
    os.mkdir(r'./zips')

    page = requests.get(url+"/scoreboard", cookies=cookie).text
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
        link_list = post.find_all("td", class_="col--problem_detail")
        print('\n', rank, uid, score, name)
        info = rank + '-' + score + '-' + name + '-' + uid
        os.mkdir(dir_ + info + '/')

        it = 0
        if len(link_list) == 0:
            it = -1

        for raw_link in link_list:

            it = it + 1
            multi_p = ""
            if it > 0:
                multi_p = "p" + str(it) + '/'
                os.mkdir(dir_ + info + "/" + multi_p)

            if not raw_link.find("a"):
                continue

            link = raw_link.find("a").get("href")
            url = "https://joj.sjtu.edu.cn" + link + "/code"
            r = requests.get(url, cookies=cookie)

            wget.download(r.url, out='./zips/' + info + "_" + str(it))

            if zipfile.is_zipfile('./zips/' + info + "_" + str(it)):
                f = zipfile.ZipFile('./zips/' + info + "_" + str(it), 'r')
                f.extractall(dir_ + info + '/' + multi_p)
                f.close()
            elif rarfile.is_rarfile('./zips/' + info + "_" + str(it)):
                z = rarfile.RarFile('./zips/' + info + "_" + str(it), 'r')
                z.extractall(dir_ + info + '/' + multi_p)
                z.close()
            else:
                print(info + "_" + str(it) + " is not a zip/rar file")


if __name__ == '__main__':
    main()
