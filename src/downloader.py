import sys, os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


import requests, time, selenium, os, pdfplumber, codecs
from selenium import webdriver
from bs4 import BeautifulSoup
from src import config

import db.interface as db
from log.logger import logger as log
from src.mail import send_mail

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(os.path.join(os.path.dirname(__file__), "chromedriver.exe"), chrome_options=chrome_options)

def get_all_info():
    '''
    动态ajax, 用浏览器获取数据比较方便
    :return: 
    '''
    current_projects = db.read_data()
    projects = []
    browser.get("http://kcb.sse.com.cn/renewal/")
    work_flag = True
    while work_flag:
        time.sleep(5) # 等待页面加载
        hrefs = browser.find_elements_by_css_selector("#dataList1_container>tbody>tr:not(:first-child) td:nth-child(2)>a")
        for href in hrefs:
            title = href.text.replace("<br>","").replace("\n","")
            if len(current_projects) and title == current_projects[0]["title"]:
                work_flag = False
                break
            else:
                projects.append({
                    "title": title,
                    "link": href.get_attribute("href")
                })
        if work_flag:
            try:
                browser.find_element_by_css_selector("a.paging_next").click()
            except selenium.common.exceptions.NoSuchElementException:
                work_flag = False
                log.info("all data loaded!")
                break
        log.info("reading projects...")
        log.info(projects)
    current_projects = projects + current_projects # 保证数据库中第一个数据是最新的.
    db.write_data(current_projects)
    # browser.close()

def dowload_pdf_and_convert():
    projects = db.read_data()
    for project in projects:
        if project.get("downloaded"):
            pass
        else:
            browser.get(project["link"])
            time.sleep(5)
            href = browser.find_elements_by_css_selector("tr#tile30 td.vs1 a")
            if len(href) != 1:
                log.error("web format changed, cannot find downloadlink")
                break
            else:
                href = href[0]
                pdf_file = requests.get(href.get_attribute("href"), stream=True)
                with open("..\\data\\{}.pdf".format(project.get("title")), "wb") as f:
                    for chunk in pdf_file.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                project["downloaded"] = time.strftime("%d_%m_%Y")
                log.info("{} has been downloaded.".format(project.get("title")))

                try:
                    with pdfplumber.open("..\\data\\{}.pdf".format(project.get("title"))) as pdf:
                        txt_filename = project.get("title") + ".txt"
                        with codecs.open("..\\data\\{}".format(txt_filename), "w", encoding="utf-8") as new_f:
                            for page in pdf.pages:
                                new_f.write(page.extract_text())
                    log.info("{} had been converted.".format(project.get("title")))
                except:
                    log.error("{} had convert failed.".format(project.get("title")))

    db.write_data(projects)

def check_and_notify():
    projects = db.read_data()
    notify_flag = False
    message = "{}:\n".format(time.strftime("%Y/%m/%d"))
    for project in projects:
        if project.get("downloaded") == "14_12_2019": # time.strftime("%d_%m_%Y")
            keyword_cnt = {}
            keywords = config.keywords.split(",")
            with open("..\\data\\{}".format(project.get("title") + ".txt"),"r", encoding="utf-8") as f:
                content = f.read()
                for keyword in keywords:
                    keyword_cnt[keyword] = content.count(keyword)
            keyword_threshold_cnt = 0
            for k,v in keyword_cnt.items():
                keyword_threshold_cnt += v
            if keyword_threshold_cnt >= config.keyword_threshold:
                notify_flag = True
                message = message + "-"*8 + "\n"
                message = message + project["title"] + "/" + project["link"] + "\n"
                for k,v in keyword_cnt.items():
                    message = message + k + " : " + str(v) + "\n"
    if notify_flag:
        send_mail(
            "科创板新股材料自动监测",
            message,
            config.email
        )


if __name__ == "__main__":
    # get_all_info()
    # dowload_pdf_and_convert()
    check_and_notify()
    browser.quit()