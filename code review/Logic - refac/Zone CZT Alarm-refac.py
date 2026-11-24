## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
CZT_FAIL_TIME_OUT = 20  ## CZT Timer는 20초 까지
CZT_FAIL_TEMP = 0       ## CZT온도가 0도 미만이면 fail로 간주
INST_CZT_QTY = engine.READPOINT("VP_FWU_CZT_Count") ## 설치된 CZT온도센서 갯수(Quantity)

## 타이머 정의
CZT_1_FAIL_TIMER = 0
CZT_2_FAIL_TIMER = 1
CZT_3_FAIL_TIMER = 2
CZT_4_FAIL_TIMER = 3
CZT_5_FAIL_TIMER = 4
CZT_6_FAIL_TIMER = 5
CZT_7_FAIL_TIMER = 6
CZT_8_FAIL_TIMER = 7
CZT_9_FAIL_TIMER = 8
CZT_10_FAIL_TIMER = 9

# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.

## CZT-1 check
if INST_CZT_QTY >= 1 and engine.READPOINT("VP_FWU_CZT-1") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_1_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-1_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_1_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-1_Failure_Alarm", FALSE)

## CZT-2 check
if INST_CZT_QTY >= 2 and engine.READPOINT("VP_FWU_CZT-2") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_2_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-2_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_2_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-2_Failure_Alarm", FALSE)

## CZT-3 check
if INST_CZT_QTY >= 3 and engine.READPOINT("VP_FWU_CZT-3") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_3_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-3_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing        
else:
    engine.SECTIMER(CZT_3_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-3_Failure_Alarm", FALSE)

## CZT-4 check
if INST_CZT_QTY >= 4 and engine.READPOINT("VP_FWU_CZT-4") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_4_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-4_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_4_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-4_Failure_Alarm", FALSE)

## CZT-5 check        
if INST_CZT_QTY >= 5 and engine.READPOINT("VP_FWU_CZT-5") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_5_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-5_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_5_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-5_Failure_Alarm", FALSE)

## CZT-6 check
if INST_CZT_QTY >= 6 and engine.READPOINT("VP_FWU_CZT-6") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_6_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-6_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_6_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-6_Failure_Alarm", FALSE)

## CZT-7 check
if INST_CZT_QTY >= 7 and engine.READPOINT("VP_FWU_CZT-7") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_7_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-7_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_7_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-7_Failure_Alarm", FALSE)

## CZT-8 check
if INST_CZT_QTY >= 8 and engine.READPOINT("VP_FWU_CZT-8") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_8_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-8_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_8_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-8_Failure_Alarm", FALSE)

## CZT-9 check
if INST_CZT_QTY >= 9 and engine.READPOINT("VP_FWU_CZT-9") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_9_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-9_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_9_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-9_Failure_Alarm", FALSE)

## CZT-10 check
if INST_CZT_QTY >= 10 and engine.READPOINT("VP_FWU_CZT-10") < CZT_FAIL_TEMP:
    if engine.SECTIMER(CZT_10_FAIL_TIMER, TMR_READ) > CZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_CZT-10_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(CZT_10_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_CZT-10_Failure_Alarm", FALSE)
# LJH[2026.1117]CZT 센서 10개 고장 감시