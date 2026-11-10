engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Alarm-1  (rev. 2026-10-28)
#  - Temperature / humidity / pressure limit alarms (RAT, RAH, SAT, SAH, CZT,
#    HZT, RDP), judged 300 s after SF start
#  - SF Failure Alarm (4 or more of 8 fans failed); no per-fan Run Fail
#    alarm point is written (same as CRAH)
#      fan comm normal : Current RPM < VP_FWU_SF Failure RPM Set
#      fan comm fault  : SAFLOW DP <= 10 Pa
#  - SAT / SAH / RAT / RAH sensor failure alarms (20 s); CZT / HZT / RDP sensor
#    failure alarms are made in Alarm-2, BMS PLC comm fault in Initialization
#  - SA flow sensor failure alarm (20 s)
#  - SF comm fault : detected in Alarm-3
#  - SAD-1~4 Partial Close (some SAD closed) / Full Close (all 4 closed) /
#    Not Open / Not Close alarms
#  - PICV and flow mismatch alarm
#  - rev. 2026-10-28 (CRAH pattern) :
#      limit alarms 300 s after SF start; sensor failure 20 s delay
#      SF Failure judged here only (Command ON, speed >= Speed Min, 60 s),
#        4 or more of 8 fans failed = 50 % capacity lost
#      SAF Failure : DP < 1 Pa while a fan runs above 300 rpm, 20 s
#        (was gated on VP_FWU_SF Start FD, which is never written)
#      SAD Full Close : alarm only, SF stop in SF Control,
#        no Command / Speed Value write here
#      PICV "open but no flow" judged only while CHW supply is normal
#        (VP_FWU_Chilled Water Supply Condition = 1)
#  - rev. 2026-10-31 : CZT / HZT / RDP limit alarms added (judged on the Max / Min
#      of the healthy sensors, hysteresis 0.5 C / 0.5 Pa)
#
# Timers (SECTIMER)
#  0 : limit alarm start delay after SF start (300 s)
#  1 : SF failure judgement delay (60 s)
#  2 : SAT sensor failure delay (20 s)
#  3 : SAH sensor failure delay (20 s)
#  4 : RAT sensor failure delay (20 s)
#  5 : RAH sensor failure delay (20 s)
#  6 : SAF sensor failure delay (20 s)
#  7 : SAD Not Open delay (120 s)
#  8 : SAD Not Close delay (120 s)
#  9 : PICV command / feedback deviation delay (40 s)
# =====================================================================

# =====================================================================
# Temperature / humidity limit alarms (300 s after SF start)
#  - Temperature : hysteresis 0.5 C, Humidity : hysteresis 5 %
# =====================================================================
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.SECTIMER(0, 1) > 300 :
	# RAT High / Low
	if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT High Alarm SP") :
		engine.WRITEPOINT("VP_FWU_RAT High Alarm", 1)
	if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT High Alarm SP") - 0.5 :
		engine.WRITEPOINT("VP_FWU_RAT High Alarm", 0)

	if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT Low Alarm SP") :
		engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 1)
	if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT Low Alarm SP") + 0.5 :
		engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 0)

	# RAH High / Low
	if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH High Alarm SP") :
		engine.WRITEPOINT("VP_FWU_RAH High Alarm", 1)
	if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH High Alarm SP") - 5 :
		engine.WRITEPOINT("VP_FWU_RAH High Alarm", 0)

	if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH Low Alarm SP") :
		engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 1)
	if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH Low Alarm SP") + 5 :
		engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 0)

	# SAT High / Low
	if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT High Alarm SP") :
		engine.WRITEPOINT("VP_FWU_SAT High Alarm", 1)
	if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT High Alarm SP") - 0.5 :
		engine.WRITEPOINT("VP_FWU_SAT High Alarm", 0)

	if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT Low Alarm SP") :
		engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 1)
	if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT Low Alarm SP") + 0.5 :
		engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 0)

	# SAH High / Low
	if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH High Alarm SP") :
		engine.WRITEPOINT("VP_FWU_SAH High Alarm", 1)
	if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH High Alarm SP") - 5 :
		engine.WRITEPOINT("VP_FWU_SAH High Alarm", 0)

	if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH Low Alarm SP") :
		engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 1)
	if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH Low Alarm SP") + 5 :
		engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 0)

	# CZT High / Low (Max / Min of the healthy sensors, same limits as RAT)
	if engine.READPOINT("VP_FWU_CZT PV Valid") == 1 :
		if engine.READPOINT("VP_FWU_CZT Max") > engine.READPOINT("VP_FWU_CZT High Alarm SP") :
			engine.WRITEPOINT("VP_FWU_CZT High Alarm", 1)
		if engine.READPOINT("VP_FWU_CZT Max") < engine.READPOINT("VP_FWU_CZT High Alarm SP") - 0.5 :
			engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
		if engine.READPOINT("VP_FWU_CZT Min") < engine.READPOINT("VP_FWU_CZT Low Alarm SP") :
			engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 1)
		if engine.READPOINT("VP_FWU_CZT Min") > engine.READPOINT("VP_FWU_CZT Low Alarm SP") + 0.5 :
			engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)
	else :
		engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
		engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)

	# HZT High / Low
	if engine.READPOINT("VP_FWU_HZT PV Valid") == 1 :
		if engine.READPOINT("VP_FWU_HZT Max") > engine.READPOINT("VP_FWU_HZT High Alarm SP") :
			engine.WRITEPOINT("VP_FWU_HZT High Alarm", 1)
		if engine.READPOINT("VP_FWU_HZT Max") < engine.READPOINT("VP_FWU_HZT High Alarm SP") - 0.5 :
			engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
		if engine.READPOINT("VP_FWU_HZT Min") < engine.READPOINT("VP_FWU_HZT Low Alarm SP") :
			engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 1)
		if engine.READPOINT("VP_FWU_HZT Min") > engine.READPOINT("VP_FWU_HZT Low Alarm SP") + 0.5 :
			engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)
	else :
		engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
		engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)

	# RDP High / Low (limits 10 / 3 Pa, hysteresis 0.5 Pa)
	if engine.READPOINT("VP_FWU_RDP PV Valid") == 1 :
		if engine.READPOINT("VP_FWU_RDP Max") > engine.READPOINT("VP_FWU_RDP High Alarm SP") :
			engine.WRITEPOINT("VP_FWU_RDP High Alarm", 1)
		if engine.READPOINT("VP_FWU_RDP Max") < engine.READPOINT("VP_FWU_RDP High Alarm SP") - 0.5 :
			engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
		if engine.READPOINT("VP_FWU_RDP Min") < engine.READPOINT("VP_FWU_RDP Low Alarm SP") :
			engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 1)
		if engine.READPOINT("VP_FWU_RDP Min") > engine.READPOINT("VP_FWU_RDP Low Alarm SP") + 0.5 :
			engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)
	else :
		engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
		engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)

# SF stopped : timer and all limit alarms reset
if engine.READPOINT("VP_FWU_SF Status") == 0 :
	engine.SECTIMER(0, 0)
	engine.WRITEPOINT("VP_FWU_RAT High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_RAH High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_SAT High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_SAH High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)
	engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
	engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)

# =====================================================================
# SF Failure (Command ON, Speed Value >= Speed Min, after 60 s)
#  - Each fan (internal judgement only) :
#      fan comm normal : Current RPM < VP_FWU_SF Failure RPM Set
#      fan comm fault  : SAFLOW DP <= 10 Pa
#  - SF Failure Alarm : 4 or more of SF-1~8 failed (50 % capacity)
# =====================================================================
if engine.READPOINT("VP_FWU_Command") == 1 and engine.READPOINT("VP_FWU_SF Speed Value") >= engine.READPOINT("VP_FWU_SF Speed Min") :
	if engine.SECTIMER(1, 1) > 60 :
		FAIL_RPM = engine.READPOINT("VP_FWU_SF Failure RPM Set")
		SF_DP_LOW = engine.READPOINT("FWU_SAFLOW DP") <= 10

		# SF-1
		if engine.READPOINT("VP_FWU_SF-1 Comm Fault") == 0 :
			SF1_FAIL = engine.READPOINT("FWU SF-1.Current RPM") < FAIL_RPM
		else :
			SF1_FAIL = SF_DP_LOW

		# SF-2
		if engine.READPOINT("VP_FWU_SF-2 Comm Fault") == 0 :
			SF2_FAIL = engine.READPOINT("FWU SF-2.Current RPM") < FAIL_RPM
		else :
			SF2_FAIL = SF_DP_LOW

		# SF-3
		if engine.READPOINT("VP_FWU_SF-3 Comm Fault") == 0 :
			SF3_FAIL = engine.READPOINT("FWU SF-3.Current RPM") < FAIL_RPM
		else :
			SF3_FAIL = SF_DP_LOW

		# SF-4
		if engine.READPOINT("VP_FWU_SF-4 Comm Fault") == 0 :
			SF4_FAIL = engine.READPOINT("FWU SF-4.Current RPM") < FAIL_RPM
		else :
			SF4_FAIL = SF_DP_LOW

		# SF-5
		if engine.READPOINT("VP_FWU_SF-5 Comm Fault") == 0 :
			SF5_FAIL = engine.READPOINT("FWU SF-5.Current RPM") < FAIL_RPM
		else :
			SF5_FAIL = SF_DP_LOW

		# SF-6
		if engine.READPOINT("VP_FWU_SF-6 Comm Fault") == 0 :
			SF6_FAIL = engine.READPOINT("FWU SF-6.Current RPM") < FAIL_RPM
		else :
			SF6_FAIL = SF_DP_LOW

		# SF-7
		if engine.READPOINT("VP_FWU_SF-7 Comm Fault") == 0 :
			SF7_FAIL = engine.READPOINT("FWU SF-7.Current RPM") < FAIL_RPM
		else :
			SF7_FAIL = SF_DP_LOW

		# SF-8
		if engine.READPOINT("VP_FWU_SF-8 Comm Fault") == 0 :
			SF8_FAIL = engine.READPOINT("FWU SF-8.Current RPM") < FAIL_RPM
		else :
			SF8_FAIL = SF_DP_LOW

		# Failed fan count (no per-fan alarm point, same as CRAH)
		SF_FAIL_CNT = 0
		if SF1_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF2_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF3_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF4_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF5_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF6_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF7_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1
		if SF8_FAIL :
			SF_FAIL_CNT = SF_FAIL_CNT + 1

		# SF Failure Alarm : 4 or more of 8 fans failed (50 % capacity)
		if SF_FAIL_CNT >= 4 :
			engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 1)
		else :
			engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 0)
else :
	engine.SECTIMER(1, 0)
	engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 0)

# =====================================================================
# Sensor failure (20 s)
#  - SAT / RAT < 0 C (0 V = -20 C, wire break)
#  - SAH / RAH < 5 %
#  (PICV Control : PICV 100 % while the SAT Failure Alarm is ON)
# =====================================================================
# SAT
if engine.READPOINT("FWU_SAT") < 0 :
	if engine.SECTIMER(2, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_SAT Failure Alarm", 1)
else :
	engine.SECTIMER(2, 0)
	engine.WRITEPOINT("VP_FWU_SAT Failure Alarm", 0)

# SAH
if engine.READPOINT("FWU_SAH") < 5 :
	if engine.SECTIMER(3, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_SAH Failure Alarm", 1)
else :
	engine.SECTIMER(3, 0)
	engine.WRITEPOINT("VP_FWU_SAH Failure Alarm", 0)

# RAT
if engine.READPOINT("FWU_RAT") < 0 :
	if engine.SECTIMER(4, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_RAT Failure Alarm", 1)
else :
	engine.SECTIMER(4, 0)
	engine.WRITEPOINT("VP_FWU_RAT Failure Alarm", 0)

# RAH
if engine.READPOINT("FWU_RAH") < 5 :
	if engine.SECTIMER(5, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_RAH Failure Alarm", 1)
else :
	engine.SECTIMER(5, 0)
	engine.WRITEPOINT("VP_FWU_RAH Failure Alarm", 0)

# SA flow sensor : DP < 1 Pa while any of the 8 fans runs above 300 rpm, 20 s
if engine.READPOINT("FWU_SAFLOW DP") < 1 and engine.MAX(engine.MAX(engine.READPOINT("FWU SF-1.Current RPM"), engine.READPOINT("FWU SF-2.Current RPM"), engine.READPOINT("FWU SF-3.Current RPM"), engine.READPOINT("FWU SF-4.Current RPM")), engine.MAX(engine.READPOINT("FWU SF-5.Current RPM"), engine.READPOINT("FWU SF-6.Current RPM"), engine.READPOINT("FWU SF-7.Current RPM"), engine.READPOINT("FWU SF-8.Current RPM"))) > 300 :
	if engine.SECTIMER(6, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_SAF Failure Alarm", 1)
else :
	engine.SECTIMER(6, 0)
	engine.WRITEPOINT("VP_FWU_SAF Failure Alarm", 0)

# =====================================================================
# SAD Partial Close Alarm (alarm only, the SF keeps running)
#  - SF running and at least one, but not all, of SAD-1~4 close status ON
#    (no delay; all closed = SAD Full Close Alarm, no Partial Close Alarm)
# =====================================================================
SAD_ALL_CLOSE = engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1
SAD_ANY_CLOSE = engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1
if engine.READPOINT("VP_FWU_SF Status") == 1 :
	if SAD_ANY_CLOSE and not SAD_ALL_CLOSE :
		engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 1)
	else :
		engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 0)
else :
	engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 0)

# =====================================================================
# SAD Full Close Alarm (SF stop is done in SF Control)
#  - Set   : SF running and SAD-1~4 close status all ON (no delay)
#  - Held  : while the SAD command is ON and all SAD stay closed
#            (the SF has stopped, so SF Status is no longer 1)
#  - Reset : a SAD leaves the closed position or the SAD command is OFF
# =====================================================================
if SAD_ALL_CLOSE and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and (engine.READPOINT("VP_FWU_SF Status") == 1 or engine.READPOINT("VP_FWU_SAD Full Close Alarm") == 1) :
	engine.WRITEPOINT("VP_FWU_SAD Full Close Alarm", 1)
else :
	engine.WRITEPOINT("VP_FWU_SAD Full Close Alarm", 0)

# =====================================================================
# SAD Not Open Alarm (Timer 7)
#  - SAD command ON and SF not running for 120 s,
#    and any of SAD-1~4 open status OFF -> alarm
#  - Reset when the SAD command is OFF or the SF is running
# =====================================================================
if engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("VP_FWU_SF Status") == 0 :
	engine.SECTIMER(8, 0)
	if engine.SECTIMER(7, 1) > 120 :
		if engine.READPOINT("FWU_SAD-1 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-2 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-3 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-4 OPEN STATUS") != 1 :
			engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 1)
		else :
			engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
	else :
		engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
else :
	engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
	engine.SECTIMER(7, 0)

# =====================================================================
# SAD Not Close Alarm (Timer 8)
#  - SAD command OFF for 120 s and any of SAD-1~4 close status OFF -> alarm
#  - Reset when the SAD command is ON
# =====================================================================
if engine.READPOINT("FWU_SAD-1_4 COMMAND") == 0 :
	engine.SECTIMER(7, 0)
	if engine.SECTIMER(8, 1) > 120 :
		if engine.READPOINT("FWU_SAD-1 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-2 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-3 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-4 CLOSE STATUS") != 1 :
			engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 1)
		else :
			engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
	else :
		engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
else :
	engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
	engine.SECTIMER(8, 0)

# =====================================================================
# PICV / flow mismatch alarm
#  - Command within feedback +/- 30 % (valve follows the command) :
#      feedback > 30 % and flow < 30 LPM : alarm (open but no flow)
#        only while chilled water supply is normal
#        (VP_FWU_Chilled Water Supply Condition = 1, written by the BMS),
#        to avoid alarms on every FWU when the chilled water plant stops
#      feedback < 1 % and flow > 10 LPM : alarm (closed but flow, passing)
#      otherwise : alarm reset (no delay)
#  - Command out of feedback +/- 30 % for 40 s : alarm (actuator fault)
# =====================================================================
if engine.READPOINT("FWU_PICV FEEDBACK") - 30 < engine.READPOINT("FWU_PICV CONTROL") < engine.READPOINT("FWU_PICV FEEDBACK") + 30 :

	# Open but no flow (chilled water supply normal only)
	if engine.READPOINT("VP_FWU_Chilled Water Supply Condition") == 1 and engine.READPOINT("FWU_PICV FEEDBACK") > 30 and engine.READPOINT("FWU-Flow.Rate") < 30 :
		engine.WRITEPOINT("VP_FWU_PICV_Alarm", 1)
	else :
		# Closed but flow (passing)
		if engine.READPOINT("FWU_PICV FEEDBACK") < 1 and engine.READPOINT("FWU-Flow.Rate") > 10 :
			engine.WRITEPOINT("VP_FWU_PICV_Alarm", 1)
		else :
			engine.WRITEPOINT("VP_FWU_PICV_Alarm", 0)
	engine.SECTIMER(9, 0)

# Command / feedback mismatch for 40 s : actuator fault
else :
	if engine.SECTIMER(9, 1) > 40 and engine.READPOINT("VP_FWU_PICV_Alarm") == 0 :
		engine.WRITEPOINT("VP_FWU_PICV_Alarm", 1)
		engine.SECTIMER(9, 0)
