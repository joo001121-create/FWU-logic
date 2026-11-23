# LJH[2026.1117]온도 센서 고장 시 대체운전, 네 밸브 닫힘과 팬 정지 연계: S ----
SPEED_OUTPUT_TIMER = 1
# 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.
# 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.
# HMI에서 최소 <= 최대를 확인할 것. 최소 30% 유지, QTS 20%는 코드 리뷰시 확인 필요.
# ΔT 목표 -2℃는 SMX01 기준 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.
# 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.
# 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.
RAT_LOOP = 1
RDP_LOOP = 2
DELTA_T_LOOP = 3
CZT_LOOP = 4
engine = ddc_logic()

## 설정값 상수: HMI에서 입력한 값을 실행할 때마다 읽어온다.
SF_CONTROL_SELECT = engine.READPOINT("VP_FWU_SF_Control_Select")    ## 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT
SF_MAX_RPM = engine.READPOINT("VP_FWU_SF_Max_RPM")                  ## 속도 100%일 때 팬 목표 RPM
RAT_PGAIN = engine.READPOINT("VP_FWU_SF_RAT_PGain")                 ## RAT 기준 팬 제어 P 게인
RAT_IGAIN = engine.READPOINT("VP_FWU_SF_RAT_IGain")                 ## RAT 기준 팬 제어 I 게인
RDP_PGAIN = engine.READPOINT("VP_FWU_SF_RDP_PGain")                 ## RDP 기준 팬 제어 P 게인
RDP_IGAIN = engine.READPOINT("VP_FWU_SF_RDP_IGain")                 ## RDP 기준 팬 제어 I 게인
DELTAT_PGAIN = engine.READPOINT("VP_FWU_SF_DeltaT_PGain")           ## ΔT 기준 팬 제어 P 게인
DELTAT_IGAIN = engine.READPOINT("VP_FWU_SF_DeltaT_IGain")           ## ΔT 기준 팬 제어 I 게인
CZT_PGAIN = engine.READPOINT("VP_FWU_SF_CZT_PGain")                 ## CZT 기준 팬 제어 P 게인
CZT_IGAIN = engine.READPOINT("VP_FWU_SF_CZT_IGain")                 ## CZT 기준 팬 제어 I 게인

b_fixed = 0
if 0 <= SF_CONTROL_SELECT < 1 :
    b_fixed = 1
if 2 <= SF_CONTROL_SELECT < 3 and engine.READPOINT("VP_FWU_RDP_PV_Valid") != 1 :
    b_fixed = 1
if 4 <= SF_CONTROL_SELECT < 5 and engine.READPOINT("VP_FWU_CZT_PV_Valid") != 1 :
    b_fixed = 1

if 1 <= SF_CONTROL_SELECT < 2 and engine.READPOINT("VP_FWU_RAT_Failure_Alarm") == 1:
    b_fixed = 1
if 3 <= SF_CONTROL_SELECT < 4 and (engine.READPOINT("VP_FWU_RAT_Failure_Alarm") == 1 or engine.READPOINT("VP_FWU_SAT_Failure_Alarm") == 1):
    b_fixed = 1
b_bms_fail = 0
if engine.READPOINT("VP_FWU_Upper_Comm_Enable") == 1 and engine.READPOINT("VP_FWU_BMS_PLC_Comm_Fault") == 1 :
    if 2 <= SF_CONTROL_SELECT < 3 or 4 <= SF_CONTROL_SELECT < 5 :
        b_bms_fail = 1
    if 0 <= SF_CONTROL_SELECT < 1 and engine.READPOINT("REMOTE_SELECTION") == 1 :
        b_bms_fail = 1
if b_bms_fail == 1 :
    b_fixed = 0

if engine.READPOINT("FWU_EMERGENCY") == 0 :
    engine.RELEASE_PRI("FWU_SF-1_4_SPEED_CONTROL", 1)       #FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨 (기존 배선이 1~4, 5~8로 나뉘어 있음)
    engine.RELEASE_PRI("FWU_SF-5_8_SPEED_CONTROL", 1)
    engine.RELEASE_PRI("FWU_SF-1.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-2.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-3.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-4.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-5.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-6.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-7.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-8.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 1)
    if engine.READPOINT("VP_FWU_Operation_Mode") == 1 :
        if engine.READPOINT("VP_FWU_Command") == 1 :
            engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", 1)
            if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == 1 and engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == 1 :
                if b_fixed == 1 :
                    speed = engine.MAX(engine.READPOINT("VP_FWU_Speed_SP"), engine.READPOINT("VP_FWU_SF_Speed_Min"))
                    speed = engine.MIN(speed, engine.READPOINT("VP_FWU_SF_Speed_Max"))
                    engine.WRITEPOINT("VP_FWU_SF_Speed_Value", speed)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and 1 <= SF_CONTROL_SELECT < 2 :
                    engine.LOOP2(1,"FWU_RAT","VP_FWU_SF_Speed_Value","VP_FWU_RAT_SP",RAT_PGAIN,RAT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),RAT_LOOP,0)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and b_bms_fail == 0 and 2 <= SF_CONTROL_SELECT < 3 :
                    engine.LOOP2(0,"VP_FWU_RDP_PV","VP_FWU_SF_Speed_Value","VP_FWU_RDP_SP",RDP_PGAIN,RDP_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),RDP_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and 3 <= SF_CONTROL_SELECT < 4 :
                    engine.LOOP2(1,"VP_FWU_DeltaT_PV","VP_FWU_SF_Speed_Value","VP_FWU_DeltaT_SP",DELTAT_PGAIN,DELTAT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),DELTA_T_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and b_bms_fail == 0 and 4 <= SF_CONTROL_SELECT < 5 :
                    engine.LOOP2(1,"VP_FWU_CZT_PV","VP_FWU_SF_Speed_Value","VP_FWU_CZT_SP",CZT_PGAIN,CZT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),CZT_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                if b_bms_fail == 1 :
                    if engine.READPOINT("VP_FWU_BMS_Comm_Fail_Mode") == 1 or engine.READPOINT("VP_FWU_SF_Speed_Value") < engine.READPOINT("VP_FWU_SF_Speed_Min") :      #VP_FWU_BMS_Comm_Fail_Mode = 1: 팬 최대 속도 운전, 0: 마지막 팬 속도 유지
                        engine.WRITEPOINT("VP_FWU_SF_Speed_Value", engine.READPOINT("VP_FWU_SF_Speed_Max"))
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)

            if engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == 1 and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == 1 :
                engine.LOOP2_INIT(RAT_LOOP)
                engine.LOOP2_INIT(RDP_LOOP)
                engine.LOOP2_INIT(DELTA_T_LOOP)
                engine.LOOP2_INIT(CZT_LOOP)
                engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)

        else:
            engine.LOOP2_INIT(RAT_LOOP)
            engine.LOOP2_INIT(RDP_LOOP)
            engine.LOOP2_INIT(DELTA_T_LOOP)
            engine.LOOP2_INIT(CZT_LOOP)
            if engine.READPOINT("VP_FWU_PICV_All_Closed") == 1 :
                engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)
            if engine.READPOINT("VP_FWU_SF_Status") == 0 :
                engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", 0)
        engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", engine.READPOINT("VP_FWU_SF_Speed_Value"), 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", engine.READPOINT("FWU_SAD-1_4_COMMAND"), 11)
    else:
        engine.LOOP2_INIT(RAT_LOOP)
        engine.LOOP2_INIT(RDP_LOOP)
        engine.LOOP2_INIT(DELTA_T_LOOP)
        engine.LOOP2_INIT(CZT_LOOP)
        engine.RELEASE_PRI("VP_FWU_SF_Speed_Value", 5)
        engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 5)
else:
    engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
    engine.LOOP2_INIT(RAT_LOOP)
    engine.LOOP2_INIT(RDP_LOOP)
    engine.LOOP2_INIT(DELTA_T_LOOP)
    engine.LOOP2_INIT(CZT_LOOP)
    engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)
    engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", 0, 11)
    if engine.READPOINT("VP_FWU_SF_Status") == 0 :
        engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", 0)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", 0, 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-1_4_SPEED_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-5_8_SPEED_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-1.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-2.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-3.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-4.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-5.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-6.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-7.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-8.Target_RPM_Set", 0, 1)

if engine.READPOINT("VP_FWU_SF_Speed_Value") > 0 :
    engine.WRITEPOINT("FWU_SF-1.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-2.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-3.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-4.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-5.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-6.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-7.Run_Command", 1)
    engine.WRITEPOINT("FWU_SF-8.Run_Command", 1)
else :
    engine.WRITEPOINT("FWU_SF-1.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-2.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-3.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-4.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-5.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-6.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-7.Run_Command", 0)
    engine.WRITEPOINT("FWU_SF-8.Run_Command", 0)

if engine.SECTIMER(SPEED_OUTPUT_TIMER, 1) > 5 :
    sf_speed = engine.READPOINT("VP_FWU_SF_Speed_Value")
    sf_rpm_set = engine.MIN(sf_speed * SF_MAX_RPM / 100, SF_MAX_RPM)
    sf_ao_set = sf_speed * SF_MAX_RPM / engine.MAX(engine.READPOINT("VP_FWU_SF_Rated_Max_RPM"), 1)

    if engine.READPOINT("VP_FWU_SF_Comm_Fault") == 1 :
        engine.WRITEPOINT("FWU_SF-1_4_SPEED_CONTROL", sf_ao_set)
        engine.WRITEPOINT("FWU_SF-5_8_SPEED_CONTROL", sf_ao_set)
        engine.WRITEPOINT("FWU_SF-1.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-2.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-3.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-4.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-5.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-6.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-7.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-8.Target_RPM_Set", 0)
    else :
        engine.WRITEPOINT("FWU_SF-1_4_SPEED_CONTROL", 0)
        engine.WRITEPOINT("FWU_SF-5_8_SPEED_CONTROL", 0)
        engine.WRITEPOINT("FWU_SF-1.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-2.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-3.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-4.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-5.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-6.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-7.Target_RPM_Set", sf_rpm_set)
        engine.WRITEPOINT("FWU_SF-8.Target_RPM_Set", sf_rpm_set)

    engine.SECTIMER(SPEED_OUTPUT_TIMER, 0)
# LJH[2026.1117]온도 고장 대체운전과 네 밸브 정지 연계: E ----
