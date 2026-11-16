engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Failover  (rev. 2026-11-13)
#  - VP_FWU_Failover Alarm : this FWU cannot supply its cooling capacity.
#    It is the information the upper control (BMS / DCIM) reads to decide a
#    backup operation of the neighbouring FWUs (done by the upper control)
#  - Failover causes (DoO "FWU Failover Criteria", F8 = 8 fans) :
#      1) SAD Not Open Alarm
#      2) SAD Full Close Alarm
#      3) SF Failure Alarm (50 % or more of the installed fans failed,
#         VP_FWU_SF Count; F8 : 4 of 8)
#  - A cause lasting 5 s sets the Failover Alarm (latched) and stops the
#    FWU once : Command / Command-HMI = 0 (P11). PICV closes in PICV Control
#    (Command 0) and the SF stops in SF Control. The operator can start the
#    FWU again.
#  - Failover Reset = 1 : the alarm is released immediately only when no
#    cause is present, Reset is held 5 s for the HMI read-back and then
#    returned to 0 (P11)
#  - rev. 2026-11-12 : cause 4 (Group Control Mode = 1 and Command = Off)
#    removed - group control is an upper control item (VP_FWU_Group Control
#    Mode stays defined, not used here). The smoke shutdown exclusion added on
#    2026-11-11 belonged to cause 4 and is removed with it.
#  - rev. 2026-11-12 (2) : backup operation removed from SF / PICV Control
#    (upper control item); the Failover Alarm no longer blocks it in this DDC
#
# Timers (SECTIMER)
#  1 : Failover cause confirmation (5 s)
#  2 : Failover Reset hold (5 s)
# =====================================================================

# ---------------------------------------------------------------------
# 1. Failover causes
# ---------------------------------------------------------------------
FAIL_TOTAL = 0

# 1) SAD Not Open, 2) SAD Full Close, 3) SF Failure (50 % or more of the fans)
if engine.READPOINT("VP_FWU_SAD Not Open Alarm") == 1 or engine.READPOINT("VP_FWU_SAD Full Close Alarm") == 1 or engine.READPOINT("VP_FWU_SF Failure Alarm") == 1 :
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
