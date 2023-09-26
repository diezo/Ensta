from .lib.Exceptions import (
    AuthenticationError,
    ChallengeError
)
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import unquote_plus


# noinspection PyPep8Naming
def NewSessionID(username: str, password: str, proxy: dict[str, str] | None = None) -> str:
    options: Options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-extensions")
    options.add_argument("disable-infobars")
    options.add_argument("--headless")

    if proxy is not None and proxy.get("https", "").strip() != "":
        options.add_argument(f"--proxy-server={proxy['https'].strip()}")

    driver: webdriver.Chrome = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/accounts/login/")

    while True:
        temp_elements = driver.find_elements(By.CLASS_NAME, "_aa4b")

        for each in temp_elements:
            each: WebElement | list[WebElement]

            if len(each.find_elements(By.CLASS_NAME, "_add6")) > 0:
                temp_elements = each.find_elements(By.CLASS_NAME, "_add6")
                break

        for each in temp_elements:
            each: WebElement | list[WebElement]

            if len(each.find_elements(By.CLASS_NAME, "_ac4d")) > 0:
                temp_elements = each.find_elements(By.CLASS_NAME, "_ac4d")
                break

        if len(temp_elements) > 0:
            elements: list[WebElement] = temp_elements
            break

    username_input: WebElement = elements[0]
    password_input: WebElement = elements[1]

    username_input.send_keys(username)
    password_input.send_keys(password)

    form_element = driver.find_element(By.ID, "loginForm")
    form_element.submit()

    sessionid: str | None = None

    while True:

        cookie_object = driver.get_cookie("sessionid")

        if cookie_object is not None and "value" in cookie_object and str(cookie_object["value"]).strip() != "":
            sessionid = unquote_plus(str(cookie_object["value"]).strip())
            break

        if "challenge" in driver.current_url:
            raise ChallengeError("Challenge required to login. This usually happens because of weak password or too many login attempts from the same IP Address. Try changing your password to a strong one.")

        try:
            driver.find_element(By.ID, "slfErrorAlert")
            break
        except:
            pass

    if sessionid is not None:
        return sessionid
    else:
        raise AuthenticationError("Incorrect username or password!")
