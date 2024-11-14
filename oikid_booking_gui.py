import tkinter as tk
from tkinter import ttk, messagebox
from oikid_booking import OikidBooking
import json
import os
from tkinter import PhotoImage
from selenium.webdriver.common.by import By
import time

class BookingGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('OiKID 自動訂課系統')
        self.window.geometry('1050x630')  # 調整視窗大小為更寬更高
        
        # 創建自定義按鈕樣式
        self.style = ttk.Style()
        self.style.configure('Booking.TButton', 
                           background='#4CAF50',  # 綠色背景
                           foreground='black',    # 黑色文字
                           font=('Arial', 12),    # 字體和大小
                           padding=10)            # 內邊距
        
        # 設置按鈕懸停效果
        self.style.map('Booking.TButton',
                      background=[('active', '#45a049')],  # 懸停時的顏色
                      foreground=[('active', 'black')])
        
        # 主要內容框架 - 增加 padding
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左側框架 - 調整寬度
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 20))
        
        # 帳號密碼區域框架 - 改為放在左側框架中
        self.credentials_frame = ttk.LabelFrame(self.left_frame, text="帳號設定", padding="10")
        self.credentials_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # 新增喜愛老師清單框架
        self.favorite_teachers_frame = ttk.LabelFrame(self.left_frame, text="新增喜愛老師清單", padding="10")
        self.favorite_teachers_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # 老師清單輸入框
        self.favorite_teachers_text = tk.Text(self.favorite_teachers_frame, height=4, width=40)
        self.favorite_teachers_text.grid(row=0, column=0, padx=5, pady=5)
        
        # 新增老師按鈕
        self.add_teachers_button = ttk.Button(self.favorite_teachers_frame, 
                                            text="新增老師", 
                                            command=self.add_favorite_teachers,
                                            style='Booking.TButton',
                                            state='disabled')
        self.add_teachers_button.grid(row=0, column=1, padx=5, pady=5)
        
        # 訂課模式框架 - 改為放在左側框架中
        self.booking_mode_frame = ttk.LabelFrame(self.left_frame, text="訂課模式", padding="10")
        self.booking_mode_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        # 載入離開圖示
        try:
            # 嘗試從當前目錄載入
            self.exit_icon = PhotoImage(file="exit_icon.png")
        except:
            try:
                # 嘗試從執行檔所在目錄載入
                import sys
                import os
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                icon_path = os.path.join(base_path, 'exit_icon.png')
                self.exit_icon = PhotoImage(file=icon_path)
            except:
                # 如果都失敗，使用文字替代
                self.exit_button = ttk.Button(self.login_buttons_frame, 
                                            text="X",
                                            command=self.confirm_exit)
                self.exit_button.grid(row=0, column=1)
                return
        
        # 如果圖示太大，可以縮小
        self.exit_icon = self.exit_icon.subsample(20, 20)  # 調整數字來改變縮放比例
        
        # 登入按鈕和離開按鈕放在同一個框架
        self.login_buttons_frame = ttk.Frame(self.credentials_frame)
        self.login_buttons_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=5)
        
        # 添加登入狀態變數
        self.is_logged_in = False
        
        # 登入按鈕
        self.login_button = ttk.Button(self.login_buttons_frame, 
                                    text="登入", 
                                    command=self.login_only,
                                    style='Booking.TButton')
        self.login_button.grid(row=0, column=0, padx=(0, 10))
        
        # 離開按鈕 - 使用圖示
        self.exit_button = ttk.Button(self.login_buttons_frame, 
                                   image=self.exit_icon,
                                   command=self.confirm_exit)
        self.exit_button.grid(row=0, column=1)
        
        # 為離開按鈕添加提示文字
        self.exit_button.bind('<Enter>', lambda e: self.show_tooltip("關閉程式"))
        self.exit_button.bind('<Leave>', lambda e: self.hide_tooltip())
        
        # 帳號輸入
        ttk.Label(self.credentials_frame, text="帳號 (Email):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(self.credentials_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 密碼輸入
        ttk.Label(self.credentials_frame, text="密碼:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.credentials_frame, textvariable=self.password_var, show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 綁定 Enter 鍵事件到密碼輸入框
        self.password_entry.bind('<Return>', lambda e: self.login_only())
        # 也可以綁定到帳號輸入框
        self.email_entry.bind('<Return>', lambda e: self.login_only())
        
        # 記住帳密選項
        self.remember_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.credentials_frame, text="記住帳號密碼", 
                       variable=self.remember_var).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 建立左右分隔框架
        self.booking_left_frame = ttk.Frame(self.booking_mode_frame)
        self.booking_left_frame.grid(row=0, column=0, padx=(0, 10))
        
        # 訂課模式選擇 - 移到左框架
        self.booking_mode = tk.StringVar(value="direct")
        ttk.Radiobutton(self.booking_left_frame, text="直接選課", 
                       variable=self.booking_mode, value="direct",
                       command=self.toggle_teacher_entry).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(self.booking_left_frame, text="指定老師", 
                       variable=self.booking_mode, value="teacher",
                       command=self.toggle_teacher_entry).grid(row=0, column=1, padx=10)
        
        # 老師名稱輸入 - 移到左框架
        ttk.Label(self.booking_left_frame, text="老師名稱:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.teacher_var = tk.StringVar()
        self.teacher_entry = ttk.Entry(self.booking_left_frame, textvariable=self.teacher_var, width=30)
        self.teacher_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 重試模式選擇和等待時間設定 - 整合在一起
        self.retry_mode = tk.StringVar(value="wait")
        ttk.Label(self.booking_left_frame, text="重試模式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(self.booking_left_frame, text="等待重試", 
                       variable=self.retry_mode, value="wait").grid(row=2, column=1, padx=(5, 0))
        
        # 等待秒數設定 - 緊接在等待重試後面
        self.wait_time_var = tk.StringVar(value="0.5")
        ttk.Entry(self.booking_left_frame, textvariable=self.wait_time_var, width=3).grid(row=2, column=2, padx=1)
        ttk.Label(self.booking_left_frame, text="秒").grid(row=2, column=3, padx=(0, 10))
        
        # 重選下週選項 - 移到最後
        ttk.Radiobutton(self.booking_left_frame, text="重選下週", 
                       variable=self.retry_mode, value="next_week").grid(row=2, column=4, padx=5)
        
        # 重試次數設定 - 保持原位
        ttk.Label(self.booking_left_frame, text="重試次數:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.max_attempts_var = tk.StringVar(value="10")
        self.max_attempts_entry = ttk.Entry(self.booking_left_frame, textvariable=self.max_attempts_var, width=10)
        self.max_attempts_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 時段選擇框架 - 調整大小和間距
        self.time_slots_frame = ttk.LabelFrame(self.main_frame, text="時段選擇", padding="15")
        self.time_slots_frame.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(0, 10))
        
        # 建立星期和時間的選擇矩陣
        self.weekdays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        self.times = [
            '12:00', '12:30',
            '13:00', '13:30',
            '14:00', '14:30',
            '15:00', '15:30',
            '16:00', '16:30',
            '17:00', '17:30',
            '18:00', '18:30',
            '19:00', '19:30',
            '20:00'
        ]
        
        # 儲存所有 Checkbutton 的變數
        self.slot_vars = {}
        
        # 建立表頭（星期）- 增加間距
        for i, day in enumerate(self.weekdays):
            ttk.Label(self.time_slots_frame, text=day).grid(row=0, column=i+1, padx=8, pady=8)
        
        # 建立時段標籤和對應的勾選框 - 增加間距
        for i, time in enumerate(self.times):
            ttk.Label(self.time_slots_frame, text=time).grid(row=i+1, column=0, padx=8, pady=5, sticky=tk.E)
            
            for j, day in enumerate(self.weekdays):
                var = tk.BooleanVar()
                self.slot_vars[(day, time)] = var
                ttk.Checkbutton(self.time_slots_frame, variable=var).grid(row=i+1, column=j+1, padx=8, pady=5)
        
        # 開始訂課按鈕 - 放在右側，設計成正方形
        self.style.configure('Square.Booking.TButton', 
                            padding=10,      # 減少內邊距
                            width=8,         # 保持原有寬度
                            height=1)        # 減少高度

        self.book_button = ttk.Button(self.booking_mode_frame, 
                                     text="開始\n訂課", 
                                     command=self.start_booking,
                                     style='Square.Booking.TButton',
                                     state='disabled')
        self.book_button.grid(row=0, column=1, rowspan=2, padx=(10, 0), sticky='ns')  # 減少 rowspan
        
        # 狀態顯示 - 調整大小
        self.status_text = tk.Text(self.left_frame, height=10, width=80)
        self.status_text.grid(row=3, column=0, pady=10)
        
        # 載入儲存的帳密
        self.load_credentials()
        
        # 初始化老師輸入框狀態
        self.toggle_teacher_entry()
        
        # 設置列和行的權重，使其能夠正確展開
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def load_credentials(self):
        """載入儲存的帳號密碼和老師清單"""
        if os.path.exists('credentials.json'):
            try:
                with open('credentials.json', 'r') as f:
                    data = json.load(f)
                    self.email_var.set(data.get('email', ''))
                    self.password_var.set(data.get('password', ''))
                    # 載入老師清單
                    teachers = data.get('teachers', '')
                    self.favorite_teachers_text.delete('1.0', tk.END)
                    if teachers:
                        self.favorite_teachers_text.insert('1.0', teachers)
            except:
                pass
    
    def save_credentials(self):
        """儲存帳號密碼和老師清單"""
        if self.remember_var.get():
            data = {
                'email': self.email_var.get(),
                'password': self.password_var.get(),
                # 儲存老師清單
                'teachers': self.favorite_teachers_text.get('1.0', tk.END).strip()
            }
            with open('credentials.json', 'w') as f:
                json.dump(data, f)
    
    def update_status(self, message):
        """更新狀態顯示"""
        self.status_text.insert(tk.END, message + '\n')
        self.status_text.see(tk.END)
        self.window.update()
    
    def toggle_teacher_entry(self):
        """切換老師稱輸入框的啟用狀態"""
        if self.booking_mode.get() == "teacher":
            self.teacher_entry.state(['!disabled'])
        else:
            self.teacher_entry.state(['disabled'])
            self.teacher_var.set("")

    def get_selected_slots(self):
        """獲取所有被選中的時段"""
        selected = []
        for (day, time), var in self.slot_vars.items():
            if var.get():
                selected.append((day, time))
        return selected

    def start_booking(self):
        """開始訂課流程"""
        # 檢查是否已登入
        if not self.is_logged_in:
            messagebox.showwarning('提示', '請先輸入帳號密碼並登入')
            return
            
        # 檢查指定老師模式
        if self.booking_mode.get() == "teacher" and not self.teacher_var.get().strip():
            messagebox.showerror('錯誤', '請輸入老師名稱')
            return
        
        # 獲取選中的時段
        selected_slots = self.get_selected_slots()
        if not selected_slots:
            messagebox.showerror('錯誤', '請至少選擇一個時段')
            return
            
        # 清空狀態顯示
        self.status_text.delete(1.0, tk.END)
        self.update_status('開始訂課流程...')
        
        try:
            # 獲取重試模式和等待時間
            retry_mode = self.retry_mode.get()
            wait_time = float(self.wait_time_var.get())
            max_attempts = int(self.max_attempts_var.get())
            
            # 開始訂課
            self.book_button.state(['disabled'])
            
            if self.booking_mode.get() == "teacher":
                self.bot.book_class(
                    teacher_name=self.teacher_var.get().strip(), 
                    selected_slots=selected_slots,
                    retry_mode=retry_mode,
                    wait_time=wait_time,
                    max_attempts=max_attempts
                )
            else:
                self.bot.book_class(
                    teacher_name=None, 
                    selected_slots=selected_slots,
                    retry_mode=retry_mode,
                    wait_time=wait_time,
                    max_attempts=max_attempts
                )
                
            self.update_status('訂課完成!')
            
        except Exception as e:
            self.update_status(f'發生錯誤: {str(e)}')
            messagebox.showerror('錯誤', f'訂課過程發生錯誤:\n{str(e)}')
            
        finally:
            self.book_button.state(['!disabled'])

    def login_only(self):
        """只執行登入功能"""
        if self.is_logged_in:  # 如果已經登入，就不執行
            return
            
        email = self.email_var.get()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror('錯誤', '請輸入帳號密碼')
            return
            
        # 儲存帳密
        self.save_credentials()
        
        # 清空狀態顯示
        self.status_text.delete(1.0, tk.END)
        self.update_status('開始登入...')
        
        try:
            # 建立訂課物件
            self.bot = OikidBooking(update_status=self.update_status)
            self.bot.email = email
            self.bot.password = password
            
            # 執行登入
            self.login_button.state(['disabled'])
            self.login_button.configure(text="登入中...")  # 更改按鈕文字
            self.bot.login()
            
            # 登入成功後
            self.is_logged_in = True  # 設置登入狀態
            self.login_button.configure(text="已登入")  # 更改按鈕文字
            self.book_button.state(['!disabled'])
            self.add_teachers_button.state(['!disabled'])  # 啟用新增老師按鈕
            self.update_status('登入成功可以開始訂課了')
            
        except Exception as e:
            self.is_logged_in = False  # 登入失敗
            self.login_button.configure(text="登入")  # 恢復按鈕文字
            self.update_status(f'登入發生錯誤: {str(e)}')
            messagebox.showerror('錯誤', f'登入過程發生錯誤:\n{str(e)}')
            self.login_button.state(['!disabled'])

    def exit_program(self):
        """關閉程式"""
        if hasattr(self, 'bot'):
            try:
                self.bot.finish()
            except:
                pass
        self.window.quit()

    def run(self):
        """執行 GUI"""
        self.window.mainloop()

    def show_tooltip(self, text):
        """顯示提示文字"""
        x, y, _, _ = self.exit_button.bbox("insert")
        x += self.exit_button.winfo_rootx() + 25
        y += self.exit_button.winfo_rooty() + 20

        # 創建提示窗口
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        """隱藏提示文字"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
    
    def confirm_exit(self):
        """確認離開程式"""
        if messagebox.askyesno('確認離開', 
                             '確定要離開程式嗎？\n這將會關閉瀏覽器並結束所有操作。'):
            self.exit_program()

    def add_favorite_teachers(self):
        """新增喜愛老師"""
        # 檢查是否已登入
        if not self.is_logged_in:
            messagebox.showwarning('提示', '請先登入')
            return

        # 獲取老師清單
        teachers = self.favorite_teachers_text.get("1.0", tk.END).strip()
        if not teachers:
            messagebox.showwarning('提示', '請輸入老師名稱')
            return
        
        teachers_list = [t.strip() for t in teachers.split('\n') if t.strip()]
        
        try:
            self.update_status('===== 開始新增喜愛老師 =====')
            # 使用 self.bot 來訪問 driver
            self.bot.add_favorite_teachers(teachers_list)
            
            # 儲存老師清單
            self.save_credentials()
            
            self.update_status('===== 新增喜愛老師完成 =====')
            
        except Exception as e:
            self.update_status(f'新增喜愛老師時發生錯誤: {str(e)}')
            messagebox.showerror('錯誤', f'新增喜愛老師時發生錯誤:\n{str(e)}')

if __name__ == '__main__':
    app = BookingGUI()
    app.run() 