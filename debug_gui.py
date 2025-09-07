#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 매크로 디버그 버전 - 핵심 문제 진단
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from datetime import datetime

print("모듈 임포트 완료")

class DebugGUI:
    def __init__(self):
        print("1. 초기화 시작")
        
        self.root = tk.Tk()
        print("2. tkinter 루트 생성 완료")
        
        self.root.title("디버그 GUI")
        self.root.geometry("600x400")
        print("3. 윈도우 설정 완료")
        
        # 기본 변수들
        self.log_queue = queue.Queue()
        self.server_time_offset = 0
        self.network_latency = 0
        print("4. 변수 초기화 완료")
        
        # GUI 생성
        self.create_widgets()
        print("5. 위젯 생성 완료")
        
        # 로그 처리기
        self.start_log_processor()
        print("6. 로그 처리기 시작 완료")
        
        print("초기화 완전 완료!")
    
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def create_widgets(self):
        """위젯 생성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="디버그 GUI", font=("맑은 고딕", 16)).pack(pady=10)
        
        # URL 입력
        ttk.Label(main_frame, text="URL:").pack(anchor=tk.W)
        self.url_var = tk.StringVar(value="https://www.google.com")
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).pack(fill=tk.X, pady=5)
        
        # 동기화 상태
        self.sync_status = tk.StringVar(value="동기화 안됨")
        ttk.Label(main_frame, text="상태:").pack(anchor=tk.W)
        ttk.Label(main_frame, textvariable=self.sync_status).pack(anchor=tk.W)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="간단한 테스트", command=self.simple_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="로그 테스트", command=self.log_test).pack(side=tk.LEFT, padx=5)
        
        # 로그 영역
        import tkinter.scrolledtext as scrolledtext
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 현재 시간 표시
        self.time_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.time_var, font=("Consolas", 12)).pack(pady=5)
        
        # 시간 업데이트 시작
        self.update_time()
    
    def simple_test(self):
        """간단한 테스트"""
        self.log("간단한 테스트 시작")
        self.sync_status.set("테스트 중...")
        
        def test_thread():
            try:
                for i in range(3):
                    time.sleep(1)
                    self.log(f"테스트 진행: {i+1}/3")
                
                self.sync_status.set("테스트 완료")
                self.log("테스트 완료!")
            except Exception as e:
                self.log(f"테스트 에러: {e}")
                self.sync_status.set("테스트 실패")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def log_test(self):
        """로그 테스트"""
        for i in range(5):
            self.log(f"로그 메시지 {i+1}")
    
    def start_log_processor(self):
        """로그 처리기"""
        def process_log():
            try:
                processed = 0
                while not self.log_queue.empty() and processed < 20:
                    message = self.log_queue.get_nowait()
                    self.log_text.insert(tk.END, message + "\\n")
                    self.log_text.see(tk.END)
                    processed += 1
            except queue.Empty:
                pass
            except Exception as e:
                print(f"로그 처리 오류: {e}")
            
            self.root.after(100, process_log)
        
        self.root.after(100, process_log)
        self.log("로그 시스템 활성화")
    
    def update_time(self):
        """시간 업데이트"""
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.time_var.set(f"현재 시간: {current_time}")
        self.root.after(500, self.update_time)
    
    def run(self):
        """실행"""
        print("mainloop 시작...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Ctrl+C 감지")
        except Exception as e:
            print(f"mainloop 에러: {e}")
        finally:
            print("mainloop 종료")


def main():
    print("디버그 프로그램 시작")
    try:
        app = DebugGUI()
        app.run()
    except Exception as e:
        print(f"프로그램 에러: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("프로그램 종료")


if __name__ == "__main__":
    main()
