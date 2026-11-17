# LJH[2026.1117]기존 Failover 원인과 래치 유지: S ----
FAILOVER_CONFIRM_TIMER = 1
FAILOVER_RESET_TIMER = 2
engine = ddc_logic()

b_fail_total = 0

if engine.READPOINT("VP_FWU_SAD Not Open Alarm") == 1 or engine.READPOINT("VP_FWU_SAD Full Close Alarm") == 1 or engine.READPOINT("VP_FWU_SF Failure Alarm") == 1 :
    b_fail_total = 1

if b_fail_total == 1 :
    if engine.SECTIMER(FAILOVER_CONFIRM_TIMER, 1) > 5 and engine.READPOINT("VP_FWU_Failover Alarm") == 0 :
        engine.WRITEPOINT("VP_FWU_Failover Alarm", 1)
        engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
        engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
else :
    engine.SECTIMER(FAILOVER_CONFIRM_TIMER, 0)

if engine.READPOINT("VP_FWU_Failover Reset") == 1 :
    if b_fail_total == 0 :
        engine.WRITEPOINT("VP_FWU_Failover Alarm", 0)
    if engine.SECTIMER(FAILOVER_RESET_TIMER, 1) > 5 :
        engine.WRITEPOINT_PRI("VP_FWU_Failover Reset", 0, 11)
        engine.SECTIMER(FAILOVER_RESET_TIMER, 0)
else :
    engine.SECTIMER(FAILOVER_RESET_TIMER, 0)
# LJH[2026.1117]기존 Failover 원인과 래치 유지: E ----
