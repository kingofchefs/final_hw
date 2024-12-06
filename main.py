#目前缺少的三项功能：
#番茄钟功能：开始任务后X分钟提醒一次，X的值可以由用户设置
#任务备注：可以为任务添加备注。
#删除已有任务：可以删除已经结束的任务。

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import time
import csv
from datetime import datetime
from pathlib import Path

def change_seconds_into_hours_minutes_seconds(seconds):
    return [int((seconds//60)//60),int((seconds//60)%60),int(seconds%60)]

class PomodoroDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('番茄钟设置')
        self.pomodoro_enabled=False
        self.interval_minutes=0

        self.label=tk.Label(self,text='是否启用番茄钟功能?')
        self.label.pack(padx=10,pady=10)

        self.enable_button=tk.Button(self,text='启用',command=self.enable_pomodoro)
        self.enable_button.pack(padx=10, pady=5)

        self.disable_button = tk.Button(self, text='关闭', command=self.disable_pomodoro)
        self.disable_button.pack(padx=10, pady=5)

    def enable_pomodoro(self):
        self.pomodoro_enabled=True
        self.ask_for_interval()
        self.destroy()

    def disable_pomodoro(self):
        self.pomodoro_enabled=False
        self.destroy()

    def ask_for_interval(self):
        interval_str = simpledialog.askstring("番茄钟间隔", "请输入提醒间隔时间（分钟）：", parent=self)
        if interval_str and interval_str.isdigit():
            self.interval_minutes = int(interval_str)
        else:
            messagebox.showerror("输入错误", "请输入有效的分钟数！")

class TimeManagerApp:
    def __init__(self, root):
        self.root=root
        self.root.title("禅定空间")

        self.task_start_time=None
        self.task_name=""
        self.records=[]
        self.pomodoro_enabled=False
        self.pomodoro_interval=0
        self.pomodoro_start_time=None
        self.task_elapsed_time=0

        self.create_widgets()

    def create_widgets(self):
        self.task_name_label=tk.Label(self.root,text="任务名称:")
        self.task_name_label.grid(row=0,column=0,padx=10,pady=10)
        #以后修改为组合框Combobox
        self.task_name_entry=tk.Entry(self.root)
        self.task_name_entry.grid(row=0,column=1,padx=10,pady=10)

        self.start_button=tk.Button(self.root,text="开始任务",command=self.start_task)
        self.start_button.grid(row=1,column=0,padx=10,pady=10)

        self.end_button=tk.Button(self.root,text="结束任务",command=self.end_task,state=tk.DISABLED)
        self.end_button.grid(row=1,column=1,padx=10,pady=10)

        self.history_button=tk.Button(self.root,text="查看历史记录",command=self.view_history)
        self.history_button.grid(row=2,column=0,padx=10,pady=10)

        self.statistics_button=tk.Button(self.root,text="查看历史统计",command=self.view_statistics)
        self.statistics_button.grid(row=2,column=1,padx=10,pady=10)

        self.time_display_label=tk.Label(self.root,text="任务进行时长: 00:00:00")
        self.time_display_label.grid(row=3,column=0,columnspan=2,pady=10)

    def update_time_display(self):
        if self.task_start_time:
            elapsed_time=time.time()-self.task_start_time
            self.task_elapsed_time=elapsed_time
            hours,minutes,seconds=change_seconds_into_hours_minutes_seconds(elapsed_time)
            time_str=f'{hours:02}:{minutes:02}:{seconds:02}'
            self.time_display_label.config(text=f'任务进行时长: {time_str}')
            self.root.after(1000,self.update_time_display)

    def start_task(self):
        self.task_name = self.task_name_entry.get()
        if not self.task_name:
            messagebox.showerror("错误","请输入任务名称！")
            return

        pomodoro_dialog = PomodoroDialog(self.root)
        self.root.wait_window(pomodoro_dialog)

        if self.pomodoro_enabled:
            self.pomodoro_start_time = time.time()
            self.schedule_pomodoro_reminder()

        self.task_start_time = time.time()
        self.update_time_display()

        self.task_start_time = time.time()              

        self.start_button.config(state=tk.DISABLED)    
        self.task_name_entry.config(state=tk.DISABLED)  
        self.end_button.config(state=tk.NORMAL)         

    def end_task(self):
        if not self.task_start_time:
            messagebox.showerror("错误","没有正在进行的任务！")
            return

        task_end_time=time.time()                           
        task_duration=task_end_time - self.task_start_time  
        task_duration_hours=change_seconds_into_hours_minutes_seconds(task_duration)[0]         
        task_duration_minutes=change_seconds_into_hours_minutes_seconds(task_duration)[1]        
        task_duration_seconds=change_seconds_into_hours_minutes_seconds(task_duration)[2]              

        task_record = {
            "task_name": self.task_name,
            "start_time": datetime.fromtimestamp(self.task_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(task_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            'duration': task_duration,
            "duration_hours": task_duration_hours,
            "duration_minutes": task_duration_minutes,
            "duration_seconds": task_duration_seconds
        }
        
        self.records.append(task_record)
        self.save_record_to_file(task_record)  

        self.task_start_time = None
        self.task_name = ""
        self.start_button.config(state=tk.NORMAL)
        self.task_name_entry.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        
        messagebox.showinfo("任务结束", f"任务 '{task_record['task_name']}' 完成！持续时间：{task_record['duration_hours']}小时{task_record['duration_minutes']}分钟{task_record['duration_seconds']}秒")

    def schedule_pomodoro_reminder(self):
        self.root.after(self.pomodoro_interval*60000, self.remind_pomodoro)

    def remind_pomodoro(self):
        if self.pomodoro_enabled and self.task_start_time:
            elapsed_time=time.time()-self.pomodoro_start_time
            if elapsed_time>=self.pomodoro_interval*60:
                messagebox.showinfo("番茄钟提醒", f"已经工作了{self.pomodoro_interval}分钟，休息一下吧！")
                self.pomodoro_start_time=time.time()
                self.schedule_pomodoro_reminder()

    def save_record_to_file(self, record):
        current_directory=Path(__file__).parent
        file_path=current_directory/"task_records.csv"

        file_exists=file_path.exists()

        with open(file_path,mode="a",newline="") as file:
            writer=csv.DictWriter(file,fieldnames=record.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
    
        file_path=Path(__file__).parent/"task_records.csv"
        with open(file_path,mode="r") as file:
            reader=csv.DictReader(file)
            for idx,row in enumerate(reader):
                record_text=f"{row['start_time']} - {row['end_time']} | {row['task_name']} | {row['duration_hours']}小时{row['duration_minutes']}分钟{row['duration_seconds']}秒"
                tk.Label(history_window,text=record_text).pack()

    def view_statistics(self):
        task_duration_by_day = {}
        
        file_path=Path(__file__).parent/"task_records.csv"
        with open(file_path,mode="r") as file:
            reader=csv.DictReader(file)
            for row in reader:
                task_date=row['start_time'].split(' ')[0]
                task_duration=float(row['duration'])
                
                if task_date not in task_duration_by_day:
                    task_duration_by_day[task_date]=0
                task_duration_by_day[task_date]+=task_duration
        
        stats_window=tk.Toplevel(self.root)
        stats_window.title("历史统计")
        
        for date,total_duration in task_duration_by_day.items():
            duration_in_hours_minutes_seconds=change_seconds_into_hours_minutes_seconds(total_duration)
            stats_text=f"{date}  总时长: {duration_in_hours_minutes_seconds[0]}小时{duration_in_hours_minutes_seconds[1]}分钟{duration_in_hours_minutes_seconds[2]}秒"
            tk.Label(stats_window, text=stats_text).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeManagerApp(root)
    root.mainloop()