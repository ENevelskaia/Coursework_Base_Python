import requests
import time
import json
from tqdm import tqdm


with open("token_vk.txt", "r") as token_vk_File:
    token_vk = token_vk_File.read().strip()

with open("token_ya.txt", "r") as token_ya_File:
    token_ya = token_ya_File.read().strip()

def create_folder(folder_path):
    host = 'https://cloud-api.yandex.net/v1/disk/resources/'
    params = {'path': folder_path}
    headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token_ya}'}
    response = requests.put(host, headers=headers, params=params)
    if response.status_code == 201:
        print("Папка создана")
    elif response.status_code == 409:
        print("Папка c таким названием существует")

def upload_photo(token, file_url, file_name):
    host = 'https://cloud-api.yandex.net/v1/disk/resources/upload/'
    params = {'path': f'/photo_vk_profile/{file_name}', 'url': file_url}
    headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {token}'}
    requests.post(host, headers=headers, params=params)
    return

def photo_max_size(dict):
    size_list = []
    for m in dict['sizes']:
        size_list.append(m['height']*m['width'])
    max_value = max(size_list)
    if max_value == 0:
         max_index = -1
    else:
         max_index = size_list.index(max_value)
    return max_value, max_index

def for_upload_photo_index(res, foto_qnty):
    max_size_list = []
    foto_max_index = []
    for item in res:
        max_size_list.append(photo_max_size(item)[0])
    foto_max_size_list = sorted(max_size_list)[-1:-(foto_qnty+1):-1]

    for i in foto_max_size_list:
        d = max_size_list.index(i)
        foto_max_index.append(d)
        max_size_list[d] = 0

    return foto_max_index

VK_URL = 'https://api.vk.com/method/photos.get'
like_URL = 'https://api.vk.com/method/likes.getList'
photo_names = []
data = []
params = {
'owner_id': '3090191',
'access_token': token_vk,
'v':'5.131',
'album_id': 'profile'
}
folder_path = '/photo_vk_profile'

create_folder(folder_path)

res = requests.get(VK_URL, params).json()['response']['items']

upload_photo_index = for_upload_photo_index(res, 5)

for i in tqdm(upload_photo_index):
    l = photo_max_size(res[i])
    photo_url = res[i]['sizes'][l[1]]['url']
    photo_size = res[i]['sizes'][l[1]]['type']
    photo_id = res[i]['id']
    like_params = {
        'owner_id': '3090191',
        'item_id': photo_id,
        'access_token': token_vk,
        'v': '5.131',
        'type': 'photo',
        'page_url': photo_url
    }
    likes = requests.get(like_URL, like_params).json()
    photo_name = likes['response']['count']
    if photo_name in photo_names:
        photo_name = photo_name + res[i]['date']
    photo_names.append(photo_name)
    upload_photo(token_ya, photo_url, photo_name)
    d = {"file_name": f'{photo_name}.jpg', "size": photo_size}
    data.append(d)
    time.sleep(0.2)

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)


