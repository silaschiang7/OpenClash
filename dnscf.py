import requests
import traceback
import time
import os
import json

# 临时设置环境变量值（仅用于测试）
os.environ["CF_API_TOKEN"] = "your_actual_cf_api_token"
os.environ["CF_ZONE_ID"] = "your_actual_cf_zone_id"
os.environ["CF_DNS_NAME"] = "your_actual_cf_dns_name"
os.environ["PUSHPLUS_TOKEN"] = "your_actual_pushplus_token"

# 获取环境变量
CF_API_TOKEN = os.environ["CF_API_TOKEN"]
CF_ZONE_ID = os.environ["CF_ZONE_ID"]
CF_DNS_NAME = os.environ["CF_DNS_NAME"]
PUSHPLUS_TOKEN = os.environ["PUSHPLUS_TOKEN"]

headers = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json'
}

def get_cf_speed_test_ip(timeout=10, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get('https://ip.164746.xyz/ipTop.html', timeout=timeout)
            if response.status_code == 200:
                return response.text
            else:
                print(f"get_cf_speed_test_ip Request failed with status {response.status_code} (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            traceback.print_exc()
            print(f"get_cf_speed_test_ip Request failed (attempt {attempt + 1}/{max_retries}): {e}")
    return None

def get_dns_records(name):
    def_info = []
    url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            records = response.json()['result']
            for record in records:
                if record['name'] == name:
                    def_info.append(record['id'])
            return def_info
        else:
            print('Error fetching DNS records:', response.text)
    except Exception as e:
        traceback.print_exc()
        print(f"get_dns_records ERROR: {e}")
    return def_info

def update_dns_record(record_id, name, cf_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record_id}'
    data = {
        'type': 'A',
        'name': name,
        'content': cf_ip
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"cf_dns_change success: ---- Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- ip：" + str(cf_ip))
            return "ip:" + str(cf_ip) + "解析" + str(name) + "成功"
        else:
            print(f"cf_dns_change ERROR: ---- Time: " + str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " ---- MESSAGE: " + response.text)
    except Exception as e:
        traceback.print_exc()
        print(f"cf_dns_change ERROR: {e}")
    return "ip:" + str(cf_ip) + "解析" + str(name) + "失败"

def push_plus(content):
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": "IP优选DNSCF推送",
        "content": content,
        "template": "markdown",
        "channel": "wechat"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=body, headers=headers)
        if response.status_code != 200:
            print(f"push_plus ERROR: {response.text}")
    except Exception as e:
        traceback.print_exc()
        print(f"push_plus ERROR: {e}")

def main():
    ip_addresses_str = get_cf_speed_test_ip()
    if ip_addresses_str:
        ip_addresses = ip_addresses_str.split(',')
        dns_records = get_dns_records(CF_DNS_NAME)
        push_plus_content = []
        for index, ip_address in enumerate(ip_addresses):
            if index < len(dns_records):
                dns = update_dns_record(dns_records[index], CF_DNS_NAME, ip_address)
                push_plus_content.append(dns)
            else:
                print(f"No DNS record available for index {index}")
                push_plus_content.append(f"No DNS record available for index {index}")
        push_plus('\n'.join(push_plus_content))
    else:
        print("Failed to get IP addresses.")
        push_plus("Failed to get IP addresses.")

if __name__ == '__main__':
    main()