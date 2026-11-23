# LJH[2026.1117]기존 Failover 원인과 래치 유지: S ----
# JSY[2026.1123]Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석): S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
FAILOVER_CONFIRM_SECONDS = 5       ## 고장 원인이 5초 넘게 이어져야 Failover로 본다
FAILOVER_RESET_HOLD_SECONDS = 5    ## Reset 입력을 5초 뒤 스스로 되돌린다 (알람 해제 대기 시간이 아님)

## 타이머 정의
FAILOVER_CONFIRM_TIMER = 1    ## Failover 원인이 이어진 시간
FAILOVER_RESET_TIMER = 2      ## Reset 입력이 켜져 있던 시간

## 전역변수 선언
mbFailTotal = FALSE   ## 댐퍼 미개방·전폐, 팬 종합 고장 중 하나라도 있으면 TRUE

## 장치 고장 원인 모으기
## 장치 고장 상태를 상위에 알리는 용도다. 옆 FWU와의 협조 운전은 상위에서 판단한다.
## 개별 PICV 알람과 Damper Signal Alarm의 추가 댐퍼 알람은 Failover 조건에 넣지 않는다.
if engine.READPOINT("VP_FWU_SAD_Not_Open_Alarm") == TRUE or engine.READPOINT("VP_FWU_SAD_Full_Close_Alarm") == TRUE or engine.READPOINT("VP_FWU_SF_Failure_Alarm") == TRUE:
    mbFailTotal = TRUE
else:
    pass  ## do_nothing

## Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다
## 계속 세워 두거나 재기동을 막는 것은 아니고, 더 높은 우선순위의 ON이 있으면 그쪽이 이긴다.
if mbFailTotal == TRUE:
    if engine.SECTIMER(FAILOVER_CONFIRM_TIMER, TMR_READ) > FAILOVER_CONFIRM_SECONDS and engine.READPOINT("VP_FWU_Failover_Alarm") == FALSE:
        engine.WRITEPOINT("VP_FWU_Failover_Alarm", TRUE)
        engine.WRITEPOINT_PRI("VP_FWU_Command", OFF, 11)
        engine.WRITEPOINT_PRI("VP_FWU_Command_HMI", OFF, 11)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(FAILOVER_CONFIRM_TIMER, TMR_CLEAR)

## Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다
## HMI/BMS가 더 높은 우선순위로 Reset을 썼다면 그 입력도 직접 풀어야 한다.
if engine.READPOINT("VP_FWU_Failover_Reset") == TRUE:
    if mbFailTotal == FALSE:
        engine.WRITEPOINT("VP_FWU_Failover_Alarm", FALSE)
    else:
        pass  ## do_nothing
    if engine.SECTIMER(FAILOVER_RESET_TIMER, TMR_READ) > FAILOVER_RESET_HOLD_SECONDS:
        engine.WRITEPOINT_PRI("VP_FWU_Failover_Reset", FALSE, 11)
        engine.SECTIMER(FAILOVER_RESET_TIMER, TMR_CLEAR)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(FAILOVER_RESET_TIMER, TMR_CLEAR)

# JSY[2026.1123]Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]기존 Failover 원인과 래치 유지: E ----
