# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: S ----
engine = ddc_logic()
# 수신 어댑터가 실제 값과 Input OK를 기록한 뒤 Sample Seq를 갱신해야 한다.
# 같은 값을 재수신해도 Seq는 갱신한다. 주소 미연결 상태에서는 Input Enable=0 유지.
# 통신 10초는 기존 유량계 감시 기준의 임시값. CH3 폴링 주기에 맞춰 확인.
b_all_closed = 1
b_monitor_ready = 1
b_any_fault = 0
b_any_comm_fault = 0
PICV_1_INPUT_TIMER = 0
PICV_1_DEVIATION_TIMER = 4
b_input_ok = engine.READPOINT("VP_FWU_PICV Input Enable") == 1 and engine.READPOINT("VP_FWU_PICV-1 Input OK") == 1
if not b_input_ok:
    engine.WRITEPOINT("VP_FWU_PICV-1 Feedback Valid", 0)
    engine.WRITEPOINT("VP_FWU_PICV-1 Sample Prev", engine.READPOINT("VP_FWU_PICV-1 Sample Seq"))
    engine.SECTIMER(PICV_1_INPUT_TIMER, 0)
else:
    if engine.READPOINT("VP_FWU_PICV-1 Sample Seq") != engine.READPOINT("VP_FWU_PICV-1 Sample Prev"):
        engine.WRITEPOINT("VP_FWU_PICV-1 Sample Prev", engine.READPOINT("VP_FWU_PICV-1 Sample Seq"))
        engine.WRITEPOINT("VP_FWU_PICV-1 Feedback Valid", 1)
        engine.SECTIMER(PICV_1_INPUT_TIMER, 0)
    else:
        if engine.SECTIMER(PICV_1_INPUT_TIMER, 1) > engine.READPOINT("VP_FWU_PICV Input Timeout"):
            engine.WRITEPOINT("VP_FWU_PICV-1 Feedback Valid", 0)
b_valid = engine.READPOINT("VP_FWU_PICV-1 Feedback Valid") == 1
position = engine.READPOINT("VP_FWU_PICV-1 Position")
if not (0 <= position <= 100):
    b_valid = 0
    engine.WRITEPOINT("VP_FWU_PICV-1 Feedback Valid", 0)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-1 Comm Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-1 Alarm", 1)
    engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-1 Comm Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV Control Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV CONTROL") < position + 30):
            if engine.SECTIMER(PICV_1_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_1_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV Flow Check Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled Water Supply Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-1 Flow") < engine.READPOINT("VP_FWU_PICV No Flow Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-1 Flow") > engine.READPOINT("VP_FWU_PICV Leak Flow Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-1 Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-1 Alarm") == 1:
    b_any_fault = 1
PICV_2_INPUT_TIMER = 1
PICV_2_DEVIATION_TIMER = 5
b_input_ok = engine.READPOINT("VP_FWU_PICV Input Enable") == 1 and engine.READPOINT("VP_FWU_PICV-2 Input OK") == 1
if not b_input_ok:
    engine.WRITEPOINT("VP_FWU_PICV-2 Feedback Valid", 0)
    engine.WRITEPOINT("VP_FWU_PICV-2 Sample Prev", engine.READPOINT("VP_FWU_PICV-2 Sample Seq"))
    engine.SECTIMER(PICV_2_INPUT_TIMER, 0)
else:
    if engine.READPOINT("VP_FWU_PICV-2 Sample Seq") != engine.READPOINT("VP_FWU_PICV-2 Sample Prev"):
        engine.WRITEPOINT("VP_FWU_PICV-2 Sample Prev", engine.READPOINT("VP_FWU_PICV-2 Sample Seq"))
        engine.WRITEPOINT("VP_FWU_PICV-2 Feedback Valid", 1)
        engine.SECTIMER(PICV_2_INPUT_TIMER, 0)
    else:
        if engine.SECTIMER(PICV_2_INPUT_TIMER, 1) > engine.READPOINT("VP_FWU_PICV Input Timeout"):
            engine.WRITEPOINT("VP_FWU_PICV-2 Feedback Valid", 0)
b_valid = engine.READPOINT("VP_FWU_PICV-2 Feedback Valid") == 1
position = engine.READPOINT("VP_FWU_PICV-2 Position")
if not (0 <= position <= 100):
    b_valid = 0
    engine.WRITEPOINT("VP_FWU_PICV-2 Feedback Valid", 0)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-2 Comm Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-2 Alarm", 1)
    engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-2 Comm Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV Control Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV CONTROL") < position + 30):
            if engine.SECTIMER(PICV_2_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_2_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV Flow Check Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled Water Supply Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-2 Flow") < engine.READPOINT("VP_FWU_PICV No Flow Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-2 Flow") > engine.READPOINT("VP_FWU_PICV Leak Flow Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-2 Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-2 Alarm") == 1:
    b_any_fault = 1
PICV_3_INPUT_TIMER = 2
PICV_3_DEVIATION_TIMER = 6
b_input_ok = engine.READPOINT("VP_FWU_PICV Input Enable") == 1 and engine.READPOINT("VP_FWU_PICV-3 Input OK") == 1
if not b_input_ok:
    engine.WRITEPOINT("VP_FWU_PICV-3 Feedback Valid", 0)
    engine.WRITEPOINT("VP_FWU_PICV-3 Sample Prev", engine.READPOINT("VP_FWU_PICV-3 Sample Seq"))
    engine.SECTIMER(PICV_3_INPUT_TIMER, 0)
else:
    if engine.READPOINT("VP_FWU_PICV-3 Sample Seq") != engine.READPOINT("VP_FWU_PICV-3 Sample Prev"):
        engine.WRITEPOINT("VP_FWU_PICV-3 Sample Prev", engine.READPOINT("VP_FWU_PICV-3 Sample Seq"))
        engine.WRITEPOINT("VP_FWU_PICV-3 Feedback Valid", 1)
        engine.SECTIMER(PICV_3_INPUT_TIMER, 0)
    else:
        if engine.SECTIMER(PICV_3_INPUT_TIMER, 1) > engine.READPOINT("VP_FWU_PICV Input Timeout"):
            engine.WRITEPOINT("VP_FWU_PICV-3 Feedback Valid", 0)
b_valid = engine.READPOINT("VP_FWU_PICV-3 Feedback Valid") == 1
position = engine.READPOINT("VP_FWU_PICV-3 Position")
if not (0 <= position <= 100):
    b_valid = 0
    engine.WRITEPOINT("VP_FWU_PICV-3 Feedback Valid", 0)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-3 Comm Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-3 Alarm", 1)
    engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-3 Comm Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV Control Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV CONTROL") < position + 30):
            if engine.SECTIMER(PICV_3_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_3_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV Flow Check Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled Water Supply Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-3 Flow") < engine.READPOINT("VP_FWU_PICV No Flow Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-3 Flow") > engine.READPOINT("VP_FWU_PICV Leak Flow Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-3 Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-3 Alarm") == 1:
    b_any_fault = 1
PICV_4_INPUT_TIMER = 3
PICV_4_DEVIATION_TIMER = 7
b_input_ok = engine.READPOINT("VP_FWU_PICV Input Enable") == 1 and engine.READPOINT("VP_FWU_PICV-4 Input OK") == 1
if not b_input_ok:
    engine.WRITEPOINT("VP_FWU_PICV-4 Feedback Valid", 0)
    engine.WRITEPOINT("VP_FWU_PICV-4 Sample Prev", engine.READPOINT("VP_FWU_PICV-4 Sample Seq"))
    engine.SECTIMER(PICV_4_INPUT_TIMER, 0)
else:
    if engine.READPOINT("VP_FWU_PICV-4 Sample Seq") != engine.READPOINT("VP_FWU_PICV-4 Sample Prev"):
        engine.WRITEPOINT("VP_FWU_PICV-4 Sample Prev", engine.READPOINT("VP_FWU_PICV-4 Sample Seq"))
        engine.WRITEPOINT("VP_FWU_PICV-4 Feedback Valid", 1)
        engine.SECTIMER(PICV_4_INPUT_TIMER, 0)
    else:
        if engine.SECTIMER(PICV_4_INPUT_TIMER, 1) > engine.READPOINT("VP_FWU_PICV Input Timeout"):
            engine.WRITEPOINT("VP_FWU_PICV-4 Feedback Valid", 0)
b_valid = engine.READPOINT("VP_FWU_PICV-4 Feedback Valid") == 1
position = engine.READPOINT("VP_FWU_PICV-4 Position")
if not (0 <= position <= 100):
    b_valid = 0
    engine.WRITEPOINT("VP_FWU_PICV-4 Feedback Valid", 0)
if not b_valid:
    b_all_closed = 0
    b_monitor_ready = 0
    b_any_comm_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-4 Comm Fault", 1)
    engine.WRITEPOINT("VP_FWU_PICV-4 Alarm", 1)
    engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
else:
    engine.WRITEPOINT("VP_FWU_PICV-4 Comm Fault", 0)
    if position >= 5:
        b_all_closed = 0
    b_valve_fault = 0
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    if engine.READPOINT("VP_FWU_PICV Control Mode") == 1:
        if not (position - 30 < engine.READPOINT("FWU_PICV CONTROL") < position + 30):
            if engine.SECTIMER(PICV_4_DEVIATION_TIMER, 1) > 40:
                b_valve_fault = 1
        else:
            engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
    else:
        engine.SECTIMER(PICV_4_DEVIATION_TIMER, 0)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if engine.READPOINT("VP_FWU_PICV Flow Check Enable") == 1:
        if engine.READPOINT("VP_FWU_Chilled Water Supply Condition") == 1 and position > 30 and engine.READPOINT("VP_FWU_PICV-4 Flow") < engine.READPOINT("VP_FWU_PICV No Flow Set"):
            b_valve_fault = 1
        if position < 1 and engine.READPOINT("VP_FWU_PICV-4 Flow") > engine.READPOINT("VP_FWU_PICV Leak Flow Set"):
            b_valve_fault = 1
    engine.WRITEPOINT("VP_FWU_PICV-4 Alarm", b_valve_fault)
if engine.READPOINT("VP_FWU_PICV-4 Alarm") == 1:
    b_any_fault = 1
if engine.READPOINT("VP_FWU_PICV Control Mode") == 0 or engine.READPOINT("VP_FWU_PICV Flow Check Enable") != 1:
    b_monitor_ready = 0
engine.WRITEPOINT("VP_FWU_PICV All Closed", b_all_closed)
engine.WRITEPOINT("VP_FWU_PICV Monitor Ready", b_monitor_ready)
engine.WRITEPOINT("VP_FWU_PICV_Alarm", b_any_fault)
engine.WRITEPOINT("VP_FWU_Flow Comm Fault", b_any_comm_fault)
# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: E ----
