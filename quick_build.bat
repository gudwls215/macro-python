@echo off
title Quick Build - 정밀 구매 타이밍 매크로

echo 🔨 간단 빌드 시작...

REM 이전 빌드 정리
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 간단 빌드 (기본 설정)
pyinstaller --onefile --noconsole --name "PrecisionTimingMacro" gui_macro.py

if exist "dist\PrecisionTimingMacro.exe" (
    echo ✅ 빌드 완료: dist\PrecisionTimingMacro.exe
    start "" "dist\"
) else (
    echo ❌ 빌드 실패
)

pause
