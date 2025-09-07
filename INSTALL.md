# 📦 설치 가이드 - 정밀 구매 타이밍 매크로 v2.0

## 🚀 빠른 설치 (Windows)

### 1️⃣ 자동 설치 방법 (추천)
```cmd
# 1. 프로젝트 폴더로 이동
cd 폴더경로

# 2. 배치 파일 실행 (자동 설치 + 실행)
run_macro.bat
```

### 2️⃣ 수동 설치 방법
```cmd
# 1. Python 설치 확인
python --version

# 2. 필수 패키지 설치
pip install -r requirements.txt

# 3. 프로그램 실행
python gui_macro.py
```

## 🔧 문제 해결

### Python이 인식되지 않을 때
```cmd
# Python 경로 확인
where python

# py 명령 사용
py --version
py -m pip install pyautogui keyboard
```

### 권한 오류가 발생할 때
```cmd
# 관리자 권한으로 명령 프롬프트 실행 후
pip install pyautogui keyboard pillow

# 또는 사용자 설치
pip install --user pyautogui keyboard pillow
```

### 특정 패키지 설치 실패
```cmd
# keyboard 모듈 오류 시 (관리자 권한 필요)
pip install keyboard

# pyautogui 의존성 오류 시
pip install pillow
pip install pyautogui
```

## 📋 설치 확인

### 패키지 설치 확인
```python
# Python 명령창에서 실행
import pyautogui
import keyboard
print("✅ 모든 패키지 설치 완료!")
```

### 프로그램 실행 확인
```cmd
python gui_macro.py
# GUI가 정상적으로 뜨면 성공!
```

## 💡 추가 정보

- **Python 버전**: 3.8 이상 권장
- **운영체제**: Windows 10/11 (macOS/Linux는 일부 기능 제한)
- **필수 권한**: 관리자 권한 실행 권장
- **네트워크**: 인터넷 연결 필요 (시간 동기화용)
