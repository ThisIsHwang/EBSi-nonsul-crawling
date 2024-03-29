from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

downloadPath = '/Users/hwangyun/Desktop/crawling'

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
#options.add_argument("headless")
options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
options.add_experimental_option('prefs', {"download.default_directory": downloadPath})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


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

def clickIt(xpath):
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    ).click()
    #driver.find_element(By.XPATH, '//*[@id="bbsId"]/option[%d]' % (m + 1))

def getIt(xpath):
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    ).text
    #driver.find_element(By.XPATH, '//*[@id="bbsId"]/option[%d]' % (m + 1))
    return element

def splitFileName(fileName):
    fileNameList = fileName.split('.')
    newFileName = ".".join(fileNameList[:-1])
    postfix = fileNameList[-1]
    return newFileName, postfix

if __name__ == '__main__':
    stop_m = 18
    stop_n = 39
    m_tempFlag = False
    n_tempFlag = False

    try:
        driver.get('https://www.ebsi.co.kr/ebs/pot/potg/retrievewEsyRmList.ebs')
        #driver.implicitly_wait(3)

        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "yearGbn"]'))
        )
        time.sleep(2)
        years = driver.find_element(By.XPATH, '// *[ @ id = "yearGbn"]').text.split()
        print(years)
        #선택할 수 있는 년도를 뽑아냄
        print("years length is ", len(years))
        y = 0

        while y < len(years):
            tempYearDirectory = downloadPath + "/" + years[y]
            createDirectory(tempYearDirectory)
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "yearGbn"] / option[%d]' % (y + 1)))
                )
                time.sleep(2)
                driver.find_element(By.XPATH, '// *[ @ id = "yearGbn"] / option[%d]' % (y + 1)).click() #년도로 설정
                time.sleep(2)
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "bbsId"]'))
                )
                #driver.implicitly_wait(3)
                time.sleep(3)
                months = driver.find_element(By.XPATH, '// *[ @ id = "bbsId"]').text.split('\n')
                #월수를 뽑아냄
                del months[-1]
                print(months)

            except Exception as e:
                print("occured excpetion from year part", e)
                continue
            print("months length is ", len(months))

            if not m_tempFlag:
                m = stop_m
                m_tempFlag = True
            else:
                m = 0
            while m < len(months):
                tempDirectory = tempYearDirectory + "/" + months[m].strip() #년도를 뽑아내서 제거함
                createDirectory(tempDirectory) #년수와 달의 폴더를 만듬
                if "7" in months[m].strip() and "4" in months[m].strip():
                    print()
                try:
                    print(y, m)
                    clickIt('//*[@id="bbsId"]/option[%d]' % (m + 1))

                    driver.implicitly_wait(1)
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,  '// *[ @ id = "pageSize"] / option[5]' ))
                    ).click() #50페이지로 만듬
                    time.sleep(3)

                    driver.implicitly_wait(1)
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "frm"] / div[5] / dl[2] / dd / p / button / span')) #논제 다운로드
                    ).click()
                    time.sleep(2)
                    #driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[5] / dl[2] / dd / p / button / span')
                    #driver.implicitly_wait(1)
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

                    file_name, postfix = splitFileName(file_name)

                    if os.path.isdir(downloadPath):  # Check this path = path to folder
                        file_path = downloadPath + "/" + file_name + "." + postfix
                        print("file_path " + file_path)
                        month, day = months[m].strip().split()
                        createDirectory(tempDirectory + "/nonje")
                        t = tempDirectory + "/nonje/" + years[y] + "_" + month + "_" + day + "." + postfix
                        print(t)
                        os.rename(file_path, t)


                    nonsulNum = int(
                        driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[5] / dl[1] / dd / p / span / em').text)
                    print("nonsulNum: ", nonsulNum)
                    driver.implicitly_wait(1)
                    element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '// *[ @ id = "pageSize"] / option[5]'))
                    )

                    driver.find_element(By.XPATH, '// *[ @ id = "pageSize"] / option[5]').click()
                    time.sleep(2)
                    if not n_tempFlag:
                        n = stop_n
                        n_tempFlag = True
                    else:
                        n = 0
                    while n < nonsulNum:
                        clickFlag = False
                        try:
                            driver.implicitly_wait(1)

                            if n != 0 and n % 50 == 0:
                                element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH,  '// *[ @ id = "frm"] / div[9] / a[3]'))
                                )
                                driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[9] / a[3]').click()
                                time.sleep(2)
                                driver.implicitly_wait(1)
                            tn = n % 50 + 2
                            element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[2] / p' % (tn)))
                            )
                            driver.implicitly_wait(1)
                            time.sleep(2)
                            t = driver.find_element(By.XPATH, '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[2] / p' % (tn)).text #답변 대기인지 여부 체크

                            print()
                            print(f"y: {y} m: {m} n: {n} ")
                            print(f"{years[y]} {months[m].strip()} {nonsulNum-n}")

                            if t == "답변대기":
                                n += 1
                                continue
                            else:
                                fuckingNoFileFlag = False

                                element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH,
                                         '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[4] / div / a' % (tn)))
                                )
                                createDirectory(tempDirectory + "/answers")

                                driver.implicitly_wait(1)
                                driver.find_element(By.XPATH,
                                                    '// *[ @ id = "frm"] / div[8] / ul / li[%d] / div[4] / div / a' % (
                                                        tn)).click() #게시물 클릭
                                clickFlag = True
                                time.sleep(2)

                                driver.implicitly_wait(1)
                                # 학생 답안 다운로드

                                #time.sleep(3)
                                teacherName = driver.find_element(By.XPATH,
                                                                  '// *[ @ id = "aform"] / div[2] / div[2] / div[1] / div[1] / ul / li[1] / span').text  # 파일 이름을 가져옴
                                try:
                                    element = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH,
                                             '// *[ @ id = "aform"] / div[2] / div[1] / div[1] / div[2] / ul / li / a'))
                                    ).click()
                                except:
                                    text = WebDriverWait(driver, 10).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH,
                                             '//*[@id="aform"]/div[2]/div[1]/div[2]'))
                                    ).text

                                    if os.path.isdir(downloadPath):
                                        month, day = months[m].strip().split()
                                        path = tempDirectory + "/answers/" + years[
                                            y] + "_" + month + "_" + day + "_studAnswer_" + teacherName + "_" + str(
                                            nonsulNum - n) + ".txt"
                                        print(path)
                                        print(text)
                                        with open(path, "w") as file:
                                            file.write(text)
                                    fuckingNoFileFlag = True

                                if not fuckingNoFileFlag:
                                    fileName = driver.find_element(By.XPATH,
                                                                   '// *[ @ id = "aform"] / div[2] / div[1] / div[1] / div[2] / ul / li / a').text  # 파일 이름을 가져옴
                                    download_wait(downloadPath)

                                    file_name, postfix = splitFileName(fileName)
                                    if os.path.isdir(downloadPath):
                                        file_path = os.path.join(downloadPath, file_name + "." + postfix)
                                        print("file_path " + file_path)
                                        month, day = months[m].strip().split()

                                        t = tempDirectory + "/answers/" + years[
                                            y] + "_" + month + "_" + day + "_studAnswer_" + teacherName + "_" + str(
                                            nonsulNum - n) + "." + postfix
                                        print(t)
                                        os.rename(file_path, t)

                                i = 2
                                fuckingNoFileFlag2 = False
                                while True:
                                    try: #
                                        element = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable(
                                                (By.XPATH,
                                                 '// *[ @ id = "aform"] / div[2] / div[%d] / div[1] / div[2] / ul / li / a' %(i)) )
                                        ).click()

                                        break
                                    except Exception as e:
                                        print(e)
                                        i += 2
                                        if i > 6:
                                            fuckingNoFileFlag2 = True
                                            break
                                        time.sleep(2)  # 답안 다운로드
                                        continue

                                if not fuckingNoFileFlag2:
                                    download_wait(downloadPath)
                                    fileName = driver.find_element(By.XPATH,
                                                                   '// *[ @ id = "aform"] / div[2] / div[%d] / div[1] / div[2] / ul / li / a' % (
                                                                       i)).text  # 파일 이름을 가져옴

                                    file_name, postfix = splitFileName(fileName)
                                    if os.path.isdir(downloadPath):  # Check this path = path to folder
                                        file_path = os.path.join(downloadPath, file_name + "." + postfix)
                                        print("file_path " + file_path)
                                        month, day = months[m].strip().split()

                                        t = tempDirectory + "/answers/" + years[
                                            y] + "_" + month + "_" + day + "_feedback_" + teacherName + "_" + str(
                                            nonsulNum - n) + "." + postfix
                                        print(t)
                                        os.rename(file_path, t)
                                else:
                                    if os.path.isdir(downloadPath):
                                        month, day = months[m].strip().split()
                                        path = tempDirectory + "/answers/" + years[
                                            y] + "_" + month + "_" + day + "_feedback_" + teacherName + "_" + str(
                                            nonsulNum - n) + ".empty"

                                        with open(path, "w") as file:
                                            file.write("")
                                fuckingNoFileFlag2 = True
                                n += 1

                        except Exception as e:
                            print(f"occured excpetion from nonsul part m: {m} n: {n}", e)
                            continue

                        finally:
                            if clickFlag:
                                driver.back()
                                clickFlag = False
                    m += 1


                except Exception as e:
                    print("occured excpetion from month part", e)
                    continue
            y += 1

        print("Loop is end")
        print("crawling is over")


    except Exception as e:
        print("Exception", e)
    finally:

        driver.quit()




