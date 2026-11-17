engine = ddc_logic()
# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.
HZT_1_FAIL_TIMER = 0
if engine.READPOINT("VP_FWU_HZT_Count") >= 1 and engine.READPOINT("VP_FWU_HZT-1") < 0:
    if engine.SECTIMER(HZT_1_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-1_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_1_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-1_Failure_Alarm", 0)
HZT_2_FAIL_TIMER = 1
if engine.READPOINT("VP_FWU_HZT_Count") >= 2 and engine.READPOINT("VP_FWU_HZT-2") < 0:
    if engine.SECTIMER(HZT_2_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-2_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_2_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-2_Failure_Alarm", 0)
HZT_3_FAIL_TIMER = 2
if engine.READPOINT("VP_FWU_HZT_Count") >= 3 and engine.READPOINT("VP_FWU_HZT-3") < 0:
    if engine.SECTIMER(HZT_3_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-3_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_3_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-3_Failure_Alarm", 0)
HZT_4_FAIL_TIMER = 3
if engine.READPOINT("VP_FWU_HZT_Count") >= 4 and engine.READPOINT("VP_FWU_HZT-4") < 0:
    if engine.SECTIMER(HZT_4_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-4_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_4_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-4_Failure_Alarm", 0)
HZT_5_FAIL_TIMER = 4
if engine.READPOINT("VP_FWU_HZT_Count") >= 5 and engine.READPOINT("VP_FWU_HZT-5") < 0:
    if engine.SECTIMER(HZT_5_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-5_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_5_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-5_Failure_Alarm", 0)
HZT_6_FAIL_TIMER = 5
if engine.READPOINT("VP_FWU_HZT_Count") >= 6 and engine.READPOINT("VP_FWU_HZT-6") < 0:
    if engine.SECTIMER(HZT_6_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-6_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_6_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-6_Failure_Alarm", 0)
HZT_7_FAIL_TIMER = 6
if engine.READPOINT("VP_FWU_HZT_Count") >= 7 and engine.READPOINT("VP_FWU_HZT-7") < 0:
    if engine.SECTIMER(HZT_7_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-7_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_7_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-7_Failure_Alarm", 0)
HZT_8_FAIL_TIMER = 7
if engine.READPOINT("VP_FWU_HZT_Count") >= 8 and engine.READPOINT("VP_FWU_HZT-8") < 0:
    if engine.SECTIMER(HZT_8_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-8_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_8_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-8_Failure_Alarm", 0)
HZT_9_FAIL_TIMER = 8
if engine.READPOINT("VP_FWU_HZT_Count") >= 9 and engine.READPOINT("VP_FWU_HZT-9") < 0:
    if engine.SECTIMER(HZT_9_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-9_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_9_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-9_Failure_Alarm", 0)
HZT_10_FAIL_TIMER = 9
if engine.READPOINT("VP_FWU_HZT_Count") >= 10 and engine.READPOINT("VP_FWU_HZT-10") < 0:
    if engine.SECTIMER(HZT_10_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_HZT-10_Failure_Alarm", 1)
else:
    engine.SECTIMER(HZT_10_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_HZT-10_Failure_Alarm", 0)
# LJH[2026.1117]HZT 센서 10개 고장 감시
