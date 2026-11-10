engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Remote Shutdown  (rev. 2026-11-10)
#  - Fire alarm (FWU_FIRE ALARM DI, smoke detector) ON for 3 s ->
#    VP_FWU_Fire Alarm = 1 (OFF : reset at once)
#  - Shutdown = Remote Shutdown Command = 1, or Fire Alarm = 1 with
#    VP_FWU_Smoke Action = 1 (QTS : continue / shutdown configurable,
#    0 = continue (default), 1 = shutdown)
#  - Shutdown (Local or Remote mode) :
#      Command / Command-HMI = 0 (P11)
#      PICV 0 %, SF analog speed 0, SF-1~8 Target RPM 0 (P2)
#      SAD-1~4 close (P2) after the SF has stopped
#      PICV, SF Speed Value, SAD command : kept value (P11) 0 as well, so
#      that nothing restarts in manual mode when the shutdown is released
#  - No shutdown : release P2
#    (Command stays 0, the operator restarts the FWU)
#  - rev. 2026-11-10 : smoke shutdown option added (QTS)
#
# Timers (SECTIMER)
#  0 : Fire alarm confirmation (3 s)
# =====================================================================

# Fire alarm (smoke detector) : alarm point only, the FWU keeps running
# unless Smoke Action = 1
if engine.READPOINT("FWU_FIRE ALARM") == 1 :
	if engine.SECTIMER(0, 1) > 3 :
		engine.WRITEPOINT("VP_FWU_Fire Alarm", 1)
else :
	engine.SECTIMER(0, 0)
	engine.WRITEPOINT("VP_FWU_Fire Alarm", 0)

SHUTDOWN = 0
if engine.READPOINT("VP_FWU_Remote Shutdown Command") == 1 :
	SHUTDOWN = 1
if engine.READPOINT("VP_FWU_Fire Alarm") == 1 and engine.READPOINT("VP_FWU_Smoke Action") == 1 :
	SHUTDOWN = 1

if SHUTDOWN == 1 :
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
	# Close SAD-1~4 after the SF has stopped
	if engine.READPOINT("VP_FWU_SF Status") == 0 :
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 2)
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 11)
else :
	# Release the shutdown priority (P2)
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
	engine.RELEASE_PRI("FWU_SAD-1_4 COMMAND", 2)
