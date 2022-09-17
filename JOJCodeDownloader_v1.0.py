import os
import requests
from bs4 import BeautifulSoup
import wget
import zipfile
import csv
import time


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
        elif line[0] == "tar":
            target = line[1]
        elif line[0] == "dir":
            dir_ = line[1]
        elif line[0] == "pre":
            prefix = line[1]
        elif line[0] == "suf":
            suffix = line[1]
        elif line[0] == "gap":
            interval = int(line[1])
    page = requests.get(url, cookies=cookie).text
    soup = BeautifulSoup(page, 'html.parser')
    while 1:
        if not os.path.exists('./zips'):
            os.mkdir(r'./zips')
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
            print(rank, uid, score, name)
            url = "https://joj.sjtu.edu.cn" + link + "/code"
            r = requests.get(url, cookies=cookie)
            filename = rank + '-' + score + '-' + name + '-' + uid
            if os.path.exists('./zips/' + filename + ".zip"):
                os.remove('./zips/' + filename + ".zip")
            wget.download(r.url, out='./zips/' + filename + ".zip")
            if not zipfile.is_zipfile('./zips/' + filename + ".zip"):
                print(filename + " is not a zip file")
                continue
            f = zipfile.ZipFile('./zips/' + filename + ".zip", 'r')
            f.extract(target, dir_)
            if os.path.exists(dir_ + prefix + filename + suffix):
                if not os.path.samefile(dir_ + target, dir_ + prefix + filename + suffix):
                    os.remove(dir_ + prefix + filename + suffix)
                    os.rename(dir_ + target, dir_ + prefix + filename + suffix)
            else:
                os.rename(dir_ + target, dir_ + prefix + filename + suffix)
        print("\nLast Update: " + time.strftime('%H:%M:%S', time.localtime(time.time())))
        print("\nNext Update: " + time.strftime('%H:%M:%S', time.localtime(time.time() + interval)))
        time.sleep(interval)


if __name__ == '__main__':
    main()
