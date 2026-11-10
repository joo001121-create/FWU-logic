engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Failover  (rev. 2026-10-28)
#  - VP_FWU_Failover Alarm : tells the BMS PLC that this FWU cannot supply its
#    cooling capacity (the BMS PLC starts the backup operation of the
#    neighbouring FWUs : fan 100 %, lower cooling set temperature)
#  - Failover causes (DoO "FWU Failover Criteria", F8 = 8 fans) :
#      1) SAD Not Open Alarm
#      2) SAD Full Close Alarm
#      3) SF Failure Alarm (4 or more of the 8 fans failed = 50 % capacity)
#      4) Group Control Mode = 1 and Operation Command = Off
#         (not judged during Remote Shutdown / Emergency, a deliberate stop)
#  - A cause lasting 5 s sets the Failover Alarm (latched) and stops the
#    FWU once : Command / Command-HMI = 0 (P11). PICV closes in PICV Control
#    (Command 0) and the SF stops in SF Control. The operator can start the
#    FWU again.
#  - Backup operation (a neighbouring FWU failed, Case 1~5) : the BMS PLC sets
#    VP_FWU_Backup Operation = 1. SF Control (speed = SF Speed Max) and PICV Control
#    (SAT setpoint - 0.5 C) increase the cooling capacity. It is ignored while this
#    FWU has its own Failover Alarm.
#  - Failover Reset = 1 : the alarm is released immediately only when no
#    cause is present, Reset is held 5 s for the HMI read-back and then
#    returned to 0 (P11)
#
# Timers (SECTIMER)
#  1 : Failover cause confirmation (5 s)
#  2 : Failover Reset hold (5 s)
# =====================================================================

# ---------------------------------------------------------------------
# 1. Failover causes
# ---------------------------------------------------------------------
FAIL_TOTAL = 0

# 1) SAD Not Open, 2) SAD Full Close, 3) SF Failure (4 or more fans)
if engine.READPOINT("VP_FWU_SAD Not Open Alarm") == 1 or engine.READPOINT("VP_FWU_SAD Full Close Alarm") == 1 or engine.READPOINT("VP_FWU_SF Failure Alarm") == 1 :
	FAIL_TOTAL = 1

# 4) Group Control Mode = 1 and Operation Command = Off
#    (a stop by Remote Shutdown / Emergency is not a failure)
if engine.READPOINT("VP_FWU_Group Control Mode") == 1 and engine.READPOINT("VP_FWU_Command") == 0 :
	if engine.READPOINT("VP_FWU_Remote Shutdown Command") == 0 and engine.READPOINT("FWU_EMERGENCY") == 0 :
		FAIL_TOTAL = 1

# ---------------------------------------------------------------------
# 2. Failover Alarm : cause confirmed for 5 s -> alarm (latched) and stop once
# ---------------------------------------------------------------------
if FAIL_TOTAL == 1 :
	if engine.SECTIMER(1, 1) > 5 and engine.READPOINT("VP_FWU_Failover Alarm") == 0 :
		engine.WRITEPOINT("VP_FWU_Failover Alarm", 1)
		engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
		engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
else :
	engine.SECTIMER(1, 0)

# ---------------------------------------------------------------------
# 3. Failover Reset
# ---------------------------------------------------------------------
if engine.READPOINT("VP_FWU_Failover Reset") == 1 :
	# Release the alarm immediately only when no cause is present
	if FAIL_TOTAL == 0 :
		engine.WRITEPOINT("VP_FWU_Failover Alarm", 0)
	# Hold the Reset for 5 s (HMI read-back), then return it to 0
	if engine.SECTIMER(2, 1) > 5 :
		engine.WRITEPOINT_PRI("VP_FWU_Failover Reset", 0, 11)
		engine.SECTIMER(2, 0)
else :
	engine.SECTIMER(2, 0)
