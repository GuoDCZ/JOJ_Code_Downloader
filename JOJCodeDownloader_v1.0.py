import os
import requests
from bs4 import BeautifulSoup
import wget
import zipfile
import rarfile
import csv
import shutil
import json


# py -m py_compile trial.py

def main():

    while True:
        
        global interval, cookie, url

        config = json.load(open('./config.json'))
        url = config[config['useWhich']]
        section = int(config['section'])  # "0" for no limit, "1" for S2-s1, "2" for S2-s2, "3" for 9/27's lab
        sid = "4f1b7eac1ce96fa26490aa035488b5dae52f7295dedde7c6a6ebaf10340725a2"
        cookie = {"save": "1", "sid": sid}

        if section > 0:
            with open('section.csv', 'r') as csvfile:
                rdr = csv.reader(csvfile)
                studentID = [row[section] for row in rdr]

        pre_page = requests.get(url, cookies=cookie).text
        pre_soup = BeautifulSoup(pre_page, 'html.parser')
        dir_ = './' + pre_soup.find("h1", class_="location-current").get_text().replace("\n", "").replace(" ", "").replace(
            ":", "").replace("'", "") + '/'

        if os.path.exists(dir_):
            shutil.rmtree(dir_)
        if os.path.exists('./zips/'):
            shutil.rmtree('./zips/')
        os.mkdir(dir_)
        os.mkdir(r'./zips')

        page = requests.get(url + "/scoreboard", cookies=cookie).text
        soup = BeautifulSoup(page, 'html.parser')

        post_list = soup.find_all("tr")
        for post in post_list:

            if not post.find_all("td"):
                continue
            if not post.find("td", class_="col--problem_detail").find("a"):
                continue

            uid = post.find("td", class_="col--uid").get_text().replace("\n", "").replace(" ", "")
            if section > 0:
                if not (uid in studentID):
                    continue
            rank = post.find("td", class_="col--rank").get_text().replace("\n", "").replace(" ", "")
            score = post.find("td", class_="col--total_score").get_text().replace("\n", "").replace(" ", "")
            name = post.find('a').get_text().replace("\n", "").replace(" ", "")
            link_list = post.find_all("td", class_="col--problem_detail")
            print('\n', rank, uid, score, name)
            info = rank + '-' + score + '-' + name + '-' + uid
            os.mkdir(dir_ + info + '/')

            it = 0
            if len(link_list) == 1:
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

        input("\nagain?")


if __name__ == '__main__':
    main()
