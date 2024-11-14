from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
import requests
import time

class OikidBooking:
    def __init__(self, update_status=None):
        self.driver = webdriver.Chrome()
        self.login_url = 'https://www.oikid.com/login.php'
        self.booking_url = 'https://www.oikid.com/?a=Student/Booking2'
        self.email = None
        self.password = None
        self.update_status = update_status or (lambda x: print(x))
        
    def login(self):
        """登入"""
        try:
            self.driver.get(self.login_url)
            sleep(3)
            
            # 輸入帳號密碼
            email_input = self.driver.find_element(By.ID, 'idEmail')
            password_input = self.driver.find_element(By.NAME, 'Password')
            
            email_input.send_keys(self.email)
            password_input.send_keys(self.password)
            
            # 勾選自動登入
            auto_login = self.driver.find_element(By.ID, 'loginOne')
            if not auto_login.is_selected():
                auto_login.click()
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, '#idForm button[type="submit"]')
            login_button.click()
            
            sleep(3)
            self.update_status('登入成功!')
            
        except Exception as e:
            self.update_status(f'登入過程發生錯誤: {str(e)}')
            
    def book_class(self, teacher_name=None, selected_slots=None, retry_mode="wait", wait_time=3, max_attempts=10):
        """自動訂課"""
        try:
            self.update_status('===== 前往訂課頁面 =====')
            self.driver.get(self.booking_url)
            sleep(3)
            self.update_status('頁面載入完成')
            
            # 切換到老師模式標籤
            self.update_status('===== 切換到老師模式 =====')
            teacher_mode = self.driver.find_element(By.CSS_SELECTOR, '.tab.tabs-A a')
            teacher_mode.click()
            sleep(1)
            self.update_status('成功切換到老師模式')
            
            # 持續嘗試直到找到可預約時段
            attempt = 0
            
            while attempt < max_attempts:
                self.update_status(f'===== 第 {attempt + 1} 次嘗試 =====')
                
                if retry_mode == "next_week" or attempt == 0:
                    self.update_status('===== 選擇課程週次 =====')
                    next_week_label = self.driver.find_element(By.CSS_SELECTOR, 'label.checkWeek[for="id_w3"]')
                    next_week_label.click()
                    self.update_status('已選擇下週課程')
                    sleep(1)
                
                if teacher_name:
                    self.update_status(f'===== 搜尋老師: {teacher_name} =====')
                    teacher_list = self.driver.find_elements(By.CLASS_NAME, 'teacherList')
                    teacher_found = False
                    
                    for teacher in teacher_list:
                        if teacher_name in teacher.text:
                            teacher.click()
                            teacher_found = True
                            self.update_status(f'找到 {teacher_name} 老師並點擊成功')
                            break
                            
                    if not teacher_found:
                        self.update_status(f'警告: 找不到 {teacher_name} 老師')
                        return
                        
                    sleep(1)
                
                # 找到可預約的時段並點擊預約
                self.update_status('===== 搜尋可預約時段 =====')
                available_slots = self.driver.find_elements(By.CLASS_NAME, 'booked1')
                
                if available_slots:
                    self.update_status(f'找到 {len(available_slots)} 個可預約時段')
                    booked_count = 0
                    
                    # 收集所有符合條件的課程 ID
                    class_ids = []
                    for slot in available_slots:
                        # 從 onclick 屬性中獲取課程資訊
                        onclick_attr = slot.get_attribute('onclick')
                        if onclick_attr:
                            # 解析 onclick 屬
                            # 格式: createClassroom(6527436, '確定預定「Aziza K Mark」老師「2024-11-06 19:00」時段？')
                            match_id = re.search(r'createClassroom\((\d+)', onclick_attr)
                            match_info = re.search(r'「(.*?)」老師.*?「(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})」', onclick_attr)
                            
                            if match_id and match_info:
                                class_id = match_id.group(1)
                                teacher_name_found = match_info.group(1)
                                time_str = match_info.group(2)  # 2024-11-06 19:00
                                
                                # 解析時間資訊
                                try:
                                    from datetime import datetime
                                    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                                    weekday = dt.weekday()  # 0-6 (週一-週日)
                                    time_only = dt.strftime('%H:%M')
                                    
                                    # 轉換星期格式
                                    weekday_map = {
                                        0: '週一', 1: '週二', 2: '週三', 
                                        3: '週四', 4: '週五', 5: '週六', 6: '週日'
                                    }
                                    full_weekday = weekday_map[weekday]
                                    
                                    # 檢查是否符合選擇的時段
                                    for day, time in selected_slots:
                                        if day == full_weekday and time == time_only:
                                            class_ids.append({
                                                'id': class_id,
                                                'time_info': time_str,
                                                'teacher_name': teacher_name_found
                                            })
                                            self.update_status(f'找到符合的時段: {full_weekday} {time_only}')
                                            break
                                        
                                except Exception as e:
                                    self.update_status(f'解析時間時發生錯誤: {str(e)}')
                                    continue
                
                    # 執行所有預約
                    self.update_status(f'找到 {len(class_ids)} 個符合條件的時段')
                    for class_info in class_ids:
                        if self._create_classroom(class_info['id'], class_info['time_info'], class_info['teacher_name']):
                            booked_count += 1
                    
                    self.update_status(f'成功預約 {booked_count} 堂課')
                    break  # 找到可預約時段後跳出迴圈
                else:
                    self.update_status(f'警告: 第 {attempt + 1} 次嘗試沒有找到可預約的時段')
                    if retry_mode == "wait":
                        self.update_status(f'等待 {wait_time} 秒後重試...')
                        sleep(wait_time)
                    else:
                        self.update_status('將重新選擇下週...')
                        sleep(0.5)
                    attempt += 1
            
            if attempt >= max_attempts:
                self.update_status('已達到最大重試次數，仍未找到可預時段')
                
        except Exception as e:
            self.update_status('===== 發生錯誤 =====')
            self.update_status(f'錯誤類型: {type(e).__name__}')
            self.update_status(f'錯誤訊息: {str(e)}')
            self.update_status('訂課過程中斷')
        finally:
            self.update_status('===== 訂課程序結束 =====')
    
    def _create_classroom(self, class_id, time_info, teacher_name):
        """執行預約 API"""
        try:
            self.update_status(f'正在預約課程 ID: {class_id}')
            
            # 發送預約請求
            booking_url = 'https://www.oikid.com/?a=Student/Booking2&b=CreateClassroom'
            data = {
                'id': class_id
            }
            
            # 使用 selenium 的 cookies
            cookies = {}
            for cookie in self.driver.get_cookies():
                cookies[cookie['name']] = cookie['value']
                
            # 印出請求資訊
            # print("\n=== API Request Info ===")
            # print(f"URL: {booking_url}")
            # print(f"Data: {data}")
            # print(f"Cookies: {cookies}")
            # print("=====================\n")
            
            response = requests.post(
                booking_url,
                data=data,
                cookies=cookies
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('Result') == True:
                        self.update_status('預約成功!')
                        self.update_status(f'老師: {teacher_name}')
                        self.update_status(f'時段: {time_info}')
                        self.update_status(f'使用點數: {result["Data"]["NeedPoints"]}')
                        return True
                    else:
                        self.update_status('預約失敗!')
                        self.update_status(f'錯誤訊息: {result["Data"]["Message"]}')
                        return False
                except:
                    self.update_status('無法解析伺服器回應')
                    return False
            else:
                self.update_status(f'伺服器回應錯誤: {response.status_code}')
                return False
                
        except Exception as e:
            self.update_status(f'預約時時發生錯誤: {str(e)}')
            return False
    
    def finish(self):
        """關閉瀏覽器"""
        self.driver.quit()
    
    def add_favorite_teachers(self, teachers_list):
        """新增喜愛老師到收藏清單"""
        try:
            # 前往正確的收藏老師頁面
            self.driver.get("https://www.oikid.com/?a=Student/TeacherPrefer")
            time.sleep(2)  # 等待頁面載入
            
            for teacher in teachers_list:
                try:
                    # 找到搜尋輸入框並輸入老師名稱
                    search_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='Name']")
                    search_input.clear()
                    search_input.send_keys(teacher)
                    
                    # 點擊搜尋按鈕
                    search_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='teacherList']")
                    search_button.click()
                    time.sleep(1)  # 等待搜尋結果
                    
                    # 在搜尋結果中尋找老師
                    teacher_list = self.driver.find_element(By.ID, "idUserTeacherList")
                    
                    # 尋找所有星星圖示
                    star_icons = teacher_list.find_elements(By.CSS_SELECTOR, "i.fa.fa-star")
                    
                    if star_icons:
                        for star in star_icons:
                            # 檢查是否已經收藏
                            if 'fa-checked' not in star.get_attribute('class'):
                                star.click()
                                self.update_status(f"已將 {teacher} 加入收藏")
                                time.sleep(1)  # 等待收藏完成
                                break
                            else:
                                self.update_status(f"{teacher} 已在收藏清單中")
                                break
                    else:
                        self.update_status(f"找不到 {teacher} 的收藏按鈕")
                    
                except Exception as e:
                    self.update_status(f"處理老師 {teacher} 時發生錯誤: {str(e)}")
                    continue
            
        except Exception as e:
            raise Exception(f"新增收藏老師失敗: {str(e)}")

# 執行訂課
if __name__ == '__main__':
    bot = OikidBooking()
    bot.book_class()
    bot.finish() 