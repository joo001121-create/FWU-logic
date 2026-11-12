engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : SF Control  (rev. 2026-11-11)
#  - HZT / CZT / RDP PV selection (Avg or Max) and Delta T PV
#  - Auto : Command = 1 -> SAD-1~4 open; SF control starts when all four
#           SAD open status are ON. 5 control modes (SF Control Select) :
#           0 Fixed value, 1 RAT, 2 RDP, 3 Delta T, 4 CZT
#           Loop direction (LDPL LOOP2 type) :
#             RAT / CZT / Delta T = 1 (PV > SP -> speed up, PV < SP -> speed down)
#             RDP                 = 0 (PV < SP -> speed up, PV > SP -> speed down)
#           All SAD-1~4 closed while Command = 1 -> SF speed 0
#           Command = 0 -> SF speed 0 after PICV feedback < 5 %,
#           SAD-1~4 close after the SF has stopped
#  - Manual : SF speed and SAD operated by the operator
#  - Emergency : Command 0 (P11), SF speed 0 (P1),
#           SAD-1~4 close (P1) after the SF has stopped
#           Fire : no interlock here. The FWU keeps running unless
#           VP_FWU_Smoke Action = 1 (smoke shutdown in Remote Shutdown, P2)
#  - BMS PLC comm fault (QTS 129~131) : RDP / CZT modes, and the fixed value
#           mode in Remote, use VP_FWU_BMS Comm Fail Mode
#           (0 = last known speed held, 1 = SF Speed Max)
#  - Auto values (SF Speed Value, SAD-1_4 COMMAND) are also written to P11 so
#    that the values are kept when the operation mode is switched to manual
#  - SF-1~8 Run Command = 1 while SF Speed Value > 0
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
#  - rev. 2026-11-11 (QTS 129~131) : BMS PLC comm fault fan speed option
#      (VP_FWU_BMS Comm Fail Mode) for the modes that use values written by the
#      BMS : RDP (2) / CZT (4) (zone sensors), fixed value (0) in Remote
#      (Speed SP). Before, RDP / CZT went to the fixed value (Speed SP).
#      RAT (1) / Delta T (3) use the FWU sensors and keep controlling.
#      Backup operation still has priority (written after).
#  - rev. 2026-11-11 (2) : Delta T loop direction 0 -> 1. Delta T = RAT - SAT
#      rises when the airflow falls, so Delta T < SP -> speed down (Delta T up),
#      Delta T > SP -> speed up (Delta T down) = LDPL type 1. With type 0 the
#      loop moved the speed the wrong way and ran away to Speed Min / Max.
#      VP_FWU_DeltaT SP default is -2 (VirtualPoint.xml) : with Delta T > 0 the
#      fan goes to Speed Max. Set the design Delta T before using mode 3.
#
# Timers (SECTIMER)
#  1 : Speed output interval (5 s)
# =====================================================================

# HZT / CZT / RDP PV selection and the adjacent zone compensation PV
# (CZT Comp PV, RDP Comp PV) are made in Initialization

# Fixed value control : SF Control Select 0, or the control PV is not available
#  (CZT / RDP : all sensors failed) -> Speed SP
#  (BMS PLC comm fault : BMS_FAIL below, not the fixed value)
SF_SEL = engine.READPOINT("VP_FWU_SF Control Select")
FIXED = 0
if 0 <= SF_SEL < 1 :
	FIXED = 1
if 2 <= SF_SEL < 3 and engine.READPOINT("VP_FWU_RDP PV Valid") != 1 :
	FIXED = 1
if 4 <= SF_SEL < 5 and engine.READPOINT("VP_FWU_CZT PV Valid") != 1 :
	FIXED = 1

# BMS PLC comm fault (QTS 129~131) : BMS_FAIL = 1 for the control modes that
# use values written by the BMS
#  - RDP (2) / CZT (4) : zone sensors written by the BMS PLC (Local or Remote)
#  - Fixed value (0)   : Speed SP written by the BMS (Remote only; in Local
#                        the Speed SP is set on the touch screen)
#  BMS_FAIL = 1 takes the place of the fixed value control of RDP / CZT
BMS_FAIL = 0
if engine.READPOINT("VP_FWU_BMS PLC Comm Fault") == 1 :
	if 2 <= SF_SEL < 3 or 4 <= SF_SEL < 5 :
		BMS_FAIL = 1
	if 0 <= SF_SEL < 1 and engine.READPOINT("REMOTE SELECTION") == 1 :
		BMS_FAIL = 1
if BMS_FAIL == 1 :
	FIXED = 0

# Delta T PV = RAT - SAT
engine.WRITEPOINT("VP_FWU_DeltaT PV", engine.READPOINT("FWU_RAT") - engine.READPOINT("FWU_SAT"))

# SF PI gains (HZT gains are read but no HZT control mode exists)
SA_HZT_P = engine.READPOINT("VP_FWU_SF HZT PGain")
SA_HZT_I = engine.READPOINT("VP_FWU_SF HZT IGain")
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
			# Open SAD-1~4
			engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 1)
			# SF control starts when SAD-1~4 open status are all ON
			if engine.READPOINT("FWU_SAD-1 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-2 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-3 OPEN STATUS") == 1 and engine.READPOINT("FWU_SAD-4 OPEN STATUS") == 1 :
				# SF Control Select : 0 Fixed value, 1 RAT, 2 RDP, 3 Delta T, 4 CZT
				# 0 : Fixed value - Speed SP limited to SF Speed Min ~ Max
				#     (also used when the RDP / CZT control PV is not available
				#      because all sensors failed)
				if FIXED == 1 :
					speed = engine.MAX(engine.READPOINT("VP_FWU_Speed SP"), engine.READPOINT("VP_FWU_SF Speed Min"))
					speed = engine.MIN(speed, engine.READPOINT("VP_FWU_SF Speed Max"))
					engine.WRITEPOINT("VP_FWU_SF Speed Value", speed)
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(3)
					engine.LOOP2_INIT(4)
				# 1 : RAT PI control (loop 1) - RAT > RAT SP -> speed up
				if FIXED == 0 and 1 <= SF_SEL < 2 :
					engine.LOOP2(1,"FWU_RAT","VP_FWU_SF Speed Value","VP_FWU_RAT SP",RAT_P,RAT_I,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),1,0)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(3)
					engine.LOOP2_INIT(4)
				# 2 : RDP PI control (loop 2) - RDP > RDP SP -> speed down
				#     PV = RDP Comp PV (own RDP, adjacent compensation included)
				if FIXED == 0 and BMS_FAIL == 0 and 2 <= SF_SEL < 3 :
					engine.LOOP2(0,"VP_FWU_RDP Comp PV","VP_FWU_SF Speed Value","VP_FWU_RDP SP",SA_RDP_P,SA_RDP_I,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),2,0)
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(3)
					engine.LOOP2_INIT(4)
				# 3 : Delta T PI control (loop 3), type 1
				#     Delta T (RAT - SAT) rises when the airflow falls :
				#     Delta T < Delta T SP -> speed down, Delta T > Delta T SP -> speed up
				if FIXED == 0 and 3 <= SF_SEL < 4 :
					engine.LOOP2(1,"VP_FWU_DeltaT PV","VP_FWU_SF Speed Value","VP_FWU_DeltaT SP",DeltaT_P,DeltaT_I,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),3,0)
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(4)
				# 4 : CZT PI control (loop 4) - CZT > CZT SP -> speed up
				#     PV = CZT Comp PV (own CZT, adjacent compensation included)
				if FIXED == 0 and BMS_FAIL == 0 and 4 <= SF_SEL < 5 :
					engine.LOOP2(1,"VP_FWU_CZT Comp PV","VP_FWU_SF Speed Value","VP_FWU_CZT SP",SA_CZT_P,SA_CZT_I,0,0,60,engine.READPOINT("VP_FWU_SF Speed Min"),engine.READPOINT("VP_FWU_SF Speed Max"),4,0)
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(3)
				# BMS PLC comm fault (QTS 129~131) : VP_FWU_BMS Comm Fail Mode
				#   0 : last known speed held (no write). SF Speed Max when there is
				#       no last speed (Speed Value below SF Speed Min, e.g. 0 after
				#       a start or after all SAD were closed)
				#   1 : SF Speed Max
				#   SF Speed Value is backupEnable=1, so the held speed is kept
				#   after a DDC duplex switchover
				if BMS_FAIL == 1 :
					if engine.READPOINT("VP_FWU_BMS Comm Fail Mode") == 1 or engine.READPOINT("VP_FWU_SF Speed Value") < engine.READPOINT("VP_FWU_SF Speed Min") :
						engine.WRITEPOINT("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Max"))
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(3)
					engine.LOOP2_INIT(4)

				# Backup operation : SF speed at the maximum setting (all control modes)
				if BACKUP == 1 :
					engine.WRITEPOINT("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Max"))
					engine.LOOP2_INIT(1)
					engine.LOOP2_INIT(2)
					engine.LOOP2_INIT(3)
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
			# SF speed 0 after the PICV has closed (feedback < 5 %)
			if engine.READPOINT("FWU_PICV FEEDBACK") < 5 :
				engine.WRITEPOINT("VP_FWU_SF Speed Value", 0)
			# Close SAD-1~4 after the SF has stopped
			if engine.READPOINT("VP_FWU_SF Status") == 0 :
				engine.WRITEPOINT("FWU_SAD-1_4 COMMAND", 0)
		# Keep the auto values at P11 (held when switched to manual)
		engine.WRITEPOINT_PRI("VP_FWU_SF Speed Value", engine.READPOINT("VP_FWU_SF Speed Value"), 11)
		engine.WRITEPOINT_PRI("FWU_SAD-1_4 COMMAND", engine.READPOINT("FWU_SAD-1_4 COMMAND"), 11)
	# Manual operation
	else:
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
# =====================================================================
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

	if engine.READPOINT("VP_FWU_SF Comm Fault") == 1 :
		# Comm fault : analog output
		engine.WRITEPOINT("FWU_SF-1_4 SPEED CONTROL", sfaoset)
		engine.WRITEPOINT("FWU_SF-5_8 SPEED CONTROL", sfaoset)
		engine.WRITEPOINT("FWU SF-1.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-2.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-3.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-4.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-5.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-6.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-7.Target RPM Set", 0)
		engine.WRITEPOINT("FWU SF-8.Target RPM Set", 0)
	else :
		# Comm normal : Modbus Target RPM
		engine.WRITEPOINT("FWU_SF-1_4 SPEED CONTROL", 0)
		engine.WRITEPOINT("FWU_SF-5_8 SPEED CONTROL", 0)
		engine.WRITEPOINT("FWU SF-1.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-2.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-3.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-4.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-5.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-6.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-7.Target RPM Set", sfrpmset)
		engine.WRITEPOINT("FWU SF-8.Target RPM Set", sfrpmset)

	engine.SECTIMER(1, 0)
