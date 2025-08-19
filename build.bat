@echo off
chcp 65001 > nul
title 정밀 구매 타이밍 매크로 v2.0 - 빌드 도구

echo.
echo ==========================================
echo  정밀 구매 타이밍 매크로 v2.0 빌드 🔨
echo ==========================================
echo.

REM 빌드 시작 시간 기록
set start_time=%time%

REM Python과 PyInstaller 확인
echo 📋 빌드 환경 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PyInstaller가 설치되지 않았습니다!
    echo 💡 설치 중...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ PyInstaller 설치 실패!
        pause
        exit /b 1
    )
)

echo ✅ 빌드 환경 확인 완료

REM 필수 패키지 확인
echo 📦 필수 패키지 확인 중...
python -c "import pyautogui, keyboard, tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 필수 패키지가 누락되었습니다!
    echo 💡 설치 중...
    pip install pyautogui keyboard pillow
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치 실패!
        pause
        exit /b 1
    )
)

echo ✅ 필수 패키지 확인 완료

REM 이전 빌드 결과물 정리
echo 🧹 이전 빌드 결과물 정리 중...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM 빌드 시작
echo.
echo 🔨 빌드 시작...
echo 💡 이 과정은 몇 분 걸릴 수 있습니다...
echo.

REM PyInstaller로 빌드
pyinstaller --clean build_config.spec

REM 빌드 결과 확인
if exist "dist\PrecisionTimingMacro.exe" (
    echo.
    echo ✅ 빌드 성공!
    echo 📁 실행 파일 위치: dist\PrecisionTimingMacro.exe
    
    REM 파일 크기 확인
    for %%A in ("dist\PrecisionTimingMacro.exe") do (
        set size=%%~zA
        set /a size_mb=!size!/1024/1024
        echo 📊 파일 크기: !size_mb! MB
    )
    
    echo.
    echo 🎯 빌드 완료된 파일:
    dir "dist\PrecisionTimingMacro.exe"
    
    echo.
    echo 🚀 실행하시겠습니까? (Y/N)
    choice /c YN /n
    if !errorlevel!==1 (
        echo 🎮 프로그램 실행 중...
        start "" "dist\PrecisionTimingMacro.exe"
    )
    
) else (
    echo.
    echo ❌ 빌드 실패!
    echo 💡 오류 로그를 확인하세요
    echo.
    echo 📋 일반적인 해결 방법:
    echo   1. 관리자 권한으로 실행
    echo   2. 바이러스 백신 실시간 검사 일시 중지
    echo   3. Windows Defender 예외 추가
    echo   4. 가상환경에서 빌드
    pause
    exit /b 1
)

REM 빌드 시간 계산
set end_time=%time%
echo.
echo ⏱️ 빌드 시작: %start_time%
echo ⏱️ 빌드 완료: %end_time%

echo.
echo 📝 추가 정보:
echo   - 실행 파일: dist\PrecisionTimingMacro.exe
echo   - 로그 폴더: 실행 파일과 같은 위치에 logs\ 폴더가 생성됩니다
echo   - 관리자 권한으로 실행하면 더 정확한 타이밍을 얻을 수 있습니다
echo.
pause
