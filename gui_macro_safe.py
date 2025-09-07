#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 GUI 버전 - 문제 해결
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import threading
import webbrowser
from datetime import datetime, timezone
from urllib.request import urlopen
import queue
import statistics
import subprocess
import os
import json

# 안전한 모듈 임포트
PYAUTOGUI_AVAILABLE = False
KEYBOARD_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    print("✅ pyautogui 로드 완료")
except ImportError:
    print("❌ pyautogui 없음")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("✅ keyboard 로드 완료")
except ImportError:
    print("❌ keyboard 없음")

print("모든 임포트 완료")

class SafeTimeSyncGUI:
    def __init__(self):
        print("SafeGUI 초기화 시작...")
        
        self.root = tk.Tk()
        self.root.title("정밀 구매 타이밍 매크로 v2.0 (안전 버전)")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # 기본 변수들
        self.server_time_offset = 0
        self.network_latency = 0
        self.is_running = False
        self.log_queue = queue.Queue()
        self.measurement_history = []
        
        print("변수 초기화 완료")
        
        # GUI 생성
        self.create_widgets()
        print("위젯 생성 완료")
        
        # 로그 처리기 시작
        self.start_log_processor()
        print("로그 처리기 시작 완료")
        
        print("SafeGUI 초기화 완료!")
    
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        ttk.Label(main_frame, text="정밀 구매 타이밍 매크로 v2.0 (안전 버전)", 
                 font=("맑은 고딕", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL 입력
        ttk.Label(main_frame, text="구매 사이트 URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value="https://www.google.com")
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 동기화 정보
        info_frame = ttk.LabelFrame(main_frame, text="동기화 정보", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.sync_status = tk.StringVar(value="❌ 동기화 안됨")
        ttk.Label(info_frame, text="상태:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.sync_status).grid(row=0, column=1, sticky=tk.W)
        
        self.latency_var = tk.StringVar(value="-")
        ttk.Label(info_frame, text="네트워크 지연:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.latency_var).grid(row=1, column=1, sticky=tk.W)
        
        self.offset_var = tk.StringVar(value="-")
        ttk.Label(info_frame, text="서버 시간차:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.offset_var).grid(row=2, column=1, sticky=tk.W)
        
        # 현재 시간 표시
        time_frame = ttk.LabelFrame(info_frame, text="실시간 시간", padding="5")
        time_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.server_time_var = tk.StringVar()
        ttk.Label(time_frame, text="서버 시간:", font=("맑은 고딕", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(time_frame, textvariable=self.server_time_var, font=("Consolas", 11, "bold"), foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        self.local_time_var = tk.StringVar()
        ttk.Label(time_frame, text="로컬 시간:", font=("맑은 고딕", 9, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(time_frame, textvariable=self.local_time_var, font=("Consolas", 11, "bold"), foreground="green").grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="🎯 간단한 동기화", command=self.simple_sync).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 테스트", command=self.test_function).pack(side=tk.LEFT, padx=5)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="실행 로그", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 시간 업데이트 시작
        self.update_current_time()
    
    def simple_sync(self):
        """간단한 동기화"""
        def sync_thread():
            try:
                self.sync_status.set("동기화 중...")
                self.log("간단한 동기화 시작...")
                
                url = self.url_var.get().strip()
                if not url:
                    url = "https://www.google.com"
                
                # 간단한 HTTP 요청으로 시간 측정
                start_time = time.time()
                try:
                    with urlopen(url, timeout=5) as response:
                        end_time = time.time()
                        latency = (end_time - start_time) / 2
                        
                        server_time_str = response.headers.get('Date')
                        if server_time_str:
                            server_time = datetime.strptime(server_time_str, '%a, %d %b %Y %H:%M:%S %Z')
                            server_time = server_time.replace(tzinfo=timezone.utc)
                            server_timestamp = server_time.timestamp()
                            
                            local_timestamp = start_time + latency
                            offset = server_timestamp - local_timestamp
                            
                            self.network_latency = latency
                            self.server_time_offset = offset
                            
                            self.sync_status.set("✅ 동기화 완료")
                            self.latency_var.set(f"{latency*1000:.1f}ms")
                            self.offset_var.set(f"{offset*1000:+.1f}ms")
                            
                            self.log(f"동기화 성공!")
                            self.log(f"네트워크 지연: {latency*1000:.1f}ms")
                            self.log(f"서버 시간차: {offset*1000:+.1f}ms")
                        else:
                            self.log("서버 시간 헤더를 찾을 수 없습니다.")
                            self.sync_status.set("동기화 부분 성공")
                
                except Exception as e:
                    self.log(f"동기화 실패: {e}")
                    self.sync_status.set("❌ 동기화 실패")
            
            except Exception as e:
                self.log(f"동기화 오류: {e}")
                self.sync_status.set("❌ 동기화 오류")
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def test_function(self):
        """테스트 기능"""
        self.log("테스트 기능 실행")
        for i in range(3):
            self.log(f"테스트 메시지 {i+1}")
    
    def start_log_processor(self):
        """로그 처리기"""
        def process_log():
            try:
                processed = 0
                while not self.log_queue.empty() and processed < 10:
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
        self.log("안전한 GUI 시작됨")
    
    def update_current_time(self):
        """현재 시간 업데이트"""
        current_local_time = datetime.now()
        local_time_str = current_local_time.strftime("%H:%M:%S.%f")[:-3]
        
        if hasattr(self, 'server_time_offset') and self.server_time_offset != 0:
            current_server_timestamp = time.time() + self.server_time_offset
            current_server_time = datetime.fromtimestamp(current_server_timestamp)
            server_time_str = current_server_time.strftime("%H:%M:%S.%f")[:-3]
            
            self.server_time_var.set(f"{server_time_str}")
            self.local_time_var.set(f"{local_time_str}")
        else:
            self.server_time_var.set("❌ 동기화 필요")
            self.local_time_var.set(f"{local_time_str}")
        
        self.root.after(500, self.update_current_time)
    
    def run(self):
        """GUI 실행"""
        print("GUI mainloop 시작...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Ctrl+C로 종료")
        except Exception as e:
            print(f"GUI 실행 오류: {e}")
        finally:
            print("GUI 종료됨")


def main():
    print("안전한 GUI 프로그램 시작")
    try:
        app = SafeTimeSyncGUI()
        app.run()
    except Exception as e:
        print(f"프로그램 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("프로그램 완전 종료")


if __name__ == "__main__":
    main()
