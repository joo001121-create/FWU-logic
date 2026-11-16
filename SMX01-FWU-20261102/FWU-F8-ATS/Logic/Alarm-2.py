engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Alarm-2  (rev. 2026-10-31)
#  - CZT / HZT / RDP sensor failure alarms (BMS PLC sensors), one timer per sensor
#      CZT-1~4, HZT-1~2 : value < 0 C for 20 s (same as RAT)
#      RDP-1~2          : value <= 0 Pa for 20 s
#  - The failure alarms are used in Initialization (next scan) : a failed sensor
#    is excluded from the Avg / Max / Min and from the control PV
#  - Alarm-1.py has no free timer, so these alarms are in this separate logic.
#    Register "Alarm-2" in DDC.xml after "Alarm-1".
#
# Timers (SECTIMER)
#  0 : CZT-1 failure delay (20 s)
#  1 : CZT-2 failure delay (20 s)
#  2 : CZT-3 failure delay (20 s)
#  3 : CZT-4 failure delay (20 s)
#  4 : HZT-1 failure delay (20 s)
#  5 : HZT-2 failure delay (20 s)
#  6 : RDP-1 failure delay (20 s)
#  7 : RDP-2 failure delay (20 s)
# =====================================================================

# CZT sensor failure (< 0, 20 s)
# CZT-1
if engine.READPOINT("VP_FWU_CZT-1") < 0 :
	if engine.SECTIMER(0, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_CZT-1 Failure Alarm", 1)
else :
	engine.SECTIMER(0, 0)
	engine.WRITEPOINT("VP_FWU_CZT-1 Failure Alarm", 0)

# CZT-2
if engine.READPOINT("VP_FWU_CZT-2") < 0 :
	if engine.SECTIMER(1, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_CZT-2 Failure Alarm", 1)
else :
	engine.SECTIMER(1, 0)
	engine.WRITEPOINT("VP_FWU_CZT-2 Failure Alarm", 0)

# CZT-3
if engine.READPOINT("VP_FWU_CZT-3") < 0 :
	if engine.SECTIMER(2, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_CZT-3 Failure Alarm", 1)
else :
	engine.SECTIMER(2, 0)
	engine.WRITEPOINT("VP_FWU_CZT-3 Failure Alarm", 0)

# CZT-4
if engine.READPOINT("VP_FWU_CZT-4") < 0 :
	if engine.SECTIMER(3, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_CZT-4 Failure Alarm", 1)
else :
	engine.SECTIMER(3, 0)
	engine.WRITEPOINT("VP_FWU_CZT-4 Failure Alarm", 0)

# HZT sensor failure (< 0, 20 s)
# HZT-1
if engine.READPOINT("VP_FWU_HZT-1") < 0 :
	if engine.SECTIMER(4, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_HZT-1 Failure Alarm", 1)
else :
	engine.SECTIMER(4, 0)
	engine.WRITEPOINT("VP_FWU_HZT-1 Failure Alarm", 0)

# HZT-2
if engine.READPOINT("VP_FWU_HZT-2") < 0 :
	if engine.SECTIMER(5, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_HZT-2 Failure Alarm", 1)
else :
	engine.SECTIMER(5, 0)
	engine.WRITEPOINT("VP_FWU_HZT-2 Failure Alarm", 0)

# RDP sensor failure (<= 0, 20 s)
# RDP-1
if engine.READPOINT("VP_FWU_RDP-1") <= 0 :
	if engine.SECTIMER(6, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_RDP-1 Failure Alarm", 1)
else :
	engine.SECTIMER(6, 0)
	engine.WRITEPOINT("VP_FWU_RDP-1 Failure Alarm", 0)

# RDP-2
if engine.READPOINT("VP_FWU_RDP-2") <= 0 :
	if engine.SECTIMER(7, 1) > 20 :
		engine.WRITEPOINT("VP_FWU_RDP-2 Failure Alarm", 1)
else :
	engine.SECTIMER(7, 0)
	engine.WRITEPOINT("VP_FWU_RDP-2 Failure Alarm", 0)
