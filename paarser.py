import time
import pandas as pd
import requests
import json
import asyncio
import httpx


'#####  Эта функция загружает все данные в базу данных ###'
def save_data_to_db(data):
        for a in data:
            cat_id = a['cat_id']
            title = a['title']
            price = a['price']
            description = a['description']
            phone = a['phone']
            city = a['city']
            image = a['images']
            imgs = {}
            for img in image:
                imgs['images'] = ("file.jpg", img, 'image/jpeg')
            try:
                nameseller = a['user']['username']
            except:
                nameseller = ''

            w = { 'user':1, 'category':cat_id,
                  'title': title, 'price': price,
                 'description': description, 'phone': phone,
                  'nameseller': nameseller, 'city':city  }
            requests.post('http://127.0.0.1:8000/create_ads/',data = w, files=imgs)


cats = {
    2043:18,
    2046: 19,
    5830: 20,
    5831: 21,
}
"""### 1-получаем json с данными по заданным запросам ####"""
"""### 2-Мы также отправлаем запросы с асихронным кодом ###"""
async def get_json(client, url, params, cat_id):
        headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "application/json, text/plain, */*",
        "device": "pc"
        }
        params['category_id'] = cat_id
        resp = await client.get(url, headers=headers, params=params)
        return resp.json()


def save_json(data):
    """### сохрание ответа в файл для наглядного просмотра ###"""
    with open('lalafo_data.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        print(f'Данные сохранены в lalafo_data.json')


def save_filter_json(data):
    with open('lalafo_filter_data.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        print(f'Данные сохранены в lalafo_filter_data.json')


def get_data_from_json(data_json, category_id):
    """### собераем нужные нам данные из json ###"""
    print(category_id)
    result = []
    for d in data_json['items']:
        post_id = d['id']
        title = d['title']
        phone = d['mobile']
        description = d['description']
        price = d['price']
        for image in d['images']:
            try:
                images = image['original_url']
            except:
                images  = 'без изображения'
        city = d['city']
        try:
            nameseller = d['user']['username']
        except:
            nameseller = ''

        result.append({
            'post_id': post_id,
            'city': city,
            'name_seller': nameseller,
            'phone': phone,
            'title': title,
            'price': price,
            'description': description,
            'images': images,
            "cat_id": category_id,
        })
    return result


def save_excel(data):
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter('lalafo_result.xlsx')
    df.to_excel(writer, 'data')
    writer.save()
    print('Все сохранено в lalafo_result.xlsx')


if __name__ == '__main__':
    start = time.time()
    result = []
    params = {
        "expand": "url",
        'city_id': 103184,  # id города (пример: 103184 - Бишкек, 103209 - Джалал-Абад, 103218 - Ош и тд)
        'category_id': 0, # категория товара (пример: 1317 - Электроника, 1501 - Транспорт, 1484 - Животные и тд)
        'per-page': 70, # количество результатов на странице
        'currency': 'KGS',   # валюта. Доступны: KGS, USD
    }


    async def main():
        """### отправлаем запросы с асихронным кодом ###"""
        async with httpx.AsyncClient() as client:
            tasks = []
            for cat_id in cats:
                url = f'https://lalafo.kg/api/search/v3/feed/search?&expand=url&per-page=20{cat_id}'
                tasks.append(asyncio.ensure_future(get_json(client,url, params, cat_id)))
                d = await asyncio.gather(*tasks)
                for a in d:
                    save_json(a)
                result.extend(get_data_from_json(a, category_id=cats.get(cat_id)))


    save_excel(result)
    asyncio.run(main())
    save_filter_json(result)
    save_data_to_db(result)


    print(len(result))
    end = time.time()
    print(end - start)