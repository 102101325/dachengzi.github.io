import requests
from bs4 import BeautifulSoup
import random
import os
import re
import time
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, Scrollbar, Listbox
import json
import jsonpath
import threading
from PIL import ImageTk, Image
cookie = {
    'login_referer': 'https%3A%2F%2Fwww.luogu.com.cn%2Fproblem%2FP1000',
    '_uid': '1093381',
    '__client_id': 'cb2e3c3b83dd70db8a568a1a34befb160f11383f',
    'C3VK': '123abc',
}

global difficulty_var, source_options, keyword_entry, result_text, source_vars, database_info_label, source_listbox, progress_window, progress_label, progress_bar, text_output, progress_bar
original_window_size = "500x400"
def update_progress():
    progress_bar.step(1)
    progress_window.after(2, update_progress)

def create_progress_window():
    global progress_window, progress_bar, text_output, progress_label
    progress_window = tk.Toplevel(root)
    progress_window.title("获取进度~")
    progress_window.geometry("500x400")

    progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
    progress_bar.pack(pady=20)

    progress_label = tk.Label(progress_window, text="爬取中...")
    progress_label.pack()
    text_output = tk.Text(progress_window, wrap=tk.WORD)
    text_output.pack(fill=tk.BOTH, expand=True)

    progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  
    update_progress()
def close_progress_window():
    if progress_window and progress_window.winfo_exists():
        progress_window.destroy()
def update_database_info():
    global database_info_label

    data_directory = "./data"
    if os.path.exists(data_directory):
        num_of_folders = len(
            [name for name in os.listdir(data_directory) if os.path.isdir(os.path.join(data_directory, name))])
    else:
        num_of_folders = 0

    global database_info_label
    database_info_label.config(text=f"获取数据: {num_of_folders}   软件版本: V1.0")

def Get_info(anum, bnum):
    headers = {
        "authority": "www.luogu.com.cn",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Cookie": "__client_id=a0306231cd05f9a814ca1bdf95c050400268bedf; _uid=0",
    }
    tag_url = 'https://www.luogu.com.cn/_lfe/tags'
    tag_html = requests.get(url=tag_url, headers=headers).json()
    tags_dicts = []
    tags_tag = list(jsonpath.jsonpath(tag_html, '$.tags')[0])
    for tag in tags_tag:
        if jsonpath.jsonpath(tag, '$.type')[0] != 1 or jsonpath.jsonpath(tag, '$.type')[0] != 4 or \
                jsonpath.jsonpath(tag, '$.type')[0] != 3:
            tags_dicts.append({'id': jsonpath.jsonpath(tag, '$.id')[0], 'name': jsonpath.jsonpath(tag, '$.name')[0]})

    arr = ['暂无级别', '入门', '普及−', '普及/提高−', '普及+/提高', '提高+/省选−', '省选/NOI−', 'NOI/NOI+/CTSC']
    ts = []
    a = (anum - 1000) // 50 + 1
    b = (bnum - 1000) // 50 + 1

    for page in range(a, b + 1):
        url = f'https://www.luogu.com.cn/problem/list?page={page}'
        html = requests.get(url=url, headers=headers).text
        urlParse = re.findall('decodeURIComponent\((.*?)\)\)', html)[0]
        htmlParse = json.loads(urllib.parse.unquote(urlParse)[1:-1])
        result = list(jsonpath.jsonpath(htmlParse, '$.currentData.problems.result')[0])

        for res in result:
            pid = jsonpath.jsonpath(res, '$.pid')[0]
            ppid = pid[1:]
            if int(ppid) < anum:
                continue
            if int(ppid) > bnum:
                break

            title = jsonpath.jsonpath(res, '$.title')[0]
            difficulty = arr[int(jsonpath.jsonpath(res, '$.difficulty')[0])]
            tags_s = list(jsonpath.jsonpath(res, '$.tags')[0])
            tags = []
            for ta in tags_s:
                for tags_dict in tags_dicts:
                    if tags_dict.get('id') == ta:
                        tags.append(tags_dict.get('name'))
            wen = {
                "题号": pid,
                "题目": title,
                "标签": tags,
                "难度": difficulty
            }
            ts.append(wen)
        print(f'第{page}页已经保存')
        text_output.insert(tk.END, f'第{page}页已经保存\n')
        text_output.see(tk.END)
        with open('info.json', 'w', encoding='utf-8') as f:
            json.dump(ts, f, ensure_ascii=False, indent=4)


def Get_MD(html):
    bs = BeautifulSoup(html, "html.parser")
    core = bs.select("article")[0]
    while not core:
        print("重试中")
        text_output.insert(tk.END, "重试中\n")
        text_output.see(tk.END)
        core = bs.select("article")[0]

    md = str(core)
    md = re.sub("<h1>", "# ", md)
    md = re.sub("<h2>", "## ", md)
    md = re.sub("<h3>", "#### ", md)
    md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
    return md

def Get_TJ_MD(html):
    soup = BeautifulSoup(html, "html.parser")
    encoded_content_element = soup.find('script')
    encoded_content = encoded_content_element.text
    start = encoded_content.find('"')
    end = encoded_content.find('"', start + 1)
    encoded_content = encoded_content[start + 1:end]
    decoded_content = urllib.parse.unquote(encoded_content)
    decoded_content = decoded_content.encode('utf-8').decode('unicode_escape')
    start = decoded_content.find('"content":"')
    end = decoded_content.find('","type":"题解"')
    decoded_content = decoded_content[start + 11:end]
    return decoded_content

def Get_Problem_title(problemID):
    url = 'https://www.luogu.com.cn/problem/P' + str(problemID)
    print('----------- 正在爬取 ' + str(problemID) + ' ------------')
    text_output.insert(tk.END, '----------- 正在爬取 ' + str(problemID) + ' ------------\n')
    text_output.see(tk.END)
    with open('d:/vscode/icoding/软工作业2/pachong/tk.txt', 'r') as f:
        lines = f.readlines()
        custom_user_agent = random.choice(lines).strip()

    headers = {
        'User-Agent': custom_user_agent,
    }
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    title = soup.find('title').text
    title = title.split('-')[0]
    title = title.strip()
    return title


def start_work(anum, bnum):
    create_progress_window()
    print("正在爬取~")
    text_output.insert(tk.END, "正在爬取~\n")
    text_output.see(tk.END)   
    Get_info(anum, bnum)
    print("爬取成功！")
    text_output.insert(tk.END, "爬取成功！\n")
    text_output.see(tk.END)   
    bnum += 1
    for problemID in range(anum, bnum):

        time.sleep(random.randint(1, 3))
        url = 'https://www.luogu.com.cn/problem/P' + str(problemID)

        title = Get_Problem_title(problemID)
        print('题目标题：' + str(title))
        text_output.insert(tk.END, '题目标题：' + str(title) + '\n')
        text_output.see(tk.END)
        print('正在爬取题目...')
        text_output.insert(tk.END, '正在爬取题目...\n')
        text_output.see(tk.END)

        with open('d:/vscode/icoding/软工作业2/pachong/tk.txt', 'r') as f:
            lines = f.readlines()
            custom_user_agent = random.choice(lines).strip()
        headers = {
            'User-Agent': custom_user_agent,
        }
        r = requests.get(url, headers=headers, cookies=cookie)
        html = r.text

        if html == 'error':
            print('题目爬取失败！')
            text_output.insert(tk.END, '题目爬取失败！\n')
            text_output.see(tk.END)

        else:
            print('已获取题目网页源码！')
            text_output.insert(tk.END, '已获取题目网页源码！\n')
            text_output.see(tk.END)


            problemMD = Get_MD(html)
            print("获取题目MD文件成功！")
            text_output.insert(tk.END, "获取题目MD文件成功！\n")
            text_output.see(tk.END)

            filename = 'P' + str(problemID) + '-' + str(title) + '.md'

            if not os.path.exists('data/' + 'P' + str(problemID) + '-' + str(title)):
                os.mkdir('data/' + 'P' + str(problemID) + '-' + str(title))
                print('已创建文件夹：P' + str(problemID) + '-' + str(title))
                text_output.insert(tk.END, '已创建文件夹：P' + str(problemID) + '-' + str(title) + '\n')
                text_output.see(tk.END)
            else:
                print('文件夹已存在，无需创建！')
                text_output.insert(tk.END, '文件夹已存在，无需创建！\n')
                text_output.see(tk.END)
            with open('data/' + 'P' + str(problemID) + '-' + str(title) + '/' + filename, 'w', encoding='utf-8') as f:
                f.write(problemMD)
            print('题目爬取成功！')
            text_output.insert(tk.END, '题目爬取成功！\n')
            text_output.see(tk.END)

        print("正在爬取题解...")
        text_output.insert(tk.END, "正在爬取题解...\n")
        text_output.see(tk.END)
        url = 'https://www.luogu.com.cn/problem/solution/P' + str(problemID)
        r = requests.get(url, headers=headers, cookies=cookie)
        html = r.text
        if html == 'error':
            print("题解爬取失败！")
            text_output.insert(tk.END, "题解爬取失败！\n")
            text_output.see(tk.END)
        else:
            print("已获取题解网页源码！")
            text_output.insert(tk.END, "已获取题解网页源码！\n")
            text_output.see(tk.END)

            solutionMD = Get_TJ_MD(html)
            print("获取题解MD文件成功！")
            text_output.insert(tk.END, "获取题解MD文件成功！\n")
            text_output.see(tk.END)

            filename = 'P' + str(problemID) + '-' + str(title) + '-题解.md'
            with open('data/' + 'P' + str(problemID) + '-' + str(title) + '/' + filename, 'w', encoding='utf-8') as f:
                f.write(solutionMD)
            print('题解爬取成功！')
            text_output.insert(tk.END, '题解爬取成功！\n')
            text_output.see(tk.END)

    update_database_info()

    print('\n')
    print('所有题目爬取完毕！')
    text_output.insert(tk.END, '\n')
    text_output.see(tk.END)

    close_progress_window()
    messagebox.showinfo(title='提示', message='所有题目爬取完毕！')

def show_frame(frame, window_size=None):
    frame.tkraise()

    if window_size:
        root.geometry(window_size)


def center_widgets(frame):
    def start_button_click():
        global progress_window
        left_range = left_range_entry.get()
        right_range = right_range_entry.get()

        try:
            left_range = int(left_range)
            right_range = int(right_range)
            if left_range < 1000 or 9635 < right_range < left_range:
                messagebox.showerror("提示：", "请输入1000-9634之间的题号，且开始题号不能大于结束题号")
                return
        except ValueError:
            messagebox.showerror("提示：", "请输入有效的整数题号")
            return
        crawl_thread = threading.Thread(target=lambda: start_work(left_range, right_range))
        crawl_thread.start()
    inner_frame = tk.Frame(frame)
    inner_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")  

    left_range_label = tk.Label(inner_frame, text="开始题号:")
    left_range_label.grid(row=0, column=0, pady=9)
    left_range_entry = tk.Entry(inner_frame)
    left_range_entry.grid(row=0, column=1, pady=9)

    right_range_label = tk.Label(inner_frame, text="结束题号:")
    right_range_label.grid(row=1, column=0, pady=9)
    right_range_entry = tk.Entry(inner_frame)
    right_range_entry.grid(row=1, column=1, pady=9)

    start_button = tk.Button(inner_frame, text="开始爬取", command=start_button_click)
    start_button.grid(row=2, column=0, columnspan=2, pady=9)

    inner_frame.columnconfigure(0, weight=1)
    inner_frame.columnconfigure(1, weight=1)
    inner_frame.rowconfigure(0, weight=1)
    inner_frame.rowconfigure(1, weight=1)
    inner_frame.rowconfigure(2, weight=1)

def perform_search():
    global difficulty_var, source_options, keyword_entry, result_text, source_vars, source_listbox

    def load_problem_data():
        try:
            with open('info.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return []

    题目数据 = load_problem_data()

    selected_tags_indices = source_listbox.curselection()
    selected_tags = [source_options[i] for i in selected_tags_indices]

    selected_difficulty = difficulty_var.get()
    keyword = keyword_entry.get().lower()  

    result_text.delete(1.0, tk.END)

    found = False

    for 题目 in 题目数据:
        难度匹配 = selected_difficulty == "所有难度" or selected_difficulty == 题目["难度"]
        标签匹配 = not selected_tags or any(tag in selected_tags for tag in 题目["标签"])
        关键词匹配 = not keyword or keyword in 题目["题目"].lower() or any(
            keyword in tag.lower() for tag in 题目["标签"])
        if 难度匹配 and 标签匹配 and 关键词匹配:
            result_text.insert(tk.END,
                               f"题号：{题目['题号']}\n题目：{题目['题目']}\n难度：{题目['难度']}\n标签：{', '.join(题目['标签'])}\n\n")
            found = True  
    if not found:
        messagebox.showinfo("未找到", "未找到匹配的题目。")
        difficulty_var.set("所有难度")
        source_listbox.selection_clear(0, tk.END)  
        keyword_entry.delete(0, tk.END)  
def get_tags_from_json():
    try:
        with open('info.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags_set = set()  
            for item in data:
                tags_set.update(item['标签'])
            return list(tags_set)
    except FileNotFoundError:
        return []
def get_selected_tags():

    source_options = get_tags_from_json()
    selected_tags = [source_options[i] for i, var in enumerate(source_vars) if var.get()]
    return selected_tags

def clear_database():
    confirm = messagebox.askokcancel("确认清空", "您确定要清空数据库吗？")
    if confirm:
        data_directory = "./data"
        if os.path.exists(data_directory):
            for item in os.listdir(data_directory):
                item_path = os.path.join(data_directory, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    for sub_item in os.listdir(item_path):
                        sub_item_path = os.path.join(item_path, sub_item)
                        os.remove(sub_item_path)
                    os.rmdir(item_path)

            info_json_path = "./info.json"
            if os.path.exists(info_json_path):
                os.remove(info_json_path)

            messagebox.showinfo("数据库清空", "数据库和 info.json 文件已成功清空。")

            update_database_info()
        else:
            messagebox.showwarning("目录不存在", "data 目录不存在，无法清空数据库。")
def build_page2():
    global difficulty_var, source_options, keyword_entry, result_text, source_vars, database_info_label, source_listbox
    # root.geometry("500x400")
    image = Image.open("d:/vscode/icoding/软工作业2/pachong/bj2.png")  # 替换为你的图片路径
    bg_image1 = ImageTk.PhotoImage(image)
    page2_frame = tk.Frame(container)
    bg_label = tk.Label(container, image=bg_image1)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)   
    page2_frame.place(relx=0.5, rely=0.5, anchor='center')
    page2_frame.grid(row=0, column=0, sticky="nsew")
    back_to_main_page2 = tk.Button(page2_frame, text="返回首页", command=return_to_main_page)
    back_to_main_page2.grid(row=0, column=0, pady=10)
    filter_frame = tk.LabelFrame(page2_frame, text="筛选条件")
    filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")
    difficulty_label = tk.Label(filter_frame, text="选择题目难度:")
    difficulty_label.grid(row=0, column=0, padx=5, pady=5)
    difficulty_var = tk.StringVar()
    difficulty_var.set("难度")  # 默认值
    difficulty_option = tk.OptionMenu(filter_frame, difficulty_var, "暂无评定", "入门", "普及−", "普及/提高−",
                                      "普及+/提高", "提高+/省选−", "省选/NOI−", "NOI/NOI+/CTSC")
    difficulty_option.grid(row=0, column=1, padx=5, pady=5)

    source_label = tk.Label(filter_frame, text="选择标签:")
    source_label.grid(row=1, column=0, padx=5, pady=5)

    source_scrollbar = Scrollbar(filter_frame, orient=tk.VERTICAL)
    source_scrollbar.grid(row=1, column=2, pady=5, sticky="ns")

    source_listbox = Listbox(filter_frame, selectmode=tk.MULTIPLE, yscrollcommand=source_scrollbar.set)
    source_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    source_options = get_tags_from_json()
    for option in source_options:
        source_listbox.insert(tk.END, option)

    source_scrollbar.config(command=source_listbox.yview)

    keyword_label = tk.Label(page2_frame, text="搜索:")
    keyword_label.grid(row=2, column=0, padx=10, pady=5)
    keyword_entry = tk.Entry(page2_frame)
    keyword_entry.grid(row=2, column=1, padx=10, pady=5)

    search_button = tk.Button(page2_frame, text="搜索", command=perform_search)
    search_button.grid(row=3, column=0, columnspan=2, pady=10)

    result_text = tk.Text(page2_frame, wrap=tk.WORD, width=40, height=10)
    result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    return page2_frame

def build_page1():
    global database_info_label
    root.geometry("500x400")
    image = Image.open("d:/vscode/icoding/软工作业2/pachong/bj2.png")  # 替换为你的图片路径
    bg_image1 = ImageTk.PhotoImage(image)
    # 创建子页面1（爬虫界面）
    page1_frame = tk.Frame(container, width=400, height=300)
    page1_frame.grid(row=0, column=0, sticky="nsew")  # 使用 grid 布局管理器
    bg_label1 = tk.Label(page1_frame, image=bg_image)
    bg_label1.place(x=0, y=0, relwidth=1, relheight=1)
    # bg_label = tk.Label(container, image=bg_image1)
    # bg_label.place(x=0, y=0, relwidth=1, relheight=1)   
    page1_frame.place(relx=0.5, rely=0.5, anchor='center')
    # 在爬虫界面上添加返回首页按钮
    back_to_main_page1 = tk.Button(page1_frame, text="返回首页", command=return_to_main_page)
    back_to_main_page1.grid(row=0, column=0, pady=10)

    # 在子页面1上创建输入框和按钮
    center_widgets(page1_frame)

    return page1_frame

def return_to_main_page():

    show_frame(main_frame)


# 主函数，程序的开始
if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()
    root.title("洛谷爬虫")
    root.geometry("500x400")

    image = Image.open("d:/vscode/icoding/软工作业2/pachong/bj2.png")  # 替换为你的图片路径
    bg_image = ImageTk.PhotoImage(image)

    # 设置窗口图标
    root.iconbitmap("d://vscode//icoding//软工作业2//pachong//bj2.png")

    # 创建一个容器，用于承载不同的页面
    container = tk.Frame(root, width=500, height=400)
    bg_label = tk.Label(container, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    container.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1) 
    # 创建主页面
    main_frame = tk.Frame(container, width=500, height=400)
    main_frame.grid(row=0, column=0, sticky="nsew")
    bg_label1 = tk.Label(main_frame, image=bg_image)
    bg_label1.place(x=0, y=0, relwidth=1, relheight=1)  
    main_frame.place(relx=0.5, rely=0.5, anchor='center')
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)
    #main_frame.pack(expand=True, pady=(container.winfo_height() - container.winfo_height()) // 2)
    # 添加标题标签
    title_label = tk.Label(main_frame)
    title_label.grid(row=0, column=0, columnspan=2)  # 使用 grid 布局管理器，跨两列

    # 在主页面上添加按钮，用于进入子页面1和子页面2
    crawler_button = ttk.Button(main_frame, text="进入爬虫", command=lambda: show_frame(build_page1()))
    crawler_button.grid(row=1, column=0, pady=40)

    data_management_button = ttk.Button(main_frame, text="数据管理", command=lambda: show_frame(build_page2()))
    data_management_button.grid(row=1, column=1, pady=40)

    # 创建一个清空数据库按钮，并绑定到clear_database函数
    clear_database_button = ttk.Button(main_frame, text="清空数据库", command=clear_database)
    clear_database_button.grid(row=1, column=2, pady=40)

    # 创建一个 Label 组件来显示数据库条数和软件版本
    database_info_label = tk.Label(main_frame, text="数据库条数: 0   软件版本: V0.0.1")
    database_info_label.grid(row=2, column=0, columnspan=2, padx=17, pady=30, sticky="ne")  # 使用 grid 布局管理器，跨两列

    # 初始化数据库信息标签
    update_database_info()

    # 初始显示主页面
    show_frame(main_frame)

    # 运行主循环
    root.mainloop()
