import argparse
import os
import time
from argparse import Namespace

import requests
from selenium import webdriver
from selenium.common import WebDriverException


def parse_args() -> Namespace:
    """
    Parses the arguments from the command line.
    :return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="robots.txt scraper")
    parser.add_argument("-u", "--url", dest="url", required=False, help="Url of the robots file")
    return parser.parse_args()


def get_screenshot(url: str, counter: int):
    """
    Gets a screenshot of the webpage and stores it in the output directory.
    :param url: The url of the webpage.
    :param counter: The counter for the screenshot.
    """
    url = url.replace("//", "/").replace(":/", "://")
    print(f'url: {url}')
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        chromedriver = webdriver.Chrome(options=options)
        chromedriver.set_window_size(1500, 1080)
        chromedriver.get(url)
        time.sleep(1)
        screenshot_path = f"screenshots/{counter}-{url.split('/')[2]}-{url.split('/')[3]}.png"
        print(f'screenshot path: {screenshot_path}')
        chromedriver.save_screenshot(screenshot_path)
    except WebDriverException:
        #continue
        print("")


    chromedriver.quit()


def main():
    args = parse_args()
    url = args.url
    os.makedirs("screenshots", exist_ok=True)
    try:
        response = requests.get(f"{url}robots.txt")

        if response.status_code == 200:
            robots_lines = response.text
            user_agent_rules = []
            capture = False

            for line in robots_lines.splitlines():
                line = line.strip().lower()
                if line.startswith("user-agent: *"):
                    capture = True
                    continue
                if capture:
                    if line == "":
                        break
                    user_agent_rules.append(line)

            for i in range(0, len(user_agent_rules)):
                user_agent_rules[i] = user_agent_rules[i].split(': ')[1]
                get_screenshot(f"{url}{user_agent_rules[i]}", i)


    except requests.RequestException as e:
        print(f"error:\n{e}")


if __name__ == "__main__":
    main()
    # url.split('/')[2]