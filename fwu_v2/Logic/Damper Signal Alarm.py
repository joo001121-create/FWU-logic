# LJH[2026.1117]댐퍼 위치 미확인 및 접점 모순 감시: S ----
engine = ddc_logic()
# 5초는 접점 순간 변화 배제용 임시값. 액추에이터 시험 후 조정.
SAD_1_UNKNOWN_TIMER = 0
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("FWU_SAD-1 OPEN STATUS") == 0 and engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 0:
    if engine.SECTIMER(SAD_1_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Unknown Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1 Position Unknown Alarm", 1)
else:
    engine.SECTIMER(SAD_1_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-1 Position Unknown Alarm", 0)
SAD_1_CONFLICT_TIMER = 4
if engine.READPOINT("FWU_SAD-1 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1:
    if engine.SECTIMER(SAD_1_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Conflict Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1 Signal Conflict Alarm", 1)
else:
    engine.SECTIMER(SAD_1_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-1 Signal Conflict Alarm", 0)
SAD_2_UNKNOWN_TIMER = 1
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("FWU_SAD-2 OPEN STATUS") == 0 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 0:
    if engine.SECTIMER(SAD_2_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Unknown Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2 Position Unknown Alarm", 1)
else:
    engine.SECTIMER(SAD_2_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-2 Position Unknown Alarm", 0)
SAD_2_CONFLICT_TIMER = 5
if engine.READPOINT("FWU_SAD-2 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1:
    if engine.SECTIMER(SAD_2_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Conflict Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2 Signal Conflict Alarm", 1)
else:
    engine.SECTIMER(SAD_2_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-2 Signal Conflict Alarm", 0)
SAD_3_UNKNOWN_TIMER = 2
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("FWU_SAD-3 OPEN STATUS") == 0 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 0:
    if engine.SECTIMER(SAD_3_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Unknown Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3 Position Unknown Alarm", 1)
else:
    engine.SECTIMER(SAD_3_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-3 Position Unknown Alarm", 0)
SAD_3_CONFLICT_TIMER = 6
if engine.READPOINT("FWU_SAD-3 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1:
    if engine.SECTIMER(SAD_3_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Conflict Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3 Signal Conflict Alarm", 1)
else:
    engine.SECTIMER(SAD_3_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-3 Signal Conflict Alarm", 0)
SAD_4_UNKNOWN_TIMER = 3
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("FWU_SAD-4 OPEN STATUS") == 0 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 0:
    if engine.SECTIMER(SAD_4_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Unknown Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4 Position Unknown Alarm", 1)
else:
    engine.SECTIMER(SAD_4_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-4 Position Unknown Alarm", 0)
SAD_4_CONFLICT_TIMER = 7
if engine.READPOINT("FWU_SAD-4 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1:
    if engine.SECTIMER(SAD_4_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD Conflict Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4 Signal Conflict Alarm", 1)
else:
    engine.SECTIMER(SAD_4_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-4 Signal Conflict Alarm", 0)
# LJH[2026.1117]댐퍼 위치 미확인 및 접점 모순 감시: E ----
