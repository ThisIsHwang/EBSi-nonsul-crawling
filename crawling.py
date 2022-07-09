from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os

downloadPath = '/Users/hwangyun/Desktop/crawling'

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
options.add_experimental_option('prefs', {"download.default_directory": downloadPath})
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def download_wait(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 20:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


def latest_download_file():
    path = downloadPath
    os.chdir(path)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    newest = files[-1]

    return newest



if __name__ == '__main__':

    try:
        driver.get('https://www.ebsi.co.kr/ebs/pot/potg/retrievewEsyRmList.ebs')
        driver.implicitly_wait(3)
        years = driver.find_element(By.XPATH, '// *[ @ id = "yearGbn"]').text.split()
        print(years)
        print("years length is ", len(years))
        y = 0
        while y < len(years):
            tempYearDirectory = downloadPath + "/" + years[y]
            createDirectory(tempYearDirectory)
            try:
                driver.find_element(By.XPATH, '// *[ @ id = "yearGbn"] / option[%d]' % (y + 1)).click()

                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '// *[ @ id = "bbsId"]'))
                )
                #driver.implicitly_wait(3)
                months = driver.find_element(By.XPATH, '// *[ @ id = "bbsId"]').text.split('\n')
                del months[-1]
                print(months)

            except Exception as e:
                print("occured excpetion from year part", e)
                continue
            print("months length is ", len(months))
            m = 0
            while m < len(months):
                tempDirectory = tempYearDirectory + "/" + months[m].strip()
                createDirectory(tempDirectory)
                try:
                    print(y, m)
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="bbsId"]/option[%d]' % (m + 1)))
                    )
                    #driver.implicitly_wait(3)
                    driver.find_element(By.XPATH, '//*[@id="bbsId"]/option[%d]' % (m + 1)).click()
                    driver.find_element(By.XPATH, '// *[ @ id = "pageSize"] / option[5]').click()
                    driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[5] / dl[2] / dd / p / button / span').click()

                    file_name = ""
                    fileends = "crdownload"
                    while "crdownload" == fileends:
                        time.sleep(1)
                        newest_file = latest_download_file()
                        if "crdownload" in newest_file:
                            fileends = "crdownload"
                        else:
                            fileends = "none"
                            file_name = newest_file

                    if os.path.isdir(downloadPath):  # Check this path = path to folder
                        file_path = downloadPath + "/" + file_name
                        print("file_path " + file_path)
                        month, day = months[m].strip().split()
                        createDirectory(tempDirectory + "/nonje")
                        t = tempDirectory + "/nonje/" + years[y] + "_" + month + "_" + day + ".hwp"
                        print(t)
                        os.rename(file_path, t)
                        pass

                    nonsulNum = int(
                        driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[5] / dl[1] / dd / p / span / em').text)
                    print("nonsulNum: ", nonsulNum)
                    driver.find_element(By.XPATH, '// *[ @ id = "pageSize"] / option[5]').click()

                    n = 0
                    while n < nonsulNum:

                        element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[2] / p' % (n + 2)))
                        )
                        t = driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[2] / p' % (
                                    n + 2)).text
                        print("n", n)
                        if t == "답변대기":
                            n += 1
                            continue
                        else:
                            clickFlag = False
                            try:
                                clickFlag = True
                                element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH,
                                         '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[4] / div / a' % (n + 2)))
                                )

                                driver.find_element(By.XPATH,
                                                    '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[4] / div / a' % (
                                                                n + 2)).click()
                                #driver.implicitly_wait(3)
                                driver.find_element(By.XPATH,
                                                    '// *[ @ id = "aform"] / div[2] / div[2] / div[1] / div[2] / ul / li / a').click()
                                fileName = driver.find_element(By.XPATH,
                                                               '// *[ @ id = "aform"] / div[2] / div[2] / div[1] / div[2] / ul / li / a').text
                                download_wait(downloadPath)
                                createDirectory(tempDirectory + "/answers")
                                if os.path.isdir(downloadPath):  # Check this path = path to folder
                                    file_path = os.path.join(downloadPath, fileName)
                                    print("file_path " + file_path)
                                    month, day = months[m].strip().split()

                                    t = tempDirectory + "/answers/" + years[y] + "_" + month + "_" + day + str(n) + ".hwp"
                                    print(t)
                                    os.rename(file_path, t)
                                    pass

                            except Exception as e:
                                print("occured excpetion from nonsul part", e)
                                continue
                            finally:
                                if clickFlag:
                                    driver.back()
                                    clickFlag = False
                            n += 1
                    y += 1
                    m += 1
                except Exception as e:
                    print("occured excpetion from month part", e)
                    continue

        print("Loop is end")
        print("crawling is over")


        pass
    except Exception as e:
        print("Exception", e)
    finally:

        driver.quit()




