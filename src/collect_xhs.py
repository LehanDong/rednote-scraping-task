import requests
import re
import os
import csv
import time
import datetime
from DrissionPage import ChromiumPage


# Example keyword for public code
keyword = 'example_keyword'

csv_file = open('search_results.csv', 'w', encoding='utf-8-sig', newline='')

csv_writer = csv.DictWriter(csv_file, fieldnames=[
    'Post URL',
    'Author Name',
    'Likes',
    'Comments',
    'Post Title',
    'Caption',
    'Date Published',
    'Video URL',
    'User URL',
    'Images URL'
])

csv_writer.writeheader()

headers = {
    'referer': f'https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/135.0.0.0 Safari/537.36'
}

dp = ChromiumPage()

max_posts = 130  # Try more in case
collected = 0

dp.listen.start('web/v1/search/notes')

dp.get(
    f'https://www.xiaohongshu.com/search_result'
    f'?keyword={keyword}&source=web_explore_feed'
)

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
            title = re.sub(
                r'[\\/:*?"<>|\n]',
                ' ',
                old_title
            )
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
            video_links = []
            video_list = note_card.get('video_list', [])
            for vd in video_list:
                info_list = vd.get('info_list', [])
                if info_list:
                    video_url = info_list[0].get('url', '')
                    if video_url:
                        video_links.append(video_url)

            video_links_str = ';'.join(video_links)
            
            # ID and URL
            author_info = note_card.get('user', {})
            author_name = author_info.get('nickname', '')
            author_id = author_info.get('user_id', '')
            author_homepage = (
                f'https://www.xiaohongshu.com/user/profile/{author_id}'
                if author_id
                else ''
            )

            id_ = item['id']
            token = item['xsec_token']

            url = (
                f'https://www.xiaohongshu.com/explore/{id_}'
                f'?xsec_token={token}&xsec_source=pc_search'
            )

            response = requests.get(
                url=url,
                headers=headers
            )

            html = response.text

            # Caption
            note_content = ''

            content_match = re.findall(
                '<meta name="description" content="(.*?)">',
                html
            )

            if content_match:
                note_content = content_match[0]


            # Time
            post_time = ''

            time_match = re.findall(
                '"time":(\\d+)',
                html
            )

            if time_match:
                import datetime
                post_time = datetime.datetime.fromtimestamp(
                    int(time_match[0]) // 1000
                ).strftime(
                    '%Y-%m-%d %H:%M:%S'
                )


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


# The exported CSV file may contain more than the target number
# of valid records because some returned records may not contain
# complete post information.

# Remove entries with missing author names.

import pandas as pd


df = pd.read_csv('search_results.csv')


df_cleaned = df.dropna(
    subset=['Author Name']
)


print(
    f"Now, we have {len(df_cleaned)} data"
)


df_top100 = df_cleaned.head(100)


df_top100.to_csv(
    'search_results_100_cleaned.csv',
    index=False
)


print(
    "search_results_100_cleaned.csv"
)
