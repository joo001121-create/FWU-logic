## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의: 
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0

## 타이머 정의: 댐퍼의 unknown delay 대응용
SAD_1_UNKNOWN_TIMER = 0
SAD_2_UNKNOWN_TIMER = 1
SAD_3_UNKNOWN_TIMER = 2
SAD_4_UNKNOWN_TIMER = 3

## 타이머 정의: 댐퍼 상태의 conflict(open과 closed가 동시에 만족) 대응용
SAD_1_CONFLICT_TIMER = 4
SAD_2_CONFLICT_TIMER = 5
SAD_3_CONFLICT_TIMER = 6
SAD_4_CONFLICT_TIMER = 7


## 전역변수 선언
mbSFstat = engine.READPOINT("VP_FWU_SF_Status") == 1	## 모든 SF의 상태가 정상이면 TRUE, 아니면 FALSE (?)
mbSADcmd = engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1	## SAD CMD가 정상이면 TRUE, 아니면 FALSE (?)

## 댐퍼1의 unknown 및 conflict alarm 처리
if mbSFstat and mbSADcmd and engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == FALSE and engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == FALSE:
    if engine.SECTIMER(SAD_1_UNKNOWN_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1_Position_Unknown_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_1_UNKNOWN_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-1_Position_Unknown_Alarm", CLEAR)

if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == TRUE:    
    if engine.SECTIMER(SAD_1_CONFLICT_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1_Signal_Conflict_Alarm", SET)
    else: 
        pass ## do_nothing            
else:
    engine.SECTIMER(SAD_1_CONFLICT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-1_Signal_Conflict_Alarm", CLEAR)

## 댐퍼2의 unknown 및 conflict alarm 처리
if mbSFstat and mbSADcmd and engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == FALSE and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == FALSE:
    if engine.SECTIMER(SAD_2_UNKNOWN_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2_Position_Unknown_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_2_UNKNOWN_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-2_Position_Unknown_Alarm", CLEAR)

if engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == TRUE:
    if engine.SECTIMER(SAD_2_CONFLICT_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2_Signal_Conflict_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_2_CONFLICT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-2_Signal_Conflict_Alarm", CLEAR)

## 댐퍼3의 unknown 및 conflict alarm 처리
if mbSFstat and mbSADcmd and engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == FALSE and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == FALSE:
    if engine.SECTIMER(SAD_3_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3_Position_Unknown_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_3_UNKNOWN_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-3_Position_Unknown_Alarm", CLEAR)

if engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == TRUE:
    if engine.SECTIMER(SAD_3_CONFLICT_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3_Signal_Conflict_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_3_CONFLICT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-3_Signal_Conflict_Alarm", CLEAR)

## 댐퍼4의 unknown 및 conflict alarm 처리
if mbSFstat and mbSADcmd and engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == FALSE and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == FALSE:
    if engine.SECTIMER(SAD_4_UNKNOWN_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4_Position_Unknown_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_4_UNKNOWN_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-4_Position_Unknown_Alarm", CLEAR)

if engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == TRUE:
    if engine.SECTIMER(SAD_4_CONFLICT_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4_Signal_Conflict_Alarm", SET)
    else: 
        pass ## do_nothing
else:
    engine.SECTIMER(SAD_4_CONFLICT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAD-4_Signal_Conflict_Alarm", CLEAR)
# LJH[2026.1117]댐퍼 위치 미확인 및 접점 모순 감시
