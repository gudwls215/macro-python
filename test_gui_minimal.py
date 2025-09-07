#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최소한의 GUI 매크로 테스트 (문제 진단용)
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from datetime import datetime

class MinimalGUI:
    def __init__(self):
        print("최소 GUI 초기화...")
        self.root = tk.Tk()
        self.root.title("최소 GUI 테스트")
        self.root.geometry("500x400")
        
        # 기본 변수들
        self.log_queue = queue.Queue()
        self.server_time_offset = 0
        
        self.create_widgets()
        self.start_log_processor()
        
        print("최소 GUI 준비 완료!")
    
    def create_widgets(self):
        """기본 위젯만 생성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="최소 GUI 테스트", font=("맑은 고딕", 16)).pack(pady=10)
        
        # 간단한 버튼
        ttk.Button(main_frame, text="로그 테스트", command=self.test_log).pack(pady=5)
        
        # 로그 텍스트
        import tkinter.scrolledtext as scrolledtext
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 시간 표시
        self.time_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.time_var, font=("Consolas", 12)).pack(pady=5)
        
        # 시간 업데이트 시작
        self.update_time()
    
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def test_log(self):
        """로그 테스트"""
        self.log("버튼 클릭 테스트!")
        
        def background_task():
            for i in range(3):
                time.sleep(1)
                self.log(f"백그라운드 작업 {i+1}/3")
        
        threading.Thread(target=background_task, daemon=True).start()
    
    def start_log_processor(self):
        """로그 처리기 시작"""
        def process_log():
            try:
                # 모든 대기 중인 메시지 처리
                processed = 0
                while not self.log_queue.empty() and processed < 10:  # 최대 10개씩 처리
                    message = self.log_queue.get_nowait()
                    self.log_text.insert(tk.END, message + "\\n")
                    self.log_text.see(tk.END)
                    processed += 1
            except queue.Empty:
                pass
            except Exception as e:
                print(f"로그 처리 오류: {e}")
            
            # 100ms 후 다시 실행
            self.root.after(100, process_log)
        
        # 초기 실행
        self.root.after(100, process_log)
        self.log("로그 시스템 시작됨")
    
    def update_time(self):
        """시간 업데이트"""
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.time_var.set(f"현재 시간: {current_time}")
        
        # 500ms 후 다시 업데이트
        self.root.after(500, self.update_time)
    
    def run(self):
        """GUI 실행"""
        print("mainloop 시작...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Ctrl+C 감지됨")
        except Exception as e:
            print(f"GUI 에러: {e}")
        finally:
            print("GUI 종료됨")


def main():
    print("최소 GUI 프로그램 시작")
    try:
        app = MinimalGUI()
        app.run()
    except Exception as e:
        print(f"메인 에러: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("프로그램 완전 종료")


if __name__ == "__main__":
    main()
