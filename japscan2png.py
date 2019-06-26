import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


USAGE = ""


BASE_DIR = "RESULT"

SITE_BASE_URL = "https://www.japscan.to"

#Profiles

#find about in on 'about:profiles' for firefox
#"C:\\Users\\eliott\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ya7snxy0.default"
F_PROFILE = None

C_PROFILE = None

def setup(args):

    if len(args) < 4 or "--help" in args[1]:
        print(USAGE)
        sys.exit()

    global FIRST_CHAPTER_URL
    global LAST_CHAPTER_NUMBER

    FIRST_CHAPTER_URL = args[2]

    try:
        LAST_CHAPTER_NUMBER = float(args[3])
    except Exception as e:
        print("Argument error: the third argument must be the number of the last chapter")
        sys.exit("wrong format argument")

    if len(args) == 5:
        global BASE_DIR
        BASE_DIR = args[4]

    if "chrome" in args[1].lower():
        print("Opening Chrome...")
        path   = os.path.join(os.getcwd(), "chromedriver.exe")
        driver = webdriver.Chrome(executable_path=path, chrome_options=C_PROFILE)

    elif "firefox" in args[1].lower():
        print("Opening Firefox...")
        path   = os.path.join(os.getcwd(), "geckodriver.exe")
        driver = webdriver.Firefox(executable_path=path, firefox_profile=F_PROFILE)

    else:
        print("Argument Error: you have to choose between Chrome and Firefox in the first argument")
        sys.exit("wrong format argument")

    return driver

def run(driver):

    driver.get(FIRST_CHAPTER_URL)
    print("Wait for redirect...")

    while True:
        time.sleep(1) #to let japscan recover his breath
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "image"))
            )
        except Exception as e:
            print("something went wrong while finding the image in the page, abort ({})".format(e))
            break

        next_image_url = SITE_BASE_URL + elem.get_attribute("data-next-link")
        new_chap, page = chap_info(driver)

        if 'actual_chap' in locals():
            if new_chap != actual_chap:
                print("chapter {} completed, starting chapter {}...".format(actual_chap, new_chap))
                actual_chap = new_chap
        else:
            actual_chap = new_chap

        write_image(elem, actual_chap, page)

        i = 0
        while i < 10:
            try:
                driver.get(next_image_url)
            except Exception:
                print("Page loading timed out: reloading... {}/10".format(i+1))
                i += 1
            else:
                break

        if i >= 10:
            print("Cannot reach the page, abort.")
            break

        if actual_chap > LAST_CHAPTER_NUMBER:
            print("Done.")
            break

def chap_info(driver):

    try:
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "breadcrumb"))
        )
    except Exception as e:
        print("something went wrong while finding the chapter infos, abort. ({})".format(e))


    elem = elem.text.split('\n')

    chap = None
    page = None

    for x in elem:
        if "Chap" in x:
            chap = float(x[5:])
        if "Page" in x:
            page = float(x[5:])

    if chap is None or page is None:
        print("something went wrong while trying to find chapter infos, stopping the gathering...")

    return chap, page

def write_image(elem, chap, page):

    path = os.path.join(os.getcwd(), BASE_DIR)

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    path  = os.path.join(path, str(chap))

    if not os.path.exists(path):
        os.makedirs(path)

    path  = os.path.join(path, str(page) + ".png")

    elem.screenshot(path)


if __name__ == "__main__":
    print("####################    JAPSCAN TO PNG    ####################")
    driver = setup(sys.argv)
    try:
        run(driver)
    except Exception as e:
        print("Error occured: {}".format(e))
    finally:
        driver.quit()
