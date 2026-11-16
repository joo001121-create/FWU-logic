engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : PICV Control  (rev. 2026-11-12)
#  - PICV PI control on SAT (SAT > PICV SAT SP -> PICV opens)
#  - Auto : control while Command = 1 and SF running; Command = 0 -> PICV 0 %
#  - SAT sensor failure : PICV 100 %
#  - Manual : PICV operated by the operator (the operator value is passed
#    through P11)
#  - Emergency : PICV 0 % (P1). Fire : no interlock here. The FWU keeps running
#    unless VP_FWU_Smoke Action = 1 (smoke shutdown in Remote Shutdown :
#    PICV 0 % (P2), kept value (P11) 0)
#  - Auto value is also written to P11 so that the value is kept when the
#    operation mode is switched from auto to manual
#  - rev. 2026-10-28 (CRAH pattern) : SAT Failure Alarm -> PICV 100 %
#      (before, a broken SAT sensor read -20 C and the loop closed the PICV)
#  - rev. 2026-10-28 (2) : Fire interlock removed, auto value mirrored to P11
#      (P11 is never released), loop deadband 0 (same as CRAH)
#      Emergency also writes 0 to P11 (no stale value in manual mode)
#  - rev. 2026-10-31 : CZT PV selection removed (done in Initialization, the
#      PICV is controlled on SAT only)
#  - rev. 2026-10-31 (F8) : backup operation SAT setpoint offset -0.5 C (F4 : -1 C)
#  - rev. 2026-11-12 : backup operation removed (upper control item; the upper
#      control can lower VP_FWU_PICV SAT SP itself). The loop setpoint is
#      VP_FWU_PICV SAT SP (was VP_FWU_PICV SAT SP Active, which is no longer
#      written; VP_FWU_Backup Operation / PICV SAT SP Active stay defined)
#
# Timers (SECTIMER) : none
# =====================================================================

# PICV PI gains
PICV_P = engine.READPOINT("VP_FWU_PICV PGain")
PICV_I = engine.READPOINT("VP_FWU_PICV IGain")

# PICV control
if engine.READPOINT("FWU_EMERGENCY") == 0 :
	# Normal : release the emergency priority (P1)
	engine.RELEASE_PRI("FWU_PICV CONTROL", 1)
	# Auto operation
	if engine.READPOINT("VP_FWU_Operation Mode") == 1:
		if engine.READPOINT("VP_FWU_Command") == 1 and engine.READPOINT("VP_FWU_SF Status") == 1 :
			# SAT sensor failure : PICV 100 %
			if engine.READPOINT("VP_FWU_SAT Failure Alarm") == 1 :
				engine.WRITEPOINT("FWU_PICV CONTROL", 100)
			# Normal : SAT PI control (loop 1), output limited to PICV MinSP ~ 100 %
			else :
				engine.LOOP2(1, "FWU_SAT", "FWU_PICV CONTROL", "VP_FWU_PICV SAT SP", PICV_P, PICV_I, 0, 1, 100, engine.READPOINT("VP_FWU_PICV MinSP"), 100, 1, 0)
		if engine.READPOINT("VP_FWU_Command") == 0 :
			# Stop : initialize the loop and close the PICV
			engine.LOOP2_INIT(1)
			engine.WRITEPOINT("FWU_PICV CONTROL", 0)
		# Keep the auto value at P11 (held when switched to manual)
		engine.WRITEPOINT_PRI("FWU_PICV CONTROL", engine.READPOINT("FWU_PICV CONTROL"), 11)
	# Manual operation
	else:
		engine.LOOP2_INIT(1)
		engine.RELEASE_PRI("FWU_PICV CONTROL", 5)
else:
	# Emergency : PICV 0 % (P1), kept value (P11) 0 so that a manual PICV
	# does not reopen when the emergency is released
	engine.LOOP2_INIT(1)
	engine.WRITEPOINT_PRI("FWU_PICV CONTROL", 0, 1)
	engine.WRITEPOINT_PRI("FWU_PICV CONTROL", 0, 11)
