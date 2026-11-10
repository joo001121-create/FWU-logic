engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Alarm-3 (Comm Fault)  (rev. 2026-11-10)
#  - SF-1~8 comm fault detection (point alarm 8 = comm fail on the fan
#    Current RPM, 10 s) and the summary VP_FWU_SF Comm Fault (any fan)
#  - ATS / flow meter comm fault (port 3, point alarm 8 on FWU-ATS.Current
#    Power / FWU-Flow.Rate, 10 s) : VP_FWU_ATS Comm Fault, VP_FWU_Flow Comm Fault
#  - Separate logic because Initialization has no free timers for 8 fans
#    (10 timers per logic). Register "Alarm-3" in DDC.xml BEFORE
#    "Initialization" (Initialization reads these points in the same scan).
#  - rev. 2026-11-10 : ATS / flow meter comm fault added (QTS ATS, flow meter)
#
# Timers (SECTIMER)
#  0~7 : SF-1~8 comm fault delay (10 s)
#  8 : ATS comm fault delay (10 s)
#  9 : Flow meter comm fault delay (10 s)
# =====================================================================

# SF-1
if engine.READPOINT_ALARM("FWU SF-1.Current RPM") == 8 :
	if engine.SECTIMER(0, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-1 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-1 Comm Fault", 0)
	engine.SECTIMER(0, 0)

# SF-2
if engine.READPOINT_ALARM("FWU SF-2.Current RPM") == 8 :
	if engine.SECTIMER(1, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-2 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-2 Comm Fault", 0)
	engine.SECTIMER(1, 0)

# SF-3
if engine.READPOINT_ALARM("FWU SF-3.Current RPM") == 8 :
	if engine.SECTIMER(2, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-3 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-3 Comm Fault", 0)
	engine.SECTIMER(2, 0)

# SF-4
if engine.READPOINT_ALARM("FWU SF-4.Current RPM") == 8 :
	if engine.SECTIMER(3, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-4 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-4 Comm Fault", 0)
	engine.SECTIMER(3, 0)

# SF-5
if engine.READPOINT_ALARM("FWU SF-5.Current RPM") == 8 :
	if engine.SECTIMER(4, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-5 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-5 Comm Fault", 0)
	engine.SECTIMER(4, 0)

# SF-6
if engine.READPOINT_ALARM("FWU SF-6.Current RPM") == 8 :
	if engine.SECTIMER(5, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-6 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-6 Comm Fault", 0)
	engine.SECTIMER(5, 0)

# SF-7
if engine.READPOINT_ALARM("FWU SF-7.Current RPM") == 8 :
	if engine.SECTIMER(6, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-7 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-7 Comm Fault", 0)
	engine.SECTIMER(6, 0)

# SF-8
if engine.READPOINT_ALARM("FWU SF-8.Current RPM") == 8 :
	if engine.SECTIMER(7, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_SF-8 Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF-8 Comm Fault", 0)
	engine.SECTIMER(7, 0)

# SF comm fault summary : any fan in comm fault
if engine.READPOINT("VP_FWU_SF-1 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-2 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-3 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-4 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-5 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-6 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-7 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-8 Comm Fault") == 1 :
	engine.WRITEPOINT("VP_FWU_SF Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_SF Comm Fault", 0)

# ATS comm fault (port 3, slave 01)
if engine.READPOINT_ALARM("FWU-ATS.Current Power") == 8 :
	if engine.SECTIMER(8, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_ATS Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_ATS Comm Fault", 0)
	engine.SECTIMER(8, 0)

# Flow meter comm fault (port 3, slave 02)
if engine.READPOINT_ALARM("FWU-Flow.Rate") == 8 :
	if engine.SECTIMER(9, 1) > 10 :
		engine.WRITEPOINT("VP_FWU_Flow Comm Fault", 1)
else :
	engine.WRITEPOINT("VP_FWU_Flow Comm Fault", 0)
	engine.SECTIMER(9, 0)
