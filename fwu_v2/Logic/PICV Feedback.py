# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: S ----
engine = ddc_logic()
# CH3에 FWU_PICV-1~4의 Position, Flow, Temperature 통신점을 등록한 뒤 Input_Enable=1로 설정
# 개도는 %, 유량은 L/min, 온도는 냉수 출구 온도(℃)로 환산
b_all_closed = 1
b_monitor_ready = 1
b_any_fault = 0
b_any_comm_fault = 0
PICV_1_DEVIATION_TIMER = 4
b_valid = 0
if engine.READPOINT("VP_FWU_PICV_Input_Enable") == 1:
    if engine.READPOINT_ALARM("FWU_PICV-1.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-1.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-1.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-1_Position", engine.READPOINT("FWU_PICV-1.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-1_Flow", engine.READPOINT("FWU_PICV-1.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-1_Temperature", engine.READPOINT("FWU_PICV-1.Temperature"))
        b_valid = 1
position = engine.READPOINT("VP_FWU_PICV-1_Position")
if not (0 <= position <= 100):
    b_valid = 0
engine.WRITEPOINT("VP_FWU_PICV-1_Feedback_Valid", b_valid)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-1_Comm_Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-1_Alarm", 1)
    engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-1_Comm_Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV_CONTROL") < position + 30):
            if engine.SECTIMER(PICV_1_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled_Water_Supply_Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-1_Flow") < engine.READPOINT("VP_FWU_PICV_No_Flow_Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-1_Flow") > engine.READPOINT("VP_FWU_PICV_Leak_Flow_Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-1_Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-1_Alarm") == 1:
    b_any_fault = 1
PICV_2_DEVIATION_TIMER = 5
b_valid = 0
if engine.READPOINT("VP_FWU_PICV_Input_Enable") == 1:
    if engine.READPOINT_ALARM("FWU_PICV-2.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-2.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-2.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-2_Position", engine.READPOINT("FWU_PICV-2.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-2_Flow", engine.READPOINT("FWU_PICV-2.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-2_Temperature", engine.READPOINT("FWU_PICV-2.Temperature"))
        b_valid = 1
position = engine.READPOINT("VP_FWU_PICV-2_Position")
if not (0 <= position <= 100):
    b_valid = 0
engine.WRITEPOINT("VP_FWU_PICV-2_Feedback_Valid", b_valid)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-2_Comm_Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-2_Alarm", 1)
    engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-2_Comm_Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV_CONTROL") < position + 30):
            if engine.SECTIMER(PICV_2_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled_Water_Supply_Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-2_Flow") < engine.READPOINT("VP_FWU_PICV_No_Flow_Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-2_Flow") > engine.READPOINT("VP_FWU_PICV_Leak_Flow_Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-2_Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-2_Alarm") == 1:
    b_any_fault = 1
PICV_3_DEVIATION_TIMER = 6
b_valid = 0
if engine.READPOINT("VP_FWU_PICV_Input_Enable") == 1:
    if engine.READPOINT_ALARM("FWU_PICV-3.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-3.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-3.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-3_Position", engine.READPOINT("FWU_PICV-3.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-3_Flow", engine.READPOINT("FWU_PICV-3.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-3_Temperature", engine.READPOINT("FWU_PICV-3.Temperature"))
        b_valid = 1
position = engine.READPOINT("VP_FWU_PICV-3_Position")
if not (0 <= position <= 100):
    b_valid = 0
engine.WRITEPOINT("VP_FWU_PICV-3_Feedback_Valid", b_valid)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-3_Comm_Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-3_Alarm", 1)
    engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-3_Comm_Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV_CONTROL") < position + 30):
            if engine.SECTIMER(PICV_3_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled_Water_Supply_Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-3_Flow") < engine.READPOINT("VP_FWU_PICV_No_Flow_Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-3_Flow") > engine.READPOINT("VP_FWU_PICV_Leak_Flow_Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-3_Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-3_Alarm") == 1:
    b_any_fault = 1
PICV_4_DEVIATION_TIMER = 7
b_valid = 0
if engine.READPOINT("VP_FWU_PICV_Input_Enable") == 1:
    if engine.READPOINT_ALARM("FWU_PICV-4.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-4.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-4.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-4_Position", engine.READPOINT("FWU_PICV-4.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-4_Flow", engine.READPOINT("FWU_PICV-4.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-4_Temperature", engine.READPOINT("FWU_PICV-4.Temperature"))
        b_valid = 1
position = engine.READPOINT("VP_FWU_PICV-4_Position")
if not (0 <= position <= 100):
    b_valid = 0
engine.WRITEPOINT("VP_FWU_PICV-4_Feedback_Valid", b_valid)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-4_Comm_Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-4_Alarm", 1)
    engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-4_Comm_Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV_CONTROL") < position + 30):
            if engine.SECTIMER(PICV_4_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled_Water_Supply_Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-4_Flow") < engine.READPOINT("VP_FWU_PICV_No_Flow_Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-4_Flow") > engine.READPOINT("VP_FWU_PICV_Leak_Flow_Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-4_Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-4_Alarm") == 1:
    b_any_fault = 1
if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 0 or engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") != 1:
    b_monitor_ready = 0
engine.WRITEPOINT("VP_FWU_PICV_All_Closed", b_all_closed)
engine.WRITEPOINT("VP_FWU_PICV_Monitor_Ready", b_monitor_ready)
engine.WRITEPOINT("VP_FWU_PICV_Alarm", b_any_fault)
engine.WRITEPOINT("VP_FWU_Flow_Comm_Fault", b_any_comm_fault)
# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: E ----
