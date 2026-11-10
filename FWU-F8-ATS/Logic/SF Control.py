engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : SF Control  (rev. 2026-11-10)
#  - Control mode selection (CTRL_MODE) and SF speed control
#  - Auto : Command = 1 -> SAD-1~4 open; SF control starts when all four
#           SAD open status are ON. 5 control modes (SF Control Select) :
#           0 Fixed value, 1 RAT, 2 RDP, 3 Delta T, 4 CZT
#           Loop direction : RAT / CZT = 1 (PV > SP -> speed up),
#                            RDP / Delta T = 0 (PV > SP -> speed down)
#           All SAD-1~4 closed while Command = 1 -> SF speed 0
#           Command = 0 -> SF speed 0 after PICV feedback < 5 % (or 60 s),
#           SAD-1~4 close after the SF has stopped
#  - Manual : SF speed and SAD operated by the operator
#  - Emergency : Command 0 (P11), SF speed 0 (P1),
#           SAD-1~4 close (P1) after the SF has stopped
#           Fire : the FWU keeps running unless VP_FWU_Smoke Action = 1
#           (smoke shutdown is done in Remote Shutdown)
#  - Auto values (SF Speed Value, SAD-1_4 COMMAND) are also written to P11 so
#    that the values are kept when the operation mode is switched to manual
#  - SF-1~8 Run Command = 1 while SF Speed Value > 0 (0 during Emergency,
#    Remote Shutdown and smoke shutdown)
#  - Speed output every 5 s, switched by the SF comm fault summary
#    (VP_FWU_SF Comm Fault = any one of SF-1~8 in comm fault) :
#           comm normal : Modbus Target RPM to SF-1~8, analog AO = 0
#           comm fault  : analog AO SF-1_4 / SF-5_8 (% of 1920 rpm),
#                         Modbus Target RPM = 0
#  - rev. 2026-10-28 (CRAH pattern) :
#      SF stop when all SAD are closed (was done by Alarm with P3 / P11)
#      SF Run Command added
#      speed output switched by the SF comm fault summary (any fan) instead
#      of "all 4 fans in comm fault", Target RPM limited to SF Max RPM,
#      interval 10 s -> 5 s
#  - Backup operation (VP_FWU_Backup Operation = 1 and no Failover Alarm, auto mode,
#    all SAD open) : SF Speed Value = SF Speed Max whatever the control mode,
#    loops initialized; back to the control mode when the BMS PLC clears it
#  - rev. 2026-10-28 (2) : Fire interlock removed, auto values mirrored to P11
#      (P11 is never released; control writes are P5, so P11 only holds the value)
#  - rev. 2026-10-31 : RDP / CZT control modes use the adjacent zone compensation
#      PV (Comp PV); fixed value control (Speed SP) when the control PV is not
#      available (all sensors failed or BMS PLC comm fault); PV selection moved
#      to Initialization
#      Emergency also writes 0 to P11 (no stale value in manual mode)
#  - rev. 2026-10-31 (2) : Backup speed (SF Speed Max) only while SAD-1~4 are
#      all open (was applied while the SAD was still moving)
#  - rev. 2026-11-10 (QTS RDF, lightweight) :
#      control mode chosen once (CTRL_MODE) instead of the FIXED flag and the
#        loop initializations repeated in every mode
#      Delta T PV calculation removed (made in Initialization in the same scan)
#      unused HZT PI gain reads removed
#      SF Control Select out of 0~4 -> fixed value (was : speed frozen)
#      RAT mode with RAT sensor failure, Delta T mode with RAT or SAT sensor
#        failure -> fixed value (was : PI control on a failed sensor)
#      BMS PLC comm fault (QTS) : Fixed / RDP / CZT modes in Remote ->
#        VP_FWU_BMS Comm Fail Mode 0 = last speed held, 1 = SF Speed Max
#        (RAT / Delta T modes use the FWU sensors and keep controlling;
#         Backup operation still has priority)
#      Command OFF : SF speed 0 after PICV feedback < 5 % or 60 s
#        (a PICV feedback failure no longer keeps the SF running)
#      Run Command 0 during Emergency, Remote Shutdown and smoke shutdown
#      speed output : one write per output point
#
# Timers (SECTIMER)
#  1 : Speed output interval (5 s)
#  2 : Command OFF - PICV close wait limit (60 s)
# =====================================================================

# HZT / CZT / RDP PV selection, the adjacent zone compensation PV
# (CZT Comp PV, RDP Comp PV) and the Delta T PV are made in Initialization

# =====================================================================
# Control mode (CTRL_MODE)
#  SF Control Select : 0 Fixed value, 1 RAT, 2 RDP, 3 Delta T, 4 CZT
#  - 0 Fixed value (Speed SP) is also used when :
#      Select is out of 0~4
#      the control PV is not available (RAT : RAT sensor failure,
#      Delta T : RAT or SAT sensor failure, RDP / CZT : all sensors failed
#      or BMS PLC comm fault)
#  - 9 BMS PLC comm fault (QTS) : Remote mode and Fixed / RDP / CZT
#      (the modes that use values written by the BMS)
# =====================================================================
SF_SEL = engine.READPOINT("VP_FWU_SF Control Select")
CTRL_MODE = 0
if 1 <= SF_SEL < 2 and engine.READPOINT("VP_FWU_RAT Failure Alarm") == 0 :
	CTRL_MODE = 1
if 2 <= SF_SEL < 3 and engine.READPOINT("VP_FWU_RDP PV Valid") == 1 :
	CTRL_MODE = 2
if 3 <= SF_SEL < 4 and engine.READPOINT("VP_FWU_RAT Failure Alarm") == 0 and engine.READPOINT("VP_FWU_SAT Failure Alarm") == 0 :
	CTRL_MODE = 3
if 4 <= SF_SEL < 5 and engine.READPOINT("VP_FWU_CZT PV Valid") == 1 :
	CTRL_MODE = 4
if engine.READPOINT("VP_FWU_BMS PLC Comm Fault") == 1 and engine.READPOINT("REMOTE SELECTION") == 1 and CTRL_MODE != 1 and CTRL_MODE != 3 :
	CTRL_MODE = 9

# SF PI gains
SA_RDP_P = engine.READPOINT("VP_FWU_SF RDP PGain")
SA_RDP_I = engine.READPOINT("VP_FWU_SF RDP IGain")
RAT_P = engine.READPOINT("VP_FWU_SF RAT PGain")
RAT_I = engine.READPOINT("VP_FWU_SF RAT IGain")
DeltaT_P = engine.READPOINT("VP_FWU_SF DeltaT PGain")
DeltaT_I = engine.READPOINT("VP_FWU_SF DeltaT IGain")
SA_CZT_P = engine.READPOINT("VP_FWU_SF CZT PGain")
SA_CZT_I = engine.READPOINT("VP_FWU_SF CZT IGain")

# Backup operation : neighbouring FWU failed (BMS PLC) and this FWU is normal
if engine.READPOINT("VP_FWU_Backup Operation") == 1 and engine.READPOINT("VP_FWU_Failover Alarm") == 0 :
	BACKUP = 1
else :
	BACKUP = 0

# SF control
if engine.READPOINT("FWU_EMERGENCY") == 0 :
	# Normal : release the emergency priority (P1)
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
	# Auto operation
	if engine.READPOINT("VP_FWU_Operation Mode") == 1 :
		if engine.READPOINT("VP_FWU_Command") == 1 :
			engine.SECTIMER(2, 0)
			# Open SAD-1~4
			engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 1)
			# SF control starts when SAD-1~4 open status are all ON
			if engine.READPOINT("FWU_SAD-1 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-2 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-3 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-4 OPEN STATUS") == 1 :
				SPD_MIN = engine.READPOINT("VP_FWU_SF Speed Min")
				SPD_MAX = engine.READPOINT("VP_FWU_SF Speed Max")
				# 0 : Fixed value - Speed SP limited to SF Speed Min ~ Max
				if CTRL_MODE == 0 :
					engine.WRITEPOINT("VP_FWU_SF Speed Value", engine.MIN(engine.MAX(engine.READPOINT("VP_FWU_Speed SP"), SPD_MIN), SPD_MAX))
				# 1 : RAT PI control (loop 1) - RAT > RAT SP -> speed up
				if CTRL_MODE == 1 :
					engine.LOOP2(1,"FWU_RAT","VP_FWU_SF Speed Value","VP_FWU_RAT SP",RAT_P,RAT_I,0,0,60,SPD_MIN,SPD_MAX,1,0)
				# 2 : RDP PI control (loop 2) - RDP > RDP SP -> speed down
				#     PV = RDP Comp PV (own RDP, adjacent compensation included)
				if CTRL_MODE == 2 :
					engine.LOOP2(0,"VP_FWU_RDP Comp PV","VP_FWU_SF Speed Value","VP_FWU_RDP SP",SA_RDP_P,SA_RDP_I,0,0,60,SPD_MIN,SPD_MAX,2,0)
				# 3 : Delta T PI control (loop 3) - Delta T > Delta T SP -> speed down
				if CTRL_MODE == 3 :
					engine.LOOP2(0,"VP_FWU_DeltaT PV","VP_FWU_SF Speed Value","VP_FWU_DeltaT SP",DeltaT_P,DeltaT_I,0,0,60,SPD_MIN,SPD_MAX,3,0)
				# 4 : CZT PI control (loop 4) - CZT > CZT SP -> speed up
				#     PV = CZT Comp PV (own CZT, adjacent compensation included)
				if CTRL_MODE == 4 :
					engine.LOOP2(1,"VP_FWU_CZT Comp PV","VP_FWU_SF Speed Value","VP_FWU_CZT SP",SA_CZT_P,SA_CZT_I,0,0,60,SPD_MIN,SPD_MAX,4,0)
				# 9 : BMS PLC comm fault (QTS)
				#     Comm Fail Mode 0 : last speed held (no write); SF Speed Max when
				#                        the held speed is below SF Speed Min (e.g. 0)
				#     Comm Fail Mode 1 : SF Speed Max
				if CTRL_MODE == 9 :
					if engine.READPOINT("VP_FWU_BMS Comm Fail Mode") == 1 or engine.READPOINT("VP_FWU_SF Speed Value") < SPD_MIN :
						engine.WRITEPOINT("VP_FWU_SF Speed Value", SPD_MAX)

				# Backup operation : SF speed at the maximum setting (all control modes,
				# written last so that it has priority)
				if BACKUP == 1 :
					engine.WRITEPOINT("VP_FWU_SF Speed Value", SPD_MAX)

				# Loops not in use are initialized (all loops during Backup operation)
				if CTRL_MODE != 1 or BACKUP == 1 :
					engine.LOOP2_INIT(1)
				if CTRL_MODE != 2 or BACKUP == 1 :
					engine.LOOP2_INIT(2)
				if CTRL_MODE != 3 or BACKUP == 1 :
					engine.LOOP2_INIT(3)
				if CTRL_MODE != 4 or BACKUP == 1 :
					engine.LOOP2_INIT(4)

			# SAD-1~4 all closed (SAD Full Close) : SF stop
			#  (the SF restarts when all SAD open again)
			if engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1 :
				engine.LOOP2_INIT(1)
				engine.LOOP2_INIT(2)
				engine.LOOP2_INIT(3)
				engine.LOOP2_INIT(4)
				engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)

			# SAD moving or some SAD closed : no write, current speed is held
		else:
			# Command OFF : initialize all loops
			engine.LOOP2_INIT(1)
			engine.LOOP2_INIT(2)
			engine.LOOP2_INIT(3)
			engine.LOOP2_INIT(4)
			# SF speed 0 after the PICV has closed (feedback < 5 %), at the latest
			# after 60 s (a PICV feedback failure does not keep the SF running)
			if engine.READPOINT("FWU_PICV FEEDBACK") < 5 or engine.SECTIMER(2, 1) > 60 :
				engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)
			# Close SAD-1~4 after the SF has stopped
			if engine.READPOINT("VP_FWU_SF Status") == 0 :
				engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 0)
		# Keep the auto values at P11 (held when switched to manual)
		engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Value"), 11)
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", engine.READPOINT("FWU_SAD-1_4 COMMAND"), 11)
	# Manual operation
	else:
		engine.SECTIMER(2, 0)
		engine.LOOP2_INIT(1)
		engine.LOOP2_INIT(2)
		engine.LOOP2_INIT(3)
		engine.LOOP2_INIT(4)
		engine.RELEASE_PRI("VP_FWU_SF Speed Value", 5)
		engine.RELEASE_PRI("FWU_SAD-1_4 COMMAND", 5)
else:
	# Emergency : Command 0 (P11), SF speed 0
	engine.WRITEPOINT_PRI("VP_FWU_Command", 0, 11)
	engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", 0, 11)
	engine.SECTIMER(2, 0)
	engine.LOOP2_INIT(1)
	engine.LOOP2_INIT(2)
	engine.LOOP2_INIT(3)
	engine.LOOP2_INIT(4)
	engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)
	engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", 0, 11)
	# Close SAD-1~4 (P1) after the SF has stopped
	if engine.READPOINT("VP_FWU_SF Status") == 0 :
		engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 0)
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 11)
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", 0, 1)
	# SF analog speed and Target RPM 0 (P1)
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

# =====================================================================
# SF Run Command (SF-1~8)
#  - 1 while SF Speed Value > 0
#  - 0 during Emergency, Remote Shutdown and smoke shutdown
#    (Fire Alarm with Smoke Action = 1), whatever the SF Speed Value
# =====================================================================
RUN = 0
if engine.READPOINT("VP_FWU_SF Speed Value") > 0 and engine.READPOINT("FWU_EMERGENCY") == 0 and engine.READPOINT("VP_FWU_Remote Shutdown Command") == 0 :
	RUN = 1
if engine.READPOINT("VP_FWU_Fire Alarm") == 1 and engine.READPOINT("VP_FWU_Smoke Action") == 1 :
	RUN = 0
engine.WRITEPOINT("FWU SF-1.Run Command", RUN)
engine.WRITEPOINT("FWU SF-2.Run Command", RUN)
engine.WRITEPOINT("FWU SF-3.Run Command", RUN)
engine.WRITEPOINT("FWU SF-4.Run Command", RUN)
engine.WRITEPOINT("FWU SF-5.Run Command", RUN)
engine.WRITEPOINT("FWU SF-6.Run Command", RUN)
engine.WRITEPOINT("FWU SF-7.Run Command", RUN)
engine.WRITEPOINT("FWU SF-8.Run Command", RUN)

# =====================================================================
# Speed output every 5 s (Timer 1)
#  - Switched by the SF comm fault summary (VP_FWU_SF Comm Fault = 1 when any
#    one of SF-1~8 is in comm fault) :
#      comm normal : Modbus Target RPM = Speed Value x Max RPM / 100
#                    (limited to Max RPM), analog AO = 0
#      comm fault  : analog AO (0-10 V) = Speed Value x Max RPM / 1920
#                    for both groups (SF-1_4, SF-5_8), Modbus Target RPM = 0
# =====================================================================
if engine.SECTIMER(1, 1) > 5 :
	SF_SPEED = engine.READPOINT("VP_FWU_SF Speed Value")
	SF_MAXRPM = engine.READPOINT("VP_FWU_SF Max RPM")
	sfrpmset = engine.MIN(SF_SPEED * SF_MAXRPM / 100, SF_MAXRPM)
	sfaoset = SF_SPEED * SF_MAXRPM / 1920

	# Comm fault : analog output, Target RPM 0 / comm normal : Target RPM, analog 0
	if engine.READPOINT("VP_FWU_SF Comm Fault") == 1 :
		sfrpmset = 0
	else :
		sfaoset = 0
	engine.WRITEPOINT("FWU_SF-1_4 SPEED CONTROL", sfaoset)
	engine.WRITEPOINT("FWU_SF-5_8 SPEED CONTROL", sfaoset)
	engine.WRITEPOINT("FWU SF-1.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-2.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-3.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-4.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-5.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-6.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-7.Target RPM Set", sfrpmset)
	engine.WRITEPOINT("FWU SF-8.Target RPM Set", sfrpmset)

	engine.SECTIMER(1, 0)
