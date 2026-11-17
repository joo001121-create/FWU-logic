# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: S ----
FIRE_CONFIRM_TIMER = 0
engine = ddc_logic()

if engine.READPOINT("FWU_FIRE ALARM") == 1 :
    if engine.SECTIMER(FIRE_CONFIRM_TIMER, 1) > 3 :
        engine.WRITEPOINT("VP_FWU_Fire Alarm", 1)
else :
    engine.SECTIMER(FIRE_CONFIRM_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_Fire Alarm", 0)

b_shutdown = 0
if engine.READPOINT("VP_FWU_Remote Shutdown Command") == 1 :
    b_shutdown = 1
if engine.READPOINT("VP_FWU_Fire Alarm") == 1 and engine.READPOINT("VP_FWU_Smoke Action") == 1 :
    b_shutdown = 1

if b_shutdown == 1 :
    engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
    engine.WRITEPOINT_PRI("FWU_PICV CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_PICV CONTROL", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", 0, 11)
    engine.WRITEPOINT_PRI("FWU_SF-1_4 SPEED CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5_8 SPEED CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-1.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-2.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-3.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-4.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-5.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-6.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-7.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-8.Target RPM Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-1.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-2.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-3.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-4.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-5.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-6.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-7.Run Command", 0, 2)
    engine.WRITEPOINT_PRI("FWU SF-8.Run Command", 0, 2)
    if engine.READPOINT("VP_FWU_SF Status") == 0 :
        engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 2)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 11)
else :
    engine.RELEASE_PRI("FWU_PICV CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-1_4 SPEED CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-5_8 SPEED CONTROL", 2)
    engine.RELEASE_PRI("FWU SF-1.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-2.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-3.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-4.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-5.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-6.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-7.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-8.Target RPM Set", 2)
    engine.RELEASE_PRI("FWU SF-1.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-2.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-3.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-4.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-5.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-6.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-7.Run Command", 2)
    engine.RELEASE_PRI("FWU SF-8.Run Command", 2)
    engine.RELEASE_PRI("FWU_SAD-1_4 COMMAND", 2)
# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: E ----
