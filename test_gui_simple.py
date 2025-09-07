#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 GUI 테스트 - 문제 진단용
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class SimpleTestGUI:
    def __init__(self):
        print("GUI 초기화 시작...")
        self.root = tk.Tk()
        self.root.title("간단한 테스트 GUI")
        self.root.geometry("400x300")
        
        print("위젯 생성 중...")
        self.create_widgets()
        
        print("GUI 준비 완료!")
    
    def create_widgets(self):
        """간단한 위젯 생성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="GUI 테스트", font=("맑은 고딕", 16)).pack(pady=10)
        
        ttk.Button(main_frame, text="테스트 버튼", command=self.test_button).pack(pady=5)
        
        self.status_label = ttk.Label(main_frame, text="준비됨")
        self.status_label.pack(pady=10)
        
        # 시간 표시
        self.time_label = ttk.Label(main_frame, text="", font=("Consolas", 12))
        self.time_label.pack(pady=5)
        
        self.update_time()
    
    def test_button(self):
        """테스트 버튼 클릭"""
        self.status_label.config(text="버튼 클릭됨!")
        
        def reset_status():
            time.sleep(2)
            self.status_label.config(text="준비됨")
        
        threading.Thread(target=reset_status, daemon=True).start()
    
    def update_time(self):
        """시간 업데이트"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"현재 시간: {current_time}")
        
        # 1초 후 다시 업데이트
        self.root.after(1000, self.update_time)
    
    def run(self):
        """GUI 실행"""
        print("mainloop 시작...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Ctrl+C 감지됨")
        except Exception as e:
            print(f"에러 발생: {e}")
        finally:
            print("GUI 종료")


def main():
    print("프로그램 시작")
    try:
        app = SimpleTestGUI()
        app.run()
    except Exception as e:
        print(f"프로그램 에러: {e}")
    finally:
        print("프로그램 종료")


if __name__ == "__main__":
    main()
