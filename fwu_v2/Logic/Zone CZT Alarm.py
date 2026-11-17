engine = ddc_logic()
# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.
CZT_1_FAIL_TIMER = 0
if engine.READPOINT("VP_FWU_CZT_Count") >= 1 and engine.READPOINT("VP_FWU_CZT-1") < 0:
    if engine.SECTIMER(CZT_1_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-1_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_1_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-1_Failure_Alarm", 0)
CZT_2_FAIL_TIMER = 1
if engine.READPOINT("VP_FWU_CZT_Count") >= 2 and engine.READPOINT("VP_FWU_CZT-2") < 0:
    if engine.SECTIMER(CZT_2_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-2_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_2_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-2_Failure_Alarm", 0)
CZT_3_FAIL_TIMER = 2
if engine.READPOINT("VP_FWU_CZT_Count") >= 3 and engine.READPOINT("VP_FWU_CZT-3") < 0:
    if engine.SECTIMER(CZT_3_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-3_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_3_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-3_Failure_Alarm", 0)
CZT_4_FAIL_TIMER = 3
if engine.READPOINT("VP_FWU_CZT_Count") >= 4 and engine.READPOINT("VP_FWU_CZT-4") < 0:
    if engine.SECTIMER(CZT_4_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-4_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_4_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-4_Failure_Alarm", 0)
CZT_5_FAIL_TIMER = 4
if engine.READPOINT("VP_FWU_CZT_Count") >= 5 and engine.READPOINT("VP_FWU_CZT-5") < 0:
    if engine.SECTIMER(CZT_5_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-5_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_5_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-5_Failure_Alarm", 0)
CZT_6_FAIL_TIMER = 5
if engine.READPOINT("VP_FWU_CZT_Count") >= 6 and engine.READPOINT("VP_FWU_CZT-6") < 0:
    if engine.SECTIMER(CZT_6_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-6_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_6_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-6_Failure_Alarm", 0)
CZT_7_FAIL_TIMER = 6
if engine.READPOINT("VP_FWU_CZT_Count") >= 7 and engine.READPOINT("VP_FWU_CZT-7") < 0:
    if engine.SECTIMER(CZT_7_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-7_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_7_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-7_Failure_Alarm", 0)
CZT_8_FAIL_TIMER = 7
if engine.READPOINT("VP_FWU_CZT_Count") >= 8 and engine.READPOINT("VP_FWU_CZT-8") < 0:
    if engine.SECTIMER(CZT_8_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-8_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_8_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-8_Failure_Alarm", 0)
CZT_9_FAIL_TIMER = 8
if engine.READPOINT("VP_FWU_CZT_Count") >= 9 and engine.READPOINT("VP_FWU_CZT-9") < 0:
    if engine.SECTIMER(CZT_9_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-9_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_9_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-9_Failure_Alarm", 0)
CZT_10_FAIL_TIMER = 9
if engine.READPOINT("VP_FWU_CZT_Count") >= 10 and engine.READPOINT("VP_FWU_CZT-10") < 0:
    if engine.SECTIMER(CZT_10_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_CZT-10_Failure_Alarm", 1)
else:
    engine.SECTIMER(CZT_10_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_CZT-10_Failure_Alarm", 0)
# LJH[2026.1117]CZT 센서 10개 고장 감시