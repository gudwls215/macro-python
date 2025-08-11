@echo off
chcp 65001 > nul
echo =============================================
echo 정밀 시간 동기화 매크로 v2.0 런처
echo =============================================
echo.

echo 🎯 사용 가능한 버전:
echo 1. GUI 버전 v2.0 (추천) ⭐ - 고정밀 타이밍, 브라우저 미리 열기
echo 2. 고급 데모 - 정밀도 테스트 및 성능 분석 도구
echo 3. 간단 버전 - 기본 라이브러리만 사용 (외부 패키지 불필요)
echo 4. 고급 버전 - Selenium 자동 클릭 (패키지 설치 필요)
echo 5. 테스트 서버 실행 - 로컬 테스트용 웹서버
echo 6. C++ 타이머 컴파일 - 마이크로초 정밀도 (선택사항)
echo.

set /p choice="선택하세요 (1-6): "

if "%choice%"=="1" (
    echo 🚀 GUI 버전 v2.0을 실행합니다...
    echo.
    echo ✨ 새로운 기능:
    echo - 고정밀 타이머 ^(±5ms 정확도^)
    echo - 브라우저 미리 열기
    echo - 연속 서버 시간 측정
    echo - 실시간 정확도 표시
    echo.
    python gui_macro.py
) else if "%choice%"=="2" (
    echo 📊 고급 데모를 실행합니다...
    echo - Python vs C++ 타이머 성능 비교
    echo - 네트워크 지연 통계 분석
    echo - 정밀도 테스트 도구
    echo.
    python advanced_demo.py
) else if "%choice%"=="3" (
    echo 📝 간단 버전을 실행합니다...
    echo - 외부 패키지 불필요
    echo - 기본 Python 라이브러리만 사용
    echo.
    python simple_macro.py
) else if "%choice%"=="4" (
    echo 🔧 고급 버전을 실행합니다...
    echo ⚠️ 주의: Selenium, requests 등 추가 패키지가 필요합니다.
    python time_sync_macro.py
) else if "%choice%"=="5" (
    echo 🌐 테스트 서버를 시작합니다...
    echo 브라우저에서 http://localhost:5000 을 열어 테스트하세요.
    echo 서버를 중지하려면 Ctrl+C를 누르세요.
    python test_server.py
) else if "%choice%"=="6" (
    echo ⚙️ C++ 정밀 타이머를 컴파일합니다...
    echo 마이크로초 단위 정밀도를 제공합니다.
    echo.
    compile_timer.bat
) else (
    echo 🎯 기본값으로 GUI 버전 v2.0을 실행합니다...
    python gui_macro.py
)

echo.
pause
