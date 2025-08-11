#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 정밀 시간 동기화 매크로 데모 v2
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import time
import statistics
from datetime import datetime
import webbrowser
import threading
from urllib.request import urlopen


class AdvancedTimeSyncDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("고급 정밀 시간 동기화 데모")
        self.root.geometry("800x600")
        
        self.measurements = []
        self.cpp_timer_available = self.check_cpp_timer()
        
        self.create_demo_widgets()
    
    def check_cpp_timer(self):
        """C++ 정밀 타이머 사용 가능 여부 확인"""
        if os.path.exists("precision_timer.exe"):
            try:
                result = subprocess.run(
                    ["precision_timer.exe", "1000"], 
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
            except:
                return False
        return False
    
    def create_demo_widgets(self):
        """데모 위젯 생성"""
        # 제목
        title = ttk.Label(self.root, text="고급 정밀 시간 동기화 데모", 
                         font=("맑은 고딕", 16, "bold"))
        title.pack(pady=10)
        
        # 상태 표시
        status_frame = ttk.LabelFrame(self.root, text="시스템 상태", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        python_timer_status = "✓ Python 고정밀 타이머 사용 가능"
        ttk.Label(status_frame, text=python_timer_status, foreground="green").pack(anchor=tk.W)
        
        cpp_status = "✓ C++ 정밀 타이머 사용 가능" if self.cpp_timer_available else "✗ C++ 정밀 타이머 없음"
        color = "green" if self.cpp_timer_available else "red"
        ttk.Label(status_frame, text=cpp_status, foreground=color).pack(anchor=tk.W)
        
        if not self.cpp_timer_available:
            ttk.Label(status_frame, text="  compile_timer.bat 실행으로 C++ 타이머를 컴파일하세요", 
                     foreground="gray").pack(anchor=tk.W)
        
        # 테스트 섹션
        test_frame = ttk.LabelFrame(self.root, text="정밀도 테스트", padding="10")
        test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # URL 입력
        url_frame = ttk.Frame(test_frame)
        url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(url_frame, text="테스트 URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="https://www.google.com")
        ttk.Entry(url_frame, textvariable=self.url_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 버튼들
        button_frame = ttk.Frame(test_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Python 타이머 테스트", 
                  command=self.test_python_timer).pack(side=tk.LEFT, padx=5)
        
        if self.cpp_timer_available:
            ttk.Button(button_frame, text="C++ 타이머 테스트", 
                      command=self.test_cpp_timer).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="네트워크 지연 측정", 
                  command=self.test_network_latency).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="브라우저 미리 열기", 
                  command=self.open_browser).pack(side=tk.LEFT, padx=5)
        
        # 결과 표시
        self.result_text = tk.Text(test_frame, height=20, width=80)
        scrollbar = ttk.Scrollbar(test_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_result(self, message):
        """결과 로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)
        self.root.update()
    
    def test_python_timer(self):
        """Python 타이머 정밀도 테스트"""
        self.log_result("=== Python 타이머 정밀도 테스트 ===")
        
        def test_thread():
            test_durations = [0.001, 0.005, 0.01, 0.05, 0.1]  # 1ms, 5ms, 10ms, 50ms, 100ms
            
            for target_duration in test_durations:
                errors = []
                
                for i in range(10):  # 각 duration당 10회 테스트
                    start_time = time.perf_counter()
                    
                    # 정밀 대기
                    end_time = start_time + target_duration
                    
                    # 큰 지연은 일반 sleep 사용
                    if target_duration > 0.01:
                        time.sleep(target_duration - 0.01)
                    
                    # 마지막 부분은 busy wait
                    while time.perf_counter() < end_time:
                        pass
                    
                    actual_duration = time.perf_counter() - start_time
                    error = (actual_duration - target_duration) * 1000  # ms 단위
                    errors.append(error)
                
                avg_error = statistics.mean(errors)
                std_error = statistics.stdev(errors) if len(errors) > 1 else 0
                
                self.log_result(f"목표 {target_duration*1000:6.1f}ms: "
                              f"오차 평균 {avg_error:+6.3f}ms ± {std_error:5.3f}ms")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_cpp_timer(self):
        """C++ 타이머 정밀도 테스트"""
        if not self.cpp_timer_available:
            self.log_result("C++ 타이머를 사용할 수 없습니다!")
            return
        
        self.log_result("=== C++ 타이머 정밀도 테스트 ===")
        
        def test_thread():
            test_durations = [1000, 5000, 10000, 50000, 100000]  # 마이크로초 단위
            
            for target_micros in test_durations:
                try:
                    result = subprocess.run(
                        ["precision_timer.exe", str(target_micros)],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if "Error:" in line:
                                self.log_result(f"목표 {target_micros/1000:6.1f}ms: {line}")
                                break
                    else:
                        self.log_result(f"C++ 타이머 실행 실패: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_result(f"C++ 타이머 타임아웃")
                except Exception as e:
                    self.log_result(f"C++ 타이머 오류: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_network_latency(self):
        """네트워크 지연 측정"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력하세요!")
            return
        
        self.log_result(f"=== 네트워크 지연 측정: {url} ===")
        
        def test_thread():
            latencies = []
            
            for i in range(20):  # 20회 측정
                try:
                    start_time = time.perf_counter()
                    
                    with urlopen(url, timeout=5) as response:
                        end_time = time.perf_counter()
                        latency = (end_time - start_time) * 1000  # ms 단위
                        latencies.append(latency)
                        
                        if i % 5 == 0:  # 5회마다 중간 결과 표시
                            self.log_result(f"측정 {i+1:2d}/20: {latency:6.1f}ms")
                    
                    time.sleep(0.5)  # 0.5초 간격
                    
                except Exception as e:
                    self.log_result(f"측정 {i+1} 실패: {e}")
            
            if latencies:
                # 통계 계산
                avg_latency = statistics.mean(latencies)
                median_latency = statistics.median(latencies)
                std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
                min_latency = min(latencies)
                max_latency = max(latencies)
                
                self.log_result(f"")
                self.log_result(f"=== 네트워크 지연 통계 ===")
                self.log_result(f"평균:     {avg_latency:6.1f}ms")
                self.log_result(f"중앙값:   {median_latency:6.1f}ms")
                self.log_result(f"표준편차: {std_latency:6.1f}ms")
                self.log_result(f"최소:     {min_latency:6.1f}ms")
                self.log_result(f"최대:     {max_latency:6.1f}ms")
                self.log_result(f"정확도:   ±{std_latency:5.1f}ms (95% 신뢰구간)")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def open_browser(self):
        """브라우저 미리 열기"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력하세요!")
            return
        
        try:
            webbrowser.open(url)
            self.log_result(f"브라우저 열림: {url}")
        except Exception as e:
            self.log_result(f"브라우저 열기 실패: {e}")
    
    def run(self):
        """데모 실행"""
        self.log_result("고급 정밀 시간 동기화 데모를 시작합니다.")
        self.log_result("각 기능을 테스트해보세요!")
        self.log_result("")
        
        self.root.mainloop()


def main():
    """메인 함수"""
    demo = AdvancedTimeSyncDemo()
    demo.run()


if __name__ == "__main__":
    main()
