SF_1_COMM_TIMER = 0
SF_2_COMM_TIMER = 1
SF_3_COMM_TIMER = 2
SF_4_COMM_TIMER = 3
SF_5_COMM_TIMER = 4
SF_6_COMM_TIMER = 5
SF_7_COMM_TIMER = 6
SF_8_COMM_TIMER = 7
ATS_COMM_TIMER = 8
COMM_FAULT_CODE = 8
FAN_COMM_CONFIRM_SECONDS = 10
ATS_COMM_CONFIRM_SECONDS = 10
# ATS는 CH2 RS485 구성으로 연결할 것. DI 입력 표기와 실제 HW 구성을 대조한다.
# 현재 XML 통신 포트 배치는 구형 맵이므로 실장 전에 수정해야 한다.
engine = ddc_logic()

if engine.READPOINT_ALARM("FWU_SF-1.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_1_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-1_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-1_Comm_Fault", 0)
    engine.SECTIMER(SF_1_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-2.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_2_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-2_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-2_Comm_Fault", 0)
    engine.SECTIMER(SF_2_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-3.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_3_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-3_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-3_Comm_Fault", 0)
    engine.SECTIMER(SF_3_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-4.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_4_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-4_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-4_Comm_Fault", 0)
    engine.SECTIMER(SF_4_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-5.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_5_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-5_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-5_Comm_Fault", 0)
    engine.SECTIMER(SF_5_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-6.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_6_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-6_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-6_Comm_Fault", 0)
    engine.SECTIMER(SF_6_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-7.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_7_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-7_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-7_Comm_Fault", 0)
    engine.SECTIMER(SF_7_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU_SF-8.Current_RPM") == COMM_FAULT_CODE :
    if engine.SECTIMER(SF_8_COMM_TIMER, 1) > FAN_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_SF-8_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-8_Comm_Fault", 0)
    engine.SECTIMER(SF_8_COMM_TIMER, 0)

if engine.READPOINT("VP_FWU_SF-1_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-2_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-3_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-4_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-5_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-6_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-7_Comm_Fault") == 1 or engine.READPOINT("VP_FWU_SF-8_Comm_Fault") == 1 :
    engine.WRITEPOINT("VP_FWU_SF_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF_Comm_Fault", 0)

if engine.READPOINT_ALARM("FWU-ATS.Current_Power") == COMM_FAULT_CODE :
    if engine.SECTIMER(ATS_COMM_TIMER, 1) > ATS_COMM_CONFIRM_SECONDS :
        engine.WRITEPOINT("VP_FWU_ATS_Comm_Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_ATS_Comm_Fault", 0)
    engine.SECTIMER(ATS_COMM_TIMER, 0)

# LJH[2026.1117]기존 단일 유량계 감시 분리
