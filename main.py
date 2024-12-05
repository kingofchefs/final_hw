import tkinter as tk
from tkinter import messagebox
import time
import csv
from datetime import datetime

class TimeManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("时间管理应用")
        
        self.task_start_time = None
        self.task_name = ""
        self.records = []
        
        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        # Task name input
        self.task_name_label = tk.Label(self.root, text="任务名称:")
        self.task_name_label.grid(row=0, column=0, padx=10, pady=10)

        self.task_name_entry = tk.Entry(self.root)
        self.task_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Start button
        self.start_button = tk.Button(self.root, text="开始任务", command=self.start_task)
        self.start_button.grid(row=1, column=0, padx=10, pady=10)

        # End button
        self.end_button = tk.Button(self.root, text="结束任务", command=self.end_task, state=tk.DISABLED)
        self.end_button.grid(row=1, column=1, padx=10, pady=10)

        # History button
        self.history_button = tk.Button(self.root, text="查看历史记录", command=self.view_history)
        self.history_button.grid(row=2, column=0, padx=10, pady=10)

        # Statistics button
        self.statistics_button = tk.Button(self.root, text="查看历史统计", command=self.view_statistics)
        self.statistics_button.grid(row=2, column=1, padx=10, pady=10)

    def start_task(self):
        self.task_name = self.task_name_entry.get()
        if not self.task_name:
            messagebox.showerror("错误", "请输入任务名称！")
            return

        self.task_start_time = time.time()  # 记录当前时间
        self.start_button.config(state=tk.DISABLED)  # 禁用开始按钮
        self.end_button.config(state=tk.NORMAL)  # 启用结束按钮
        self.task_name_entry.config(state=tk.DISABLED)  # 禁用任务名称输入框

    def end_task(self):
        if not self.task_start_time:
            messagebox.showerror("错误", "没有正在进行的任务！")
            return

        task_end_time = time.time()  # 记录任务结束时间
        task_duration = task_end_time - self.task_start_time  # 计算任务持续时间
        task_duration_minutes = round(task_duration / 60, 2)  # 转换为分钟

        task_record = {
            "task_name": self.task_name,
            "start_time": datetime.fromtimestamp(self.task_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(task_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            "duration": task_duration_minutes
        }
        
        self.records.append(task_record)
        self.save_record_to_file(task_record)  # 保存记录到文件

        self.task_start_time = None
        self.task_name = ""
        self.start_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        self.task_name_entry.config(state=tk.NORMAL)
        
        messagebox.showinfo("任务结束", f"任务 '{task_record['task_name']}' 完成！持续时间：{task_duration_minutes} 分钟")

    def save_record_to_file(self, record):
        # 保存任务记录到CSV文件
        with open("task_records.csv", mode="a", newline="") as file:
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
