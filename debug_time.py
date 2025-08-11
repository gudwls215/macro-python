#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timezone
from urllib.request import urlopen

def test_time_sync():
    # 현재 로컬 시간 확인
    print('=== 시간 동기화 테스트 ===')
    local_now = datetime.now()
    utc_now = datetime.utcnow()
    
    print(f'현재 로컬 시간: {local_now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'현재 UTC 시간: {utc_now.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'로컬 타임스탬프: {time.time():.3f}')
    
    # 구글 서버 시간 확인
    try:
        print('\n=== 서버 응답 테스트 ===')
        local_before = time.time()
        
        with urlopen('https://www.google.com', timeout=10) as response:
            local_after = time.time()
            latency = (local_after - local_before) / 2
            
            server_time_str = response.headers.get('Date')
            print(f'서버 응답 헤더: {dict(response.headers)}')
            print(f'구글 서버 시간 헤더: {server_time_str}')
            print(f'네트워크 지연: {latency*1000:.1f}ms')
            
            if server_time_str:
                # 다양한 형식으로 파싱 시도
                time_formats = [
                    '%a, %d %b %Y %H:%M:%S GMT',
                    '%a, %d %b %Y %H:%M:%S %Z',
                    '%d %b %Y %H:%M:%S GMT',
                ]
                
                server_time = None
                for fmt in time_formats:
                    try:
                        server_time = datetime.strptime(server_time_str, fmt)
                        print(f'성공한 시간 형식: {fmt}')
                        break
                    except ValueError as e:
                        print(f'형식 {fmt} 실패: {e}')
                        continue
                
                if server_time:
                    server_time_utc = server_time.replace(tzinfo=timezone.utc)
                    server_timestamp = server_time_utc.timestamp()
                    local_timestamp = local_before + latency
                    offset = server_timestamp - local_timestamp
                    
                    print(f'\n=== 결과 ===')
                    print(f'파싱된 서버 시간: {server_time.strftime("%Y-%m-%d %H:%M:%S")} UTC')
                    print(f'서버 타임스탬프: {server_timestamp:.3f}')
                    print(f'보정된 로컬 타임스탬프: {local_timestamp:.3f}')
                    print(f'시간차 (초): {offset:.3f}')
                    print(f'시간차 (ms): {offset*1000:.1f}ms')
                    
                    # 정상적인 범위 확인
                    if abs(offset) > 3600:  # 1시간 이상 차이
                        print(f'⚠️  경고: 시간차가 비정상적으로 큽니다! ({abs(offset)/3600:.1f}시간)')
                    elif abs(offset) > 60:  # 1분 이상 차이
                        print(f'⚠️  주의: 시간차가 큽니다! ({abs(offset):.1f}초)')
                    else:
                        print(f'✓ 정상적인 시간차입니다.')
                else:
                    print('❌ 서버 시간 파싱에 실패했습니다.')
            else:
                print('❌ 서버에서 Date 헤더를 받지 못했습니다.')
                
    except Exception as e:
        print(f'❌ 테스트 실패: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_time_sync()
