# LJH[2026.1117]상위 감시와 외부 센서 집계: S ----
SF_STATUS_TIMER = 5
UPPER_HEARTBEAT_TIMER = 6
UPPER_RESET_TIMER = 7
engine = ddc_logic()
# 상위가 없는 모델은 감시를 끄고 Local 고정속도/RAT/ΔT를 사용한다.
# 감시를 끄면 외부 온도·차압은 제어 입력으로 쓰지 않는다.
b_upper_enabled = engine.READPOINT("VP_FWU_Upper_Comm_Enable") == 1
heartbeat = engine.READPOINT("VP_FWU_BMS_PLC_Heartbeat")
b_hb_ok = 0
if not b_upper_enabled:
    engine.SECTIMER(UPPER_HEARTBEAT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", heartbeat)
    engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", 0)
else:
    if engine.READPOINT("VP_FWU_Upper_Comm_Enable_Prev") != 1:
        engine.SECTIMER(UPPER_HEARTBEAT_TIMER, 0)
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", heartbeat)
    if heartbeat != engine.READPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev"):
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", heartbeat)
        engine.SECTIMER(UPPER_HEARTBEAT_TIMER, 0)
        b_hb_ok = 1
    else:
        if engine.SECTIMER(UPPER_HEARTBEAT_TIMER, 1) > engine.READPOINT("VP_FWU_Upper_Comm_Timeout"):
            engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", 1)
        else:
            b_hb_ok = 1
engine.WRITEPOINT("VP_FWU_Upper_Comm_Enable_Prev", b_upper_enabled)
if engine.READPOINT("VP_FWU_BMS_PLC_Comm_Reset") == 1:
    if b_hb_ok == 1:
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", 0)
    if engine.SECTIMER(UPPER_RESET_TIMER, 1) > 5:
        engine.WRITEPOINT_PRI("VP_FWU_BMS_PLC_Comm_Reset", 0, 11)
        engine.SECTIMER(UPPER_RESET_TIMER, 0)
else:
    engine.SECTIMER(UPPER_RESET_TIMER, 0)
b_upper_ok = b_upper_enabled and engine.READPOINT("VP_FWU_BMS_PLC_Comm_Fault") == 0
# 사용 개수는 0~10 정수. 상위 대표값 하나를 받으면 사용 개수를 1로 설정.
czt_count = 0
czt_sum = 0
czt_max = -1000
czt_min = 1000
if engine.READPOINT("VP_FWU_CZT_Count") >= 1 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-1_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-1")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 2 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-2_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-2")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 3 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-3_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-3")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 4 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-4_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-4")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 5 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-5_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-5")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 6 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-6_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-6")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 7 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-7_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-7")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 8 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-8_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-8")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 9 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-9_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-9")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if engine.READPOINT("VP_FWU_CZT_Count") >= 10 and b_upper_ok and engine.READPOINT("VP_FWU_CZT-10_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_CZT-10")
    czt_count = czt_count + 1
    czt_sum = czt_sum + sensor_value
    czt_max = engine.MAX(czt_max, sensor_value)
    czt_min = engine.MIN(czt_min, sensor_value)
if czt_count > 0:
    engine.WRITEPOINT("VP_FWU_CZT_Avg", czt_sum / czt_count)
    engine.WRITEPOINT("VP_FWU_CZT_Max", czt_max)
    engine.WRITEPOINT("VP_FWU_CZT_Min", czt_min)
    engine.WRITEPOINT("VP_FWU_CZT_PV_Valid", 1)
else:
    engine.WRITEPOINT("VP_FWU_CZT_Avg", 0)
    engine.WRITEPOINT("VP_FWU_CZT_Max", 0)
    engine.WRITEPOINT("VP_FWU_CZT_Min", 0)
    engine.WRITEPOINT("VP_FWU_CZT_PV_Valid", 0)
if engine.READPOINT("VP_FWU_CZT_PV_Valid") == 1:
    if engine.READPOINT("VP_FWU_CZT_Select") == 0:
        engine.WRITEPOINT("VP_FWU_CZT_PV", engine.READPOINT("VP_FWU_CZT_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_CZT_PV", engine.READPOINT("VP_FWU_CZT_Max"))
else:
    engine.WRITEPOINT("VP_FWU_CZT_PV", 0)
hzt_count = 0
hzt_sum = 0
hzt_max = -1000
hzt_min = 1000
if engine.READPOINT("VP_FWU_HZT_Count") >= 1 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-1_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-1")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 2 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-2_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-2")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 3 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-3_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-3")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 4 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-4_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-4")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 5 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-5_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-5")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 6 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-6_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-6")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 7 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-7_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-7")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 8 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-8_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-8")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 9 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-9_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-9")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if engine.READPOINT("VP_FWU_HZT_Count") >= 10 and b_upper_ok and engine.READPOINT("VP_FWU_HZT-10_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_HZT-10")
    hzt_count = hzt_count + 1
    hzt_sum = hzt_sum + sensor_value
    hzt_max = engine.MAX(hzt_max, sensor_value)
    hzt_min = engine.MIN(hzt_min, sensor_value)
if hzt_count > 0:
    engine.WRITEPOINT("VP_FWU_HZT_Avg", hzt_sum / hzt_count)
    engine.WRITEPOINT("VP_FWU_HZT_Max", hzt_max)
    engine.WRITEPOINT("VP_FWU_HZT_Min", hzt_min)
    engine.WRITEPOINT("VP_FWU_HZT_PV_Valid", 1)
else:
    engine.WRITEPOINT("VP_FWU_HZT_Avg", 0)
    engine.WRITEPOINT("VP_FWU_HZT_Max", 0)
    engine.WRITEPOINT("VP_FWU_HZT_Min", 0)
    engine.WRITEPOINT("VP_FWU_HZT_PV_Valid", 0)
if engine.READPOINT("VP_FWU_HZT_PV_Valid") == 1:
    if engine.READPOINT("VP_FWU_HZT_Select") == 0:
        engine.WRITEPOINT("VP_FWU_HZT_PV", engine.READPOINT("VP_FWU_HZT_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_HZT_PV", engine.READPOINT("VP_FWU_HZT_Max"))
else:
    engine.WRITEPOINT("VP_FWU_HZT_PV", 0)
rdp_count = 0
rdp_sum = 0
rdp_max = -1000
rdp_min = 1000
if engine.READPOINT("VP_FWU_RDP_Count") >= 1 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-1_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-1")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 2 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-2_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-2")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 3 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-3_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-3")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 4 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-4_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-4")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 5 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-5_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-5")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 6 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-6_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-6")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 7 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-7_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-7")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 8 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-8_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-8")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 9 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-9_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-9")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if engine.READPOINT("VP_FWU_RDP_Count") >= 10 and b_upper_ok and engine.READPOINT("VP_FWU_RDP-10_Failure_Alarm") == 0:
    sensor_value = engine.READPOINT("VP_FWU_RDP-10")
    rdp_count = rdp_count + 1
    rdp_sum = rdp_sum + sensor_value
    rdp_max = engine.MAX(rdp_max, sensor_value)
    rdp_min = engine.MIN(rdp_min, sensor_value)
if rdp_count > 0:
    engine.WRITEPOINT("VP_FWU_RDP_Avg", rdp_sum / rdp_count)
    engine.WRITEPOINT("VP_FWU_RDP_Max", rdp_max)
    engine.WRITEPOINT("VP_FWU_RDP_Min", rdp_min)
    engine.WRITEPOINT("VP_FWU_RDP_PV_Valid", 1)
else:
    engine.WRITEPOINT("VP_FWU_RDP_Avg", 0)
    engine.WRITEPOINT("VP_FWU_RDP_Max", 0)
    engine.WRITEPOINT("VP_FWU_RDP_Min", 0)
    engine.WRITEPOINT("VP_FWU_RDP_PV_Valid", 0)
if engine.READPOINT("VP_FWU_RDP_PV_Valid") == 1:
    if engine.READPOINT("VP_FWU_RDP_Select") == 0:
        engine.WRITEPOINT("VP_FWU_RDP_PV", engine.READPOINT("VP_FWU_RDP_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_RDP_PV", engine.READPOINT("VP_FWU_RDP_Min"))
else:
    engine.WRITEPOINT("VP_FWU_RDP_PV", 0)
czh_count = 0
czh_sum = 0
czh_max = -1000
czh_min = 1000
if engine.READPOINT("VP_FWU_CZH_Count") >= 1:
    sensor_value = engine.READPOINT("VP_FWU_CZH-1")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 2:
    sensor_value = engine.READPOINT("VP_FWU_CZH-2")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 3:
    sensor_value = engine.READPOINT("VP_FWU_CZH-3")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 4:
    sensor_value = engine.READPOINT("VP_FWU_CZH-4")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 5:
    sensor_value = engine.READPOINT("VP_FWU_CZH-5")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 6:
    sensor_value = engine.READPOINT("VP_FWU_CZH-6")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 7:
    sensor_value = engine.READPOINT("VP_FWU_CZH-7")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 8:
    sensor_value = engine.READPOINT("VP_FWU_CZH-8")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 9:
    sensor_value = engine.READPOINT("VP_FWU_CZH-9")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if engine.READPOINT("VP_FWU_CZH_Count") >= 10:
    sensor_value = engine.READPOINT("VP_FWU_CZH-10")
    czh_count = czh_count + 1
    czh_sum = czh_sum + sensor_value
    czh_max = engine.MAX(czh_max, sensor_value)
    czh_min = engine.MIN(czh_min, sensor_value)
if czh_count > 0:
    engine.WRITEPOINT("VP_FWU_CZH_Avg", czh_sum / czh_count)
    engine.WRITEPOINT("VP_FWU_CZH_Max", czh_max)
    engine.WRITEPOINT("VP_FWU_CZH_Min", czh_min)
else:
    engine.WRITEPOINT("VP_FWU_CZH_Avg", 0)
    engine.WRITEPOINT("VP_FWU_CZH_Max", 0)
    engine.WRITEPOINT("VP_FWU_CZH_Min", 0)
# 팬 수는 F8 기준 고정. F4/F6는 팬별 입출력과 고장 집계를 함께 변경한다.
# 풍량 계수·정격 RPM·운전 차압은 새 팬 제원으로 팬 개발팀 확인 필요.
# FMS 1대로 개별 팬 풍량은 확인할 수 없다. QTS 수준은 팬별 감지 입력 추가 검토.
# 공통 차압 대체 판정은 다른 팬이 만든 차압으로 정지 팬을 구분하지 못할 수 있다.
engine.WRITEPOINT("VP_FWU_DeltaT_PV", engine.READPOINT("FWU_RAT") - engine.READPOINT("FWU_SAT"))

b_sf_1_comm_fault = engine.READPOINT("VP_FWU_SF-1_Comm_Fault")
b_sf_2_comm_fault = engine.READPOINT("VP_FWU_SF-2_Comm_Fault")
b_sf_3_comm_fault = engine.READPOINT("VP_FWU_SF-3_Comm_Fault")
b_sf_4_comm_fault = engine.READPOINT("VP_FWU_SF-4_Comm_Fault")
b_sf_5_comm_fault = engine.READPOINT("VP_FWU_SF-5_Comm_Fault")
b_sf_6_comm_fault = engine.READPOINT("VP_FWU_SF-6_Comm_Fault")
b_sf_7_comm_fault = engine.READPOINT("VP_FWU_SF-7_Comm_Fault")
b_sf_8_comm_fault = engine.READPOINT("VP_FWU_SF-8_Comm_Fault")

fail_rpm = engine.READPOINT("VP_FWU_SF_Failure_RPM_Set")
saflow_dp = engine.READPOINT("FWU_SAFLOW_DP")
run_dp = engine.READPOINT("VP_FWU_SF_Run_DP_Set")
b_sf_run = 0

if b_sf_1_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-1.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_2_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-2.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_3_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-3.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_4_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-4.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_5_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-5.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_6_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-6.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_7_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-7.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_8_comm_fault == 1 :
    if saflow_dp > run_dp :
        b_sf_run = 1
else :
    if engine.READPOINT("FWU_SF-8.Current_RPM") >= fail_rpm :
        b_sf_run = 1

if b_sf_run != engine.READPOINT("VP_FWU_SF_Status") :
    if engine.SECTIMER(SF_STATUS_TIMER, 1) > 5 :
        engine.WRITEPOINT("VP_FWU_SF_Status", b_sf_run)
        engine.SECTIMER(SF_STATUS_TIMER, 0)
else :
    engine.SECTIMER(SF_STATUS_TIMER, 0)

if engine.READPOINT("VP_FWU_SF_Status") == 1 and engine.READPOINT("FWU_SAFLOW_DP") >= 5 :
    sa_flow = engine.READPOINT("VP_FWU_SA_Flow_Coef") * engine.READPOINT("FWU_SAFLOW_DP") ** 0.5 * engine.READPOINT("VP_FWU_SAF_VA-2")
    engine.WRITEPOINT("VP_FWU_SA_Flow", sa_flow)
else :
    engine.WRITEPOINT("VP_FWU_SA_Flow", 0)

if engine.READPOINT("REMOTE_SELECTION") == 1 :
    engine.RELEASE_PRI("VP_FWU_Command", 5)
    engine.WRITEPOINT("VP_FWU_Command-HMI", engine.READPOINT("VP_FWU_Command"))
    engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", engine.READPOINT("VP_FWU_Command"), 11)
else :
    engine.RELEASE_PRI("VP_FWU_Command-HMI", 5)
    engine.WRITEPOINT("VP_FWU_Command", engine.READPOINT("VP_FWU_Command-HMI"))
    engine.WRITEPOINT_PRI("VP_FWU_Command", engine.READPOINT("VP_FWU_Command-HMI"), 11)

engine.WRITEPOINT("VP_FWU_SF_Max_RPM", engine.MIN(engine.READPOINT("VP_FWU_SF_Design_RPM") * engine.READPOINT("VP_FWU_SF_Max_RPM_Ratio") / 100, engine.READPOINT("VP_FWU_SF_Rated_Max_RPM")))
# LJH[2026.1117]상위 감시와 외부 센서 집계: E ----
