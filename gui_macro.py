#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 버전 시간 동기화 매크로
tkinter를 사용한 사용자 친화적 인터페이스
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
import ctypes
from ctypes import wintypes
import subprocess
import os
import json
import logging

# pyautogui와 keyboard 모듈 임포트 (선택적)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # pyautogui 실행 중 마우스를 화면 모서리로 이동하여 정지하는 기능 비활성화
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0  # 기본 지연 제거
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("❌ pyautogui 모듈이 설치되지 않았습니다.")
    print("💡 설치 방법: pip install pyautogui")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard 모듈이 설치되지 않았습니다.")
    print("💡 설치 방법: pip install keyboard")


class TimeSyncMacroGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("정밀 구매 타이밍 매크로 v2.0")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        self.server_time_offset = 0
        self.network_latency = 0
        self.is_running = False
        self.log_queue = queue.Queue()
        self.measurement_history = []  # 측정 히스토리 저장
        self.browser_opened = False
        self.timing_adjustments = []  # 타이밍 조정 히스토리
        
        # 구매 버튼 위치 관련 변수들
        self.purchase_button_positions = []  # 여러 좌표 저장
        self.position_capture_mode = False  # 좌표 캡처 모드 온/오프
        self.position_listener = None  # 키보드 리스너
        
        # 로깅 시스템 초기화
        self.setup_logging()
        
        # Windows 고해상도 타이머 설정
        self.setup_high_resolution_timer()
        
        self.create_widgets()
        self.start_log_processor()
    
    def setup_logging(self):
        """로깅 시스템 설정"""
        # logs 폴더가 없으면 생성
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # 로그 파일명 (날짜별로 생성)
        log_filename = f"timing_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file_path = os.path.join(logs_dir, log_filename)
        
        # 로거 설정
        self.logger = logging.getLogger('TimingSyncMacro')
        self.logger.setLevel(logging.DEBUG)
        
        # 파일 핸들러 (상세 로그)
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(levelname)8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        
        # 초기 로그 기록
        self.logger.info("="*80)
        self.logger.info("정밀 구매 타이밍 매크로 v2.0 시작")
        self.logger.info(f"프로그램 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        self.logger.info("="*80)
        
        self.log_file_path = log_filename
        self.log(f"📄 로그 파일 생성: {log_filename}")
    
    def setup_high_resolution_timer(self):
        """Windows 고해상도 타이머 설정 (개선된 버전)"""
        try:
            import ctypes
            # Windows에서 최고 정밀도 타이머 요청
            winmm = ctypes.windll.winmm
            
            # 1ms 정밀도 요청 (기본)
            result = winmm.timeBeginPeriod(1)
            
            # 더 높은 정밀도 시도 (0.5ms)
            try:
                result2 = winmm.timeBeginPeriod(1)  # Windows는 보통 1ms가 최소
                self.log(f"⚡ 고해상도 타이머 설정: 1ms (결과: {result})")
            except:
                self.log(f"⚡ 기본 고해상도 타이머 설정: 1ms (결과: {result})")
            
            # 프로세스 우선순위 높이기 (선택적)
            try:
                # psutil이 있으면 사용
                try:
                    import psutil
                    import os
                    # 현재 프로세스의 우선순위를 높음으로 설정
                    p = psutil.Process(os.getpid())
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                    self.log("🚀 프로세스 우선순위 향상 (psutil)")
                except ImportError:
                    # psutil이 없어도 Windows API로 시도
                    kernel32 = ctypes.windll.kernel32
                    handle = kernel32.GetCurrentProcess()
                    # HIGH_PRIORITY_CLASS = 0x00000080
                    kernel32.SetPriorityClass(handle, 0x00000080)
                    self.log("🚀 프로세스 우선순위 향상 (Windows API)")
            except Exception as e:
                self.log(f"프로세스 우선순위 설정 실패: {e}")
                    
        except Exception as e:
            self.log(f"고해상도 타이머 설정 실패: {e}")
    
    def precise_sleep(self, duration):
        """정밀한 대기 함수 (최적화된 hybrid 방식)"""
        if duration <= 0:
            return
        
        end_time = time.perf_counter() + duration
        
        # 적응적 대기 전략
        if duration > 0.05:  # 50ms 이상 - 일반 sleep으로 대부분 대기
            time.sleep(duration - 0.005)  # 5ms 여유 두고 sleep
        elif duration > 0.01:  # 10-50ms - 부분 sleep
            time.sleep(duration * 0.7)  # 70%만 sleep
        elif duration > 0.002:  # 2-10ms - 짧은 sleep
            time.sleep(duration * 0.3)  # 30%만 sleep
        # 2ms 이하는 pure busy wait
        
        # 나머지 시간을 busy wait으로 정밀하게
        while time.perf_counter() < end_time:
            pass  # CPU 집중 대기
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="정밀 구매 타이밍 매크로 v2.0", 
                               font=("맑은 고딕", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL 입력
        ttk.Label(main_frame, text="구매 사이트 URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value="https://")
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 목표 시간 입력
        ttk.Label(main_frame, text="구매 시간:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(main_frame, textvariable=self.time_var, width=50)
        self.time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 시간 형식 안내
        time_help = ttk.Label(main_frame, text="형식: HH:MM:SS.mmm 또는 YYYY-MM-DD HH:MM:SS.mmm (밀리초 포함 가능)", 
                             foreground="gray")
        time_help.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # 빠른 시간 설정 버튼들
        quick_frame = ttk.Frame(main_frame)
        quick_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(quick_frame, text="3초 후", 
                  command=lambda: self.set_quick_time(3)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="5초 후", 
                  command=lambda: self.set_quick_time(5)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="10초 후", 
                  command=lambda: self.set_quick_time(10)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="30초 후", 
                  command=lambda: self.set_quick_time(30)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="1분 후", 
                  command=lambda: self.set_quick_time(60)).pack(side=tk.LEFT, padx=5)
        
        # 동기화 정보 표시
        info_frame = ttk.LabelFrame(main_frame, text="동기화 정보", padding="10")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.sync_status = tk.StringVar(value="동기화 안됨")
        ttk.Label(info_frame, text="상태:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.sync_status).grid(row=0, column=1, sticky=tk.W)
        
        self.latency_var = tk.StringVar(value="-")
        ttk.Label(info_frame, text="네트워크 지연:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.latency_var).grid(row=1, column=1, sticky=tk.W)
        
        self.offset_var = tk.StringVar(value="-")
        ttk.Label(info_frame, text="서버 시간차:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.offset_var).grid(row=2, column=1, sticky=tk.W)
        
        # 정확도 및 측정 횟수 표시
        self.accuracy_var = tk.StringVar(value="-")
        ttk.Label(info_frame, text="정확도 (표준편차):").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.accuracy_var).grid(row=3, column=1, sticky=tk.W)
        
        self.measurement_count_var = tk.StringVar(value="0")
        ttk.Label(info_frame, text="측정 횟수:").grid(row=4, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.measurement_count_var).grid(row=4, column=1, sticky=tk.W)
        
        # 현재 시간 표시 (개선된 세로 배치)
        time_frame = ttk.LabelFrame(info_frame, text="실시간 시간", padding="5")
        time_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 서버 시간
        self.server_time_var = tk.StringVar()
        ttk.Label(time_frame, text="서버 시간:", font=("맑은 고딕", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        server_time_label = ttk.Label(time_frame, textvariable=self.server_time_var, 
                                     font=("Consolas", 11, "bold"), foreground="blue")
        server_time_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 로컬 시간
        self.local_time_var = tk.StringVar()
        ttk.Label(time_frame, text="로컬 시간:", font=("맑은 고딕", 9, "bold")).grid(row=1, column=0, sticky=tk.W)
        local_time_label = ttk.Label(time_frame, textvariable=self.local_time_var, 
                                    font=("Consolas", 11, "bold"), foreground="green")
        local_time_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 시간차 표시
        self.time_diff_var = tk.StringVar()
        ttk.Label(time_frame, text="시간차:", font=("맑은 고딕", 9, "bold")).grid(row=2, column=0, sticky=tk.W)
        time_diff_label = ttk.Label(time_frame, textvariable=self.time_diff_var, 
                                   font=("Consolas", 10, "bold"), foreground="red")
        time_diff_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        self.sync_button = ttk.Button(button_frame, text="시간 동기화 (5회)", 
                                     command=lambda: self.sync_time(5))
        self.sync_button.pack(side=tk.LEFT, padx=5)
        
        self.sync_intensive_button = ttk.Button(button_frame, text="정밀 동기화 (20회)", 
                                               command=lambda: self.sync_time(20))
        self.sync_intensive_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(button_frame, text="구매 매크로 시작", 
                                      command=self.start_macro)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", 
                                     command=self.stop_macro, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 두 번째 줄 버튼들
        button_frame2 = ttk.Frame(main_frame)
        button_frame2.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        self.open_browser_button = ttk.Button(button_frame2, text="브라우저 미리 열기", 
                                             command=self.open_browser_early)
        self.open_browser_button.pack(side=tk.LEFT, padx=5)
        
        # 구매 버튼 위치 설정 (개선된 버전)
        self.set_position_button = ttk.Button(button_frame2, text="🎯 좌표 캡처 모드 (OFF)", 
                                             command=self.toggle_position_capture_mode)
        self.set_position_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame2, text="🗑️ 좌표 초기화", 
                  command=self.clear_all_positions).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame2, text="로그 지우기", 
                  command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame2, text="로그 파일 열기", 
                  command=self.open_log_file).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame2, text="요약 리포트", 
                  command=self.export_timing_summary).pack(side=tk.RIGHT, padx=5)
        
        # 로그 표시
        log_frame = ttk.LabelFrame(main_frame, text="실행 로그", padding="10")
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        # 시간 업데이트 시작
        self.update_current_time()
    
    def log(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def start_log_processor(self):
        """로그 처리 스레드 시작"""
        def process_log():
            try:
                while True:
                    message = self.log_queue.get_nowait()
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
            except queue.Empty:
                pass
            finally:
                self.root.after(100, process_log)
        
        self.root.after(100, process_log)
    
    def update_current_time(self):
        """현재 시간 업데이트 (개선된 세로 비교 형식)"""
        # 현재 로컬 시간
        current_local_time = datetime.now()
        local_time_str = current_local_time.strftime("%H:%M:%S.%f")[:-3]  # ms까지 표시
        
        if hasattr(self, 'server_time_offset') and self.server_time_offset != 0:
            # 서버 시간 계산 (로컬 시간 + 오프셋)
            current_server_timestamp = time.time() + self.server_time_offset
            current_server_time = datetime.fromtimestamp(current_server_timestamp)
            server_time_str = current_server_time.strftime("%H:%M:%S.%f")[:-3]
            
            # 시간차 계산 (밀리초)
            time_diff_ms = self.server_time_offset * 1000
            
            # GUI 업데이트
            self.server_time_var.set(f"{server_time_str}")
            self.local_time_var.set(f"{local_time_str}")
            
            # 시간차 색상 설정
            if abs(time_diff_ms) < 100:  # 100ms 이하
                diff_color = "green"
                status_icon = "✅"
            elif abs(time_diff_ms) < 500:  # 500ms 이하
                diff_color = "orange"
                status_icon = "⚠️"
            else:  # 500ms 초과
                diff_color = "red"
                status_icon = "❌"
            
            self.time_diff_var.set(f"{status_icon} {time_diff_ms:+.1f}ms")
            
            # 동기화 상태 업데이트
            sync_status_text = f"✅ 동기화 완료 ({abs(time_diff_ms):.1f}ms 차이)"
            if hasattr(self, 'sync_status'):
                self.sync_status.set(sync_status_text)
                
        else:
            # 동기화 안된 상태
            self.server_time_var.set("❌ 동기화 필요")
            self.local_time_var.set(f"{local_time_str}")
            self.time_diff_var.set("--- ms")
            
            if hasattr(self, 'sync_status'):
                self.sync_status.set("❌ 동기화 안됨")
        
        self.root.after(50, self.update_current_time)  # 50ms마다 업데이트 (더 빠르게)
    
    def open_browser_early(self):
        """브라우저 미리 열기 (최적화된 버전)"""
        url = self.url_var.get().strip()
        if not url or url == "https://":
            messagebox.showerror("오류", "URL을 입력하세요.")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)
        
        try:
            # Chrome을 고성능 모드로 실행
            import subprocess
            
            # Chrome 전용 최적화 플래그
            chrome_flags = [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-gpu-vsync', 
                '--max_old_space_size=4096',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-ipc-flooding-protection',
                '--aggressive-cache-discard',
                '--disable-extensions',
                '--no-sandbox'
            ]
            
            chrome_path = None
            possible_paths = [
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if chrome_path:
                # Chrome을 고성능으로 미리 실행
                cmd = [chrome_path] + chrome_flags + [url]
                subprocess.Popen(cmd)
                self.log("🚀 Chrome 고성능 모드로 페이지 미리 로드 중...")
            else:
                # 기본 브라우저로 실행
                webbrowser.open(url)
                self.log("📱 기본 브라우저로 페이지 로드 중...")
            
            self.browser_opened = True
            
            # 페이지 완전 로딩 대기 (비동기)
            def wait_for_page_load():
                time.sleep(3)  # 페이지 기본 로딩
                self.log("✅ 브라우저 준비 완료! 매크로 실행 시 즉시 클릭됩니다.")
            
            threading.Thread(target=wait_for_page_load, daemon=True).start()
            
        except Exception as e:
            self.log(f"브라우저 열기 실패: {e}")
            # 백업으로 기본 브라우저 사용
            webbrowser.open(url)
            self.browser_opened = True
    
    def toggle_position_capture_mode(self):
        """좌표 캡처 모드 온/오프 토글"""
        self.position_capture_mode = not self.position_capture_mode
        
        if self.position_capture_mode:
            # 캡처 모드 시작
            self.set_position_button.config(text="🟢 좌표 캡처 모드 (ON)")
            self.start_position_capture()
            self.log("🎯 좌표 캡처 모드 활성화!")
            self.log("💡 사용법:")
            self.log("  1. 구매 버튼 위에 마우스 커서를 올리세요")
            self.log("  2. Z키를 눌러 좌표를 추가하세요")
            self.log("  3. 여러 버튼이 있다면 반복하세요")
            self.log("  4. 완료되면 다시 버튼을 클릭해 모드를 끄세요")
        else:
            # 캡처 모드 종료
            self.set_position_button.config(text="🎯 좌표 캡처 모드 (OFF)")
            self.stop_position_capture()
            self.log("🎯 좌표 캡처 모드 비활성화")
            
            if len(self.purchase_button_positions) > 0:
                self.log(f"✅ 총 {len(self.purchase_button_positions)}개 좌표 저장됨:")
                for i, (x, y) in enumerate(self.purchase_button_positions):
                    self.log(f"  버튼 {i+1}: ({x}, {y})")
                self.log("🚀 매크로 실행 시 모든 좌표를 동시에 클릭합니다!")
            else:
                self.log("⚠️ 저장된 좌표가 없습니다")
    
    def start_position_capture(self):
        """좌표 캡처 시작 (키보드 리스너 활성화)"""
        try:
            import keyboard
            
            def on_z_key():
                """Z키가 눌렸을 때 현재 마우스 위치 저장"""
                try:
                    import pyautogui
                    x, y = pyautogui.position()
                    self.purchase_button_positions.append((x, y))
                    
                    self.log(f"📍 좌표 {len(self.purchase_button_positions)} 추가: ({x}, {y})")
                    
                    # 간단한 피드백
                    try:
                        import winsound
                        winsound.Beep(1500, 100)  # 높은 음으로 확인
                    except:
                        pass
                        
                except Exception as e:
                    self.log(f"❌ 좌표 추가 실패: {e}")
            
            # Z키 리스너 등록
            keyboard.on_press_key('z', lambda _: on_z_key())
            self.position_listener = keyboard
            
        except ImportError:
            self.log("❌ keyboard 모듈이 설치되지 않았습니다.")
            self.log("💡 설치 방법: pip install keyboard")
            self.position_capture_mode = False
            self.set_position_button.config(text="🎯 좌표 캡처 모드 (OFF)")
        except Exception as e:
            self.log(f"❌ 키보드 리스너 시작 실패: {e}")
            self.position_capture_mode = False
            self.set_position_button.config(text="🎯 좌표 캡처 모드 (OFF)")
    
    def stop_position_capture(self):
        """좌표 캡처 종료 (키보드 리스너 비활성화)"""
        try:
            if self.position_listener:
                self.position_listener.unhook_all()
                self.position_listener = None
        except Exception as e:
            self.log(f"키보드 리스너 종료 중 오류: {e}")
    
    def clear_all_positions(self):
        """모든 저장된 좌표 삭제"""
        self.purchase_button_positions = []
        self.log("🗑️ 모든 좌표가 삭제되었습니다")
    
    def set_purchase_button_position(self):
        """기존 방식 (호환성 유지)"""
        self.log("⚠️ 기존 방식은 새로운 좌표 캡처 모드로 변경되었습니다")
        self.log("💡 '좌표 캡처 모드' 버튼을 사용하세요!")
    
    def continuous_sync_monitoring(self, url, duration=30):
        """연속적인 시간 동기화 모니터링"""
        self.log(f"{duration}초 동안 연속 모니터링을 시작합니다...")
        
        start_time = time.perf_counter()
        measurements = []
        
        while time.perf_counter() - start_time < duration and self.is_running:
            try:
                local_before = time.perf_counter()
                
                with urlopen(url, timeout=5) as response:
                    local_after = time.perf_counter()
                    latency = (local_after - local_before) / 2
                    
                    server_time_str = response.headers.get('Date')
                    if server_time_str:
                        server_time = datetime.strptime(
                            server_time_str, '%a, %d %b %Y %H:%M:%S %Z'
                        ).replace(tzinfo=timezone.utc)
                        
                        server_timestamp = server_time.timestamp()
                        local_timestamp = local_before + latency
                        offset = server_timestamp - local_timestamp
                        
                        measurements.append({
                            'latency': latency,
                            'offset': offset,
                            'timestamp': local_before
                        })
                        
                        if len(measurements) % 5 == 0:  # 5회마다 로그
                            self.log(f"연속 측정 {len(measurements)}회: 지연 {latency*1000:.1f}ms")
                
                self.precise_sleep(1.0)  # 1초 간격
                
            except Exception as e:
                self.log(f"연속 측정 오류: {e}")
                self.precise_sleep(1.0)
        
        if measurements:
            # 통계 계산
            latencies = [m['latency'] for m in measurements]
            offsets = [m['offset'] for m in measurements]
            
            self.network_latency = statistics.median(latencies)
            self.server_time_offset = statistics.median(offsets)
            
            latency_std = statistics.stdev(latencies) if len(latencies) > 1 else 0
            offset_std = statistics.stdev(offsets) if len(offsets) > 1 else 0
            
            self.log(f"연속 측정 완료: {len(measurements)}회")
            self.log(f"평균 지연: {self.network_latency*1000:.1f}ms (±{latency_std*1000:.1f}ms)")
            self.log(f"시간차: {self.server_time_offset*1000:.1f}ms (±{offset_std*1000:.1f}ms)")
            
            return True
        
        return False
    
    def set_quick_time(self, seconds_later):
        """빠른 시간 설정 (현재 시간 기준)"""
        # 항상 현재 로컬 시간 기준으로 설정 (더 직관적)
        target_datetime = datetime.fromtimestamp(time.time() + seconds_later)
        self.time_var.set(target_datetime.strftime("%H:%M:%S"))
        
        if hasattr(self, 'server_time_offset') and self.server_time_offset != 0:
            # 서버 시간도 함께 표시
            server_target = datetime.fromtimestamp(time.time() + self.server_time_offset + seconds_later)
            self.log(f"목표 시간 설정: {seconds_later}초 후")
            self.log(f"  로컬 시간: {target_datetime.strftime('%H:%M:%S')}")
            self.log(f"  서버 시간: {server_target.strftime('%H:%M:%S')}")
        else:
            self.log(f"목표 시간이 {seconds_later}초 후로 설정되었습니다")
    
    def set_quick_time_precise(self, seconds_later):
        """정밀한 빠른 시간 설정 (밀리초 단위)"""
        # 밀리초까지 포함하여 설정
        target_datetime = datetime.fromtimestamp(time.time() + seconds_later)
        
        # 밀리초까지 표시
        time_str = target_datetime.strftime("%H:%M:%S.%f")[:-3]  # 마이크로초를 밀리초로 변환
        self.time_var.set(time_str)
        
        if hasattr(self, 'server_time_offset') and self.server_time_offset != 0:
            # 서버 시간도 함께 표시
            server_target = datetime.fromtimestamp(time.time() + self.server_time_offset + seconds_later)
            self.log(f"정밀 목표 시간 설정: {seconds_later}초 후")
            self.log(f"  로컬 시간: {target_datetime.strftime('%H:%M:%S.%f')[:-3]}")
            self.log(f"  서버 시간: {server_target.strftime('%H:%M:%S.%f')[:-3]}")
        else:
            self.log(f"정밀 목표 시간이 {seconds_later}초 후로 설정되었습니다 ({time_str})")
    
    def parse_target_time(self, target_time):
        """목표 시간 파싱 (밀리초 지원)
        
        지원 형식:
        - HH:MM:SS (예: 15:30:45)
        - HH:MM:SS.mmm (예: 15:30:45.123)
        - YYYY-MM-DD HH:MM:SS (예: 2025-08-22 15:30:45)
        - YYYY-MM-DD HH:MM:SS.mmm (예: 2025-08-22 15:30:45.123)
        
        Returns:
            tuple: (target_datetime, target_timestamp)
        """
        target_time = target_time.strip()
        
        # 지원하는 시간 형식들 (밀리초 포함)
        formats = [
            # 전체 날짜/시간 + 밀리초
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            # 시간만 + 밀리초
            '%H:%M:%S.%f',
            '%H:%M:%S',
            # 추가 형식들
            '%Y/%m/%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
        ]
        
        # 각 형식으로 파싱 시도
        for fmt in formats:
            try:
                if '%Y' in fmt:
                    # 전체 날짜/시간이 포함된 경우
                    target_datetime = datetime.strptime(target_time, fmt)
                    target_timestamp = target_datetime.timestamp()
                    self.log(f"목표 시간 파싱 성공 (전체): {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    return target_datetime, target_timestamp
                else:
                    # 시간만 입력된 경우 (오늘 날짜 적용)
                    if hasattr(self, 'server_time_offset') and self.server_time_offset != 0:
                        # 서버 시간 기준으로 오늘 날짜 계산
                        server_now = datetime.fromtimestamp(time.time() + self.server_time_offset)
                        today = server_now.date()
                    else:
                        today = datetime.now().date()
                    
                    time_part = datetime.strptime(target_time, fmt).time()
                    target_datetime = datetime.combine(today, time_part)
                    target_timestamp = target_datetime.timestamp()
                    
                    self.log(f"목표 시간 파싱 성공 (시간만): {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    return target_datetime, target_timestamp
                    
            except ValueError:
                continue
        
        # 모든 형식으로 파싱 실패한 경우
        raise ValueError(f"지원하지 않는 시간 형식입니다.\n"
                        f"지원 형식:\n"
                        f"  - HH:MM:SS (예: 15:30:45)\n"
                        f"  - HH:MM:SS.mmm (예: 15:30:45.123)\n"
                        f"  - YYYY-MM-DD HH:MM:SS (예: 2025-08-22 15:30:45)\n"
                        f"  - YYYY-MM-DD HH:MM:SS.mmm (예: 2025-08-22 15:30:45.123)\n"
                        f"입력값: '{target_time}'")
    
    def sync_time(self, num_samples=5):
        """시간 동기화 실행"""
        url = self.url_var.get().strip()
        if not url or url == "https://":
            messagebox.showerror("오류", "URL을 입력하세요.")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)
        
        def sync_thread():
            try:
                self.log(f"시간 동기화 시작... ({num_samples}회 측정)")
                self.sync_button.config(state=tk.DISABLED)
                self.sync_intensive_button.config(state=tk.DISABLED)
                
                # 브라우저 미리 열기
                if not self.browser_opened:
                    try:
                        webbrowser.open(url)
                        self.browser_opened = True
                        self.log("브라우저를 미리 열었습니다.")
                        time.sleep(2)  # 브라우저 로딩 대기
                    except Exception as e:
                        self.log(f"브라우저 미리 열기 실패: {e}")
                
                success = self.measure_server_time_offset(url, num_samples)
                
                if success:
                    self.sync_status.set("동기화 완료")
                    self.latency_var.set(f"{self.network_latency*1000:.1f}ms")
                    self.offset_var.set(f"{self.server_time_offset*1000:.1f}ms")
                    
                    # 정확도 계산
                    if len(self.measurement_history) > 1:
                        latencies = [m['latency'] for m in self.measurement_history[-num_samples:]]
                        std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
                        self.accuracy_var.set(f"±{std_dev*1000:.1f}ms")
                    
                    self.measurement_count_var.set(str(len(self.measurement_history)))
                    self.log("시간 동기화 완료!")
                else:
                    self.sync_status.set("동기화 실패")
                    self.log("시간 동기화 실패!")
                
            finally:
                self.sync_button.config(state=tk.NORMAL)
                self.sync_intensive_button.config(state=tk.NORMAL)
        
        threading.Thread(target=sync_thread, daemon=True).start()
    
    def measure_server_time_offset(self, url, num_samples):
        """서버 시간 동기화 측정 (초정밀 버전 + 상세 로깅)"""
        offsets = []
        latencies = []
        
        self.log(f"정밀 시간 동기화 시작... (총 {num_samples}회 측정)")
        
        # 로그 파일에 동기화 세션 시작 기록
        self.logger.info("="*60)
        self.logger.info(f"서버 시간 동기화 세션 시작")
        self.logger.info(f"대상 URL: {url}")
        self.logger.info(f"측정 횟수: {num_samples}회")
        self.logger.info(f"세션 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        self.logger.info("-"*60)
        
        for i in range(num_samples):
            try:
                # 여러 번 측정해서 가장 빠른 응답 시간 사용 (네트워크 지연 최소화)
                best_latency = float('inf')
                best_offset = 0
                best_measurement = None
                
                # 각 샘플마다 3번 빠른 측정 시도
                for attempt in range(3):
                    try:
                        local_before_real = time.time()
                        local_before_precise = time.perf_counter()
                        
                        with urlopen(url, timeout=5) as response:
                            local_after_real = time.time()
                            local_after_precise = time.perf_counter()
                            
                            # 정밀한 지연시간 계산
                            latency = (local_after_precise - local_before_precise) / 2
                            
                            server_time_str = response.headers.get('Date')
                            if server_time_str:
                                # 서버 시간 파싱
                                server_time = None
                                time_formats = [
                                    '%a, %d %b %Y %H:%M:%S GMT',
                                    '%a, %d %b %Y %H:%M:%S %Z',
                                    '%d %b %Y %H:%M:%S GMT',
                                ]
                                
                                for fmt in time_formats:
                                    try:
                                        server_time = datetime.strptime(server_time_str, fmt)
                                        break
                                    except ValueError:
                                        continue
                                
                                if server_time:
                                    server_time = server_time.replace(tzinfo=timezone.utc)
                                    server_timestamp = server_time.timestamp()
                                    
                                    # 네트워크 지연을 고려한 로컬 시간
                                    local_timestamp_at_server = local_before_real + latency
                                    offset = server_timestamp - local_timestamp_at_server
                                    
                                    # 가장 빠른 응답(낮은 지연시간) 선택
                                    if latency < best_latency:
                                        best_latency = latency
                                        best_offset = offset
                                        best_measurement = {
                                            'sample': i + 1,
                                            'attempt': attempt + 1,
                                            'latency': latency,
                                            'offset': offset,
                                            'local_before': local_before_real,
                                            'local_after': local_after_real,
                                            'server_time': server_timestamp,
                                            'server_time_str': server_time_str,
                                            'local_timestamp_at_server': local_timestamp_at_server,
                                            'response_time': (local_after_precise - local_before_precise) * 1000  # ms
                                        }
                    
                    except Exception as e:
                        self.logger.warning(f"측정 {i+1} 시도 {attempt+1} 실패: {e}")
                        continue
                    
                    # 아주 짧은 간격으로 재시도
                    time.sleep(0.01)
                
                if best_measurement:
                    latencies.append(best_latency)
                    offsets.append(best_offset)
                    self.measurement_history.append(best_measurement)
                    
                    # 로그 파일에 상세 측정 결과 기록
                    self.logger.info(f"측정 {i+1:2d}/{num_samples} | "
                                   f"지연: {best_latency*1000:6.1f}ms | "
                                   f"오프셋: {best_offset*1000:+7.1f}ms | "
                                   f"응답시간: {best_measurement['response_time']:6.1f}ms | "
                                   f"시도: {best_measurement['attempt']}/3")
                    
                    # JSON 형태로 상세 데이터도 기록
                    self.logger.debug(f"측정 {i+1} 상세: {json.dumps(best_measurement, default=str, indent=None)}")
                    
                    # 상세 로그 (매 5회마다)
                    if (i + 1) % 5 == 0 or i == 0:
                        local_time_str = datetime.fromtimestamp(best_measurement['local_timestamp_at_server']).strftime('%H:%M:%S.%f')[:-3]
                        server_time_display = datetime.fromtimestamp(best_measurement['server_time']).strftime('%H:%M:%S.%f')[:-3]
                        
                        self.log(f"측정 {i+1}/{num_samples}: 지연 {best_latency*1000:.1f}ms, 시간차 {best_offset*1000:+.1f}ms (시도 {best_measurement['attempt']}/3)")
                        if i == 0:  # 첫 번째 측정만 상세 표시
                            self.log(f"  로컬: {local_time_str}, 서버: {server_time_display}")
                else:
                    self.logger.warning(f"측정 {i+1} 완전 실패: 모든 시도에서 측정 불가")
                
                # 측정 간격 (더 정밀하게)
                self.precise_sleep(0.02)  # 20ms 간격
                
            except Exception as e:
                self.log(f"측정 {i+1} 실패: {e}")
                self.logger.error(f"측정 {i+1} 실패: {e}")
                continue
        
        if offsets and latencies:
            # 고급 이상값 제거 - 표준편차 기반
            def remove_outliers_advanced(data):
                if len(data) < 3:
                    return data
                
                import statistics
                mean_val = statistics.mean(data)
                stdev_val = statistics.stdev(data) if len(data) > 1 else 0
                
                # 2 표준편차 이내의 값만 유지
                filtered = [x for x in data if abs(x - mean_val) <= 2 * stdev_val]
                return filtered if len(filtered) >= 2 else data
            
            # 지연시간 기준으로 이상값 제거 (네트워크 상태 고려)
            clean_indices = []
            latency_threshold = statistics.median(latencies) * 1.5  # 중앙값의 1.5배 이하만 사용
            
            for i, lat in enumerate(latencies):
                if lat <= latency_threshold:
                    clean_indices.append(i)
            
            if clean_indices:
                clean_offsets = [offsets[i] for i in clean_indices]
                clean_latencies = [latencies[i] for i in clean_indices]
                
                # 추가 정제
                clean_offsets = remove_outliers_advanced(clean_offsets)
                clean_latencies = remove_outliers_advanced(clean_latencies)
                
                if clean_offsets and clean_latencies:
                    # 최종 값 계산 - 중앙값 사용 (더 안정적)
                    self.server_time_offset = statistics.median(clean_offsets)
                    self.network_latency = statistics.median(clean_latencies)
                    
                    # 정확도 분석
                    offset_std = statistics.stdev(clean_offsets) if len(clean_offsets) > 1 else 0
                    latency_std = statistics.stdev(clean_latencies) if len(clean_latencies) > 1 else 0
                    
                    # 동기화 결과를 로그 파일에 상세 기록
                    sync_result = {
                        'timestamp': datetime.now().isoformat(),
                        'total_samples': num_samples,
                        'valid_samples': len(clean_offsets),
                        'filtered_samples': len(offsets) - len(clean_offsets),
                        'final_server_offset_ms': self.server_time_offset * 1000,
                        'final_network_latency_ms': self.network_latency * 1000,
                        'offset_std_dev_ms': offset_std * 1000,
                        'latency_std_dev_ms': latency_std * 1000,
                        'estimated_accuracy_ms': (offset_std + latency_std) * 1000,
                        'raw_offsets_ms': [o * 1000 for o in offsets],
                        'raw_latencies_ms': [l * 1000 for l in latencies],
                        'clean_offsets_ms': [o * 1000 for o in clean_offsets],
                        'clean_latencies_ms': [l * 1000 for l in clean_latencies]
                    }
                    
                    self.logger.info("-"*60)
                    self.logger.info("동기화 결과 통계:")
                    self.logger.info(f"  전체 측정: {num_samples}회 → 유효: {len(clean_offsets)}회 (필터링: {len(offsets) - len(clean_offsets)}회)")
                    self.logger.info(f"  서버 시간차: {self.server_time_offset*1000:+.3f}ms ± {offset_std*1000:.3f}ms")
                    self.logger.info(f"  네트워크 지연: {self.network_latency*1000:.3f}ms ± {latency_std*1000:.3f}ms")
                    self.logger.info(f"  예상 정확도: ±{(offset_std + latency_std)*1000:.3f}ms")
                    self.logger.info(f"  오프셋 범위: {min(clean_offsets)*1000:+.1f} ~ {max(clean_offsets)*1000:+.1f}ms")
                    self.logger.info(f"  지연 범위: {min(clean_latencies)*1000:.1f} ~ {max(clean_latencies)*1000:.1f}ms")
                    
                    # JSON 형태로 상세 통계 저장
                    self.logger.debug(f"동기화 상세 통계: {json.dumps(sync_result, indent=2)}")
                    
                    self.logger.info("="*60)
                    
                    # 상세 결과 로그
                    self.log("=" * 50)
                    self.log("🎯 정밀 동기화 완료!")
                    self.log(f"📊 사용된 측정값: {len(clean_offsets)}/{num_samples}개")
                    self.log(f"🌐 서버 시간차: {self.server_time_offset*1000:+.1f}ms (±{offset_std*1000:.1f}ms)")
                    self.log(f"⚡ 네트워크 지연: {self.network_latency*1000:.1f}ms (±{latency_std*1000:.1f}ms)")
                    self.log(f"🔬 예상 정확도: ±{(offset_std + latency_std)*1000:.1f}ms")
                    self.log(f"📄 로그 저장됨: {self.log_file_path}")
                    self.log("=" * 50)
                    
                    return True
                
        self.logger.error("동기화 실패: 유효한 측정값이 없음")
        return False
    
    def start_macro(self):
        """매크로 시작"""
        url = self.url_var.get().strip()
        target_time = self.time_var.get().strip()
        
        if not url or url == "https://":
            messagebox.showerror("오류", "URL을 입력하세요.")
            return
        
        if not target_time:
            messagebox.showerror("오류", "목표 시간을 입력하세요.")
            return
        
        if self.server_time_offset == 0:
            if messagebox.askyesno("확인", "시간 동기화가 되지 않았습니다. 먼저 동기화하시겠습니까?"):
                self.sync_time()
                return
        
        def macro_thread():
            try:
                self.is_running = True
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                # 목표 시간 파싱 (서버 시간 기준으로 해석) - 밀리초 지원
                try:
                    target_datetime, target_timestamp = self.parse_target_time(target_time)
                    self.log(f"목표 시간: {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                except ValueError as e:
                    self.log(f"시간 형식 오류! {str(e)}")
                    return
                self.log("정확한 타이밍 대기 중...")
                
                # 목표 시간까지의 대략적인 대기
                while self.is_running:
                    # 현재 실제 시간 사용 (서버 오프셋 적용)
                    current_time = time.time() + self.server_time_offset
                    time_until_target = target_timestamp - current_time
                    
                    if time_until_target <= 0:
                        self.log("목표 시간이 이미 지났습니다!")
                        break
                    
                    # 로그 업데이트 (너무 자주 하지 않도록)
                    if time_until_target > 1 and int(time_until_target) % 1 == 0:
                        self.log(f"남은 시간: {time_until_target:.1f}초")
                    elif time_until_target <= 1:
                        self.log(f"남은 시간: {time_until_target:.3f}초")
                    
                    # 정밀 타이밍 진입 (네트워크 지연보다 조금 더 일찍)
                    if time_until_target <= (self.network_latency + 0.1):  # 100ms 여유로 확대
                        self.log(f"정밀 타이밍 모드 진입! (네트워크지연: {self.network_latency*1000:.1f}ms)")
                        
                        # 이전 실행 결과를 바탕으로 동적 조정 (더 강력하게)
                        adjustment = 0
                        if hasattr(self, 'timing_adjustments') and len(self.timing_adjustments) > 0:
                            # 최근 3회 평균을 사용해 강력하게 보정
                            recent_results = self.timing_adjustments[-3:]
                            avg_error = sum(recent_results) / len(recent_results)
                            adjustment = -avg_error * 0.8  # 오차의 80%를 보정 (더 강력)
                            self.log(f"📈 동적 조정: {adjustment:+.1f}ms (최근 평균 오차: {avg_error:+.1f}ms)")
                        
                        # 목표: 서버에 10ms 늦게 도착하도록 설정
                        target_arrival_delay_ms = 10 + adjustment
                        target_arrival_delay_ms = max(5, min(20, target_arrival_delay_ms))  # 5~20ms 범위
                        target_arrival_delay = target_arrival_delay_ms / 1000.0
                        
                        # 실제 측정된 클릭 실행 시간 반영 및 동적 조정
                        if hasattr(self, 'execution_time_history') and len(self.execution_time_history) > 0:
                            # 최근 실행 시간들의 가중 평균 사용 (최근 것에 더 높은 가중치)
                            recent_times = self.execution_time_history[-5:]  # 최근 5회
                            if len(recent_times) >= 3:
                                weights = [0.4, 0.3, 0.2, 0.1][:len(recent_times)]  # 최근 것부터 높은 가중치
                                weights = weights[::-1]  # 순서 맞춤
                                weighted_avg = sum(t * w for t, w in zip(recent_times, weights)) / sum(weights)
                                click_execution_time = weighted_avg
                                self.log(f"🕐 가중평균 실행시간: {click_execution_time*1000:.1f}ms (최근 {len(recent_times)}회)")
                            else:
                                click_execution_time = sum(recent_times) / len(recent_times)
                                self.log(f"🕐 동적 실행시간: {click_execution_time*1000:.1f}ms (최근 {len(recent_times)}회 평균)")
                        else:
                            # 최적화된 초기 추정값 (새로운 클릭 함수 기준)
                            if hasattr(self, 'purchase_button_positions') and len(self.purchase_button_positions) > 0:
                                # 여러 좌표가 있을 때의 예상 실행시간
                                base_time = 0.008  # 8ms (첫 번째 클릭)
                                additional_time = len(self.purchase_button_positions) * 0.002  # 추가 클릭당 2ms
                                click_execution_time = base_time + additional_time
                                self.log(f"🕐 다중좌표 실행시간: {click_execution_time*1000:.1f}ms ({len(self.purchase_button_positions)}개 좌표)")
                            else:
                                click_execution_time = 0.025  # 25ms (키보드/위치 클릭)
                                self.log(f"🕐 초기 실행시간: {click_execution_time*1000:.1f}ms (최적화 추정값)")
                        
                        # ⭐ 핵심 수정: 서버 시간 기준으로 직접 계산
                        # 목표 도착 시간 = target_timestamp + target_arrival_delay
                        target_arrival_time = target_timestamp + target_arrival_delay
                        
                        # 클릭해야 할 서버 시간 = 목표 도착 시간 - 네트워크 지연 - 클릭 실행 시간
                        required_server_click_time = target_arrival_time - self.network_latency - click_execution_time
                        
                        # 로컬 시간으로 변환 (서버 시간 - 오프셋)
                        precise_target_time = required_server_click_time - self.server_time_offset
                        
                        # 안전 검증
                        current_local_time = time.time()
                        if precise_target_time <= current_local_time:
                            self.log("⚠️ 경고: 계산된 클릭 시간이 이미 지났습니다!")
                            # 최소 지연으로 즉시 실행
                            precise_target_time = current_local_time + 0.001
                            required_server_click_time = precise_target_time + self.server_time_offset
                            target_arrival_time = required_server_click_time + self.network_latency + click_execution_time
                        
                        # 예상 도착 시간 계산 검증
                        predicted_arrival = required_server_click_time + click_execution_time + self.network_latency
                        
                        self.log(f"🎯 클릭 목표 시간 (서버): {datetime.fromtimestamp(required_server_click_time).strftime('%H:%M:%S.%f')[:-3]}")
                        self.log(f"📡 예상 도착 시간 (서버): {datetime.fromtimestamp(predicted_arrival).strftime('%H:%M:%S.%f')[:-3]}")
                        self.log(f"⏱️ 목표 도착 지연: +{target_arrival_delay_ms:.1f}ms")
                        
                        # 정밀한 busy wait (로컬 시간 기준)
                        while True:
                            current_local_time = time.time()
                            remaining = precise_target_time - current_local_time
                            
                            if remaining <= 0:
                                break
                            
                            # 매우 정밀한 대기 전략
                            if remaining <= 0.0005:  # 0.5ms 이하 - 순수 busy wait
                                continue
                            elif remaining <= 0.002:  # 2ms 이하 - 마이크로 슬립
                                time.sleep(0.0001)  # 0.1ms
                            elif remaining <= 0.01:  # 10ms 이하 - 짧은 슬립
                                time.sleep(remaining * 0.3)  # 남은 시간의 30%만 슬립
                            else:
                                sleep_time = remaining - 0.003  # 3ms 여유
                                if sleep_time > 0:
                                    self.precise_sleep(sleep_time)
                        
                        # 정확한 실행 시간 기록
                        execution_start_time = time.time()
                        
                        self.log("� 정밀 클릭 실행!")
                        
                        # 웹사이트 열기 및 구매 버튼 클릭
                        self.click_purchase_button(url)
                        
                        # 실행 완료 시간 기록
                        execution_end_time = time.time()
                        actual_execution_time = execution_end_time - execution_start_time
                        
                        # 정확한 서버 시간 계산
                        actual_server_click_time = execution_start_time + self.server_time_offset
                        actual_arrival_time = actual_server_click_time + actual_execution_time + self.network_latency
                        
                        # 시간 차이 계산 (ms 단위)
                        click_delay_ms = (actual_server_click_time - target_timestamp) * 1000
                        arrival_delay_ms = (actual_arrival_time - target_timestamp) * 1000
                        
                        # 디버그 정보
                        self.log(f"🔍 디버그 정보:")
                        self.log(f"  목표 시간: {target_timestamp:.3f}")
                        self.log(f"  실제 클릭(서버): {actual_server_click_time:.3f}")  
                        self.log(f"  실제 도착(예상): {actual_arrival_time:.3f}")
                        self.log(f"  클릭 실행시간: {actual_execution_time:.3f}s")
                        self.log(f"  네트워크 지연: {self.network_latency:.3f}s")
                        
                        # 결과 검증
                        timing_status = "🔴 타이밍 오류"
                        if actual_arrival_time < target_timestamp:
                            timing_status = "🔴 너무 빠름! (도착시간이 목표시간보다 빠름)"
                        elif arrival_delay_ms > 20:
                            timing_status = "🔴 너무 늦음! (20ms 초과)"
                        elif 0 <= arrival_delay_ms <= 20:
                            if arrival_delay_ms <= 10:
                                timing_status = "🟢 완벽! (±10ms 이내)"
                            else:
                                timing_status = "🟡 양호 (20ms 이내)"
                        
                        self.log("=" * 70)
                        self.log("📊 정밀 타이밍 분석 결과")
                        self.log("=" * 70)
                        self.log(f"🎯 목표 시간: {datetime.fromtimestamp(target_timestamp).strftime('%H:%M:%S.%f')[:-3]}")
                        self.log(f"🚀 실제 클릭 (서버): {datetime.fromtimestamp(actual_server_click_time).strftime('%H:%M:%S.%f')[:-3]}")
                        self.log(f"📡 예상 도착 (서버): {datetime.fromtimestamp(actual_arrival_time).strftime('%H:%M:%S.%f')[:-3]}")
                        self.log(f"")
                        self.log(f"⚡ 클릭 실행 시간: {actual_execution_time*1000:.1f}ms")
                        self.log(f"⏱️ 클릭 지연: {click_delay_ms:+.1f}ms")
                        self.log(f"🌐 도착 지연: {arrival_delay_ms:+.1f}ms")
                        self.log(f"📊 상태: {timing_status}")
                        
                        # 조건 검증 로그
                        self.log("=" * 70)
                        self.log("✅ 조건 검증")
                        condition1 = actual_arrival_time >= target_timestamp
                        condition2 = arrival_delay_ms <= 20
                        
                        self.log(f"조건1 (도착≥목표): {'✅ 통과' if condition1 else '❌ 실패'}")
                        self.log(f"조건2 (20ms이내): {'✅ 통과' if condition2 else '❌ 실패'}")
                        
                        if condition1 and condition2:
                            self.log("🎉 모든 조건 만족!")
                        else:
                            self.log("⚠️ 조건 불만족 - 다시 실행하면 자동으로 조정됩니다")
                        
                        # 결과를 히스토리에 저장 (다음 실행 시 동적 조정용)
                        if not hasattr(self, 'timing_adjustments'):
                            self.timing_adjustments = []
                        if not hasattr(self, 'execution_time_history'):
                            self.execution_time_history = []
                        
                        # 타이밍 오차와 실제 실행 시간 저장
                        self.timing_adjustments.append(arrival_delay_ms)
                        self.execution_time_history.append(actual_execution_time)
                        
                        # 히스토리는 최대 10개만 유지
                        if len(self.timing_adjustments) > 10:
                            self.timing_adjustments = self.timing_adjustments[-10:]
                        if len(self.execution_time_history) > 10:
                            self.execution_time_history = self.execution_time_history[-10:]
                        
                        # 매크로 실행 결과를 로그 파일에 상세 기록
                        execution_result = {
                            'timestamp': datetime.now().isoformat(),
                            'target_time': target_timestamp,
                            'target_datetime': datetime.fromtimestamp(target_timestamp).isoformat(),
                            'actual_click_time': execution_start_time,
                            'actual_server_click_time': actual_server_click_time,
                            'actual_arrival_time': actual_arrival_time,
                            'execution_time_ms': actual_execution_time * 1000,
                            'click_delay_ms': click_delay_ms,
                            'arrival_delay_ms': arrival_delay_ms,
                            'network_latency_ms': self.network_latency * 1000,
                            'server_time_offset_ms': self.server_time_offset * 1000,
                            'timing_status': timing_status,
                            'condition1_pass': condition1,
                            'condition2_pass': condition2,
                            'adjustment_used_ms': adjustment,
                            'target_arrival_delay_ms': target_arrival_delay_ms,
                            'predicted_execution_time_ms': click_execution_time * 1000,
                            'actual_vs_predicted_execution_diff_ms': (actual_execution_time - click_execution_time) * 1000
                        }
                        
                        self.logger.info("="*60)
                        self.logger.info("매크로 실행 결과")
                        self.logger.info(f"목표 시간: {datetime.fromtimestamp(target_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                        self.logger.info(f"실제 클릭: {datetime.fromtimestamp(actual_server_click_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} (서버시간)")
                        self.logger.info(f"예상 도착: {datetime.fromtimestamp(actual_arrival_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} (서버시간)")
                        self.logger.info(f"클릭 지연: {click_delay_ms:+.3f}ms | 도착 지연: {arrival_delay_ms:+.3f}ms")
                        self.logger.info(f"실행 시간: {actual_execution_time*1000:.3f}ms (예상: {click_execution_time*1000:.3f}ms)")
                        self.logger.info(f"조건1 (도착≥목표): {'PASS' if condition1 else 'FAIL'} | 조건2 (≤20ms): {'PASS' if condition2 else 'FAIL'}")
                        self.logger.info(f"전체 결과: {'SUCCESS' if condition1 and condition2 else 'FAIL'}")
                        
                        # JSON 형태로 상세 실행 데이터 저장
                        self.logger.debug(f"매크로 실행 상세: {json.dumps(execution_result, indent=2)}")
                        self.logger.info("="*60)
                        
                        # 통계 정보 표시
                        if len(self.timing_adjustments) >= 2:
                            avg_error = sum(self.timing_adjustments) / len(self.timing_adjustments)
                            self.log(f"📊 평균 오차 (최근 {len(self.timing_adjustments)}회): {avg_error:+.1f}ms")
                        
                        self.log("=" * 70)
                        
                        # 소리 알림 (결과에 따라)
                        try:
                            import winsound
                            if condition1 and condition2 and arrival_delay_ms <= 10:
                                # 완벽 - 성공음 (높은음)
                                for i in range(3):
                                    winsound.Beep(2000, 100)
                                    time.sleep(0.05)
                            elif condition1 and condition2:
                                # 양호 - 보통음
                                for i in range(2):
                                    winsound.Beep(1500, 150)
                                    time.sleep(0.05)
                            else:
                                # 조건 불만족 - 경고음 (낮은음)
                                winsound.Beep(400, 500)
                        except:
                            pass
                        
                        break
                    
                    # 적응적 대기 간격
                    if time_until_target > 10:
                        time.sleep(1.0)  # 10초 이상 남으면 1초 간격
                    elif time_until_target > 1:
                        time.sleep(0.1)  # 1-10초 남으면 0.1초 간격
                    else:
                        self.precise_sleep(0.001)  # 1초 미만 남으면 1ms 간격
                
            finally:
                self.is_running = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
        
        threading.Thread(target=macro_thread, daemon=True).start()
    
    def click_purchase_button(self, url):
        """구매 버튼을 자동으로 클릭 (다중 좌표 동시 클릭 버전)"""
        try:
            click_start_time = time.perf_counter()
            
            # pyautogui를 사용한 초고속 다중 클릭
            try:
                import pyautogui
                
                # ⚡ 최고 속도 설정
                pyautogui.FAILSAFE = False  # 안전모드 완전 해제
                pyautogui.PAUSE = 0  # 모든 대기시간 제거
                
                # 🎯 방법 1: 저장된 다중 좌표 동시 클릭 (최우선 - 가장 빠름)
                if hasattr(self, 'purchase_button_positions') and len(self.purchase_button_positions) > 0:
                    try:
                        self.log(f"🎯 {len(self.purchase_button_positions)}개 좌표 동시 클릭 시작!")
                        
                        # 모든 좌표를 빠르게 연속 클릭
                        for i, (x, y) in enumerate(self.purchase_button_positions):
                            pyautogui.click(x, y, duration=0)
                            self.log(f"  ⚡ 클릭 {i+1}: ({x}, {y})")
                            
                            # 동시성을 위해 아주 짧은 대기만
                            if i < len(self.purchase_button_positions) - 1:
                                time.sleep(0.001)  # 1ms만 대기
                        
                        click_end_time = time.perf_counter()
                        actual_click_time = (click_end_time - click_start_time) * 1000
                        self.log(f"🎯 다중 클릭 완료! 소요시간: {actual_click_time:.1f}ms")
                        return
                        
                    except Exception as e:
                        self.log(f"다중 좌표 클릭 실패: {e}")
                
                # 🚀 방법 2: 키보드 즉시 실행 (저장된 좌표가 없을 때)
                try:
                    self.log("⚡ 저장된 좌표 없음 - 키보드 클릭으로 대체")
                    
                    # Enter 키 즉시 실행 (가장 빠름)
                    pyautogui.press('enter')
                    
                    # 백업으로 Space 키도 즉시 실행
                    pyautogui.press('space')
                    
                    self.log("⚡ 키보드 즉시 실행 (Enter/Space)")
                    
                    click_end_time = time.perf_counter()
                    actual_click_time = (click_end_time - click_start_time) * 1000
                    self.log(f"🎯 키보드 클릭 완료! 소요시간: {actual_click_time:.1f}ms")
                    return
                    
                except Exception as e:
                    self.log(f"키보드 클릭 실패: {e}")
                
                # 🚀 방법 3: 화면 예상 위치 연타 (마지막 백업)
                try:
                    screen_width, screen_height = pyautogui.size()
                    
                    # 일반적인 구매 버튼 위치들
                    backup_positions = [
                        (int(screen_width * 0.85), int(screen_height * 0.75)),   # 우하단
                        (int(screen_width * 0.5), int(screen_height * 0.8)),    # 중앙 하단
                        (int(screen_width * 0.9), int(screen_height * 0.6)),    # 우측 중간
                    ]
                    
                    self.log(f"🔄 백업 위치 {len(backup_positions)}곳 연타")
                    
                    for i, pos in enumerate(backup_positions):
                        pyautogui.click(pos[0], pos[1], duration=0)
                        if i < len(backup_positions) - 1:
                            time.sleep(0.002)  # 2ms 대기
                    
                    click_end_time = time.perf_counter()
                    actual_click_time = (click_end_time - click_start_time) * 1000
                    self.log(f"🔄 백업 클릭 완료! 소요시간: {actual_click_time:.1f}ms")
                    return
                    
                except Exception as e:
                    self.log(f"백업 위치 클릭 실패: {e}")
                
                click_end_time = time.perf_counter()
                actual_click_time = (click_end_time - click_start_time) * 1000
                self.log(f"🔄 모든 클릭 시도 완료! 소요시간: {actual_click_time:.1f}ms")
                
            except ImportError:
                # pyautogui 없을 때 Windows API 직접 사용
                try:
                    import ctypes
                    
                    # Windows API로 직접 키보드 이벤트 전송
                    VK_RETURN = 0x0D
                    VK_SPACE = 0x20
                    
                    # Enter 키 누르기/떼기
                    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0)
                    
                    # Space 키 누르기/떼기
                    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 0, 0)  
                    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 2, 0)
                    
                    click_end_time = time.perf_counter()
                    actual_click_time = (click_end_time - click_start_time) * 1000
                    
                    self.log(f"⚡ Windows API 직접 실행! 소요시간: {actual_click_time:.1f}ms")
                    
                except Exception as e:
                    self.log(f"Windows API 실패: {e}")
                    click_end_time = time.perf_counter()
                    actual_click_time = (click_end_time - click_start_time) * 1000
                    self.log(f"❌ 모든 클릭 방법 실패! 수동 클릭 필요. 소요시간: {actual_click_time:.1f}ms")
                
        except Exception as e:
            click_end_time = time.perf_counter()
            actual_click_time = (click_end_time - click_start_time) * 1000
            self.log(f"❌ 클릭 오류: {e} (소요시간: {actual_click_time:.1f}ms)")
            self.log("🔄 수동으로 클릭하세요!")
    
    def stop_macro(self):
        """매크로 중지"""
        self.is_running = False
        self.log("매크로가 중지되었습니다.")
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
    
    def open_log_file(self):
        """로그 파일 열기"""
        try:
            log_file_to_open = None
            
            # 1. 현재 인스턴스의 로그 파일이 있는지 확인
            if hasattr(self, 'log_file_path') and os.path.exists(self.log_file_path):
                log_file_to_open = self.log_file_path
            else:
                # 2. logs 폴더에서 가장 최근 로그 파일 찾기
                logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
                if os.path.exists(logs_dir):
                    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
                    if log_files:
                        # 가장 최근 파일 선택
                        log_files.sort(reverse=True)
                        log_file_to_open = os.path.join(logs_dir, log_files[0])
                
                # 3. 메인 디렉토리의 로그 파일도 확인
                if not log_file_to_open:
                    main_dir = os.path.dirname(os.path.abspath(__file__))
                    main_log_files = [f for f in os.listdir(main_dir) if f.endswith('.log')]
                    if main_log_files:
                        main_log_files.sort(reverse=True)
                        log_file_to_open = os.path.join(main_dir, main_log_files[0])
            
            if log_file_to_open and os.path.exists(log_file_to_open):
                # Windows에서 기본 텍스트 에디터로 열기
                os.startfile(log_file_to_open)
                self.log(f"📄 로그 파일을 열었습니다: {log_file_to_open}")
            else:
                messagebox.showwarning("경고", "로그 파일을 찾을 수 없습니다.\n매크로를 한 번 실행한 후 다시 시도해주세요.")
                
        except Exception as e:
            self.log(f"❌ 로그 파일 열기 실패: {e}")
            messagebox.showerror("오류", f"로그 파일 열기 실패:\n{e}")
    
    def export_timing_summary(self):
        """타이밍 요약 리포트 내보내기"""
        try:
            if not hasattr(self, 'timing_adjustments') or len(self.timing_adjustments) == 0:
                messagebox.showwarning("경고", "실행 히스토리가 없습니다.")
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timing_summary_{timestamp}.json"
            
            # 통계 계산
            avg_error = sum(self.timing_adjustments) / len(self.timing_adjustments)
            std_error = statistics.stdev(self.timing_adjustments) if len(self.timing_adjustments) > 1 else 0
            
            avg_execution = sum(self.execution_time_history) / len(self.execution_time_history) if hasattr(self, 'execution_time_history') and len(self.execution_time_history) > 0 else 0
            
            summary_data = {
                'export_time': datetime.now().isoformat(),
                'server_time_offset_ms': self.server_time_offset * 1000 if hasattr(self, 'server_time_offset') else 0,
                'network_latency_ms': self.network_latency * 1000 if hasattr(self, 'network_latency') else 0,
                'execution_count': len(self.timing_adjustments),
                'average_error_ms': avg_error,
                'error_std_dev_ms': std_error,
                'average_execution_time_ms': avg_execution * 1000,
                'success_rate': len([x for x in self.timing_adjustments if 0 <= x <= 20]) / len(self.timing_adjustments) * 100,
                'timing_errors_ms': self.timing_adjustments,
                'execution_times_ms': [t * 1000 for t in self.execution_time_history] if hasattr(self, 'execution_time_history') else []
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"📊 타이밍 요약 리포트 생성: {filename}")
            messagebox.showinfo("완료", f"타이밍 요약 리포트가 생성되었습니다:\n{filename}")
            
        except Exception as e:
            error_msg = f"요약 리포트 생성 실패: {e}"
            self.log(f"❌ {error_msg}")
            messagebox.showerror("오류", error_msg)
    
    def run(self): 
        """GUI 실행"""
        try:
            self.root.mainloop()
        finally:
            # 프로그램 종료 시 로그 정리
            if hasattr(self, 'logger'):
                self.logger.info("="*60)
                self.logger.info("프로그램 종료")
                self.logger.info(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                if hasattr(self, 'timing_adjustments') and len(self.timing_adjustments) > 0:
                    avg_error = sum(self.timing_adjustments) / len(self.timing_adjustments)
                    success_count = len([x for x in self.timing_adjustments if 0 <= x <= 20])
                    self.logger.info(f"세션 통계: 실행 {len(self.timing_adjustments)}회, 성공 {success_count}회 ({success_count/len(self.timing_adjustments)*100:.1f}%)")
                    self.logger.info(f"평균 오차: {avg_error:+.1f}ms")
                self.logger.info("="*60)
                
                # 로거 정리
                for handler in self.logger.handlers[:]:
                    handler.close()
                    self.logger.removeHandler(handler)


def main():
    """메인 함수"""
    app = TimeSyncMacroGUI()
    app.run()


if __name__ == "__main__":
    main()
 