import json
import random
import threading
import time
import requests
from datetime import datetime
import yaml

period_time = 0
min_favorite = 0
name_file_acc_st_has_favorite = ""
time_sleep = 0
lock = threading.Lock()
maximum_scroll = 3

def write_to_file(filename, content):
    with lock:
        with open(filename, 'a') as file:  # Mở file ở chế độ 'a' để ghi thêm vào file
            file.write(content + '\n')

# đọc file yml và gán vào các setting trên
def load_settings_from_yml(file_path):
    global period_time, min_favorite, name_file_acc_st_has_favorite, time_sleep, maximum_scroll
    with open(file_path, 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)

        # Truy cập vào mục 'setting' trong YAML
        setting = settings.get('setting', {})

        # Lấy các giá trị từ mục 'setting'
        period_time = setting.get('period_time')
        min_favorite = setting.get('min_favorite')
        name_file_acc_st_has_favorite = setting.get('name_file_acc_st_has_favorite')
        time_sleep = setting.get('time_sleep')
        maximum_scroll = setting.get('maximum_scroll')

def find_objects_with_cursor(data, target_key = "cursorType", target_value = "Bottom"):
    results = []
    if isinstance(data, dict):  # If the data is a dictionary
        for key, value in data.items():
            if key == target_key and value == target_value:
                results.append(data)
            else:
                results.extend(find_objects_with_cursor(value, target_key, target_value))
    elif isinstance(data, list):  # If the data is a list
        for item in data:
            results.extend(find_objects_with_cursor(item, target_key, target_value))
    return results


def calculate_time_difference(time_str):
    # Chuyển chuỗi thời gian thành đối tượng datetime
    time_format = "%a %b %d %H:%M:%S %z %Y"
    time_obj = datetime.strptime(time_str, time_format)
    # Lấy thời gian hiện tại
    current_time = datetime.now(time_obj.tzinfo)
    # Tính chênh lệch thời gian
    time_difference = current_time - time_obj
    # Tính số giờ chênh lệch
    hours_difference = time_difference.total_seconds() / 3600
    return hours_difference

def convert_twitter_to_x(url):
    # Tách các phần của URL
    parts = url.split("/")
    
    # Kiểm tra xem URL có đủ các phần cần thiết
    if len(parts) > 5:
        # Tạo URL mới với domain x.com và bỏ phần video/1
        new_url = f"https://x.com/{parts[3]}/status/{parts[5]}"
        return new_url
    else:
        return "URL không hợp lệ"
    


def fetch_links_from_acc(list_acc_check, list_user):

    global period_time, flag, min_favorite, max_favorite, name_file_acc_st_has_favorite, time_sleep, maximum_scroll
    
    links = []
    i = 0
    list_proxy = []

    with open('list_proxy.txt', 'r') as file:
        list_proxy = file.read().splitlines()

    for user in list_user:
        print(f"Đang kiểm tra {user}...")

        acc_check = list_acc_check[i]
        print(f"Đang sử dụng tài khoản thứ {i + 1} để check...")
        
        raw_proxy = random.choice(list_proxy)
        proxy_parts = raw_proxy.split(':')
        proxy = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"

        proxies = {
            "http": proxy,
            "https": proxy
        }

        # URL endpoint
        url = "https://x.com/i/api/graphql/UN1i3zUiCWa-6r-Uaho4fw/SearchTimeline"

        # Các tham số variables (được mã hóa dưới dạng JSON)
        variables = {
            "rawQuery": f'{user.strip()}' ,       # Từ khóa tìm kiếm
            "count": 100,          # Số kết quả muốn lấy
            "querySource": "typed_query",  # Nguồn tìm kiếm, có thể là "typed_query" hoặc khác
            "product": "Top"       # Loại sản phẩm tìm kiếm
        }

        # Các tính năng bổ sung trong API request
        features = {
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        }

        

        # Tham số cho request (bao gồm variables và features)
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }
        cursor_bottom = None
        time_scroll = 0
        while time_scroll < maximum_scroll:
            time_scroll += 1
            headers = {
                "Content-Type": "application/json",
                "Authorization": acc_check["bearer_token"],  # Bearer token từ tài khoản
                 "x-csrf-token": acc_check["csrf_token"],    # CSRF token từ tài khoản
                "Cookie": acc_check["cookie"]                # Cookie từ tài khoản
            }
            if(cursor_bottom != None):
                params["cursor"] = cursor_bottom
            # Gửi request
            response = requests.get(url, headers=headers, params=params, proxies=proxies)
            
            # Kiểm tra xem request có thành công không
            if response.status_code == 200:
                data = response.json()
                try:
                    data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]
                except:
                    print(f"Lỗi ck tại acc thứ {i}, đang chuyển sang acc khác...")
                    list_acc_check.remove(acc_check)
                    # chọn ngẫu nhiên 1 acc khác
                    acc_check = random.choice(list_acc_check)
                    print(f"Đang sử dụng tài khoản ngẫu nhiên để check...")
                    continue
                for entry in data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]:
                    try:
                        image_url = entry["content"]["itemContent"]["tweet_results"]['result']['legacy']['entities']["media"][0]["expanded_url"]    
                    except:
                        # nếu như post ko ảnh thì bỏ qua
                        continue
                    created_at = entry["content"]["itemContent"]["tweet_results"]['result']['legacy']['created_at']
                    print("created_at: ", created_at)
                    total_hours = calculate_time_difference(created_at)

                    parts = image_url.split("/")
                    if(parts[3] == user.strip()):
                        if total_hours < period_time:
                            favorite_count = entry["content"]["itemContent"]["tweet_results"]['result']['legacy']['favorite_count']
                            if favorite_count >= min_favorite:
                                url_clean = convert_twitter_to_x(image_url)
                                if url_clean not in links:
                                    links.append(url_clean)
                                    write_to_file(name_file_acc_st_has_favorite,url_clean)
                                    print(f"User: {parts[3]} có seacrh top  - {favorite_count} tim - {url_clean}")
                                    time_scroll = maximum_scroll
                                    break
                try:
                    cursor_bottom = find_objects_with_cursor(response.json())[0]["value"]
                except:
                    # nếu như không còn cursor thì break
                    break
                time.sleep(3)
            else:
                print(f"Lỗi ck tại acc thứ {i}, đang chuyển sang acc khác...")
                list_acc_check.remove(acc_check)
                # chọn ngẫu nhiên 1 acc khác
                acc_check = random.choice(list_acc_check)
                cursor_bottom = None
                time_scroll = 0
                print(f"Đang sử dụng tài khoản ngẫu nhiên để check...")

        if i >= len(list_acc_check) - 1:
            i = 0
        else:
            i = i + 1
        
        print(f"Đã check xong user {user}")
        print("===============================================")
        time.sleep(time_sleep)

# ====================================================================================================
# Load settings from the yml file 
load_settings_from_yml('settings.yml')

with open('acc_check.json', 'r') as file:
    list_acc_check = json.load(file)

with open('user.txt', 'r') as file:
    list_user = file.read().splitlines()

fetch_links_from_acc(list_acc_check, list_user)
