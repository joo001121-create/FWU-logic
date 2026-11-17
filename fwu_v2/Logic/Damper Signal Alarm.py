engine = ddc_logic()

SAD_1_UNKNOWN_TIMER = 0
if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == 0 and engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == 0:
    if engine.SECTIMER(SAD_1_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1_Position_Unknown_Alarm", 1)
else:
    engine.SECTIMER(SAD_1_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-1_Position_Unknown_Alarm", 0)
SAD_1_CONFLICT_TIMER = 4
if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == 1:
    if engine.SECTIMER(SAD_1_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-1_Signal_Conflict_Alarm", 1)
else:
    engine.SECTIMER(SAD_1_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-1_Signal_Conflict_Alarm", 0)
SAD_2_UNKNOWN_TIMER = 1
if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == 0 and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == 0:
    if engine.SECTIMER(SAD_2_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2_Position_Unknown_Alarm", 1)
else:
    engine.SECTIMER(SAD_2_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-2_Position_Unknown_Alarm", 0)
SAD_2_CONFLICT_TIMER = 5
if engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == 1:
    if engine.SECTIMER(SAD_2_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-2_Signal_Conflict_Alarm", 1)
else:
    engine.SECTIMER(SAD_2_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-2_Signal_Conflict_Alarm", 0)
SAD_3_UNKNOWN_TIMER = 2
if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == 0 and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == 0:
    if engine.SECTIMER(SAD_3_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3_Position_Unknown_Alarm", 1)
else:
    engine.SECTIMER(SAD_3_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-3_Position_Unknown_Alarm", 0)
SAD_3_CONFLICT_TIMER = 6
if engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == 1:
    if engine.SECTIMER(SAD_3_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-3_Signal_Conflict_Alarm", 1)
else:
    engine.SECTIMER(SAD_3_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-3_Signal_Conflict_Alarm", 0)
SAD_4_UNKNOWN_TIMER = 3
if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == 0 and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == 0:
    if engine.SECTIMER(SAD_4_UNKNOWN_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Unknown_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4_Position_Unknown_Alarm", 1)
else:
    engine.SECTIMER(SAD_4_UNKNOWN_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-4_Position_Unknown_Alarm", 0)
SAD_4_CONFLICT_TIMER = 7
if engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == 1:
    if engine.SECTIMER(SAD_4_CONFLICT_TIMER, 1) > engine.READPOINT("VP_FWU_SAD_Conflict_Delay"):
        engine.WRITEPOINT("VP_FWU_SAD-4_Signal_Conflict_Alarm", 1)
else:
    engine.SECTIMER(SAD_4_CONFLICT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAD-4_Signal_Conflict_Alarm", 0)
# LJH[2026.1117]댐퍼 위치 미확인 및 접점 모순 감시
