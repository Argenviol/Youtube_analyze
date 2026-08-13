<#
.SYNOPSIS
  refresh.py 의 수집 그룹을 Windows 작업 스케줄러에 등록한다.

.DESCRIPTION
  PRD 9절 기준. GitHub Actions 대신 로컬 스케줄러로 자동화한다.
  저장소·시크릿·과금 이슈가 없는 대신 PC가 켜져 있어야 한다.

  ⚠ 프로젝트 8(동시시청자)은 소급 수집이 불가능하다.
     PC가 꺼져 있던 구간은 영구 공백이 되며 나중에 메울 방법이 없다.

.EXAMPLE
  # 무엇이 등록될지 먼저 확인 (아무것도 바꾸지 않음)
  powershell -File scripts/register_tasks.ps1

  # 실제 등록
  powershell -File scripts/register_tasks.ps1 -Apply

  # 등록 해제
  powershell -File scripts/register_tasks.ps1 -Remove -Apply

.NOTES
  - 기본 동작은 dry-run 이다. -Apply 없이는 시스템을 건드리지 않는다.
  - 현재 사용자 계정으로만 등록하므로 관리자 권한이 필요 없다.
  - API 키는 사용자 환경변수(setx)에서 읽으므로 이 스크립트에 담기지 않는다.
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$RefreshScript = Join-Path $RepoRoot 'scripts\refresh.py'
$Prefix = 'StelLiveAnalytics'

# 작업 정의. refresh.py 의 GROUPS 와 일치해야 한다.
#   live    — 10분. 소급 불가라 가장 중요하다.
#   daily   — 01·02·03·06. search.list 를 쓰지 않아 쿼터가 가볍다(~250 units).
#   weekly  — 04·05. search.list 33회 = 3,300 units 라 주 1회로 묶었다.
#   monthly — 09. DART 공시가 분기·연간 단위라 더 자주 돌 이유가 없다.
$Tasks = @(
    @{ Name = "$Prefix-Live";    Group = 'live';    Kind = 'Minutes'; Every = 10 }
    @{ Name = "$Prefix-Daily";   Group = 'daily';   Kind = 'Daily';   At = '05:00' }
    @{ Name = "$Prefix-Weekly";  Group = 'weekly';  Kind = 'Weekly';  At = '05:30'; Day = 'Sunday' }
    @{ Name = "$Prefix-Monthly"; Group = 'monthly'; Kind = 'Monthly'; At = '06:00'; DayOfMonth = 5 }
)

function Test-Prerequisites {
    $problems = @()
    if (-not (Test-Path $Python))        { $problems += "Python 을 찾을 수 없습니다: $Python" }
    if (-not (Test-Path $RefreshScript)) { $problems += "refresh.py 를 찾을 수 없습니다: $RefreshScript" }
    if (-not [Environment]::GetEnvironmentVariable('YOUTUBE_API_KEY', 'User')) {
        $problems += "사용자 환경변수 YOUTUBE_API_KEY 가 없습니다 (daily/weekly 그룹이 실패합니다)"
    }
    return $problems
}

function Show-Plan {
    Write-Host ""
    Write-Host "등록 대상" -ForegroundColor Cyan
    Write-Host ("-" * 62)
    foreach ($t in $Tasks) {
        $when = switch ($t.Kind) {
            'Minutes' { "$($t.Every)분마다" }
            'Daily'   { "매일 $($t.At)" }
            'Weekly'  { "매주 $($t.Day) $($t.At)" }
            'Monthly' { "매월 $($t.DayOfMonth)일 $($t.At)" }
        }
        "{0,-28} {1,-16} refresh.py --group {2}" -f $t.Name, $when, $t.Group | Write-Host
    }
    Write-Host ("-" * 62)
    Write-Host "실행 계정 : $env:USERNAME (관리자 권한 불필요)"
    Write-Host "작업 폴더 : $RepoRoot"
    Write-Host ""
}

function Remove-Tasks {
    foreach ($t in $Tasks) {
        $existing = Get-ScheduledTask -TaskName $t.Name -ErrorAction SilentlyContinue
        if (-not $existing) { Write-Host "  - $($t.Name) : 없음 (건너뜀)"; continue }
        if ($Apply) {
            Unregister-ScheduledTask -TaskName $t.Name -Confirm:$false
            Write-Host "  - $($t.Name) : 제거됨" -ForegroundColor Yellow
        } else {
            Write-Host "  - $($t.Name) : 제거 예정 (dry-run)"
        }
    }
}

function Register-Tasks {
    $failed = @()
    foreach ($t in $Tasks) {
      # 한 작업이 실패해도 나머지는 등록한다. 전부 중단시키면 어느 것이
      # 문제인지 알기 어렵고, 이미 정상인 작업까지 못 올라간다.
      try {
        $action = New-ScheduledTaskAction -Execute $Python `
            -Argument "`"$RefreshScript`" --group $($t.Group)" `
            -WorkingDirectory $RepoRoot

        $trigger = switch ($t.Kind) {
            'Minutes' {
                # 반복 트리거는 만료 없이 무한 반복시킨다.
                #
                # ⚠ -RepetitionDuration ([TimeSpan]::MaxValue) 를 주면 안 된다.
                #   P99999999DT23H59M59S 로 직렬화되는데 작업 스케줄러가 이를
                #   "범위를 벗어난 값"으로 거부한다(HRESULT 0x80041318).
                #   Duration 을 아예 지정하지 않는 것이 곧 "무기한"이다.
                $tr = New-ScheduledTaskTrigger -Once -At (Get-Date)
                $tr.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) `
                    -RepetitionInterval (New-TimeSpan -Minutes $t.Every)).Repetition
                $tr
            }
            'Daily'  { New-ScheduledTaskTrigger -Daily -At $t.At }
            'Weekly' { New-ScheduledTaskTrigger -Weekly -DaysOfWeek $t.Day -At $t.At }
            'Monthly' {
                # New-ScheduledTaskTrigger 에는 -Monthly 가 없다. CIM 클래스로 직접 만든다.
                #   DaysOfMonth : 비트마스크. 1일=bit0 이므로 N일 = 1 shl (N-1)
                #   MonthOfYear : 단수형이다(MonthsOfYear 아님). 0xFFF = 12개월 전부
                $cls = Get-CimClass -ClassName MSFT_TaskMonthlyTrigger `
                    -Namespace Root/Microsoft/Windows/TaskScheduler
                $mt = New-CimInstance -CimClass $cls -ClientOnly
                $mt.DaysOfMonth = [int](1 -shl ($t.DayOfMonth - 1))
                $mt.MonthOfYear = 4095
                $mt.StartBoundary = ([DateTime]::Today.AddDays(1).ToString('yyyy-MM-dd') + 'T' + $t.At + ':00')
                $mt.Enabled = $true
                $mt
            }
        }

        # StartWhenAvailable: PC가 꺼져 있어 놓친 실행을 켜진 직후 한 번 만회한다.
        #   (10분 간격 시계열의 공백 자체를 메워주지는 못한다 — 그건 불가능하다)
        # DontStopOnIdleEnd / 배터리 조건 해제: 노트북에서 조용히 멈추는 걸 막는다.
        $settings = New-ScheduledTaskSettingsSet `
            -StartWhenAvailable `
            -DontStopIfGoingOnBatteries `
            -AllowStartIfOnBatteries `
            -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
            -MultipleInstances IgnoreNew

        if (-not $Apply) {
            Write-Host "  + $($t.Name) : 등록 예정 (dry-run)"
            continue
        }

        # Register-ScheduledTask 에 -Trigger 로 raw CimInstance(월간 트리거)를 넘기면
        # "매개 변수가 틀립니다"로 거부된다. New-ScheduledTask 로 먼저 조립한 뒤
        # -InputObject 로 넘기면 정상 동작한다.
        $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings `
            -Description "StelLive 팬덤 애널리틱스 · $($t.Group) 그룹 수집"
        Register-ScheduledTask -TaskName $t.Name -InputObject $task -Force | Out-Null
        Write-Host "  + $($t.Name) : 등록됨" -ForegroundColor Green
      }
      catch {
        # 월간 트리거는 CIM 경로가 환경에 따라 까다로워서 schtasks.exe 로 폴백한다.
        if ($t.Kind -eq 'Monthly') {
            $tr = '"{0}" "{1}\scripts\refresh.py" --group {2}' -f $Python, $RepoRoot, $t.Group
            $out = & schtasks.exe /Create /TN $t.Name /TR $tr /SC MONTHLY `
                /D $t.DayOfMonth /ST $t.At /F 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  + $($t.Name) : 등록됨 (schtasks 폴백)" -ForegroundColor Green
                continue
            }
            $failed += $t.Name
            Write-Host "  ! $($t.Name) : 등록 실패 — $out" -ForegroundColor Red
            continue
        }
        $failed += $t.Name
        Write-Host "  ! $($t.Name) : 등록 실패 — $($_.Exception.Message)" -ForegroundColor Red
      }
    }

    if ($failed.Count -gt 0) {
        Write-Host ""
        Write-Host "등록되지 않은 작업: $($failed -join ', ')" -ForegroundColor Red
        Write-Host "나머지는 정상 등록됐습니다. 실패한 것만 원인을 확인하세요." -ForegroundColor Red
    }
}

# ---------------------------------------------------------------------------

$problems = Test-Prerequisites
if ($problems.Count -gt 0) {
    Write-Host "사전 조건 미충족:" -ForegroundColor Red
    $problems | ForEach-Object { Write-Host "  · $_" -ForegroundColor Red }
    if (-not $Remove) { exit 1 }
}

Show-Plan

if ($Remove) {
    Write-Host "작업 제거" -ForegroundColor Cyan
    Remove-Tasks
} else {
    Write-Host "작업 등록" -ForegroundColor Cyan
    Register-Tasks
}

Write-Host ""
if ($Apply) {
    Write-Host "완료. 확인: Get-ScheduledTask -TaskName '$Prefix-*'"
    if (-not $Remove) {
        Write-Host ""
        Write-Host "⚠ PC가 꺼져 있는 동안 프로젝트 8(동시시청자)은 수집되지 않고," -ForegroundColor Yellow
        Write-Host "  그 구간은 소급이 불가능해 영구 공백으로 남습니다." -ForegroundColor Yellow
        Write-Host "  설정 → 시스템 → 전원 및 배터리 에서 절전을 '안 함'으로 두는 것을 권장합니다." -ForegroundColor Yellow
    }
} else {
    Write-Host "dry-run 이었습니다. 실제로 적용하려면 -Apply 를 붙이세요." -ForegroundColor Yellow
}
