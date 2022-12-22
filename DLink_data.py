import requests
import json
from pandas.io import json
import access

USERS = {'90:f0:52:7f:dc:12': "Валерич",
         '18:87:40:47:fd:43': "Василич_мобила",
         'dc:f5:05:9a:ba:1f': "Василич_ноут",
         '22:ee:d1:7c:8d:7b': "Романыч"}


def get_data(
        link="http://192.168.130.101/devinfo?area=notice%7CDevice.WiFi.%7CDevice.Statistics.WiFi.Radio.1.AccessPoint"
             ".%7CDevice.Network.Server.%7CDevice.Hostnames.&_=44575&need_auth=1"):
    url = "http://192.168.130.101/login"
    query = {"login": access.login, "password": access.password, "staysigned": "false"}
    cookies = {"device_mode": "router", "DMSD-Access-Token": "INVALID_TOKEN"}
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
        "DNT": "1",
        "Cookie": "device_mode=router; DMSD-Access-Token=INVALID_TOKEN",
        "Content-Length": "61",
        "Host": "192.168.130.101"}
    session.cookies.update(cookies)
    resp = session.post(url, json=query, headers=headers)
    otv = json.loads(resp.text)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
        "DNT": "1",
        "Cookie": f"device_mode=router; DMSD-Access-Token={otv['result']['AccessToken']}; device-session-id={resp.cookies.get('device-session-id')}",
        "Content-Length": "61",
        "Host": "192.168.130.101"}
    cookies = {"device_mode": "router", "DMSD-Access-Token": otv['result']['AccessToken'],
               "device-session-id": resp.cookies.get('device-session-id')}
    session.cookies.update(cookies)
    resp = session.get(link)
    json_data = json.loads(resp.text)
    wifi = \
        json_data['result']['Device.Statistics.WiFi.Radio.1.AccessPoint.']['Device']['Statistics']['WiFi']['Radio'][
            '1'][
            'AccessPoint']['1']['AssociatedDevice']
    return wifi


def save_file(data):
    for mac in data:
        d = data[mac]
        if type(d) is not dict:
            continue
        name = USERS[d['MACAddress']]
        filename = f"{name}.log"
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        if not lines:
            last_line = "0,0,0"
        else:
            last_line = lines[-1].strip()
        line = ",".join([d['MACAddress'], str(d['TotalBytesReceived']), str(d['ConnectTime'])])
        time_last = last_line.split(",")[-1]
        time_new = line.split(",")[-1].strip()
        if time_new < time_last:
            file = open(filename, "a")
            file.write('\n' + line)
            file.close()
        else:
            lines = lines[:-1]
            lines.append(line)
            file = open(filename, "w")
            file.writelines(lines)
            file.close()
    print("save data D-Link")

def main():
    data = get_data()
    save_file(data)
