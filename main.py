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
    def __init__(self,parent,on_update):
        super().__init__(parent)
        self.title('番茄钟设置')
        self.pomodoro_enabled=False
        self.pomodoro_gap=0

        self.on_update=on_update

        self.label=tk.Label(self, text='是否启用番茄钟功能?')
        self.label.pack(padx=10, pady=10)

        self.enable_button=tk.Button(self,text='启用',command=self.enable_pomodoro)
        self.enable_button.pack(padx=10, pady=5)

        self.disable_button=tk.Button(self,text='关闭',command=self.disable_pomodoro)
        self.disable_button.pack(padx=10, pady=5)

    def enable_pomodoro(self):
        self.pomodoro_enabled=True
        self.ask_for_gap()
        self.on_update(self.pomodoro_enabled,self.pomodoro_gap)
        self.destroy()

    def disable_pomodoro(self):
        self.pomodoro_enabled=False
        self.on_update(self.pomodoro_enabled, self.pomodoro_gap) 
        self.destroy()

    def ask_for_gap(self):
        gap_str=simpledialog.askstring("番茄钟间隔","请输入提醒间隔时间（分钟）：",parent=self)
        if gap_str and gap_str.isdigit():
            self.pomodoro_gap=int(gap_str)
        else:
            messagebox.showerror("输入错误", "请输入有效的分钟数！")
            self.ask_for_gap()

class TimeManagerApp:
    def __init__(self, root):
        self.root=root
        self.root.title("禅定空间")

        self.task_start_time=None
        self.task_name=""
        self.task_note=""
        self.records=[]
        self.pomodoro_enabled=False
        self.pomodoro_gap=0
        self.pomodoro_start_time=None
        self.pomodoro_reminder_time=None
        self.task_elapsed_time=0

        self.create_widgets()

    def create_widgets(self):
        self.task_name_label=tk.Label(self.root,text="任务名称:")
        self.task_name_label.grid(row=0,column=0,padx=10,pady=10)
        
        self.task_name_entry=tk.Entry(self.root)
        self.task_name_entry.grid(row=0,column=1,padx=10,pady=10)

        self.task_note_label=tk.Label(self.root,text="任务备注：")
        self.task_note_label.grid(row=1,column=0,padx=10,pady=10)

        self.task_note_entry=tk.Entry(self.root)
        self.task_note_entry.grid(row=1,column=1,padx=10,pady=10)

        self.start_button=tk.Button(self.root,text="开始任务",command=self.start_task)
        self.start_button.grid(row=2,column=0,padx=10,pady=10)

        self.end_button=tk.Button(self.root,text="结束任务",command=self.end_task,state=tk.DISABLED)
        self.end_button.grid(row=2,column=2,padx=10,pady=10)

        self.history_button=tk.Button(self.root,text="查看历史记录",command=self.view_history)
        self.history_button.grid(row=3,column=0,padx=10,pady=10)

        self.delete_history_button=tk.Button(self.root,text="删除历史记录",command=self.delete_history)
        self.delete_history_button.grid(row=3,column=1,padx=10,pady=10)

        self.statistics_button=tk.Button(self.root,text="查看历史统计",command=self.view_statistics)
        self.statistics_button.grid(row=3,column=2,padx=10,pady=10)

        self.time_display_label=tk.Label(self.root,text="任务进行时长: 00:00:00")
        self.time_display_label.grid(row=4,column=0,columnspan=2,pady=10)

    def update_time_display(self):
        if self.task_start_time:
            elapsed_time=time.time()-self.task_start_time
            self.task_elapsed_time=elapsed_time
            hours,minutes,seconds=change_seconds_into_hours_minutes_seconds(elapsed_time)
            time_str=f'{hours:02}:{minutes:02}:{seconds:02}'
            self.time_display_label.config(text=f'任务进行时长: {time_str}')
            self.root.after(1000,self.update_time_display)

    def start_task(self):
        self.task_name=self.task_name_entry.get()
        self.task_note=self.task_note_entry.get()

        if not self.task_name:
            messagebox.showerror("错误","请输入任务名称！")
            return

        pomodoro_dialog = PomodoroDialog(self.root,self.update_pomodoro_settings)
        self.root.wait_window(pomodoro_dialog)

        if self.pomodoro_enabled:
            self.pomodoro_start_time=time.time()
            self.schedule_pomodoro_reminder()

        self.task_start_time=time.time()
        self.update_time_display()       

        self.start_button.config(state=tk.DISABLED)    
        self.task_name_entry.config(state=tk.DISABLED)  
        self.task_note_entry.config(state=tk.DISABLED)
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
            "task_note":self.task_note,
            "start_time": datetime.fromtimestamp(self.task_start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": datetime.fromtimestamp(task_end_time).strftime('%Y-%m-%d %H:%M:%S'),
            'duration': task_duration,
            "duration_hours": task_duration_hours,
            "duration_minutes": task_duration_minutes,
            "duration_seconds": task_duration_seconds
        }
        
        self.records.append(task_record)
        self.save_record_to_file(task_record)  

        self.task_start_time=None
        self.task_name=""
        self.task_note=""
        self.start_button.config(state=tk.NORMAL)
        self.task_name_entry.config(state=tk.NORMAL)
        self.task_note_entry.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        
        messagebox.showinfo("任务结束",f"任务 '{task_record['task_name']}' 完成！持续时间：{task_record['duration_hours']}小时{task_record['duration_minutes']}分钟{task_record['duration_seconds']}秒")

    def update_pomodoro_settings(self,enabled,gap):
        self.pomodoro_enabled=enabled
        self.pomodoro_gap=gap

    def schedule_pomodoro_reminder(self):
        if self.pomodoro_enabled and self.pomodoro_gap>0:
            self.pomodoro_reminder_time=self.pomodoro_start_time+self.pomodoro_gap*60 
            self.check_pomodoro_reminder()

    def check_pomodoro_reminder(self):
        if self.pomodoro_enabled:
            current_time=time.time()
            if current_time>=self.pomodoro_reminder_time:
                messagebox.showinfo("番茄钟提醒", "时间到了！休息一下吧！")
                self.pomodoro_start_time=current_time
                self.pomodoro_reminder_time=self.pomodoro_start_time+self.pomodoro_gap*60
            self.root.after(60000,self.check_pomodoro_reminder)

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
        history_window=tk.Toplevel(self.root)
        history_window.title("历史记录")

        text_widget=tk.Text(history_window,width=100,height=20)
        text_widget.pack(padx=10, pady=10)

        file_path=Path(__file__).parent/"task_records.csv"

        if not file_path.exists():
            text_widget.insert(tk.END,"没有历史记录！")
            return

        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader):
                start_time=f"{row['start_time']}"
                end_time=f"{row['end_time']}"
                task_name=f"{row['task_name']}"
                task_note=f"{row['task_note']}" 
                duration=f"{row['duration_hours']}小时{row['duration_minutes']}分钟{row['duration_seconds']}秒"
                text_widget.insert(tk.END, f"{start_time} - {end_time} | {task_name} | {task_note} | {duration}\n")
            
            text_widget.config(state=tk.DISABLED)

    def delete_history(self):
        confirmation=messagebox.askyesno("确认删除","您确定要删除所有历史记录吗？")
        if confirmation:
            file_path=Path(__file__).parent/"task_records.csv"
            if file_path.exists():
                file_path.unlink()
                messagebox.showinfo("成功","历史记录已成功删除！")
            else:
                messagebox.showerror("错误","没有历史记录！")

    def view_statistics(self):
        task_duration_by_day={}
        task_category_duration_by_day={}
        
        stats_window=tk.Toplevel(self.root)
        stats_window.title("历史统计")

        text_widget=tk.Text(stats_window)
        text_widget.pack(padx=10,pady=10)

        file_path=Path(__file__).parent/"task_records.csv"
        
        if not file_path.exists():
            text_widget.insert(tk.END,"没有历史统计！")
            return

        with open(file_path,mode="r") as file:
            reader=csv.DictReader(file)
            for row in reader:
                task_date=row['start_time'].split(' ')[0]
                task_duration=float(row['duration'])
                task_category=row['task_name']


                if task_date not in task_duration_by_day:
                    task_duration_by_day[task_date]=0
                task_duration_by_day[task_date]+=task_duration

                if task_date not in task_category_duration_by_day:
                    task_category_duration_by_day[task_date]={}

                if task_category not in task_category_duration_by_day[task_date]:
                    task_category_duration_by_day[task_date][task_category]=0
                task_category_duration_by_day[task_date][task_category]+=task_duration

        for date,total_duration in task_duration_by_day.items():
            duration_in_hours_minutes_seconds=change_seconds_into_hours_minutes_seconds(total_duration)
            stats_text=f"{date} 总时长: {duration_in_hours_minutes_seconds[0]}小时 {duration_in_hours_minutes_seconds[1]}分钟 {duration_in_hours_minutes_seconds[2]}秒"
            text_widget.insert(tk.END,f"{stats_text}\n")
        
        for date, category_durations in task_category_duration_by_day.items():
            for category, category_duration in category_durations.items():
                duration_in_hours_minutes_seconds = change_seconds_into_hours_minutes_seconds(category_duration)
                stats_text=f"{date} {category} 总时长: {duration_in_hours_minutes_seconds[0]}小时 {duration_in_hours_minutes_seconds[1]}分钟 {duration_in_hours_minutes_seconds[2]}秒"
                text_widget.insert(tk.END,f"{stats_text}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeManagerApp(root)
    root.mainloop()