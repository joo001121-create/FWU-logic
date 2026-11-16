engine = ddc_logic()

# =====================================================================
# FWU-F8-ATS : Initialization  (rev. 2026-11-13)
#  - BMS PLC comm status (heartbeat unchanged for 30 s = comm fault, latched;
#    cleared by the operator with BMS PLC Comm Reset)
#  - CZT / HZT / RDP Avg, Max, Min of the healthy sensors only (sensor failure
#    alarms come from Alarm-2); CZH Avg, Max, Min (zone values from the BMS PLC)
#  - Zone PV selection and PV Valid (CZT / HZT Avg or Max, RDP Avg or Min)
#  - Delta T PV (RAT - SAT)
#  - SF-1~8 comm fault : detected in "Alarm-3"
#  - SF Status : ON when any of the 8 fans is running, judged per fan
#      fan comm normal : Current RPM > VP_FWU_SF Failure RPM Set
#      fan comm fault  : RPM is not available -> SAFLOW DP > VP_FWU_SF Run DP Set
#      SF Status changes only when the new state lasts 5 s (ON and OFF)
#  - SA flow calculation (DP < 5 Pa or SF stopped : 0)
#  - Local / Remote command selection
#  - SF Max RPM (design RPM x VP_FWU_SF Max RPM Ratio, limited to
#    VP_FWU_SF Rated Max RPM)
#  - rev. 2026-10-31 (F8) : 8 fans; SF comm fault detection moved to "Alarm-3"
#  - rev. 2026-10-28 (CRAH pattern) :
#      SF comm fault moved here from Alarm (10 s delay, summary = any fan)
#      SF Status uses SAFLOW DP for a fan in comm fault
#      SA flow is calculated only when DP >= 5 Pa (no sqrt of a negative DP)
#      low-flow SF Failure Alarm removed (SF Failure is judged in Alarm only)
#  - rev. 2026-10-28 (2) : SF Status judged per fan (comm normal / comm fault)
#      with 5 s ON/OFF confirmation (CRAC pattern)
#  - rev. 2026-10-31 : BMS PLC comm status, zone sensor failure exclusion
#      (failure alarms from Alarm-2, used one scan later),
#      adjacent zone compensation, RDP Select 1 = Min (was Max),
#      zone PV selection moved here from SF Control / PICV Control
#  - rev. 2026-11-12 : adjacent zone compensation removed (upper control item;
#      points kept, not used). CZT / RDP control modes use CZT PV / RDP PV.
#      Delta T PV is made only here (the copy in SF Control removed)
#  - rev. 2026-11-13 : model dependent values moved to setting points
#      (defaults = the former fixed values) : fan running DP 10 Pa ->
#      VP_FWU_SF Run DP Set, SA flow coefficient 235.751976 -> VP_FWU_SA Flow Coef,
#      SF Max RPM 110 % / 1920 rpm -> VP_FWU_SF Max RPM Ratio / Rated Max RPM
#
# Timers (SECTIMER)
#  (1~4 : not used, SF-1~8 comm fault delays are in "Alarm-3")
#  5 : SF Status confirmation (5 s)
#  6 : BMS PLC heartbeat no-change delay (30 s)
#  7 : BMS PLC Comm Reset hold (5 s)
# =====================================================================

# =====================================================================
# BMS PLC communication (the CZT / HZT / RDP values come from the BMS PLC)
#  - VP_FWU_BMS PLC Heartbeat is changed periodically by the BMS PLC.
#    No change for 30 s -> VP_FWU_BMS PLC Comm Fault = 1 (latched)
#  - The return to normal is decided by the operator : VP_FWU_BMS PLC Comm Reset
#    = 1 clears the comm fault only while the heartbeat is changing; the Reset
#    is held 5 s (HMI read-back) and then returned to 0 (P11)
#  - Comm fault : the BMS PLC values are not used (treated as failed)
# =====================================================================
HB = engine.READPOINT("VP_FWU_BMS PLC Heartbeat")
if HB != engine.READPOINT("VP_FWU_BMS PLC Heartbeat Prev") :
	engine.WRITEPOINT("VP_FWU_BMS PLC Heartbeat Prev", HB)
	engine.SECTIMER(6, 0)
	HB_OK = 1
else :
	if engine.SECTIMER(6, 1) > 30 :
		HB_OK = 0
		engine.WRITEPOINT("VP_FWU_BMS PLC Comm Fault", 1)
	else :
		HB_OK = 1

# Operator reset (only while the heartbeat is changing)
if engine.READPOINT("VP_FWU_BMS PLC Comm Reset") == 1 :
	if HB_OK == 1 :
		engine.WRITEPOINT("VP_FWU_BMS PLC Comm Fault", 0)
	if engine.SECTIMER(7, 1) > 5 :
		engine.WRITEPOINT_PRI("VP_FWU_BMS PLC Comm Reset", 0, 11)
		engine.SECTIMER(7, 0)
else :
	engine.SECTIMER(7, 0)

if engine.READPOINT("VP_FWU_BMS PLC Comm Fault") == 1 :
	BMS_OK = 0
else :
	BMS_OK = 1

# CZT (cold zone temperature) : CZT-1~4, failure < 0 C (same as RAT)
czt1= engine.READPOINT("VP_FWU_CZT-1")
czt2= engine.READPOINT("VP_FWU_CZT-2")
czt3= engine.READPOINT("VP_FWU_CZT-3")
czt4= engine.READPOINT("VP_FWU_CZT-4")
# CZT sensor failure alarms are made in Alarm-2 (one timer per sensor)

# CZT Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
CZT_CNT = 0
CZT_SUM = 0
CZT_MAXV = -1000
CZT_MINV = 1000
if BMS_OK == 1 and engine.READPOINT("VP_FWU_CZT-1 Failure Alarm") == 0 :
	CZT_CNT = CZT_CNT + 1
	CZT_SUM = CZT_SUM + czt1
	CZT_MAXV = engine.MAX(CZT_MAXV, czt1)
	CZT_MINV = engine.MIN(CZT_MINV, czt1)
if BMS_OK == 1 and engine.READPOINT("VP_FWU_CZT-2 Failure Alarm") == 0 :
	CZT_CNT = CZT_CNT + 1
	CZT_SUM = CZT_SUM + czt2
	CZT_MAXV = engine.MAX(CZT_MAXV, czt2)
	CZT_MINV = engine.MIN(CZT_MINV, czt2)
if BMS_OK == 1 and engine.READPOINT("VP_FWU_CZT-3 Failure Alarm") == 0 :
	CZT_CNT = CZT_CNT + 1
	CZT_SUM = CZT_SUM + czt3
	CZT_MAXV = engine.MAX(CZT_MAXV, czt3)
	CZT_MINV = engine.MIN(CZT_MINV, czt3)
if BMS_OK == 1 and engine.READPOINT("VP_FWU_CZT-4 Failure Alarm") == 0 :
	CZT_CNT = CZT_CNT + 1
	CZT_SUM = CZT_SUM + czt4
	CZT_MAXV = engine.MAX(CZT_MAXV, czt4)
	CZT_MINV = engine.MIN(CZT_MINV, czt4)
if CZT_CNT > 0 :
	engine.WRITEPOINT("VP_FWU_CZT Avg", CZT_SUM / CZT_CNT)
	engine.WRITEPOINT("VP_FWU_CZT Max", CZT_MAXV)
	engine.WRITEPOINT("VP_FWU_CZT Min", CZT_MINV)
	engine.WRITEPOINT("VP_FWU_CZT PV Valid", 1)
else :
	engine.WRITEPOINT("VP_FWU_CZT Avg", 0)
	engine.WRITEPOINT("VP_FWU_CZT Max", 0)
	engine.WRITEPOINT("VP_FWU_CZT Min", 0)
	engine.WRITEPOINT("VP_FWU_CZT PV Valid", 0)

# HZT (hot zone temperature) : HZT-1~2, failure < 0 C (same as RAT)
hzt1= engine.READPOINT("VP_FWU_HZT-1")
hzt2= engine.READPOINT("VP_FWU_HZT-2")
# HZT sensor failure alarms are made in Alarm-2 (one timer per sensor)

# HZT Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
HZT_CNT = 0
HZT_SUM = 0
HZT_MAXV = -1000
HZT_MINV = 1000
if BMS_OK == 1 and engine.READPOINT("VP_FWU_HZT-1 Failure Alarm") == 0 :
	HZT_CNT = HZT_CNT + 1
	HZT_SUM = HZT_SUM + hzt1
	HZT_MAXV = engine.MAX(HZT_MAXV, hzt1)
	HZT_MINV = engine.MIN(HZT_MINV, hzt1)
if BMS_OK == 1 and engine.READPOINT("VP_FWU_HZT-2 Failure Alarm") == 0 :
	HZT_CNT = HZT_CNT + 1
	HZT_SUM = HZT_SUM + hzt2
	HZT_MAXV = engine.MAX(HZT_MAXV, hzt2)
	HZT_MINV = engine.MIN(HZT_MINV, hzt2)
if HZT_CNT > 0 :
	engine.WRITEPOINT("VP_FWU_HZT Avg", HZT_SUM / HZT_CNT)
	engine.WRITEPOINT("VP_FWU_HZT Max", HZT_MAXV)
	engine.WRITEPOINT("VP_FWU_HZT Min", HZT_MINV)
	engine.WRITEPOINT("VP_FWU_HZT PV Valid", 1)
else :
	engine.WRITEPOINT("VP_FWU_HZT Avg", 0)
	engine.WRITEPOINT("VP_FWU_HZT Max", 0)
	engine.WRITEPOINT("VP_FWU_HZT Min", 0)
	engine.WRITEPOINT("VP_FWU_HZT PV Valid", 0)

# RDP (room differential pressure) : RDP-1~2, failure <= 0 Pa
rdp1= engine.READPOINT("VP_FWU_RDP-1")
rdp2= engine.READPOINT("VP_FWU_RDP-2")
# RDP sensor failure alarms are made in Alarm-2 (one timer per sensor)

# RDP Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
RDP_CNT = 0
RDP_SUM = 0
RDP_MAXV = -1000
RDP_MINV = 1000
if BMS_OK == 1 and engine.READPOINT("VP_FWU_RDP-1 Failure Alarm") == 0 :
	RDP_CNT = RDP_CNT + 1
	RDP_SUM = RDP_SUM + rdp1
	RDP_MAXV = engine.MAX(RDP_MAXV, rdp1)
	RDP_MINV = engine.MIN(RDP_MINV, rdp1)
if BMS_OK == 1 and engine.READPOINT("VP_FWU_RDP-2 Failure Alarm") == 0 :
	RDP_CNT = RDP_CNT + 1
	RDP_SUM = RDP_SUM + rdp2
	RDP_MAXV = engine.MAX(RDP_MAXV, rdp2)
	RDP_MINV = engine.MIN(RDP_MINV, rdp2)
if RDP_CNT > 0 :
	engine.WRITEPOINT("VP_FWU_RDP Avg", RDP_SUM / RDP_CNT)
	engine.WRITEPOINT("VP_FWU_RDP Max", RDP_MAXV)
	engine.WRITEPOINT("VP_FWU_RDP Min", RDP_MINV)
	engine.WRITEPOINT("VP_FWU_RDP PV Valid", 1)
else :
	engine.WRITEPOINT("VP_FWU_RDP Avg", 0)
	engine.WRITEPOINT("VP_FWU_RDP Max", 0)
	engine.WRITEPOINT("VP_FWU_RDP Min", 0)
	engine.WRITEPOINT("VP_FWU_RDP PV Valid", 0)

# CZH (cold zone humidity) : Avg / Max / Min of CZH-1~4
czh1= engine.READPOINT("VP_FWU_CZH-1")
czh2= engine.READPOINT("VP_FWU_CZH-2")
czh3= engine.READPOINT("VP_FWU_CZH-3")
czh4= engine.READPOINT("VP_FWU_CZH-4")
engine.WRITEPOINT("VP_FWU_CZH Avg", (czh1 + czh2 + czh3 + czh4) / 4)
engine.WRITEPOINT("VP_FWU_CZH Max", engine.MAX(czh1, czh2, czh3, czh4))
engine.WRITEPOINT("VP_FWU_CZH Min", engine.MIN(czh1, czh2, czh3, czh4))

# =====================================================================
# Zone PV selection (healthy sensors only; PV Valid = 0 when no healthy
# sensor is left or the BMS PLC is in comm fault -> SF Control uses fixed value)
#  - CZT / HZT : Select 0 = Avg, 1 = Max
#  - RDP       : Select 0 = Avg, 1 = Min
# =====================================================================
if engine.READPOINT("VP_FWU_CZT PV Valid") == 1 :
	if engine.READPOINT("VP_FWU_CZT Select") == 0 :
		engine.WRITEPOINT("VP_FWU_CZT PV", engine.READPOINT("VP_FWU_CZT Avg"))
	else :
		engine.WRITEPOINT("VP_FWU_CZT PV", engine.READPOINT("VP_FWU_CZT Max"))
else :
	engine.WRITEPOINT("VP_FWU_CZT PV", 0)

if engine.READPOINT("VP_FWU_HZT PV Valid") == 1 :
	if engine.READPOINT("VP_FWU_HZT Select") == 0 :
		engine.WRITEPOINT("VP_FWU_HZT PV", engine.READPOINT("VP_FWU_HZT Avg"))
	else :
		engine.WRITEPOINT("VP_FWU_HZT PV", engine.READPOINT("VP_FWU_HZT Max"))
else :
	engine.WRITEPOINT("VP_FWU_HZT PV", 0)

if engine.READPOINT("VP_FWU_RDP PV Valid") == 1 :
	if engine.READPOINT("VP_FWU_RDP Select") == 0 :
		engine.WRITEPOINT("VP_FWU_RDP PV", engine.READPOINT("VP_FWU_RDP Avg"))
	else :
		engine.WRITEPOINT("VP_FWU_RDP PV", engine.READPOINT("VP_FWU_RDP Min"))
else :
	engine.WRITEPOINT("VP_FWU_RDP PV", 0)

# Adjacent zone compensation : removed from this logic (rev. 2026-11-12).
#  To be done by the upper control (BMS / DCIM) when needed. The points stay
#  defined but are not used here : VP_FWU_CZT Adj-1~4, VP_FWU_RDP Adj-1~2,
#  VP_FWU_Adj Comp Weight, VP_FWU_CZT / RDP Comp Own Margin,
#  VP_FWU_CZT / RDP Comp PV. The CZT / RDP control modes use CZT PV / RDP PV.

# Delta T PV = RAT - SAT (used by the SF Control Delta T mode)
engine.WRITEPOINT("VP_FWU_DeltaT PV", engine.READPOINT("FWU_RAT") - engine.READPOINT("FWU_SAT"))

# =====================================================================
# SF Comm Fault points are written in "Alarm-3" (SF-1~8 and summary)
# =====================================================================
SF1_CF = engine.READPOINT("VP_FWU_SF-1 Comm Fault")
SF2_CF = engine.READPOINT("VP_FWU_SF-2 Comm Fault")
SF3_CF = engine.READPOINT("VP_FWU_SF-3 Comm Fault")
SF4_CF = engine.READPOINT("VP_FWU_SF-4 Comm Fault")
SF5_CF = engine.READPOINT("VP_FWU_SF-5 Comm Fault")
SF6_CF = engine.READPOINT("VP_FWU_SF-6 Comm Fault")
SF7_CF = engine.READPOINT("VP_FWU_SF-7 Comm Fault")
SF8_CF = engine.READPOINT("VP_FWU_SF-8 Comm Fault")

# =====================================================================
# SF Status : ON when any fan is running (per fan)
#  - Fan comm normal : Current RPM > VP_FWU_SF Failure RPM Set
#  - Fan comm fault  : RPM is not available -> SAFLOW DP > VP_FWU_SF Run DP Set
# =====================================================================
FAIL_RPM = engine.READPOINT("VP_FWU_SF Failure RPM Set")
SAFLOW_DP = engine.READPOINT("FWU_SAFLOW DP")
RUN_DP = engine.READPOINT("VP_FWU_SF Run DP Set")
SF_RUN = 0

# SF-1
if SF1_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-1.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-2
if SF2_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-2.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-3
if SF3_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-3.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-4
if SF4_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-4.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-5
if SF5_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-5.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-6
if SF6_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-6.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-7
if SF7_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-7.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF-8
if SF8_CF == 1 :
	if SAFLOW_DP > RUN_DP :
		SF_RUN = 1
else :
	if engine.READPOINT("FWU SF-8.Current RPM") > FAIL_RPM :
		SF_RUN = 1

# SF Status with 5 s confirmation (ON and OFF) :
#  the status changes only when the new state lasts 5 s (timer 5)
if SF_RUN != engine.READPOINT("VP_FWU_SF Status") :
	if engine.SECTIMER(5, 1) > 5 :
		engine.WRITEPOINT("VP_FWU_SF Status", SF_RUN)
		engine.SECTIMER(5, 0)
else :
	engine.SECTIMER(5, 0)

# =====================================================================
# SA flow (CMH) = VP_FWU_SA Flow Coef (235.751976) x sqrt(SAFLOW DP) x SAF VA-2
#  - SF stopped or DP < 5 Pa : 0
# =====================================================================
if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.READPOINT("FWU_SAFLOW DP") >= 5 :
	saflow = engine.READPOINT("VP_FWU_SA Flow Coef") * engine.READPOINT("FWU_SAFLOW DP") ** 0.5 * engine.READPOINT("VP_FWU_SAF VA-2")
	engine.WRITEPOINT("VP_FWU_SA Flow", saflow)
else :
	engine.WRITEPOINT("VP_FWU_SA Flow", 0)

# =====================================================================
# Local / Remote selection (REMOTE SELECTION DI)
#  - Remote (1) : BMS command (VP_FWU_Command) is used, copied to Command-HMI
#  - Local  (0) : touch screen command (VP_FWU_Command-HMI) is used, copied to Command
# =====================================================================
if engine.READPOINT("REMOTE SELECTION") == 1 :
	engine.RELEASE_PRI("VP_FWU_Command", 5)
	engine.WRITEPOINT("VP_FWU_Command-HMI", engine.READPOINT("VP_FWU_Command"))
	engine.WRITEPOINT_PRI("VP_FWU_Command-HMI", engine.READPOINT("VP_FWU_Command"), 11)
else :
	engine.RELEASE_PRI("VP_FWU_Command-HMI", 5)
	engine.WRITEPOINT("VP_FWU_Command", engine.READPOINT("VP_FWU_Command-HMI"))
	engine.WRITEPOINT_PRI("VP_FWU_Command", engine.READPOINT("VP_FWU_Command-HMI"), 11)

# SF Max RPM = Design RPM x Max RPM Ratio (110 %), limited to the fan rated max (1920 rpm)
engine.WRITEPOINT("VP_FWU_SF Max RPM", engine.MIN(engine.READPOINT("VP_FWU_SF Design RPM") * engine.READPOINT("VP_FWU_SF Max RPM Ratio") / 100, engine.READPOINT("VP_FWU_SF Rated Max RPM")))
