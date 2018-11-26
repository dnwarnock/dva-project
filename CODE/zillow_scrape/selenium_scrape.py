import os
import sys
import csv
import time
import json
import uuid
import random
from retrying import retry
from selenium import webdriver
from subprocess import check_call
from collections import defaultdict
from selenium.webdriver.common.proxy import *


def get_proxy():
    """Returns a random proxy ip from the collection"""
    with open('proxies.csv', 'r') as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            data.append(row)
    return random.choice(data)

def get_firefox_driver(headless=False, proxy_ip=None):
    """Returns selenium Firefox web driver."""
    proxy_ip = get_proxy()  # always get proxy now
    print('using proxy: {}'.format(proxy_ip))
    if headless:
        os.environ['MOZ_HEADLESS'] = '1'
    if proxy_ip:
        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': proxy_ip,
            'ftpProxy': proxy_ip,
            'sslProxy': proxy_ip,
            'noProxy': ''
        })
        return webdriver.Firefox(proxy=proxy)
    else:
        return webdriver.Firefox()

def refresh_driver(current_driver):
    current_driver.quit()
    return get_firefox_driver(headless=True)

def prepare_input_file(file_name):
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        data = []
        loop_ct = 0
        for row in reader:
            loop_ct += 1
            if loop_ct == 1:
                continue # skip headers
            address = row[1].replace(row[5], "").replace(row[6], "").strip()
            address = " ".join([address, "Austin, TX", row[6]])
            data.append((row[0], address))
    return data

def get_processed_addresses(processed_addresses_path):
    if not os.path.isfile(processed_addresses_path):
        return set([])
    else:
        data = []
        with open(processed_addresses_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row[0])
        return set(data)

def flush(data, output_path, processed_addresses_path):
    """takes ouput data and flushes to file, then to s3"""
    ofile_name = str(uuid.uuid4()) + '.json'
    with open(ofile_name, 'w') as f:
        json.dump(data, f)

    print('uploading file {file} to {path}'.format(
            file=ofile_name,
            path=output_path)
        )
    check_call("aws s3 cp {file} {path}".format(
            file=ofile_name,
            path=output_path
        ),
        shell=True
    )
    os.remove(ofile_name)

    # also dump the ids we just saved incase we need to restart
    set_file = processed_addresses_path
    with open(set_file, 'a') as f:
        for adr in data:
            f.write(str(adr['id']))
            f.write('\n')

def main(addresses, output_path, processed_addresses_path, flush_threshold=5):
    driver = get_firefox_driver(headless=True)
    driver.implicitly_wait(20) # seconds
    combined_data = []
    loop_ct = 0

    processed_addresses = get_processed_addresses(processed_addresses_path)

    for address in addresses:

        if address[0] in processed_addresses:
            continue  # skip properties we've already pulled

        loop_ct += 1
        if loop_ct % 1000 == 0:
            print('refreshing driver')
            driver = refresh_driver(driver)

        print('fetching data from address : {}'.format(address))
        data = defaultdict(lambda: [])
        data['id'] = address[0]
        data['address'] = address[1]
        driver.get("https://www.zillow.com/homes/for_sale/{}_rb/".format(address[1].replace(" ", "-")))
        time.sleep(0.5)
        driver.save_screenshot("pics/{}.png".format(address[1].replace(" ", "-")))

        try:
            zestimate = driver.find_element_by_class_name("zestimate-value")
            data["zestimate"] = zestimate.text
        except:
            pass

        fact_values = driver.find_elements_by_class_name("fact-value")

        for i in range(len(fact_values)):
            label = fact_values[i].find_element_by_xpath("..")
            child_text = fact_values[i].text
            parent_text = label.text.replace(child_text, "").replace(":", "").replace("\n", "").replace(" ", "")
            if parent_text == '':
                continue
            data[parent_text.lower()].append(child_text.lower())

        cateory_values = driver.find_elements_by_class_name("category-facts")
        for i in range(len(cateory_values)):
            label = cateory_values[i].find_element_by_xpath("..")
            child_text = cateory_values[i].text
            parent_text = label.text.replace(child_text, "").replace(":", "").replace("\n", "").replace(" ", "")
            if parent_text == '':
                continue
            data[parent_text.lower()].append(child_text.lower())

        print(data)
        combined_data.append(data)
        if len(combined_data) > flush_threshold:
            flush(combined_data, output_path, processed_addresses_path)
            combined_data = []

    flush(combined_data, output_path, processed_addresses_path)
    driver.quit()
    return True

if __name__ == '__main__':
    file_name = sys.argv[1]  # local file of addresses
    output_path = sys.argv[2]  # s3 path to where the files go
    processed_addresses_path = sys.argv[3]
    addresses = prepare_input_file(file_name)

    retry_ct = 10
    while retry_ct > 0:
        try:
            main(addresses, output_path, processed_addresses_path)
            break # stop if it made it all the way
        except Exception as e:
            retry_ct -= 1
            # if we failed for some reason, take a nap and try again
            print("scraper broke on.. trying again")
            print("exception: {}".format(e))
            time.sleep(30)

    if retry_ct > 0:
        print("finish completely")
    else:
        print("stopped after 10 attempts")
