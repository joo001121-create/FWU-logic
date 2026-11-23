# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: S ----
FIRE_CONFIRM_TIMER = 0
FIRE_CONFIRM_SECONDS = 3
engine = ddc_logic()

if engine.READPOINT("FWU_FIRE_ALARM") == 1 :
    if engine.SECTIMER(FIRE_CONFIRM_TIMER, 1) > FIRE_CONFIRM_SECONDS :      #FIRE_CONFIRM_SECONDS=3
        engine.WRITEPOINT("VP_FWU_Fire_Alarm", 1)
else :
    engine.SECTIMER(FIRE_CONFIRM_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Fire_Alarm", 0)

# Smoke_Action_Set: 0=알람만, 1=정지. HMI: 화재 감지 시 운전 방식.
# 일반 운전 ON/OFF와 별개의 강제 정지이며 로컬·수동 운전에도 적용한다.
# 하드웨어 화재 차단 회로는 이 설정으로 무효화되지 않는다.
b_shutdown = 0
if engine.READPOINT("VP_FWU_Remote_Shutdown_Command") == 1 :        #사용자 입력
    b_shutdown = 1
if engine.READPOINT("VP_FWU_Fire_Alarm") == 1 and engine.READPOINT("VP_FWU_Smoke_Action_Set") == 1 :        #VP_FWU_Smoke_Action_Set: 사용자 입력
    b_shutdown = 1

if b_shutdown == 1 :
    engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", 0, 11)
    engine.WRITEPOINT_PRI("FWU_SF-1_4_SPEED_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5_8_SPEED_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-1.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-2.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-3.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-4.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-6.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-7.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-8.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-1.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-2.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-3.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-4.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-6.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-7.Run_Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-8.Run_Command", 0, 2)
    if engine.READPOINT("VP_FWU_SF_Status") == 0 :
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", 0, 2)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", 0, 11)
else :
    # P2 해제 후 상위 우선순위에 남은 운전 명령에 따라 재기동할 수 있다.
    # P11 OFF는 별도 재기동 금지 래치가 아니다.
    engine.RELEASE_PRI("FWU_PICV_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-1_4_SPEED_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-5_8_SPEED_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-1.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-2.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-3.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-4.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-5.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-6.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-7.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-8.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-1.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-2.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-3.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-4.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-5.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-6.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-7.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-8.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 2)
# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: E ----
