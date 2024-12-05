#目前缺少的三项功能：
#番茄钟功能：开始任务后X分钟提醒一次，X的值可以由用户设置
#任务备注：可以为任务添加备注。
#删除已有任务：可以删除已经结束的任务。

import tkinter as tk
from tkinter import messagebox
import time
import csv
from datetime import datetime

class TimeManagerApp:
    def __init__(self, root):
        self.root=root
        self.root.title("禅定空间")

        self.task_start_time=None
        self.task_name=""
        self.records=[]
        
        self.create_widgets()

    def create_widgets(self):
        # Task name input
        self.task_name_label = tk.Label(self.root,text="任务名称:")
        self.task_name_label.grid(row=0,column=0,padx=10,pady=10)
        #以后修改为组合框Combobox
        self.task_name_entry = tk.Entry(self.root)
        self.task_name_entry.grid(row=0,column=1,padx=10,pady=10)

        self.start_button = tk.Button(self.root,text="开始任务",command=self.start_task)
        self.start_button.grid(row=1,column=0,padx=10,pady=10)

        self.end_button = tk.Button(self.root,text="结束任务",command=self.end_task,state=tk.DISABLED)
        self.end_button.grid(row=1,column=1,padx=10,pady=10)

        self.history_button = tk.Button(self.root, text="查看历史记录",command=self.view_history)
        self.history_button.grid(row=2,column=0,padx=10,pady=10)

        self.statistics_button = tk.Button(self.root, text="查看历史统计",command=self.view_statistics)
        self.statistics_button.grid(row=2, column=1, padx=10, pady=10)

    def start_task(self):
        self.task_name = self.task_name_entry.get()
        if not self.task_name:
            messagebox.showerror("错误","请输入任务名称！")
            return

        self.task_start_time = time.time()              #记录当前时间

        self.start_button.config(state=tk.DISABLED)     #禁用开始按钮
        self.task_name_entry.config(state=tk.DISABLED)  #禁用任务名称输入框
        self.end_button.config(state=tk.NORMAL)         #启用结束按钮

    def end_task(self):
        if not self.task_start_time:
            messagebox.showerror("错误","没有正在进行的任务！")
            return

        task_end_time=time.time()                           #记录任务结束时间
        task_duration=task_end_time - self.task_start_time  #计算任务持续时间
        task_duration_hours=(task_duration//60)//60         #小时数
        task_duration_minutes=(task_duration//60)%60        #分钟数
        task_duration_seconds=task_duration%60              #秒数

        #存储单次任务记录
        task_record = {
            "task_name": self.task_name,
            "start_time": datetime.fromtimestamp(self.task_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(task_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "duration": [task_duration_hours,task_duration_minutes,task_duration_seconds]
        }
        
        self.records.append(task_record)
        self.save_record_to_file(task_record)  #保存记录到文件

        self.task_start_time = None
        self.task_name = ""
        self.start_button.config(state=tk.NORMAL)
        self.task_name_entry.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        
        messagebox.showinfo("任务结束", f"任务 '{task_record['task_name']}' 完成！持续时间：{task_duration_minutes} 分钟")

    def save_record_to_file(self, record):
        # 保存任务记录到CSV文件
        with open("./src/task_records.csv", mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=record.keys())
            writer.writerow(record)

    def view_history(self):
        # 查看历史记录
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        
        with open("task_records.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader):
                record_text = f"{row['start_time']} - {row['end_time']} | {row['task_name']} | {row['duration']} 分钟"
                tk.Label(history_window, text=record_text).pack()

    def view_statistics(self):
        # 查看历史统计
        task_duration_by_day = {}
        
        with open("task_records.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                task_date = row['start_time'].split(' ')[0]
                task_duration = float(row['duration'])
                
                if task_date not in task_duration_by_day:
                    task_duration_by_day[task_date] = 0
                task_duration_by_day[task_date] += task_duration
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("历史统计")
        
        for date, total_duration in task_duration_by_day.items():
            stats_text = f"{date} - 总时长: {total_duration} 分钟"
            tk.Label(stats_window, text=stats_text).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeManagerApp(root)
    root.mainloop()