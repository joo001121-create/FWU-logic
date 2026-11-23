LEAK_TIMER = 8
FILTER_TIMER = 9
# 누수 입력 DI 주소는 HW 확인 후 연결
LEAK_CONFIRM_SECONDS = 5
FILTER_CONFIRM_SECONDS = 30
engine = ddc_logic()
if engine.READPOINT("FWU_LEAK_DETECT") == 1 :
    if engine.SECTIMER(LEAK_TIMER, 1) > LEAK_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_Leak_Alarm", 1)
else :
    engine.SECTIMER(LEAK_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Leak_Alarm", 0)

# 필터 알람은 기존대로 입력 ON이 30초를 초과하면 발생하고 OFF 시 해제한다.
# 향후 필터 교체시점 예측 방식 적용 예정(차압 스위치 작동풍량 출원의뢰서 참조).
# OFF->ON 전환 시 풍량을 기록하고, 새 필터/교체 기준 필터의 기준풍량과
# 비교한 막힘 지표 및 운전시간 이력으로 잔여 운전시간을 예측한다.
if engine.READPOINT("FWU_FILTER_ALARM") == 1 :
    if engine.SECTIMER(FILTER_TIMER, 1) > FILTER_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_Filter_Alarm", 1)
else :
    engine.SECTIMER(FILTER_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Filter_Alarm", 0)
# LJH[2026.1117]센서 알람 분리와 누수 필터 감시 유지
