#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime

def test_precise_timing():
    print("=== 정밀 타이밍 테스트 ===")
    
    # 5초 후 목표 시간 설정
    target_time = time.time() + 5.0
    target_dt = datetime.fromtimestamp(target_time)
    
    print(f"목표 시간: {target_dt.strftime('%H:%M:%S.%f')[:-3]}")
    print("5초 후 정확히 실행됩니다...")
    
    # 네트워크 지연 시뮬레이션
    simulated_latency = 0.05  # 50ms
    click_execution_time = 0.003  # 3ms
    target_delay = 0.01  # 10ms
    
    # 정밀 클릭 시점 계산
    precise_target = target_time - simulated_latency - click_execution_time + target_delay
    
    print(f"계산된 클릭 시점: {datetime.fromtimestamp(precise_target).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"예상 도착 시간: {datetime.fromtimestamp(target_time + target_delay).strftime('%H:%M:%S.%f')[:-3]}")
    
    # 정밀 대기
    while True:
        current_time = time.time()
        remaining = precise_target - current_time
        
        if remaining <= 0:
            break
        
        if remaining <= 0.0005:  # 0.5ms 이하
            continue
        elif remaining <= 0.002:  # 2ms 이하
            time.sleep(0.0001)
        elif remaining <= 0.01:  # 10ms 이하
            time.sleep(remaining * 0.3)
        else:
            time.sleep(remaining - 0.003)
    
    # 실행!
    execution_time = time.time()
    predicted_arrival = execution_time + simulated_latency
    
    # 결과 분석
    target_vs_execution = (execution_time - target_time) * 1000
    target_vs_arrival = (predicted_arrival - target_time) * 1000
    
    print("\n=== 결과 ===")
    print(f"실제 실행 시간: {datetime.fromtimestamp(execution_time).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"예상 도착 시간: {datetime.fromtimestamp(predicted_arrival).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"클릭 지연: {target_vs_execution:+.1f}ms")
    print(f"도착 지연: {target_vs_arrival:+.1f}ms")
    
    # 조건 검증
    condition1 = predicted_arrival >= target_time
    condition2 = target_vs_arrival <= 20
    
    print(f"\n조건1 (도착≥목표): {'✅ 통과' if condition1 else '❌ 실패'}")
    print(f"조건2 (20ms이내): {'✅ 통과' if condition2 else '❌ 실패'}")
    
    if condition1 and condition2:
        print("🎉 테스트 성공!")
    else:
        print("❌ 테스트 실패")

if __name__ == "__main__":
    test_precise_timing()
