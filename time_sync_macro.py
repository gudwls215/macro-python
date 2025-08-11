#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정확한 시간 동기화 매크로
- 특정 사이트의 서버시간과 지연율을 측정
- 목표 시간에 정확히 요청이 서버에 도착하도록 클릭 타이밍 조절
"""

import time
import requests
import statistics
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading
import json
import re
from urllib.parse import urljoin, urlparse


class TimeSyncMacro:
    def __init__(self):
        self.driver = None
        self.server_time_offset = 0  # 서버시간과 로컬시간의 차이 (초)
        self.network_latency = 0     # 평균 네트워크 지연시간 (초)
        self.latency_samples = []    # 지연시간 샘플들
        self.target_url = ""
        self.button_selector = ""
        self.target_time = None
        
    def setup_driver(self, headless=False):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
        
    def measure_server_time_offset(self, url, num_samples=5):
        """서버 시간과 로컬 시간의 차이를 측정"""
        print(f"서버 시간 동기화 측정 중... ({num_samples}회 측정)")
        
        offsets = []
        latencies = []
        
        for i in range(num_samples):
            try:
                # 요청 전 로컬 시간
                local_before = time.time()
                
                # HEAD 요청으로 서버 헤더 정보 가져오기
                response = requests.head(url, timeout=10)
                
                # 요청 후 로컬 시간
                local_after = time.time()
                
                # 네트워크 지연시간 계산 (왕복시간의 절반)
                latency = (local_after - local_before) / 2
                latencies.append(latency)
                
                # 서버 시간 추출
                server_time_str = response.headers.get('Date')
                if server_time_str:
                    # RFC 2822 형식 파싱
                    server_time = datetime.strptime(
                        server_time_str, 
                        '%a, %d %b %Y %H:%M:%S %Z'
                    ).replace(tzinfo=timezone.utc)
                    
                    server_timestamp = server_time.timestamp()
                    local_timestamp = local_before + latency  # 네트워크 지연 보정
                    
                    offset = server_timestamp - local_timestamp
                    offsets.append(offset)
                    
                    print(f"  측정 {i+1}: 지연시간 {latency*1000:.1f}ms, 시간차 {offset*1000:.1f}ms")
                
                time.sleep(0.1)  # 연속 요청 간격
                
            except Exception as e:
                print(f"  측정 {i+1} 실패: {e}")
                continue
        
        if offsets and latencies:
            self.server_time_offset = statistics.median(offsets)
            self.network_latency = statistics.median(latencies)
            
            print(f"\n동기화 결과:")
            print(f"  평균 네트워크 지연: {self.network_latency*1000:.1f}ms")
            print(f"  서버-로컬 시간차: {self.server_time_offset*1000:.1f}ms")
            print(f"  지연시간 표준편차: {statistics.stdev(latencies)*1000:.1f}ms")
            
            return True
        else:
            print("시간 동기화 실패!")
            return False
    
    def get_accurate_server_time(self):
        """현재 정확한 서버 시간 반환"""
        local_time = time.time()
        server_time = local_time + self.server_time_offset
        return server_time
    
    def wait_for_element(self, selector, timeout=30):
        """요소가 나타날 때까지 대기"""
        try:
            if selector.startswith('//'):
                # XPath
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector.startswith('#'):
                # ID
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.ID, selector[1:]))
                )
            elif selector.startswith('.'):
                # Class
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, selector[1:]))
                )
            else:
                # CSS Selector
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            return element
        except Exception as e:
            print(f"요소를 찾을 수 없습니다: {selector}")
            print(f"오류: {e}")
            return None
    
    def precise_click(self, target_time_str, button_selector):
        """정확한 시간에 클릭 실행"""
        # 목표 시간 파싱
        try:
            target_datetime = datetime.strptime(target_time_str, '%Y-%m-%d %H:%M:%S')
            target_timestamp = target_datetime.timestamp()
        except ValueError:
            try:
                # 시간만 입력된 경우 (오늘 날짜 적용)
                today = datetime.now().date()
                time_part = datetime.strptime(target_time_str, '%H:%M:%S').time()
                target_datetime = datetime.combine(today, time_part)
                target_timestamp = target_datetime.timestamp()
            except ValueError:
                print("시간 형식이 잘못되었습니다. 'YYYY-MM-DD HH:MM:SS' 또는 'HH:MM:SS' 형식을 사용하세요.")
                return False
        
        print(f"목표 시간: {target_datetime}")
        
        # 버튼 요소 미리 찾기
        button_element = self.wait_for_element(button_selector)
        if not button_element:
            return False
        
        print("버튼 요소를 찾았습니다. 클릭 대기 중...")
        
        # 클릭 타이밍 계산
        while True:
            current_server_time = self.get_accurate_server_time()
            time_until_target = target_timestamp - current_server_time
            
            # 목표 시간이 지났으면 즉시 클릭
            if time_until_target <= 0:
                print("목표 시간이 이미 지났습니다. 즉시 클릭합니다.")
                break
            
            # 남은 시간 표시 (1초마다)
            if int(time_until_target) != int(time_until_target + 1):
                print(f"남은 시간: {time_until_target:.3f}초")
            
            # 네트워크 지연을 고려한 클릭 타이밍
            if time_until_target <= self.network_latency:
                print(f"네트워크 지연({self.network_latency*1000:.1f}ms)을 고려하여 클릭 실행!")
                break
            
            time.sleep(0.001)  # 1ms 정밀도
        
        # 클릭 실행
        try:
            click_time = time.time()
            button_element.click()
            actual_server_time = click_time + self.server_time_offset
            
            print(f"클릭 완료!")
            print(f"실제 서버 도착 예상 시간: {datetime.fromtimestamp(actual_server_time + self.network_latency)}")
            print(f"목표 시간과의 차이: {(actual_server_time + self.network_latency - target_timestamp)*1000:.1f}ms")
            
            return True
            
        except Exception as e:
            print(f"클릭 실패: {e}")
            return False
    
    def run_macro(self, url, button_selector, target_time, headless=False):
        """매크로 실행"""
        self.target_url = url
        self.button_selector = button_selector
        
        try:
            print("=== 정밀 시간 동기화 매크로 시작 ===")
            print(f"대상 URL: {url}")
            print(f"버튼 셀렉터: {button_selector}")
            print(f"목표 시간: {target_time}")
            
            # 1. 서버 시간 동기화
            print("\n1. 서버 시간 동기화 중...")
            if not self.measure_server_time_offset(url, num_samples=5):
                print("서버 시간 동기화에 실패했습니다.")
                return False
            
            # 2. 브라우저 설정
            print("\n2. 브라우저 설정 중...")
            self.setup_driver(headless=headless)
            
            # 3. 페이지 로드
            print("\n3. 페이지 로딩 중...")
            self.driver.get(url)
            
            # 4. 정밀 클릭 실행
            print("\n4. 정밀 클릭 대기 중...")
            success = self.precise_click(target_time, button_selector)
            
            if success:
                print("\n=== 매크로 실행 완료 ===")
            else:
                print("\n=== 매크로 실행 실패 ===")
            
            # 결과 확인을 위해 잠시 대기
            time.sleep(3)
            
            return success
            
        except Exception as e:
            print(f"매크로 실행 중 오류 발생: {e}")
            return False
        
        finally:
            # 브라우저 종료
            if self.driver:
                self.driver.quit()
    
    def test_latency_continuously(self, url, duration=60):
        """지속적인 지연시간 모니터링 (테스트용)"""
        print(f"{duration}초 동안 지연시간을 모니터링합니다...")
        
        start_time = time.time()
        latencies = []
        
        while time.time() - start_time < duration:
            try:
                before = time.time()
                response = requests.head(url, timeout=5)
                after = time.time()
                
                latency = (after - before) * 1000  # ms 단위
                latencies.append(latency)
                
                print(f"지연시간: {latency:.1f}ms")
                time.sleep(1)
                
            except Exception as e:
                print(f"측정 실패: {e}")
                time.sleep(1)
        
        if latencies:
            print(f"\n=== 지연시간 통계 ===")
            print(f"평균: {statistics.mean(latencies):.1f}ms")
            print(f"중앙값: {statistics.median(latencies):.1f}ms")
            print(f"최소: {min(latencies):.1f}ms")
            print(f"최대: {max(latencies):.1f}ms")
            print(f"표준편차: {statistics.stdev(latencies):.1f}ms")


def main():
    """메인 함수"""
    print("=== 정밀 시간 동기화 매크로 ===")
    print("특정 시간에 정확히 서버에 요청이 도착하도록 클릭하는 매크로입니다.\n")
    
    # 사용자 입력
    url = input("대상 웹사이트 URL을 입력하세요: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print("\n버튼 셀렉터 입력 방법:")
    print("  - CSS Selector: button.submit-btn")
    print("  - ID: #submit-button")
    print("  - Class: .submit-btn")
    print("  - XPath: //button[@id='submit']")
    
    button_selector = input("클릭할 버튼의 셀렉터를 입력하세요: ").strip()
    
    print("\n시간 입력 형식:")
    print("  - 전체: 2025-08-11 14:30:00")
    print("  - 시간만: 14:30:00 (오늘 날짜 적용)")
    
    target_time = input("목표 시간을 입력하세요: ").strip()
    
    headless = input("\n브라우저를 숨김 모드로 실행하시겠습니까? (y/N): ").strip().lower() == 'y'
    
    # 매크로 실행
    macro = TimeSyncMacro()
    
    # 지연시간 테스트 옵션
    test_latency = input("\n먼저 네트워크 지연시간을 테스트하시겠습니까? (y/N): ").strip().lower() == 'y'
    if test_latency:
        duration = int(input("테스트 시간(초, 기본값 30): ").strip() or "30")
        macro.test_latency_continuously(url, duration)
        
        proceed = input("\n매크로를 계속 실행하시겠습니까? (Y/n): ").strip().lower()
        if proceed == 'n':
            return
    
    # 실제 매크로 실행
    success = macro.run_macro(url, button_selector, target_time, headless)
    
    if success:
        print("매크로가 성공적으로 실행되었습니다!")
    else:
        print("매크로 실행에 실패했습니다.")


if __name__ == "__main__":
    main()
