import re
import urllib.request
import requests
import itertools
import threading
import time
import sys
import json
from datetime import datetime
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()

done = False


def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rWorking... ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!\n')


t = threading.Thread(target=animate)
t.start()
dt = datetime.now()
url = 'jenkins/ajaxBuildQueue'
reqs = requests.get(url, verify=False)
soup = BeautifulSoup(reqs.text, 'html.parser')

jobs_dict = {key: [] for key in ["ubuntu_waiting_ok", "ubuntu_ghost",
                                 "macos_waiting_ok", "macos_ghost",
                                 "windows_waiting_ok", "windows_ghost",
                                 "frameworks_waiting_ok", "frameworks_ghost",
                                 "others_waiting_ok", "others_ghost"]}

link_list = soup.find_all('a', href=re.compile("private-ci"))

for link in link_list:
    # print(f"{link_list.index(link) + 1}/{len(link_list)} https://jenkins.com{link.get('href')}")
    link = f"https://jenkins.com{link.get('href')}"
    page = urllib.request.urlopen(link).read()
    value = (page.decode("UTF-8").find("Progress:"))
    if value == -1:
        if "linux-ubuntu" in link:
            jobs_dict["ubuntu_ghost"].append(link)
        elif "linux-macos" in link:
            jobs_dict["macos_ghost"].append(link)
        elif "frameworks.ai.openvino" in link:
            jobs_dict["frameworks_ghost"].append(link)
        elif "windows" in link:
            jobs_dict["windows_ghost"].append(link)
        else:
            jobs_dict["others_ghost"].append(link)
    else:
        if "linux-ubuntu" in link:
            jobs_dict["ubuntu_waiting_ok"].append(link)
        elif "linux-macos" in link:
            jobs_dict["macos_waiting_ok"].append(link)
        elif "frameworks.ai.openvino" in link:
            jobs_dict["frameworks_waiting_ok"].append(link)
        elif "windows" in link:
            jobs_dict["windows_waiting_ok"].append(link)
        else:
            jobs_dict["others_waiting_ok"].append(link)
done = True

"""
Comment two below lines to disable dictionary preview
"""
print(f"\nDictionary:")
print(json.dumps(jobs_dict, indent=4))
print(f"Date and time of check: {dt}")
s = 0
ok = 0
ubuntu = 0
ghost = 0
print("------------------------------------------")
for k, v in jobs_dict.items():
    item_count = len([item for item in v if item])
    print(f"{k:25} ==> {item_count:16d}")
    ok = ok + item_count if "waiting_ok" in k else ok
    ghost = ghost + item_count if "ghost" in k else ghost
    ubuntu = ubuntu + item_count if "ubuntu_waiting_ok" in k else ubuntu
    s = s + item_count
print("------------------------------------------")
print(f"Count values of waiting_ok: {ok:18d}")
print(f"Count values of waiting_ok (no ubuntu): {ok-ubuntu:6d}")
print(f"Count values of ghost: {ghost:23d}")
print(f"Count values in dictionary: {s:18d}")
print(f"Count jobs links on list: {len(link_list):20d}")
print("Seems ok!") if s == len(link_list) else print("Values do not match! Check what is wrong.")
