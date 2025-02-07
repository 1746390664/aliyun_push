# -*- coding: utf-8 -*-  
"""  
@file       : ali_task_page.py  
@Project    : pythonToolsProject  
@AuThor     : Aura Service  
@CreateTime : 2025/1/15 15:02  
@Description:  
解析阿里云社区为 表格形式html  标记有效、活动  
用于githubpage  
"""

import requests  
import datetime  
from urllib.parse import urlparse  

# 请求API并获取数据  
def fetch_data():  
    url = "https://developer.aliyun.com/developer/api/task/getMissionPage?taskLevel=-1&taskType=-1&giftType=all&pageNum=1&pageSize=50"  
    headers = {  
        "accept": "application/json, text/plain, */*",  
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",  
        "bx-v": "2.5.26",  
        "priority": "u=1, i",  
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",  
        "sec-ch-ua-mobile": "?0",  
        "sec-ch-ua-platform": "\"Windows\"",  
        "sec-fetch-dest": "empty",  
        "sec-fetch-mode": "cors",  
        "sec-fetch-site": "same-origin",  
        "Referrer-Policy": "no-referrer-when-downgrade"  
    }  

    try:  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  
        data = response.json()  
        if data["success"] and data["code"] == "200":  
            return data["data"]["list"]  
        else:  
            return []  
    except requests.exceptions.RequestException as e:  
        print(f"请求错误: {e}")  
        return []  

# 解析URL，提取任务类别（即域名后面的第一个值）  
def parse_task_category(url):  
    try:  
        parsed_url = urlparse(url)  
        path_segments = parsed_url.path.strip("/").split("/")  
        if path_segments:  
            return path_segments[0]  
        return ""  
    except Exception as e:  
        print(f"解析URL失败: {e}")  
        return ""  

# 标记新增和失效活动  
def mark_new_and_invalid_activities(today_data):  
    # 获取今天的日期  
    today_date = datetime.date.today()  

    marked_today_data = []  
    for activity in today_data:  
        # 标记是否新增  
        activity_start_date = datetime.datetime.strptime(activity['gmtStart'], "%Y-%m-%d %H:%M:%S").date()  
        is_new = '是' if activity_start_date == today_date else '否'  

        # 标记是否有效  
        current_time = datetime.datetime.now()  
        gmt_end = datetime.datetime.strptime(activity['gmtEnd'], "%Y-%m-%d %H:%M:%S")  
        is_valid = '有效' if gmt_end > current_time else '失效'  

        # 提取任务类别  
        task_category = parse_task_category(activity.get('url', ''))  

        # 添加标记  
        activity['is_new'] = is_new  
        activity['status'] = is_valid  
        activity['task_category'] = task_category  # 新增字段，展示任务类别  

        marked_today_data.append(activity)  

    return marked_today_data  

# 生成HTML表格  
def generate_html_table(data, title):  
    html = f"<h2>{title}</h2><style>.col-title{{width:200px;}}.col-description{{width:200px;}}.col-gift{{width:100px;}}.col-start{{width:150px;}}.col-end{{width:150px;}}.col-new{{width:100px;}}.col-status{{width:100px;}}.col-task{{width:100px;}}.col-url{{width:100px;}}table{{border-collapse:collapse;}}th,td{{border:1px solid black;padding:10px;}}</style><table><thead><tr><th class='col-title'>活动标题</th><th class='col-description'>描述</th><th class='col-gift'>奖品</th><th class='col-start'>开始时间</th><th class='col-end'>结束时间</th><th class='col-new'>是否新增</th><th class='col-status'>活动状态</th><th class='col-task'>任务类别</th><th class='col-url'>活动链接</th></tr></thead><tbody>"  

    for activity in data:  
        gifts = ", ".join(activity.get('giftList', {}).get('awardList', []))  
        html += f"<tr><td>{activity['title']}</td><td>{activity['description']}</td><td>{gifts}</td><td>{activity['gmtStart']}</td><td>{activity['gmtEnd']}</td><td>{activity['is_new']}</td><td>{activity['status']}</td><td>{activity['task_category']}</td><td><a href='{activity['url']}' target='_blank'>查看详情</a></td></tr>"  

    html += "</tbody></table>"  
    return html  

def generate_html_report():  
    today_data = fetch_data()  

    # 标记新增和失效活动  
    today_html = generate_html_table(mark_new_and_invalid_activities(today_data),  
                                     f"今日活动 ({datetime.date.today()})") if today_data else "<p>今日没有活动数据。</p>"  

    full_html = f"<html><head><title>活动报告</title></head><body><h1>每日活动报告</h1>{today_html}</body></html>"  

    return full_html  

if __name__ == "__main__":  
    try:  
        html_report = generate_html_report()  
        open("index.html", "w", encoding="utf-8").write(html_report)  
    except Exception as e:  
        print(f"生成报告时发生错误: {e}")
