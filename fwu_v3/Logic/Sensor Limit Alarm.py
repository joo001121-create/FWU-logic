# JSY[2026.1123]Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용: S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
LIMIT_START_SECONDS = 300          ## 팬이 돈 뒤 300초 동안은 상·하한 알람을 보지 않는다 (기동 직후 흔들림)
SENSOR_FAIL_CONFIRM_SECONDS = 20   ## 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장
FMS_FAIL_CONFIRM_SECONDS = 20      ## 팬은 도는데 차압이 낮은 상태가 20초 넘게 이어지면 FMS 고장
TEMPERATURE_VALID_MIN = 0          ## 온도가 0℃ 미만이면 측정값을 믿지 않는다
HUMIDITY_VALID_MIN = 5             ## 습도가 5% 미만이면 측정값을 믿지 않는다
PRESSURE_HYSTERESIS = 0.5          ## 차압 알람 해제 폭 (Pa)
TEMPERATURE_HYSTERESIS = 0.5       ## 온도 알람 해제 폭 (℃)
HUMIDITY_HYSTERESIS = 5            ## 습도 알람 해제 폭 (%)

## 타이머 정의 (번호는 Alarm-1에서 쓰던 그대로)
LIMIT_TIMER = 0       ## 팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연)
SAT_FAIL_TIMER = 2    ## SAT 값이 유효 범위 밖에 있던 시간
SAH_FAIL_TIMER = 3    ## SAH 값이 유효 범위 밖에 있던 시간
RAT_FAIL_TIMER = 4    ## RAT 값이 유효 범위 밖에 있던 시간
RAH_FAIL_TIMER = 5    ## RAH 값이 유효 범위 밖에 있던 시간
SAF_FAIL_TIMER = 6    ## 팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단)

## 전역변수 선언: 내부 센서값을 믿을 수 있는지
mbRATValid = engine.READPOINT("FWU_RAT") >= TEMPERATURE_VALID_MIN
mbRAHValid = engine.READPOINT("FWU_RAH") >= HUMIDITY_VALID_MIN
mbSATValid = engine.READPOINT("FWU_SAT") >= TEMPERATURE_VALID_MIN
mbSAHValid = engine.READPOINT("FWU_SAH") >= HUMIDITY_VALID_MIN

## 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다
## HMI에서도 이 구간은 정상 측정으로 보이지 않게 할 것
if mbRATValid == TRUE:
    pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", FALSE)

if mbRAHValid == TRUE:
    pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", FALSE)

if mbSATValid == TRUE:
    pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", FALSE)

if mbSAHValid == TRUE:
    pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", FALSE)

## 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다
if engine.READPOINT("VP_FWU_SF_Status") == ON and engine.SECTIMER(LIMIT_TIMER, TMR_READ) > LIMIT_START_SECONDS:
    if mbRATValid == TRUE:
        if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", FALSE)
        else:
            pass  ## do_nothing

        if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        pass  ## do_nothing

    if mbRAHValid == TRUE:
        if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH_High_Alarm_SP") - HUMIDITY_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", FALSE)
        else:
            pass  ## do_nothing

        if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH_Low_Alarm_SP") + HUMIDITY_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        pass  ## do_nothing

    if mbSATValid == TRUE:
        if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", FALSE)
        else:
            pass  ## do_nothing

        if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        pass  ## do_nothing

    if mbSAHValid == TRUE:
        if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH_High_Alarm_SP") - HUMIDITY_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", FALSE)
        else:
            pass  ## do_nothing

        if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH_Low_Alarm_SP") + HUMIDITY_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        pass  ## do_nothing

    ## CZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다
    if engine.READPOINT("VP_FWU_CZT_PV_Valid") == TRUE:
        if engine.READPOINT("VP_FWU_CZT_Max") > engine.READPOINT("VP_FWU_CZT_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_CZT_Max") < engine.READPOINT("VP_FWU_CZT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", FALSE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_CZT_Min") < engine.READPOINT("VP_FWU_CZT_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_CZT_Min") > engine.READPOINT("VP_FWU_CZT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", FALSE)
        engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", FALSE)

    ## HZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다
    if engine.READPOINT("VP_FWU_HZT_PV_Valid") == TRUE:
        if engine.READPOINT("VP_FWU_HZT_Max") > engine.READPOINT("VP_FWU_HZT_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_HZT_Max") < engine.READPOINT("VP_FWU_HZT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", FALSE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_HZT_Min") < engine.READPOINT("VP_FWU_HZT_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_HZT_Min") > engine.READPOINT("VP_FWU_HZT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", FALSE)
        engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", FALSE)

    ## RDP: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다
    if engine.READPOINT("VP_FWU_RDP_PV_Valid") == TRUE:
        if engine.READPOINT("VP_FWU_RDP_Max") > engine.READPOINT("VP_FWU_RDP_High_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_RDP_Max") < engine.READPOINT("VP_FWU_RDP_High_Alarm_SP") - PRESSURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", FALSE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_RDP_Min") < engine.READPOINT("VP_FWU_RDP_Low_Alarm_SP"):
            engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", TRUE)
        else:
            pass  ## do_nothing
        if engine.READPOINT("VP_FWU_RDP_Min") > engine.READPOINT("VP_FWU_RDP_Low_Alarm_SP") + PRESSURE_HYSTERESIS:
            engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", FALSE)
        else:
            pass  ## do_nothing
    else:
        engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", FALSE)
        engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", FALSE)

else:
    pass  ## do_nothing

## 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다
if engine.READPOINT("VP_FWU_SF_Status") == OFF:
    engine.SECTIMER(LIMIT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", FALSE)
else:
    pass  ## do_nothing

## 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장
if mbSATValid == TRUE:
    engine.SECTIMER(SAT_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAT_Failure_Alarm", FALSE)
else:
    if engine.SECTIMER(SAT_FAIL_TIMER, TMR_READ) > SENSOR_FAIL_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SAT_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing

if mbSAHValid == TRUE:
    engine.SECTIMER(SAH_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAH_Failure_Alarm", FALSE)
else:
    if engine.SECTIMER(SAH_FAIL_TIMER, TMR_READ) > SENSOR_FAIL_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SAH_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing

if mbRATValid == TRUE:
    engine.SECTIMER(RAT_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RAT_Failure_Alarm", FALSE)
else:
    if engine.SECTIMER(RAT_FAIL_TIMER, TMR_READ) > SENSOR_FAIL_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_RAT_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing

if mbRAHValid == TRUE:
    engine.SECTIMER(RAH_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_RAH_Failure_Alarm", FALSE)
else:
    if engine.SECTIMER(RAH_FAIL_TIMER, TMR_READ) > SENSOR_FAIL_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_RAH_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing

## FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다
## RPM과 차압이 안 맞는 것만 보는 것이라, 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다
## (engine.MAX는 인자를 5개까지만 받아서 팬 1~4, 5~8로 나눠 구한 뒤 다시 비교한다)
if engine.READPOINT("FWU_SAFLOW_DP") < engine.READPOINT("VP_FWU_SAF_Fail_DP_Set") and engine.MAX(engine.MAX(engine.READPOINT("FWU_SF-1.Current_RPM"), engine.READPOINT("FWU_SF-2.Current_RPM"), engine.READPOINT("FWU_SF-3.Current_RPM"), engine.READPOINT("FWU_SF-4.Current_RPM")), engine.MAX(engine.READPOINT("FWU_SF-5.Current_RPM"), engine.READPOINT("FWU_SF-6.Current_RPM"), engine.READPOINT("FWU_SF-7.Current_RPM"), engine.READPOINT("FWU_SF-8.Current_RPM"))) > engine.READPOINT("VP_FWU_SAF_Fail_RPM_Set"):
    if engine.SECTIMER(SAF_FAIL_TIMER, TMR_READ) > FMS_FAIL_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SAF_Failure_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(SAF_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SAF_Failure_Alarm", FALSE)

# JSY[2026.1123]Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용: E ----
# LJH[2026.1117]내부 센서 유효성 및 팬·댐퍼 알람
