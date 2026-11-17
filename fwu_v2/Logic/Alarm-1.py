LIMIT_TIMER = 0
FAN_FAIL_TIMER = 1
SAT_FAIL_TIMER = 2
SAH_FAIL_TIMER = 3
RAT_FAIL_TIMER = 4
RAH_FAIL_TIMER = 5
SAF_FAIL_TIMER = 6
SAD_OPEN_TIMER = 7
SAD_CLOSE_TIMER = 8
FAN_COUNT = 8
LIMIT_START_SECONDS = 300
FAN_FAIL_CONFIRM_SECONDS = 60
SENSOR_FAIL_CONFIRM_SECONDS = 20
FMS_FAIL_CONFIRM_SECONDS = 20
DAMPER_TRAVEL_SECONDS = 120
TEMPERATURE_VALID_MIN = 0
HUMIDITY_VALID_MIN = 5
PRESSURE_HYSTERESIS = 0.5
TEMPERATURE_HYSTERESIS = 0.5
HUMIDITY_HYSTERESIS = 5
# F4/F6는 개별 팬 판정과 입출력을 함께 변경. Count VP로 모델을 전환하지 않는다.
engine = ddc_logic()

# 고장 확정 전이라도 무효 측정값으로 고온·저온/고습·저습을 판정하지 않는다.
# HMI에서는 이 구간을 정상 측정으로 표시하지 말 것.
b_rat_valid = engine.READPOINT("FWU_RAT") >= TEMPERATURE_VALID_MIN
if not b_rat_valid :
    engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", 0)
b_rah_valid = engine.READPOINT("FWU_RAH") >= HUMIDITY_VALID_MIN
if not b_rah_valid :
    engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", 0)
b_sat_valid = engine.READPOINT("FWU_SAT") >= TEMPERATURE_VALID_MIN
if not b_sat_valid :
    engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", 0)
b_sah_valid = engine.READPOINT("FWU_SAH") >= HUMIDITY_VALID_MIN
if not b_sah_valid :
    engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", 0)

if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.SECTIMER(LIMIT_TIMER, 1) > LIMIT_START_SECONDS :
    if b_rat_valid :
        if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", 1)
        if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", 0)

        if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", 1)
        if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", 0)

    if b_rah_valid :
        if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", 1)
        if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH_High_Alarm_SP") - HUMIDITY_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", 0)

        if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", 1)
        if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH_Low_Alarm_SP") + HUMIDITY_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", 0)

    if b_sat_valid :
        if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", 1)
        if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", 0)

        if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", 1)
        if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", 0)

    if b_sah_valid :
        if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", 1)
        if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH_High_Alarm_SP") - HUMIDITY_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", 0)

        if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", 1)
        if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH_Low_Alarm_SP") + HUMIDITY_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", 0)

    if engine.READPOINT("VP_FWU_CZT_PV_Valid") == 1 :
        if engine.READPOINT("VP_FWU_CZT_Max") > engine.READPOINT("VP_FWU_CZT_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", 1)
        if engine.READPOINT("VP_FWU_CZT_Max") < engine.READPOINT("VP_FWU_CZT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", 0)
        if engine.READPOINT("VP_FWU_CZT_Min") < engine.READPOINT("VP_FWU_CZT_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", 1)
        if engine.READPOINT("VP_FWU_CZT_Min") > engine.READPOINT("VP_FWU_CZT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", 0)
        engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", 0)

    if engine.READPOINT("VP_FWU_HZT_PV_Valid") == 1 :
        if engine.READPOINT("VP_FWU_HZT_Max") > engine.READPOINT("VP_FWU_HZT_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", 1)
        if engine.READPOINT("VP_FWU_HZT_Max") < engine.READPOINT("VP_FWU_HZT_High_Alarm_SP") - TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", 0)
        if engine.READPOINT("VP_FWU_HZT_Min") < engine.READPOINT("VP_FWU_HZT_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", 1)
        if engine.READPOINT("VP_FWU_HZT_Min") > engine.READPOINT("VP_FWU_HZT_Low_Alarm_SP") + TEMPERATURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", 0)
        engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", 0)

    if engine.READPOINT("VP_FWU_RDP_PV_Valid") == 1 :
        if engine.READPOINT("VP_FWU_RDP_Max") > engine.READPOINT("VP_FWU_RDP_High_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", 1)
        if engine.READPOINT("VP_FWU_RDP_Max") < engine.READPOINT("VP_FWU_RDP_High_Alarm_SP") - PRESSURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", 0)
        if engine.READPOINT("VP_FWU_RDP_Min") < engine.READPOINT("VP_FWU_RDP_Low_Alarm_SP") :
            engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", 1)
        if engine.READPOINT("VP_FWU_RDP_Min") > engine.READPOINT("VP_FWU_RDP_Low_Alarm_SP") + PRESSURE_HYSTERESIS :
            engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", 0)
        engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", 0)

if engine.READPOINT("VP_FWU_SF_Status") == 0 :
    engine.SECTIMER(LIMIT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAT_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAH_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAH_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAT_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAH_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAH_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_CZT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_CZT_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_HZT_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_HZT_Low_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RDP_High_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RDP_Low_Alarm", 0)

if engine.READPOINT("VP_FWU_Command") == 1 and engine.READPOINT("VP_FWU_SF_Speed_Value") >= engine.READPOINT("VP_FWU_SF_Speed_Min") :
    if engine.SECTIMER(FAN_FAIL_TIMER, 1) > FAN_FAIL_CONFIRM_SECONDS :
        fail_rpm = engine.READPOINT("VP_FWU_SF_Failure_RPM_Set")
        b_sf_dp_low = engine.READPOINT("FWU_SAFLOW_DP") <= engine.READPOINT("VP_FWU_SF_Run_DP_Set")

        if engine.READPOINT("VP_FWU_SF-1_Comm_Fault") == 0 :
            b_sf_1_fail = engine.READPOINT("FWU_SF-1.Current_RPM") < fail_rpm
        else :
            b_sf_1_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-2_Comm_Fault") == 0 :
            b_sf_2_fail = engine.READPOINT("FWU_SF-2.Current_RPM") < fail_rpm
        else :
            b_sf_2_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-3_Comm_Fault") == 0 :
            b_sf_3_fail = engine.READPOINT("FWU_SF-3.Current_RPM") < fail_rpm
        else :
            b_sf_3_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-4_Comm_Fault") == 0 :
            b_sf_4_fail = engine.READPOINT("FWU_SF-4.Current_RPM") < fail_rpm
        else :
            b_sf_4_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-5_Comm_Fault") == 0 :
            b_sf_5_fail = engine.READPOINT("FWU_SF-5.Current_RPM") < fail_rpm
        else :
            b_sf_5_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-6_Comm_Fault") == 0 :
            b_sf_6_fail = engine.READPOINT("FWU_SF-6.Current_RPM") < fail_rpm
        else :
            b_sf_6_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-7_Comm_Fault") == 0 :
            b_sf_7_fail = engine.READPOINT("FWU_SF-7.Current_RPM") < fail_rpm
        else :
            b_sf_7_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-8_Comm_Fault") == 0 :
            b_sf_8_fail = engine.READPOINT("FWU_SF-8.Current_RPM") < fail_rpm
        else :
            b_sf_8_fail = b_sf_dp_low

        sf_fail_count = 0
        if b_sf_1_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", 0)
        if b_sf_2_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", 0)
        if b_sf_3_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", 0)
        if b_sf_4_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", 0)
        if b_sf_5_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", 0)
        if b_sf_6_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", 0)
        if b_sf_7_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", 0)
        if b_sf_8_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", 0)

        # 종합 팬 고장 기준은 SMX01의 절반 이상 고장을 임시로 유지한다.
        # 신규 팬의 정압-풍량 곡선과 허용 최대속도를 기준으로, 팬 고장 시에도
        # 요구 정압에서 목표 풍량을 확보할 수 있는 고장 허용 대수를 확인할 것.
        # 확인 결과에 맞춰 아래 종합 고장 대수 기준과 Failover 정지 연계를 재검토한다.
        if sf_fail_count * 2 >= FAN_COUNT :
            engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", 0)
else :
    engine.SECTIMER(FAN_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", 0)

if not b_sat_valid :
    if engine.SECTIMER(SAT_FAIL_TIMER, 1) > SENSOR_FAIL_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SAT_Failure_Alarm", 1)
else :
    engine.SECTIMER(SAT_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAT_Failure_Alarm", 0)

if not b_sah_valid :
    if engine.SECTIMER(SAH_FAIL_TIMER, 1) > SENSOR_FAIL_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SAH_Failure_Alarm", 1)
else :
    engine.SECTIMER(SAH_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAH_Failure_Alarm", 0)

if not b_rat_valid :
    if engine.SECTIMER(RAT_FAIL_TIMER, 1) > SENSOR_FAIL_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_RAT_Failure_Alarm", 1)
else :
    engine.SECTIMER(RAT_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAT_Failure_Alarm", 0)

if not b_rah_valid :
    if engine.SECTIMER(RAH_FAIL_TIMER, 1) > SENSOR_FAIL_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_RAH_Failure_Alarm", 1)
else :
    engine.SECTIMER(RAH_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAH_Failure_Alarm", 0)

# FMS 고장은 RPM과 차압의 불일치로 추정한다. 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다.
if engine.READPOINT("FWU_SAFLOW_DP") < engine.READPOINT("VP_FWU_SAF_Fail_DP_Set") and engine.MAX(engine.MAX(engine.READPOINT("FWU_SF-1.Current_RPM"), engine.READPOINT("FWU_SF-2.Current_RPM"), engine.READPOINT("FWU_SF-3.Current_RPM"), engine.READPOINT("FWU_SF-4.Current_RPM")), engine.MAX(engine.READPOINT("FWU_SF-5.Current_RPM"), engine.READPOINT("FWU_SF-6.Current_RPM"), engine.READPOINT("FWU_SF-7.Current_RPM"), engine.READPOINT("FWU_SF-8.Current_RPM"))) > engine.READPOINT("VP_FWU_SAF_Fail_RPM_Set") :
    if engine.SECTIMER(SAF_FAIL_TIMER, 1) > FMS_FAIL_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SAF_Failure_Alarm", 1)
else :
    engine.SECTIMER(SAF_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAF_Failure_Alarm", 0)

b_sad_all_close = engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == 1
b_sad_any_close = engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == 1 or engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == 1 or engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == 1 or engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == 1
if engine.READPOINT("VP_FWU_SF_Status") == 1 :
    if b_sad_any_close and not b_sad_all_close :
        engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", 1)
    else :
        engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", 0)

if b_sad_all_close and engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and (engine.READPOINT("VP_FWU_SF_Status") == 1 or engine.READPOINT("VP_FWU_SAD_Full_Close_Alarm") == 1) :
    engine.WRITEPOINT("VP_FWU_SAD_Full_Close_Alarm", 1)
else :
    engine.WRITEPOINT("VP_FWU_SAD_Full_Close_Alarm", 0)

if engine.READPOINT("FWU_SAD-1_4_COMMAND") == 1 and engine.READPOINT("VP_FWU_SF_Status") == 0 :
    engine.SECTIMER(SAD_CLOSE_TIMER, 0)
    if engine.SECTIMER(SAD_OPEN_TIMER, 1) > DAMPER_TRAVEL_SECONDS :
        if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") != 1 or engine.READPOINT("FWU_SAD-2_OPEN_STATUS") != 1 or engine.READPOINT("FWU_SAD-3_OPEN_STATUS") != 1 or engine.READPOINT("FWU_SAD-4_OPEN_STATUS") != 1 :
            engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", 0)
    engine.SECTIMER(SAD_OPEN_TIMER, 0)

if engine.READPOINT("FWU_SAD-1_4_COMMAND") == 0 :
    engine.SECTIMER(SAD_OPEN_TIMER, 0)
    if engine.SECTIMER(SAD_CLOSE_TIMER, 1) > DAMPER_TRAVEL_SECONDS :
        if engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") != 1 or engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") != 1 or engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") != 1 or engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") != 1 :
            engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", 0)
    engine.SECTIMER(SAD_CLOSE_TIMER, 0)

# LJH[2026.1117]내부 센서 유효성 및 팬·댐퍼 알람
