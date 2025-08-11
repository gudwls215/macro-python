#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyautogui
import time

def test_auto_click():
    print("=== pyautogui 자동 클릭 테스트 ===")
    
    # 안전 설정
    pyautogui.FAILSAFE = True  # 테스트 시에는 안전 모드 켜기
    
    print("5초 후 메모장을 열고 자동으로 텍스트를 입력합니다...")
    
    # 카운트다운
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    try:
        # 메모장 열기 (Windows + R -> notepad)
        pyautogui.hotkey('win', 'r')
        time.sleep(1)
        pyautogui.typewrite('notepad')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)
        
        # 메모장에 텍스트 입력
        test_text = "자동 클릭 테스트 성공!\n현재 시간: " + time.strftime("%Y-%m-%d %H:%M:%S")
        pyautogui.typewrite(test_text, interval=0.05)
        
        print("✅ 자동 클릭 테스트 완료!")
        print("메모장에 텍스트가 입력되었는지 확인하세요.")
        
        # 마우스 위치 확인
        x, y = pyautogui.position()
        print(f"현재 마우스 위치: ({x}, {y})")
        
        # 화면 크기 확인
        screen_width, screen_height = pyautogui.size()
        print(f"화면 크기: {screen_width} x {screen_height}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_auto_click()
