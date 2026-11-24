## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
RDP_FAIL_TIME_OUT = 20  ## RDP Timer는 20초 까지
RDP_FAIL_DP = 0         ## RDP차압이 0Pa 이하이면 fail로 간주
INST_RDP_QTY = engine.READPOINT("VP_FWU_RDP_Count") ## 설치된 RDP차압센서 갯수(Quantity)

## 타이머 정의
RDP_1_FAIL_TIMER = 0
RDP_2_FAIL_TIMER = 1
RDP_3_FAIL_TIMER = 2
RDP_4_FAIL_TIMER = 3
RDP_5_FAIL_TIMER = 4
RDP_6_FAIL_TIMER = 5
RDP_7_FAIL_TIMER = 6
RDP_8_FAIL_TIMER = 7
RDP_9_FAIL_TIMER = 8
RDP_10_FAIL_TIMER = 9

# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.

## RDP-1 check
if INST_RDP_QTY >= 1 and engine.READPOINT("VP_FWU_RDP-1") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_1_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-1_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_1_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-1_Failure_Alarm", FALSE)

## RDP-2 check
if INST_RDP_QTY >= 2 and engine.READPOINT("VP_FWU_RDP-2") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_2_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-2_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_2_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-2_Failure_Alarm", FALSE)

## RDP-3 check
if INST_RDP_QTY >= 3 and engine.READPOINT("VP_FWU_RDP-3") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_3_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-3_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_3_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-3_Failure_Alarm", FALSE)

## RDP-4 check
if INST_RDP_QTY >= 4 and engine.READPOINT("VP_FWU_RDP-4") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_4_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-4_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_4_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-4_Failure_Alarm", FALSE)

## RDP-5 check
if INST_RDP_QTY >= 5 and engine.READPOINT("VP_FWU_RDP-5") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_5_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-5_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_5_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-5_Failure_Alarm", FALSE)

## RDP-6 check
if INST_RDP_QTY >= 6 and engine.READPOINT("VP_FWU_RDP-6") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_6_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-6_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_6_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-6_Failure_Alarm", FALSE)

## RDP-7 check
if INST_RDP_QTY >= 7 and engine.READPOINT("VP_FWU_RDP-7") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_7_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-7_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_7_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-7_Failure_Alarm", FALSE)

## RDP-8 check
if INST_RDP_QTY >= 8 and engine.READPOINT("VP_FWU_RDP-8") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_8_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-8_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_8_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-8_Failure_Alarm", FALSE)

## RDP-9 check
if INST_RDP_QTY >= 9 and engine.READPOINT("VP_FWU_RDP-9") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_9_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-9_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_9_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-9_Failure_Alarm", FALSE)

## RDP-10 check
if INST_RDP_QTY >= 10 and engine.READPOINT("VP_FWU_RDP-10") <= RDP_FAIL_DP:
    if engine.SECTIMER(RDP_10_FAIL_TIMER, TMR_READ) > RDP_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_RDP-10_Failure_Alarm", TRUE)
else:
    engine.SECTIMER(RDP_10_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RDP-10_Failure_Alarm", FALSE)
# LJH[2026.1117]RDP 센서 10개 고장 감시