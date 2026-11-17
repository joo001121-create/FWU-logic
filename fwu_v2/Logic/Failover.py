# LJH[2026.1117]기존 Failover 원인과 래치 유지: S ----
FAILOVER_CONFIRM_TIMER = 1
FAILOVER_RESET_TIMER = 2
FAILOVER_CONFIRM_SECONDS = 5
FAILOVER_RESET_HOLD_SECONDS = 5
engine = ddc_logic()

# 장치의 고장 상태를 상위에 알린다. 인접 FWU의 협조 운전은 상위에서 판단한다.
# 개별 PICV 및 추가 댐퍼 신호 알람은 전체 Failover 조건에 포함하지 않는다.
b_fail_total = 0

if engine.READPOINT("VP_FWU_SAD_Not_Open_Alarm") == 1 or engine.READPOINT("VP_FWU_SAD_Full_Close_Alarm") == 1 or engine.READPOINT("VP_FWU_SF_Failure_Alarm") == 1 :
    b_fail_total = 1

# 알람 최초 발생 시 P11 OFF를 한 번 기록한다. 지속 정지/재기동 금지는 아니다.
# 더 높은 우선순위의 ON이 있으면 이 OFF보다 우선한다.
if b_fail_total == 1 :
    if engine.SECTIMER(FAILOVER_CONFIRM_TIMER, 1) > FAILOVER_CONFIRM_SECONDS and engine.READPOINT("VP_FWU_Failover_Alarm") == 0 :
        engine.WRITEPOINT("VP_FWU_Failover_Alarm", 1)
        engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
        engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
else :
    engine.SECTIMER(FAILOVER_CONFIRM_TIMER, 0)

# 원인이 사라진 뒤 리셋해야 알람이 해제된다.
# 5초는 리셋 입력 복귀 시간이며, 알람 해제 대기시간이 아니다.
# HMI/BMS가 더 높은 우선순위로 Reset을 쓰면 해당 입력도 해제해야 한다.
if engine.READPOINT("VP_FWU_Failover_Reset") == 1 :
    if b_fail_total == 0 :
        engine.WRITEPOINT("VP_FWU_Failover_Alarm", 0)
    if engine.SECTIMER(FAILOVER_RESET_TIMER, 1) > FAILOVER_RESET_HOLD_SECONDS :
        engine.WRITEPOINT_PRI("VP_FWU_Failover_Reset", 0, 11)
        engine.SECTIMER(FAILOVER_RESET_TIMER, 0)
else :
    engine.SECTIMER(FAILOVER_RESET_TIMER, 0)
# LJH[2026.1117]기존 Failover 원인과 래치 유지: E ----
