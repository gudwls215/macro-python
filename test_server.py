#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 테스트 웹서버
매크로 테스트용 로컬 웹페이지를 제공합니다.
"""

from flask import Flask, render_template_string, request, jsonify
import time
from datetime import datetime
import threading

app = Flask(__name__)

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>매크로 테스트 페이지</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .time-display {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #e8f4fd;
            border-radius: 5px;
        }
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        button {
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .submit-btn {
            background: #4CAF50;
            color: white;
        }
        .submit-btn:hover {
            background: #45a049;
        }
        .buy-btn {
            background: #ff6b6b;
            color: white;
        }
        .buy-btn:hover {
            background: #ff5252;
        }
        .test-btn {
            background: #2196F3;
            color: white;
        }
        .test-btn:hover {
            background: #1976D2;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #e8f5e8;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            display: none;
        }
        .log {
            max-height: 200px;
            overflow-y: auto;
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 10px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 12px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-box {
            background: #f0f7ff;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>매크로 테스트 페이지</h1>
        
        <div class="time-display" id="currentTime">
            현재 서버 시간: Loading...
        </div>
        
        <div class="button-group">
            <button class="submit-btn" id="submit-button" onclick="handleClick('제출')">
                제출 버튼
            </button>
            <button class="buy-btn" id="buy-button" onclick="handleClick('구매')">
                구매 버튼
            </button>
            <button class="test-btn" id="test-button" onclick="handleClick('테스트')">
                테스트 버튼
            </button>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="clickCount">0</div>
                <div class="stat-label">총 클릭 횟수</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="avgDelay">0ms</div>
                <div class="stat-label">평균 지연시간</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="lastClick">-</div>
                <div class="stat-label">마지막 클릭</div>
            </div>
        </div>
        
        <div class="result" id="result">
            <strong>클릭 성공!</strong>
            <p id="resultText"></p>
        </div>
        
        <div class="log" id="clickLog">
            <div><strong>클릭 로그:</strong></div>
        </div>
    </div>

    <script>
        let clickCount = 0;
        let clickTimes = [];
        
        // 서버 시간 업데이트
        function updateTime() {
            fetch('/api/time')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('currentTime').textContent = 
                        '현재 서버 시간: ' + data.time;
                })
                .catch(error => console.error('Time update error:', error));
        }
        
        // 클릭 처리
        function handleClick(buttonName) {
            const clickTime = new Date();
            clickCount++;
            clickTimes.push(clickTime.getTime());
            
            // 서버에 클릭 정보 전송
            fetch('/api/click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    button: buttonName,
                    client_time: clickTime.toISOString(),
                    timestamp: clickTime.getTime()
                })
            })
            .then(response => response.json())
            .then(data => {
                // 결과 표시
                const result = document.getElementById('result');
                const resultText = document.getElementById('resultText');
                
                resultText.innerHTML = 
                    `버튼: ${buttonName}<br>` +
                    `클라이언트 시간: ${clickTime.toLocaleString()}<br>` +
                    `서버 수신 시간: ${data.server_time}<br>` +
                    `지연시간: ${data.delay_ms}ms`;
                
                result.style.display = 'block';
                
                // 로그 추가
                const log = document.getElementById('clickLog');
                const logEntry = document.createElement('div');
                logEntry.innerHTML = 
                    `[${clickTime.toLocaleTimeString()}] ${buttonName} 클릭 - ` +
                    `지연: ${data.delay_ms}ms`;
                log.appendChild(logEntry);
                log.scrollTop = log.scrollHeight;
                
                // 통계 업데이트
                updateStats(data.delay_ms, clickTime);
            })
            .catch(error => {
                console.error('Click error:', error);
            });
        }
        
        function updateStats(delayMs, clickTime) {
            document.getElementById('clickCount').textContent = clickCount;
            document.getElementById('lastClick').textContent = 
                clickTime.toLocaleTimeString();
            
            // 평균 지연시간 계산 (최근 10개)
            const recentDelays = window.recentDelays || [];
            recentDelays.push(delayMs);
            if (recentDelays.length > 10) recentDelays.shift();
            window.recentDelays = recentDelays;
            
            const avgDelay = recentDelays.reduce((a, b) => a + b, 0) / recentDelays.length;
            document.getElementById('avgDelay').textContent = Math.round(avgDelay) + 'ms';
        }
        
        // 초기화
        updateTime();
        setInterval(updateTime, 1000);
        
        // 페이지 로드 완료 알림
        console.log('매크로 테스트 페이지가 준비되었습니다.');
        console.log('사용 가능한 셀렉터:');
        console.log('- #submit-button (제출 버튼)');
        console.log('- #buy-button (구매 버튼)');
        console.log('- #test-button (테스트 버튼)');
        console.log('- .submit-btn (CSS 클래스)');
        console.log('- .buy-btn (CSS 클래스)');
        console.log('- .test-btn (CSS 클래스)');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """메인 페이지"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/time')
def get_time():
    """현재 서버 시간 반환"""
    current_time = datetime.now()
    return jsonify({
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'timestamp': time.time() * 1000,
        'iso': current_time.isoformat()
    })

@app.route('/api/click', methods=['POST'])
def handle_click():
    """클릭 이벤트 처리"""
    data = request.get_json()
    server_receive_time = datetime.now()
    
    # 클라이언트 시간과 서버 시간 비교
    client_time = datetime.fromisoformat(data['client_time'].replace('Z', '+00:00'))
    client_timestamp = data['timestamp']
    server_timestamp = time.time() * 1000
    
    delay_ms = int(server_timestamp - client_timestamp)
    
    print(f"[CLICK] {data['button']} - 지연시간: {delay_ms}ms")
    
    return jsonify({
        'success': True,
        'button': data['button'],
        'server_time': server_receive_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'client_time': data['client_time'],
        'delay_ms': delay_ms,
        'timestamp': server_timestamp
    })

def run_server(port=5000):
    """서버 실행"""
    print(f"매크로 테스트 서버 시작...")
    print(f"URL: http://localhost:{port}")
    print(f"테스트용 셀렉터:")
    print(f"  - #submit-button")
    print(f"  - #buy-button") 
    print(f"  - #test-button")
    print(f"  - .submit-btn")
    print(f"  - .buy-btn")
    print(f"  - .test-btn")
    print(f"\n서버를 중지하려면 Ctrl+C를 누르세요.")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_server(port)
