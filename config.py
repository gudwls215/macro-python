# 정밀 시간 동기화 매크로 설정 파일

# 기본 설정
DEFAULT_SETTINGS = {
    "time_sync_samples": 5,  # 서버 시간 동기화 측정 횟수
    "precision_ms": 1,       # 시간 정밀도 (밀리초)
    "timeout": 30,           # 요소 대기 시간 (초)
    "headless": False,       # 기본 브라우저 표시 설정
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 일반적인 버튼 셀렉터 예시
COMMON_SELECTORS = {
    "submit_button": [
        "input[type='submit']",
        "button[type='submit']",
        ".submit-btn",
        "#submit",
        "//button[contains(text(), '제출')]",
        "//button[contains(text(), '신청')]",
        "//button[contains(text(), '구매')]",
        "//input[@type='submit']"
    ],
    "buy_button": [
        ".buy-btn",
        "#buy-button",
        "button.purchase",
        "//button[contains(text(), '구매')]",
        "//button[contains(text(), 'Buy')]",
        "//a[contains(@class, 'buy')]"
    ],
    "login_button": [
        ".login-btn",
        "#login",
        "button[type='submit']",
        "//button[contains(text(), '로그인')]",
        "//button[contains(text(), 'Login')]"
    ]
}

# 테스트용 사이트 예시
TEST_SITES = {
    "time_server": "https://worldtimeapi.org/",
    "httpbin": "https://httpbin.org/",
    "google": "https://www.google.com/",
    "github": "https://github.com/"
}
