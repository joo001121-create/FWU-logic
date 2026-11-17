# LJH[2026.1117]온도 고장 대체운전과 네 밸브 정지 연계: S ----
SPEED_OUTPUT_TIMER = 1
# 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.
# 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.
# HMI에서 최소 <= 최대를 확인할 것. 최소 30% 유지, QTS 20%는 팬 개발팀 확인 필요.
# ΔT 목표 -2℃는 SMX01 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.
# 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.
# 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.
RAT_LOOP = 1
RDP_LOOP = 2
DELTA_T_LOOP = 3
CZT_LOOP = 4
engine = ddc_logic()

sf_select = engine.READPOINT("VP_FWU_SF Control Select")
b_fixed = 0
if 0 <= sf_select < 1 :
    b_fixed = 1
if 2 <= sf_select < 3 and engine.READPOINT("VP_FWU_RDP PV Valid") != 1 :
    b_fixed = 1
if 4 <= sf_select < 5 and engine.READPOINT("VP_FWU_CZT PV Valid") != 1 :
    b_fixed = 1

if 1 <= sf_select < 2 and engine.READPOINT("VP_FWU_RAT Failure Alarm") == 1:
    b_fixed = 1
if 3 <= sf_select < 4 and (engine.READPOINT("VP_FWU_RAT Failure Alarm") == 1 or engine.READPOINT("VP_FWU_SAT Failure Alarm") == 1):
    b_fixed = 1
b_bms_fail = 0
if engine.READPOINT("VP_FWU_Upper Comm Enable") == 1 and engine.READPOINT("VP_FWU_BMS PLC Comm Fault") == 1 :
    if 2 <= sf_select < 3 or 4 <= sf_select < 5 :
        b_bms_fail = 1
    if 0 <= sf_select < 1 and engine.READPOINT("REMOTE SELECTION") == 1 :
        b_bms_fail = 1
if b_bms_fail == 1 :
    b_fixed = 0

sa_rdp_p = engine.READPOINT("VP_FWU_SF RDP PGain")
sa_rdp_i = engine.READPOINT("VP_FWU_SF RDP IGain")
rat_p = engine.READPOINT("VP_FWU_SF RAT PGain")
rat_i = engine.READPOINT("VP_FWU_SF RAT IGain")
delta_t_p = engine.READPOINT("VP_FWU_SF DeltaT PGain")
delta_t_i = engine.READPOINT("VP_FWU_SF DeltaT IGain")
sa_czt_p = engine.READPOINT("VP_FWU_SF CZT PGain")
sa_czt_i = engine.READPOINT("VP_FWU_SF CZT IGain")

if engine.READPOINT("FWU_EMERGENCY") == 0 :
    engine.RELEASE_PRI("FWU_SF-1_4 SPEED CONTROL", 1)
    engine.RELEASE_PRI("FWU_SF-5_8 SPEED CONTROL", 1)
    engine.RELEASE_PRI("FWU SF-1.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-2.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-3.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-4.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-5.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-6.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-7.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU SF-8.Target RPM Set", 1)
    engine.RELEASE_PRI("FWU_SAD-1_4 COMMAND", 1)
    if engine.READPOINT("VP_FWU_Operation Mode") == 1 :
        if engine.READPOINT("VP_FWU_Command") == 1 :
            engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 1)
            if engine.READPOINT("FWU_SAD-1 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-2 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-3 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-4 OPEN STATUS") == 1 :
                if b_fixed == 1 :
                    speed = engine.MAX(engine.READPOINT("VP_FWU_Speed SP"), engine.READPOINT("VP_FWU_SF Speed Min"))
                    speed = engine.MIN(speed, engine.READPOINT("VP_FWU_SF Speed Max"))
                    engine.WRITEPOINT("VP_FWU_SF Speed Value", speed)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and 1 <= sf_select < 2 :
                    engine.LOOP2(1,"FWU_RAT","VP_FWU_SF Speed Value","VP_FWU_RAT SP",rat_p,rat_i,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),RAT_LOOP,0)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and b_bms_fail == 0 and 2 <= sf_select < 3 :
                    engine.LOOP2(0,"VP_FWU_RDP PV","VP_FWU_SF Speed Value","VP_FWU_RDP SP",sa_rdp_p,sa_rdp_i,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),RDP_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and 3 <= sf_select < 4 :
                    engine.LOOP2(1,"VP_FWU_DeltaT PV","VP_FWU_SF Speed Value","VP_FWU_DeltaT SP",delta_t_p,delta_t_i,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),DELTA_T_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                if b_fixed == 0 and b_bms_fail == 0 and 4 <= sf_select < 5 :
                    engine.LOOP2(1,"VP_FWU_CZT PV","VP_FWU_SF Speed Value","VP_FWU_CZT SP",sa_czt_p,sa_czt_i,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),CZT_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                if b_bms_fail == 1 :
                    if engine.READPOINT("VP_FWU_BMS Comm Fail Mode") == 1 or engine.READPOINT("VP_FWU_SF Speed Value") < engine.READPOINT("VP_FWU_SF Speed Min") :
                        engine.WRITEPOINT("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Max"))
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)

            if engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1 :
                engine.LOOP2_INIT(RAT_LOOP)
                engine.LOOP2_INIT(RDP_LOOP)
                engine.LOOP2_INIT(DELTA_T_LOOP)
                engine.LOOP2_INIT(CZT_LOOP)
                engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)

        else:
            engine.LOOP2_INIT(RAT_LOOP)
            engine.LOOP2_INIT(RDP_LOOP)
            engine.LOOP2_INIT(DELTA_T_LOOP)
            engine.LOOP2_INIT(CZT_LOOP)
            if engine.READPOINT("VP_FWU_PICV All Closed") == 1 :
                engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)
            if engine.READPOINT("VP_FWU_SF Status") == 0 :
                engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 0)
        engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Value"), 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", engine.READPOINT("FWU_SAD-1_4 COMMAND"), 11)
    else:
        engine.LOOP2_INIT(RAT_LOOP)
        engine.LOOP2_INIT(RDP_LOOP)
        engine.LOOP2_INIT(DELTA_T_LOOP)
        engine.LOOP2_INIT(CZT_LOOP)
        engine.RELEASE_PRI("VP_FWU_SF Speed Value", 5)
        engine.RELEASE_PRI("FWU_SAD-1_4 COMMAND", 5)
else:
    engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
    engine.LOOP2_INIT(RAT_LOOP)
    engine.LOOP2_INIT(RDP_LOOP)
    engine.LOOP2_INIT(DELTA_T_LOOP)
    engine.LOOP2_INIT(CZT_LOOP)
    engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)
    engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", 0, 11)
    if engine.READPOINT("VP_FWU_SF Status") == 0 :
        engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 0)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-1_4 SPEED CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-5_8 SPEED CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-1.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-2.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-3.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-4.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-5.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-6.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-7.Target RPM Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU SF-8.Target RPM Set", 0, 1)

if engine.READPOINT("VP_FWU_SF Speed Value") > 0 :
    engine.WRITEPOINT("FWU SF-1.Run Command", 1)
    engine.WRITEPOINT("FWU SF-2.Run Command", 1)
    engine.WRITEPOINT("FWU SF-3.Run Command", 1)
    engine.WRITEPOINT("FWU SF-4.Run Command", 1)
    engine.WRITEPOINT("FWU SF-5.Run Command", 1)
    engine.WRITEPOINT("FWU SF-6.Run Command", 1)
    engine.WRITEPOINT("FWU SF-7.Run Command", 1)
    engine.WRITEPOINT("FWU SF-8.Run Command", 1)
else :
    engine.WRITEPOINT("FWU SF-1.Run Command", 0)
    engine.WRITEPOINT("FWU SF-2.Run Command", 0)
    engine.WRITEPOINT("FWU SF-3.Run Command", 0)
    engine.WRITEPOINT("FWU SF-4.Run Command", 0)
    engine.WRITEPOINT("FWU SF-5.Run Command", 0)
    engine.WRITEPOINT("FWU SF-6.Run Command", 0)
    engine.WRITEPOINT("FWU SF-7.Run Command", 0)
    engine.WRITEPOINT("FWU SF-8.Run Command", 0)

if engine.SECTIMER(SPEED_OUTPUT_TIMER, 1) > 5 :
    sf_speed = engine.READPOINT("VP_FWU_SF Speed Value")
    sf_max_rpm = engine.READPOINT("VP_FWU_SF Max RPM")
    sf_rpm_set = engine.MIN(sf_speed * sf_max_rpm / 100, sf_max_rpm)
    sf_ao_set = sf_speed * sf_max_rpm / engine.MAX(engine.READPOINT("VP_FWU_SF Rated Max RPM"), 1)

    if engine.READPOINT("VP_FWU_SF Comm Fault") == 1 :
        engine.WRITEPOINT("FWU_SF-1_4 SPEED CONTROL", sf_ao_set)
        engine.WRITEPOINT("FWU_SF-5_8 SPEED CONTROL", sf_ao_set)
        engine.WRITEPOINT("FWU SF-1.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-2.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-3.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-4.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-5.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-6.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-7.Target RPM Set", 0)
        engine.WRITEPOINT("FWU SF-8.Target RPM Set", 0)
    else :
        engine.WRITEPOINT("FWU_SF-1_4 SPEED CONTROL", 0)
        engine.WRITEPOINT("FWU_SF-5_8 SPEED CONTROL", 0)
        engine.WRITEPOINT("FWU SF-1.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-2.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-3.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-4.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-5.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-6.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-7.Target RPM Set", sf_rpm_set)
        engine.WRITEPOINT("FWU SF-8.Target RPM Set", sf_rpm_set)

    engine.SECTIMER(SPEED_OUTPUT_TIMER, 0)
# LJH[2026.1117]온도 고장 대체운전과 네 밸브 정지 연계: E ----
