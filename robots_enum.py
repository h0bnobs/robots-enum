import argparse
import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def parse_args():
    parser = argparse.ArgumentParser(description="robots.txt scraper and screenshotter")
    parser.add_argument("-u", "--url", required=True, help="Base URL (including scheme) of the site")
    return parser.parse_args()


def fetch_allowed_paths(base_url):
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/robots.txt")
        resp.raise_for_status()
    except requests.RequestException as err:
        raise SystemExit(f"Error fetching robots.txt: {err}")
    rules = []
    capture = False
    for line in resp.text.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            capture = True
            continue
        if capture:
            if not line or line.lower().startswith("sitemap"):
                break
            key, _, path = line.partition(":")
            if key.strip().lower() in ("allow", "disallow"):
                rules.append(path.strip())
    return rules


def init_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--disable-web-security")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1500, 1080)
    return driver


def main():
    args = parse_args()
    os.makedirs("screenshots", exist_ok=True)
    paths = fetch_allowed_paths(args.url)
    if not paths:
        print("No user-agent rules found.")
        return
    print(f"Found {len(paths)} paths, capturing screenshots...")
    driver = init_driver()
    for idx, path in enumerate(paths, 1):
        full_url = f"{args.url.rstrip('/')}/{path.lstrip('/')}"
        try:
            driver.get(full_url)
            time.sleep(1)
            domain = args.url.split("//", 1)[-1].rstrip('/')
            filename = f"{idx:02d}-{domain}-{path.strip('/').replace('/', '_')}.png"
            dest = os.path.join("screenshots", filename)
            driver.save_screenshot(dest)
            print(f"{idx}/{len(paths)} -> {dest}")
        except WebDriverException:
            print(f"Failed to capture: {full_url}")
    driver.quit()


if __name__ == "__main__":
    main()
