#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 시간 동기화 매크로 (기본 패키지만 사용)
외부 패키지 없이 기본 Python 라이브러리만 사용하는 버전
"""

import time
import threading
import webbrowser
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
import re
import json


class SimpleTimeSyncMacro:
    def __init__(self):
        self.server_time_offset = 0  # 서버시간과 로컬시간의 차이 (초)
        self.network_latency = 0     # 평균 네트워크 지연시간 (초)
        self.target_url = ""
        self.target_time = None
        
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
                with urlopen(url, timeout=10) as response:
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
            # 중앙값 사용 (이상값 제거)
            offsets.sort()
            latencies.sort()
            
            mid = len(offsets) // 2
            self.server_time_offset = offsets[mid] if len(offsets) % 2 == 1 else (offsets[mid-1] + offsets[mid]) / 2
            
            mid = len(latencies) // 2
            self.network_latency = latencies[mid] if len(latencies) % 2 == 1 else (latencies[mid-1] + latencies[mid]) / 2
            
            # 표준편차 계산
            if len(latencies) > 1:
                mean_latency = sum(latencies) / len(latencies)
                variance = sum((x - mean_latency) ** 2 for x in latencies) / (len(latencies) - 1)
                std_dev = variance ** 0.5
            else:
                std_dev = 0
            
            print(f"\n동기화 결과:")
            print(f"  평균 네트워크 지연: {self.network_latency*1000:.1f}ms")
            print(f"  서버-로컬 시간차: {self.server_time_offset*1000:.1f}ms")
            print(f"  지연시간 표준편차: {std_dev*1000:.1f}ms")
            
            return True
        else:
            print("시간 동기화 실패!")
            return False
    
    def get_accurate_server_time(self):
        """현재 정확한 서버 시간 반환"""
        local_time = time.time()
        server_time = local_time + self.server_time_offset
        return server_time
    
    def wait_for_target_time(self, target_time_str):
        """정확한 시간까지 대기하고 알림"""
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
        print("정확한 타이밍을 위해 대기 중...")
        
        # 목표 시간까지 대기
        while True:
            current_server_time = self.get_accurate_server_time()
            time_until_target = target_timestamp - current_server_time
            
            # 목표 시간이 지났으면 즉시 알림
            if time_until_target <= 0:
                print("목표 시간이 이미 지났습니다!")
                break
            
            # 남은 시간 표시 (1초마다)
            if int(time_until_target) != int(time_until_target + 1):
                print(f"남은 시간: {time_until_target:.3f}초")
            
            # 네트워크 지연을 고려한 타이밍
            if time_until_target <= self.network_latency:
                print(f"네트워크 지연({self.network_latency*1000:.1f}ms)을 고려하여 알림!")
                print("지금 클릭하세요!")
                
                # 알림음 (Windows)
                try:
                    import winsound
                    winsound.Beep(1000, 500)  # 1000Hz, 0.5초
                except:
                    print("삐! 삐! 삐!")  # 소리가 나지 않으면 텍스트로 알림
                
                break
            
            time.sleep(0.001)  # 1ms 정밀도
        
        # 실제 시간 계산
        action_time = time.time()
        actual_server_time = action_time + self.server_time_offset
        
        print(f"알림 완료!")
        print(f"실제 서버 도착 예상 시간: {datetime.fromtimestamp(actual_server_time + self.network_latency)}")
        print(f"목표 시간과의 차이: {(actual_server_time + self.network_latency - target_timestamp)*1000:.1f}ms")
        
        return True
    
    def open_website_at_time(self, url, target_time):
        """특정 시간에 웹사이트 열기"""
        print("=== 간단한 시간 동기화 매크로 ===")
        print(f"대상 URL: {url}")
        print(f"목표 시간: {target_time}")
        
        try:
            # 1. 서버 시간 동기화
            print("\n1. 서버 시간 동기화 중...")
            if not self.measure_server_time_offset(url, num_samples=5):
                print("서버 시간 동기화에 실패했습니다.")
                return False
            
            # 2. 목표 시간까지 대기 및 알림
            print("\n2. 정확한 타이밍 대기 중...")
            success = self.wait_for_target_time(target_time)
            
            if success:
                print("\n3. 웹사이트를 엽니다...")
                webbrowser.open(url)
                print("=== 매크로 실행 완료 ===")
            
            return success
            
        except Exception as e:
            print(f"매크로 실행 중 오류 발생: {e}")
            return False
    
    def test_latency_continuously(self, url, duration=60):
        """지속적인 지연시간 모니터링"""
        print(f"{duration}초 동안 지연시간을 모니터링합니다...")
        
        start_time = time.time()
        latencies = []
        
        while time.time() - start_time < duration:
            try:
                before = time.time()
                with urlopen(url, timeout=5) as response:
                    after = time.time()
                
                latency = (after - before) * 1000  # ms 단위
                latencies.append(latency)
                
                print(f"지연시간: {latency:.1f}ms")
                time.sleep(1)
                
            except Exception as e:
                print(f"측정 실패: {e}")
                time.sleep(1)
        
        if latencies:
            latencies.sort()
            n = len(latencies)
            mean = sum(latencies) / n
            median = latencies[n//2] if n % 2 == 1 else (latencies[n//2-1] + latencies[n//2]) / 2
            
            if n > 1:
                variance = sum((x - mean) ** 2 for x in latencies) / (n - 1)
                std_dev = variance ** 0.5
            else:
                std_dev = 0
            
            print(f"\n=== 지연시간 통계 ===")
            print(f"평균: {mean:.1f}ms")
            print(f"중앙값: {median:.1f}ms")
            print(f"최소: {min(latencies):.1f}ms")
            print(f"최대: {max(latencies):.1f}ms")
            print(f"표준편차: {std_dev:.1f}ms")


def main():
    """메인 함수"""
    print("=== 간단한 시간 동기화 매크로 ===")
    print("특정 시간에 정확한 타이밍으로 알림하는 매크로입니다.")
    print("(웹브라우저 자동화는 제외, 수동 클릭 필요)\n")
    
    # 사용자 입력
    url = input("대상 웹사이트 URL을 입력하세요: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print("\n시간 입력 형식:")
    print("  - 전체: 2025-08-11 14:30:00")
    print("  - 시간만: 14:30:00 (오늘 날짜 적용)")
    
    target_time = input("목표 시간을 입력하세요: ").strip()
    
    # 매크로 실행
    macro = SimpleTimeSyncMacro()
    
    # 지연시간 테스트 옵션
    test_latency = input("\n먼저 네트워크 지연시간을 테스트하시겠습니까? (y/N): ").strip().lower() == 'y'
    if test_latency:
        duration = int(input("테스트 시간(초, 기본값 30): ").strip() or "30")
        macro.test_latency_continuously(url, duration)
        
        proceed = input("\n매크로를 계속 실행하시겠습니까? (Y/n): ").strip().lower()
        if proceed == 'n':
            return
    
    # 실제 매크로 실행
    success = macro.open_website_at_time(url, target_time)
    
    if success:
        print("매크로가 성공적으로 실행되었습니다!")
        print("알림이 울릴 때 수동으로 버튼을 클릭하세요!")
    else:
        print("매크로 실행에 실패했습니다.")


if __name__ == "__main__":
    main()
