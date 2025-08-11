#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용 예제 및 테스트 스크립트
"""

from time_sync_macro import TimeSyncMacro
from config import DEFAULT_SETTINGS, COMMON_SELECTORS, TEST_SITES
import time
from datetime import datetime, timedelta


def example_basic_usage():
    """기본 사용 예제"""
    print("=== 기본 사용 예제 ===")
    
    macro = TimeSyncMacro()
    
    # 예제 설정
    url = "https://example.com"
    button_selector = "#submit-button"
    target_time = "14:30:00"  # 오늘 오후 2시 30분
    
    # 매크로 실행
    success = macro.run_macro(url, button_selector, target_time, headless=False)
    
    if success:
        print("매크로 실행 성공!")
    else:
        print("매크로 실행 실패!")


def example_advanced_usage():
    """고급 사용 예제"""
    print("=== 고급 사용 예제 ===")
    
    macro = TimeSyncMacro()
    
    # 1. 먼저 서버와 시간 동기화만 테스트
    url = "https://httpbin.org/"
    if macro.measure_server_time_offset(url, num_samples=10):
        print(f"시간 동기화 성공!")
        print(f"네트워크 지연: {macro.network_latency*1000:.2f}ms")
        print(f"서버 시간 차이: {macro.server_time_offset*1000:.2f}ms")
    
    # 2. 현재 정확한 서버 시간 확인
    current_server_time = macro.get_accurate_server_time()
    print(f"현재 서버 시간: {datetime.fromtimestamp(current_server_time)}")
    
    # 3. 10초 후 실행 예약
    future_time = datetime.fromtimestamp(current_server_time + 10)
    target_time_str = future_time.strftime("%H:%M:%S")
    
    print(f"10초 후 ({target_time_str}) 실행 예약")


def test_time_precision():
    """시간 정밀도 테스트"""
    print("=== 시간 정밀도 테스트 ===")
    
    # 여러 사이트의 지연시간 비교
    test_urls = [
        "https://www.google.com/",
        "https://github.com/",
        "https://httpbin.org/",
        "https://worldtimeapi.org/"
    ]
    
    macro = TimeSyncMacro()
    
    for url in test_urls:
        print(f"\n{url} 테스트 중...")
        try:
            if macro.measure_server_time_offset(url, num_samples=3):
                print(f"  지연시간: {macro.network_latency*1000:.1f}ms")
                print(f"  시간차: {macro.server_time_offset*1000:.1f}ms")
        except Exception as e:
            print(f"  오류: {e}")


def interactive_selector_finder():
    """대화형 셀렉터 찾기 도구"""
    print("=== 대화형 셀렉터 찾기 ===")
    
    url = input("대상 웹사이트 URL: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    macro = TimeSyncMacro()
    macro.setup_driver(headless=False)
    
    try:
        print("페이지 로딩 중...")
        macro.driver.get(url)
        
        print("\n브라우저가 열렸습니다. 대상 요소를 확인하고 셀렉터를 입력하세요.")
        print("일반적인 셀렉터 예시:")
        for category, selectors in COMMON_SELECTORS.items():
            print(f"\n{category}:")
            for selector in selectors[:3]:  # 상위 3개만 표시
                print(f"  {selector}")
        
        while True:
            selector = input("\n테스트할 셀렉터 (종료하려면 'quit'): ").strip()
            if selector.lower() == 'quit':
                break
            
            element = macro.wait_for_element(selector, timeout=5)
            if element:
                print(f"✓ 요소를 찾았습니다: {element.tag_name}")
                print(f"  텍스트: {element.text[:50]}...")
                
                test_click = input("테스트 클릭하시겠습니까? (y/N): ").strip().lower()
                if test_click == 'y':
                    try:
                        element.click()
                        print("✓ 클릭 성공!")
                    except Exception as e:
                        print(f"✗ 클릭 실패: {e}")
            else:
                print("✗ 요소를 찾을 수 없습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        macro.driver.quit()


def create_scheduled_macro():
    """예약된 매크로 생성"""
    print("=== 예약 매크로 생성 ===")
    
    # 사용자 입력
    url = input("URL: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    selector = input("버튼 셀렉터: ").strip()
    
    # 시간 선택
    print("\n시간 입력 방식:")
    print("1. 특정 시간 (예: 14:30:00)")
    print("2. N초 후 (예: 10)")
    print("3. N분 후 (예: 5m)")
    
    time_input = input("시간: ").strip()
    
    if time_input.endswith('m'):
        # N분 후
        minutes = int(time_input[:-1])
        target_time = datetime.now() + timedelta(minutes=minutes)
        target_time_str = target_time.strftime("%H:%M:%S")
    elif time_input.isdigit():
        # N초 후
        seconds = int(time_input)
        target_time = datetime.now() + timedelta(seconds=seconds)
        target_time_str = target_time.strftime("%H:%M:%S")
    else:
        # 특정 시간
        target_time_str = time_input
    
    print(f"\n예약된 매크로:")
    print(f"  URL: {url}")
    print(f"  셀렉터: {selector}")
    print(f"  실행 시간: {target_time_str}")
    
    confirm = input("\n실행하시겠습니까? (y/N): ").strip().lower()
    if confirm == 'y':
        macro = TimeSyncMacro()
        macro.run_macro(url, selector, target_time_str, headless=False)


def main():
    """메인 메뉴"""
    while True:
        print("\n" + "="*50)
        print("정밀 시간 동기화 매크로 도구")
        print("="*50)
        print("1. 매크로 실행")
        print("2. 시간 동기화 테스트")
        print("3. 지연시간 비교 테스트")
        print("4. 셀렉터 찾기 도구")
        print("5. 예약 매크로 생성")
        print("6. 기본 사용 예제")
        print("0. 종료")
        
        choice = input("\n선택: ").strip()
        
        try:
            if choice == '1':
                # 메인 매크로 실행
                from time_sync_macro import main as run_main_macro
                run_main_macro()
            elif choice == '2':
                test_url = input("테스트할 URL (기본값: https://httpbin.org/): ").strip()
                if not test_url:
                    test_url = "https://httpbin.org/"
                macro = TimeSyncMacro()
                macro.measure_server_time_offset(test_url, num_samples=5)
            elif choice == '3':
                test_time_precision()
            elif choice == '4':
                interactive_selector_finder()
            elif choice == '5':
                create_scheduled_macro()
            elif choice == '6':
                example_basic_usage()
            elif choice == '0':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n\n작업이 취소되었습니다.")
        except Exception as e:
            print(f"\n오류 발생: {e}")
        
        input("\n계속하려면 Enter를 누르세요...")


if __name__ == "__main__":
    main()
