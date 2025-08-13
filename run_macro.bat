@echo off
chcp 65001 > nul
title 정밀 구매 타이밍 매크로 v2.0

echo.
echo ==========================================
echo  정밀 구매 타이밍 매크로 v2.0 🎯
echo ==========================================
echo.

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo 💡 https://www.python.org/downloads/ 에서 Python을 설치하세요
    echo.
    pause
    exit /b 1
)

echo ✅ Python 설치 확인됨

REM 필수 패키지 설치 확인
echo 📦 필수 패키지 확인 중...
python -c "import pyautogui, keyboard" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 필수 패키지가 설치되지 않았습니다!
    echo 💡 자동 설치를 시작합니다...
    echo.
    
    REM 필수 패키지 설치
    echo 📦 pyautogui 설치 중...
    pip install pyautogui pillow
    echo 📦 keyboard 설치 중...
    pip install keyboard
    
    REM 설치 확인
    python -c "import pyautogui, keyboard" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치 실패!
        echo 💡 관리자 권한으로 명령 프롬프트를 실행하고 다시 시도하세요
        echo 💡 또는 수동 설치: pip install pyautogui keyboard pillow
        pause
        exit /b 1
    )
)

echo ✅ 필수 패키지 설치 확인됨
echo.
echo 🚀 GUI 매크로 실행 중...
echo 💡 프로그램이 시작되면 이 창은 최소화됩니다
echo.

REM GUI 매크로 실행
python gui_macro.py

REM 실행 완료
echo.
echo 📝 프로그램이 종료되었습니다
echo 💡 문제가 있다면 로그 파일을 확인하세요
pause
