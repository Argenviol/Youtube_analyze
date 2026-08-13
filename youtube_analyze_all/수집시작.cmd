@echo off
chcp 65001 > nul
setlocal

REM ============================================================
REM  StelLive 동시시청자 수집기 (수동 실행)
REM
REM  이 창이 열려 있는 동안 10분마다 수집합니다.
REM  창을 닫거나 Ctrl+C 를 누르면 멈춥니다.
REM
REM  프로젝트 8(동시시청자)은 소급 수집이 불가능합니다.
REM  이 창이 꺼져 있던 시간은 데이터가 비어 있게 됩니다.
REM ============================================================

set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "ROOT=%~dp0"
set PYTHONIOENCODING=utf-8

if not exist "%PY%" (
  echo [오류] Python 을 찾을 수 없습니다:
  echo        %PY%
  echo.
  pause
  exit /b 1
)

title StelLive 수집기 - 닫으면 수집이 멈춥니다

echo.
echo  StelLive 동시시청자 수집기
echo  ------------------------------------------------------------
echo  10분마다 수집합니다. 멈추려면 이 창을 닫으세요.
echo  수집 중에는 대시보드 데이터도 함께 갱신됩니다.
echo  ------------------------------------------------------------
echo.

cd /d "%ROOT%"
"%PY%" "scripts\refresh.py" --group live --loop 10

echo.
echo  수집이 종료됐습니다.
pause
