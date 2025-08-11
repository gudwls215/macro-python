#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 정밀 시간 동기화 매크로 데모
- C++ 정밀 타이머 연동
- 연속 모니터링
- 브라우저 미리 열기
- 통계 분석
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
    """GUI 버전 데모"""
    print("=== GUI 버전 데모 ===")
    print("사용자 친화적인 그래픽 인터페이스로 매크로를 설정하고 실행할 수 있습니다.")
    print("- 시간 동기화 버튼으로 서버와 시간 맞추기")
    print("- 빠른 시간 설정 버튼들 (5초 후, 10초 후 등)")
    print("- 실시간 로그 및 상태 표시")
    
    try:
        subprocess.run([sys.executable, "gui_macro.py"], check=True)
    except FileNotFoundError:
        print("gui_macro.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\nGUI 데모가 중단되었습니다.")


def run_simple_demo():
    """간단 버전 데모"""
    print("=== 간단 버전 데모 ===")
    print("기본 Python 라이브러리만 사용하는 버전입니다.")
    print("- 서버 시간 동기화")
    print("- 정확한 타이밍에 알림 및 웹사이트 열기")
    print("- 외부 패키지 의존성 없음")
    
    try:
        subprocess.run([sys.executable, "simple_macro.py"], check=True)
    except FileNotFoundError:
        print("simple_macro.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n간단 버전 데모가 중단되었습니다.")


def run_advanced_demo():
    """고급 버전 데모 (Selenium 필요)"""
    print("=== 고급 버전 데모 ===")
    print("Selenium을 사용한 완전 자동화 버전입니다.")
    print("- 자동 브라우저 제어")
    print("- 정밀한 버튼 클릭")
    print("- 다양한 셀렉터 지원")
    
    try:
        # 패키지 확인
        import requests
        import selenium
        print("필요한 패키지가 설치되어 있습니다.")
        subprocess.run([sys.executable, "time_sync_macro.py"], check=True)
    except ImportError as e:
        print(f"필요한 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령으로 패키지를 설치하세요:")
        print("pip install requests selenium webdriver-manager")
    except FileNotFoundError:
        print("time_sync_macro.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n고급 버전 데모가 중단되었습니다.")


def run_test_server():
    """테스트 서버 실행"""
    print("=== 테스트 서버 실행 ===")
    print("매크로 테스트를 위한 로컬 웹서버를 시작합니다.")
    print("서버가 시작되면 http://localhost:5000 에서 테스트할 수 있습니다.")
    
    try:
        import flask
        print("Flask가 설치되어 있습니다. 서버를 시작합니다...")
        subprocess.run([sys.executable, "test_server.py"], check=True)
    except ImportError:
        print("Flask가 설치되지 않았습니다.")
        print("다음 명령으로 Flask를 설치하세요: pip install flask")
    except FileNotFoundError:
        print("test_server.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n테스트 서버가 중단되었습니다.")


def time_sync_test():
    """시간 동기화 테스트"""
    print("=== 시간 동기화 테스트 ===")
    
    # 간단한 시간 동기화 테스트
    import time
    from datetime import datetime
    from urllib.request import urlopen
    
    test_urls = [
        "https://www.google.com/",
        "https://httpbin.org/",
        "https://github.com/"
    ]
    
    print("여러 사이트의 응답 시간을 측정합니다...\n")
    
    for url in test_urls:
        try:
            start_time = time.time()
            with urlopen(url, timeout=5) as response:
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                
                server_time_str = response.headers.get('Date', 'N/A')
                print(f"URL: {url}")
                print(f"응답 시간: {latency:.1f}ms")
                print(f"서버 시간: {server_time_str}")
                print("-" * 40)
                
        except Exception as e:
            print(f"URL: {url}")
            print(f"오류: {e}")
            print("-" * 40)


def show_file_info():
    """프로젝트 파일 정보 표시"""
    print("=== 프로젝트 파일 구조 ===")
    
    files_info = {
        "gui_macro.py": "GUI 버전 - 사용자 친화적 인터페이스",
        "simple_macro.py": "간단 버전 - 기본 라이브러리만 사용",
        "time_sync_macro.py": "고급 버전 - Selenium 자동화",
        "test_server.py": "테스트용 웹서버",
        "config.py": "설정 파일",
        "examples.py": "사용 예제 모음",
        "start.bat": "Windows 배치 실행 파일",
        "README.md": "프로젝트 설명서"
    }
    
    current_dir = os.getcwd()
    print(f"현재 디렉토리: {current_dir}\n")
    
    for filename, description in files_info.items():
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✓ {filename:<20} - {description} ({file_size:,} bytes)")
        else:
            print(f"✗ {filename:<20} - 파일 없음")
    
    print()


def main():
    """메인 메뉴"""
    while True:
        print("\n" + "=" * 60)
        print("정밀 시간 동기화 매크로 - 데모 및 테스트")
        print("=" * 60)
        print("1. GUI 버전 데모 실행")
        print("2. 간단 버전 데모 실행")
        print("3. 고급 버전 데모 실행 (Selenium)")
        print("4. 테스트 서버 실행")
        print("5. 시간 동기화 테스트")
        print("6. 프로젝트 파일 정보")
        print("7. 사용법 안내")
        print("0. 종료")
        
        try:
            choice = input("\n선택하세요 (0-7): ").strip()
            
            if choice == '1':
                run_gui_demo()
            elif choice == '2':
                run_simple_demo()
            elif choice == '3':
                run_advanced_demo()
            elif choice == '4':
                run_test_server()
            elif choice == '5':
                time_sync_test()
            elif choice == '6':
                show_file_info()
            elif choice == '7':
                print_usage_guide()
            elif choice == '0':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 선택입니다. 0-7 사이의 숫자를 입력하세요.")
                
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")
        
        input("\n계속하려면 Enter를 누르세요...")


def print_usage_guide():
    """사용법 안내"""
    guide = """
=== 사용법 안내 ===

1. GUI 버전 (추천)
   - 가장 사용하기 쉬운 버전
   - 그래픽 인터페이스로 모든 설정 가능
   - 실시간 로그 및 상태 확인

2. 간단 버전
   - 외부 패키지 없이 기본 Python만 사용
   - 콘솔 기반 인터페이스
   - 정확한 타이밍에 소리 알림

3. 고급 버전
   - Selenium을 사용한 완전 자동화
   - 자동 버튼 클릭 기능
   - 다양한 CSS/XPath 셀렉터 지원

=== 시간 입력 형식 ===
- 시간만: 14:30:00 (오늘 날짜 적용)
- 전체: 2025-08-11 14:30:00

=== 사용 팁 ===
- 안정적인 인터넷 연결 사용
- 먼저 시간 동기화 실행
- 테스트 서버로 동작 확인 후 실제 사용

=== 주의사항 ===
- 웹사이트 이용약관 준수
- 과도한 요청 금지
- 교육/테스트 목적으로만 사용
"""
    print(guide)


if __name__ == "__main__":
    main()
