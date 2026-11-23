## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
HZT_FAIL_TIME_OUT = 20  ## HZT Timer는 20초 까지
HZT_FAIL_TEMP = 0       ## HZT온도가 0도 미만이면 fail로 간주
INST_HZT_QTY = engine.READPOINT("VP_FWU_HZT_Count") ## 설치된 HZT온도센서 갯수(Quantity)

## 타이머 정의
HZT_1_FAIL_TIMER = 0
HZT_2_FAIL_TIMER = 1
HZT_3_FAIL_TIMER = 2
HZT_4_FAIL_TIMER = 3
HZT_5_FAIL_TIMER = 4
HZT_6_FAIL_TIMER = 5
HZT_7_FAIL_TIMER = 6
HZT_8_FAIL_TIMER = 7
HZT_9_FAIL_TIMER = 8
HZT_10_FAIL_TIMER = 9

# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.

## HZT-1 check
if INST_HZT_QTY >= 1 and engine.READPOINT("VP_FWU_HZT-1") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_1_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-1_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing        
else:
    engine.SECTIMER(HZT_1_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-1_Failure_Alarm", FALSE)

## HZT-2 check
if INST_HZT_QTY >= 2 and engine.READPOINT("VP_FWU_HZT-2") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_2_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-2_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing        
else:
    engine.SECTIMER(HZT_2_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-2_Failure_Alarm", FALSE)

## HZT-3 check
if INST_HZT_QTY >= 3 and engine.READPOINT("VP_FWU_HZT-3") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_3_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-3_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing        
else:    
    engine.SECTIMER(HZT_3_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-3_Failure_Alarm", FALSE)

## HZT-4 check
if INST_HZT_QTY >= 4 and engine.READPOINT("VP_FWU_HZT-4") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_4_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-4_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing        
else:
    engine.SECTIMER(HZT_4_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-4_Failure_Alarm", FALSE)

## HZT-5 check
if INST_HZT_QTY >= 5 and engine.READPOINT("VP_FWU_HZT-5") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_5_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-5_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_5_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-5_Failure_Alarm", FALSE)

## HZT-6 check
if INST_HZT_QTY >= 6 and engine.READPOINT("VP_FWU_HZT-6") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_6_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-6_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_6_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-6_Failure_Alarm", FALSE)

## HZT-7 check
if INST_HZT_QTY >= 7 and engine.READPOINT("VP_FWU_HZT-7") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_7_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-7_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_7_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-7_Failure_Alarm", FALSE)

## HZT-8 check
if INST_HZT_QTY >= 8 and engine.READPOINT("VP_FWU_HZT-8") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_8_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-8_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_8_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-8_Failure_Alarm", FALSE)

## HZT-9 check
if INST_HZT_QTY >= 9 and engine.READPOINT("VP_FWU_HZT-9") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_9_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-9_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_9_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-9_Failure_Alarm", FALSE)

## HZT-10 check
if INST_HZT_QTY >= 10 and engine.READPOINT("VP_FWU_HZT-10") < HZT_FAIL_TEMP:
    if engine.SECTIMER(HZT_10_FAIL_TIMER, TMR_READ) > HZT_FAIL_TIME_OUT:
        engine.WRITEPOINT("VP_FWU_HZT-10_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing                
else:
    engine.SECTIMER(HZT_10_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_HZT-10_Failure_Alarm", FALSE)
# LJH[2026.1117]HZT 센서 10개 고장 감시
