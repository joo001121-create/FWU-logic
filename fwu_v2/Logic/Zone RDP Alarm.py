# LJH[2026.1117]RDP 센서 10개 고장 감시: S ----
engine = ddc_logic()
# 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.
RDP_1_FAIL_TIMER = 0
if engine.READPOINT("VP_FWU_RDP_Count") >= 1 and engine.READPOINT("VP_FWU_RDP-1") <= 0:
    if engine.SECTIMER(RDP_1_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-1_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_1_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-1_Failure_Alarm", 0)
RDP_2_FAIL_TIMER = 1
if engine.READPOINT("VP_FWU_RDP_Count") >= 2 and engine.READPOINT("VP_FWU_RDP-2") <= 0:
    if engine.SECTIMER(RDP_2_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-2_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_2_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-2_Failure_Alarm", 0)
RDP_3_FAIL_TIMER = 2
if engine.READPOINT("VP_FWU_RDP_Count") >= 3 and engine.READPOINT("VP_FWU_RDP-3") <= 0:
    if engine.SECTIMER(RDP_3_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-3_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_3_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-3_Failure_Alarm", 0)
RDP_4_FAIL_TIMER = 3
if engine.READPOINT("VP_FWU_RDP_Count") >= 4 and engine.READPOINT("VP_FWU_RDP-4") <= 0:
    if engine.SECTIMER(RDP_4_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-4_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_4_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-4_Failure_Alarm", 0)
RDP_5_FAIL_TIMER = 4
if engine.READPOINT("VP_FWU_RDP_Count") >= 5 and engine.READPOINT("VP_FWU_RDP-5") <= 0:
    if engine.SECTIMER(RDP_5_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-5_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_5_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-5_Failure_Alarm", 0)
RDP_6_FAIL_TIMER = 5
if engine.READPOINT("VP_FWU_RDP_Count") >= 6 and engine.READPOINT("VP_FWU_RDP-6") <= 0:
    if engine.SECTIMER(RDP_6_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-6_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_6_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-6_Failure_Alarm", 0)
RDP_7_FAIL_TIMER = 6
if engine.READPOINT("VP_FWU_RDP_Count") >= 7 and engine.READPOINT("VP_FWU_RDP-7") <= 0:
    if engine.SECTIMER(RDP_7_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-7_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_7_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-7_Failure_Alarm", 0)
RDP_8_FAIL_TIMER = 7
if engine.READPOINT("VP_FWU_RDP_Count") >= 8 and engine.READPOINT("VP_FWU_RDP-8") <= 0:
    if engine.SECTIMER(RDP_8_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-8_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_8_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-8_Failure_Alarm", 0)
RDP_9_FAIL_TIMER = 8
if engine.READPOINT("VP_FWU_RDP_Count") >= 9 and engine.READPOINT("VP_FWU_RDP-9") <= 0:
    if engine.SECTIMER(RDP_9_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-9_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_9_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-9_Failure_Alarm", 0)
RDP_10_FAIL_TIMER = 9
if engine.READPOINT("VP_FWU_RDP_Count") >= 10 and engine.READPOINT("VP_FWU_RDP-10") <= 0:
    if engine.SECTIMER(RDP_10_FAIL_TIMER, 1) > 20:
        engine.WRITEPOINT("VP_FWU_RDP-10_Failure_Alarm", 1)
else:
    engine.SECTIMER(RDP_10_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RDP-10_Failure_Alarm", 0)
# LJH[2026.1117]RDP 센서 10개 고장 감시: E ----
