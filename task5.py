import requests
import re
import os
import csv
import time
import datetime
from DrissionPage import ChromiumPage


csv_file = open('task5.csv', 'w', encoding='utf-8-sig', newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=[
    'Post URL','Author Name','Likes','Comments','Post Title','Caption','Date Published','Video URL',
    'User URL','Images URL'
])
csv_writer.writeheader()

headers = {
    'referer': 'https://www.xiaohongshu.com/search_result?keyword=%25E5%25A3%2581%25E7%25BA%25B84k%25E9%25AB%2598%25E6%25B8%2585%25E6%2589%258B%25E6%259C%25BA&source=web_explore_feed',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
}

dp = ChromiumPage()
max_posts = 130  # Try more in case
collected = 0
dp.listen.start('web/v1/search/notes')
dp.get('https://www.xiaohongshu.com/search_result?keyword=NIO&source=web_explore_feed')

while collected < max_posts:
    r = dp.listen.wait()
    json_data = r.response.body
    items = json_data['data']['items']
    if not items:
        print('No More Poster')
        break
    for item in items:
        if collected >= max_posts:
            break
        try:
            note_card = item.get('note_card', {})
            interact_info = note_card.get('interact_info', {})
            like_count = interact_info.get('liked_count', '')
            comment_count = interact_info.get('comment_count', '')

            # Title
            old_title = note_card.get('display_title', '')
            title = re.sub(r'[\\/:*?"<>|\n]', ' ', old_title)
            
            # img link
            img_list = []
            image_list = note_card.get('image_list', [])
            for idx, img in enumerate(image_list):
                info_list = img.get('info_list', [])
                if info_list:
                    img_url = info_list[0].get('url', '')
                    if img_url:
                        img_list.append(img_url)
            img_links_str = ';'.join(img_list) 
            
            # video link
            video_list = []
            video_list = note_card.get('video_list', [])
            for vd in video_list:
                info_list = vd.get('info_list', [])
                if info_list:
                    video_url = info_list[0].get('url', '')
                    if video_url:
                        video_list.append(video_url)
            video_links_str = ';'.join(video_list) 


            # ID and URL
            author_info = note_card.get('user', {})
            author_name = author_info.get('nickname', '')
            author_id = author_info.get('user_id', '')
            author_homepage = f'https://www.xiaohongshu.com/user/profile/{author_id}' if author_id else ''

            id_ = item['id']
            token = item['xsec_token']
            url = f'https://www.xiaohongshu.com/explore/{id_}?xsec_token={token}&xsec_source=pc_search'
            # print(url)
            response = requests.get(url=url, headers=headers)
            html = response.text
           
           # Caption
            note_content = ''
            content_match = re.findall('<meta name="description" content="(.*?)">', html)
            if content_match:
                note_content = content_match[0]
            # Time
            post_time = ''
            time_match = re.findall('"time":(\d+)', html)
            if time_match:
                import datetime
                post_time = datetime.datetime.fromtimestamp(int(time_match[0])//1000).strftime('%Y-%m-%d %H:%M:%S')

            # csv
            csv_writer.writerow({
                'Post URL': url,                
                'Author Name': author_name,
                'Likes': like_count,
                'Comments': comment_count,
                'Post Title': title,
                'Caption': note_content,
                'Date Published': post_time,
                'Video URL': video_links_str,
                'User URL': author_homepage,
                'Images URL': img_links_str,
            })
            collected += 1
        except Exception as e:
            print(e)
    dp.scroll.to_bottom()
    time.sleep(2)

csv_file.close()

# The exported CSV file now contain 130 records. 
# Some of them include post links but no actual content — these are likely "You may also like" type of links. 
# Remove these entries by checking for missing poster names (where the author is marked as "NA").

import pandas as pd

df = pd.read_csv('task5.csv')

df_cleaned = df.dropna(subset=['Author Name'])

print(f"Now, we have {len(df_cleaned)} data")
# 100
df_top100 = df_cleaned.head(100)
df_top100.to_csv('task5_100_cleaned.csv', index=False)

print("task5_100_cleaned.csv")

