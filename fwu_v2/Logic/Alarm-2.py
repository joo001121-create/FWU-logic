# LJH[2026.1117]센서 알람 분리와 누수 필터 감시 유지: S ----
LEAK_TIMER = 8
FILTER_TIMER = 9
# 누수 입력 DI 주소는 HW 확인 후 연결. 외부 센서 고장은 Zone 블록에서 처리.
engine = ddc_logic()
if engine.READPOINT("FWU_LEAK DETECT") == 1 :
    if engine.SECTIMER(LEAK_TIMER, 1) > 5 :
        engine.WRITEPOINT("VP_FWU_Leak Alarm", 1)
else :
    engine.SECTIMER(LEAK_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Leak Alarm", 0)

if engine.READPOINT("FWU_FILTER ALARM") == 1 :
    if engine.SECTIMER(FILTER_TIMER, 1) > 30 :
        engine.WRITEPOINT("VP_FWU_Filter Alarm", 1)
else :
    engine.SECTIMER(FILTER_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Filter Alarm", 0)
# LJH[2026.1117]센서 알람 분리와 누수 필터 감시 유지: E ----
