# JSY[2026.1123]Alarm-2에서 이름 변경(누수·필터 알람만 남아 내용에 맞춤), Coding Rule 적용: S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
LEAK_CONFIRM_SECONDS = 5       ## 누수 신호가 5초 넘게 이어지면 알람
FILTER_CONFIRM_SECONDS = 30    ## 필터 차압 스위치가 30초 넘게 켜져 있으면 알람

## 타이머 정의 (번호는 Alarm-2에서 쓰던 그대로)
LEAK_TIMER = 8      ## 누수 신호가 이어진 시간
FILTER_TIMER = 9    ## 필터 차압 스위치가 켜져 있던 시간

## 누수 알람: 알람만 내고 장비는 세우지 않는다 (QTS: 누수가 있어도 정지하면 안 됨)
# 누수 입력 DI는 IO.xml CPU00-DI1에 등록(2026-11-24, 제안 단자). 배선을 이 단자에 맞추고 접점 극성(1 = 누수) 확인
if engine.READPOINT("FWU_LEAK_DETECT") == TRUE:
    if engine.SECTIMER(LEAK_TIMER, TMR_READ) > LEAK_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_Leak_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(LEAK_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_Leak_Alarm", FALSE)

## 필터 알람
# 필터 알람은 기존대로 입력 ON이 30초를 초과하면 발생하고 OFF 시 해제한다.
# 향후 필터 교체시점 예측 방식 적용 예정(차압 스위치 작동풍량 출원의뢰서 참조).
# OFF->ON 전환 시 풍량을 기록하고, 새 필터/교체 기준 필터의 기준풍량과
# 비교한 막힘 지표 및 운전시간 이력으로 잔여 운전시간을 예측한다.
if engine.READPOINT("FWU_FILTER_ALARM") == TRUE:
    if engine.SECTIMER(FILTER_TIMER, TMR_READ) > FILTER_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_Filter_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(FILTER_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_Filter_Alarm", FALSE)

# JSY[2026.1123]Alarm-2에서 이름 변경(누수·필터 알람만 남아 내용에 맞춤), Coding Rule 적용: E ----
# LJH[2026.1117]센서 알람 분리와 누수 필터 감시 유지
