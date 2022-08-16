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
url = 'jenkins.com/ajaxBuildQueue'
reqs = requests.get(url, verify=False)
soup = BeautifulSoup(reqs.text, 'html.parser')

jobs_dict = {key: [] for key in ["linux_waiting_ok", "linux_ghost",
                                 "macos_waiting_ok", "macos_ghost",
                                 "windows_waiting_ok", "windows_ghost",
                                 "maintenance_waiting_ok", "maintenance_ghost",
                                 "frameworks_waiting_ok", "frameworks_ghost",
                                 "nightly_waiting_ok", "nightly_ghost",
                                 "others_waiting_ok", "others_ghost"]}
# print(soup)
link_list = soup.find_all('a', href=re.compile("private-ci|ci-maintenance"))

# print()
# for x in link_list:
#    print(x)

linuxToCheck = ['ubuntu18', 'ubuntu20', 'debian', 'android', 'yocto', 'rhel8', 'nightlyJobs » build<wbr/>-linux',
                'nightlyJobs » klocwork<wbr/>-linux']
for x in link_list:

    search_string = re.search(r'tooltip="(.*?)</a', str(x)).group(1)
    link = f"https://jenkins.com{x.get('href')}"
    page = urllib.request.urlopen(link).read()
    value = (page.decode("UTF-8").find("Progress:"))

    if value == -1:
        if "macos1015" in search_string:
            jobs_dict["macos_ghost"].append(link)
        elif "windows" in search_string:
            jobs_dict["windows_ghost"].append(link)
        elif any(linux in search_string for linux in linuxToCheck):
            jobs_dict["linux_ghost"].append(link)
        elif "maintenance" in search_string:
            jobs_dict["maintenance_ghost"].append(link)
        elif "frameworks" in search_string:
            jobs_dict["frameworks_ghost"].append(link)
        else:
            jobs_dict["others_ghost"].append(link)
    else:
        if "macos1015" in search_string:
            jobs_dict["macos_waiting_ok"].append(link)
        elif "windows" in search_string:
            jobs_dict["windows_waiting_ok"].append(link)
        elif any(linux in search_string for linux in linuxToCheck):
            jobs_dict["linux_waiting_ok"].append(link)
        elif "maintenance" in search_string:
            jobs_dict["maintenance_waiting_ok"].append(link)
        elif "frameworks" in search_string:
            jobs_dict["frameworks_waiting_ok"].append(link)
        else:
            jobs_dict["others_waiting_ok"].append(link)

    # print(f"{link_list.index(link) + 1}/{len(link_list)} https://openvino-ci.toolbox.iotg.sclab.intel.com{link.get('href')}")

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
