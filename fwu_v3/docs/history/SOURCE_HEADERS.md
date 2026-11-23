# v1 주석 이력 보존

기준 a017e7f. 기존 파일의 이력 주석을 보존한다. v2의 현재 동작 설명이 아니다.

## Alarm-1.py

```text

# =====================================================================
# FWU-F8-ATS : Alarm-1  (rev. 2026-11-13)
#  - Temperature / humidity / pressure limit alarms (RAT, RAH, SAT, SAH, CZT,
#    HZT, RDP), judged 300 s after SF start
#  - SF-1~8 Run Fail Alarm (per fan, QTS 109) and SF Failure Alarm
#    (50 % or more of the installed fans failed, VP_FWU_SF Count)
#      fan comm normal : Current RPM < VP_FWU_SF Failure RPM Set
#      fan comm fault  : SAFLOW DP <= VP_FWU_SF Run DP Set (default 10 Pa)
#  - SAT / SAH / RAT / RAH sensor failure alarms (20 s); CZT / HZT / RDP sensor
#    failure alarms are made in Alarm-2, BMS PLC comm fault in Initialization
#  - SA flow sensor failure alarm (20 s)
#  - SF comm fault : detected in Alarm-3
#  - SAD-1~4 Partial Close (some SAD closed) / Full Close (all 4 closed) /
#    Not Open / Not Close alarms
#  - PICV and flow mismatch alarm (flow based checks not judged while the
#    flow meter is in comm fault, VP_FWU_Flow Comm Fault from Alarm-3)
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
#  - rev. 2026-11-11 (QTS) :
#      QTS 109 : the per-fan judgement (SF1_FAIL ~ SF8_FAIL) is written to the
#        existing points VP_FWU_SF-1~8 Run Fail Alarm (all 0 when the judgement
#        condition is off). SF Failure Alarm (4 or more fans) unchanged.
#      Flow meter comm fault : the "open but no flow" / "closed but flow"
#        checks are not judged (frozen flow value); the command / feedback
#        deviation check is unchanged
#  - rev. 2026-11-13 : model dependent values moved to setting points
#      (defaults = the former fixed values) :
#      SF Failure : 4 -> 50 % of VP_FWU_SF Count (8 -> 4 fans, same result)
#      fan comm fault judgement DP 10 Pa -> VP_FWU_SF Run DP Set
#      SAF failure 300 rpm / 1 Pa -> VP_FWU_SAF Fail RPM Set / Fail DP Set
#      PICV flow 30 / 10 LPM -> VP_FWU_PICV No Flow Set / Leak Flow Set
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
# SF stopped : timer and all limit alarms reset
# =====================================================================
# SF Failure (Command ON, Speed Value >= Speed Min, after 60 s)
#  - Each fan (internal judgement only) :
#      fan comm normal : Current RPM < VP_FWU_SF Failure RPM Set
#      fan comm fault  : SAFLOW DP <= VP_FWU_SF Run DP Set (default 10 Pa)
#  - SF-n Run Fail Alarm : per fan judgement result (QTS 109)
#  - SF Failure Alarm : 50 % or more of the installed fans failed
#      (failed count x 2 >= VP_FWU_SF Count; 8 fans -> 4, 9 -> 5, 5 -> 3)
# =====================================================================
# =====================================================================
# Sensor failure (20 s)
#  - SAT / RAT < 0 C (0 V = -20 C, wire break)
#  - SAH / RAH < 5 %
#  (PICV Control : PICV 100 % while the SAT Failure Alarm is ON)
# =====================================================================
# SAT
# SAH
# RAT
# RAH
# SA flow sensor : DP < VP_FWU_SAF Fail DP Set (1 Pa) while any of the 8 fans runs
# above VP_FWU_SAF Fail RPM Set (300 rpm), 20 s
# =====================================================================
# SAD Partial Close Alarm (alarm only, the SF keeps running)
#  - SF running and at least one, but not all, of SAD-1~4 close status ON
#    (no delay; all closed = SAD Full Close Alarm, no Partial Close Alarm)
# =====================================================================
# =====================================================================
# SAD Full Close Alarm (SF stop is done in SF Control)
#  - Set   : SF running and SAD-1~4 close status all ON (no delay)
#  - Held  : while the SAD command is ON and all SAD stay closed
#            (the SF has stopped, so SF Status is no longer 1)
#  - Reset : a SAD leaves the closed position or the SAD command is OFF
# =====================================================================
# =====================================================================
# SAD Not Open Alarm (Timer 7)
#  - SAD command ON and SF not running for 120 s,
#    and any of SAD-1~4 open status OFF -> alarm
#  - Reset when the SAD command is OFF or the SF is running
# =====================================================================
# =====================================================================
# SAD Not Close Alarm (Timer 8)
#  - SAD command OFF for 120 s and any of SAD-1~4 close status OFF -> alarm
#  - Reset when the SAD command is ON
# =====================================================================
# =====================================================================
# PICV / flow mismatch alarm
#  - Command within feedback +/- 30 % (valve follows the command) :
#      feedback > 30 % and flow < VP_FWU_PICV No Flow Set (30 LPM) : alarm
#        (open but no flow)
#        only while chilled water supply is normal
#        (VP_FWU_Chilled Water Supply Condition = 1, written by the BMS),
#        to avoid alarms on every FWU when the chilled water plant stops
#      feedback < 1 % and flow > VP_FWU_PICV Leak Flow Set (10 LPM) : alarm
#        (closed but flow, passing)
#      otherwise : alarm reset (no delay)
#      flow meter comm fault (VP_FWU_Flow Comm Fault = 1) : the two flow
#        based checks are not judged, alarm reset (frozen flow value)
#  - Command out of feedback +/- 30 % for 40 s : alarm (actuator fault)
# =====================================================================
# Command / feedback mismatch for 40 s : actuator fault

```

## Alarm-2.py

```text

# =====================================================================
# FWU-F8-ATS : Alarm-2  (rev. 2026-11-11)
#  - CZT / HZT / RDP sensor failure alarms (BMS PLC sensors), one timer per sensor
#      CZT-1~4, HZT-1~2 : value < 0 C for 20 s (same as RAT)
#      RDP-1~2          : value <= 0 Pa for 20 s
#  - The failure alarms are used in Initialization (next scan) : a failed sensor
#    is excluded from the Avg / Max / Min and from the control PV
#  - Alarm-1.py has no free timer, so these alarms are in this separate logic.
#    Register "Alarm-2" in DDC.xml after "Alarm-1".
#  - Leak alarm (QTS 142) : FWU_LEAK DETECT (rope leak detector DI) ON for 5 s
#      -> VP_FWU_Leak Alarm = 1. Alarm only, the FWU keeps running
#      (QTS : the presence of water will NOT shut down the unit)
#  - Filter alarm (QTS 104 / 141) : FWU_FILTER ALARM (filter DP switch DI)
#      ON for 30 s -> VP_FWU_Filter Alarm = 1. Alarm only
#  - Both reset at once when the input is OFF
#  - rev. 2026-11-11 (QTS) : leak / filter alarms added. FWU_LEAK DETECT,
#      VP_FWU_Leak Alarm and VP_FWU_Filter Alarm must be defined before this
#      logic is downloaded (written at the end of this file)
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
#  8 : Leak alarm delay (5 s)
#  9 : Filter alarm delay (30 s)
# =====================================================================
# CZT sensor failure (< 0, 20 s)
# CZT-1
# CZT-2
# CZT-3
# CZT-4
# HZT sensor failure (< 0, 20 s)
# HZT-1
# HZT-2
# RDP sensor failure (<= 0, 20 s)
# RDP-1
# RDP-2
# =====================================================================
# Leak alarm (QTS 142) : alarm only, no shutdown
# =====================================================================
# =====================================================================
# Filter alarm (QTS 104 / 141) : alarm only
# =====================================================================

```

## Alarm-3.py

```text

# =====================================================================
# FWU-F8-ATS : Alarm-3 (SF Comm Fault)  (rev. 2026-11-11)
#  - SF-1~8 comm fault detection (point alarm 8 = comm fail on the fan
#    Current RPM, 10 s) and the summary VP_FWU_SF Comm Fault (any fan)
#  - Separate logic because Initialization has no free timers for 8 fans
#    (10 timers per logic). Register "Alarm-3" in DDC.xml BEFORE
#    "Initialization" (Initialization reads these points in the same scan).
#  - ATS / flow meter (port 3) comm fault (point alarm 8 = comm fail, 10 s) :
#      VP_FWU_ATS Comm Fault  : FWU-ATS.Current Power
#      VP_FWU_Flow Comm Fault : FWU-Flow.Rate (Alarm-1 does not judge the
#                               flow based PICV checks while it is ON)
#  - rev. 2026-11-11 (QTS 140 / 148) : ATS / flow meter comm fault added
#
# Timers (SECTIMER)
#  0~7 : SF-1~8 comm fault delay (10 s)
#  8   : ATS comm fault delay (10 s)
#  9   : Flow meter comm fault delay (10 s)
# =====================================================================
# SF-1
# SF-2
# SF-3
# SF-4
# SF-5
# SF-6
# SF-7
# SF-8
# SF comm fault summary : any fan in comm fault
# =====================================================================
# ATS / flow meter comm fault (port 3, point alarm 8 = comm fail, 10 s)
# =====================================================================
# ATS
# Flow meter

```

## Failover.py

```text

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
# 1) SAD Not Open, 2) SAD Full Close, 3) SF Failure (50 % or more of the fans)
# ---------------------------------------------------------------------
# 2. Failover Alarm : cause confirmed for 5 s -> alarm (latched) and stop once
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# 3. Failover Reset
# ---------------------------------------------------------------------

```

## Initialization.py

```text

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
# Operator reset (only while the heartbeat is changing)
# CZT (cold zone temperature) : CZT-1~4, failure < 0 C (same as RAT)
# CZT sensor failure alarms are made in Alarm-2 (one timer per sensor)
# CZT Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
# HZT (hot zone temperature) : HZT-1~2, failure < 0 C (same as RAT)
# HZT sensor failure alarms are made in Alarm-2 (one timer per sensor)
# HZT Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
# RDP (room differential pressure) : RDP-1~2, failure <= 0 Pa
# RDP sensor failure alarms are made in Alarm-2 (one timer per sensor)
# RDP Avg / Max / Min of the healthy sensors only (BMS PLC comm fault : none)
# CZH (cold zone humidity) : Avg / Max / Min of CZH-1~4
# =====================================================================
# Zone PV selection (healthy sensors only; PV Valid = 0 when no healthy
# sensor is left or the BMS PLC is in comm fault -> SF Control uses fixed value)
#  - CZT / HZT : Select 0 = Avg, 1 = Max
#  - RDP       : Select 0 = Avg, 1 = Min
# =====================================================================
# Adjacent zone compensation : removed from this logic (rev. 2026-11-12).
#  To be done by the upper control (BMS / DCIM) when needed. The points stay
#  defined but are not used here : VP_FWU_CZT Adj-1~4, VP_FWU_RDP Adj-1~2,
#  VP_FWU_Adj Comp Weight, VP_FWU_CZT / RDP Comp Own Margin,
#  VP_FWU_CZT / RDP Comp PV. The CZT / RDP control modes use CZT PV / RDP PV.
# Delta T PV = RAT - SAT (used by the SF Control Delta T mode)
# =====================================================================
# SF Comm Fault points are written in "Alarm-3" (SF-1~8 and summary)
# =====================================================================
# =====================================================================
# SF Status : ON when any fan is running (per fan)
#  - Fan comm normal : Current RPM > VP_FWU_SF Failure RPM Set
#  - Fan comm fault  : RPM is not available -> SAFLOW DP > VP_FWU_SF Run DP Set
# =====================================================================
# SF-1
# SF-2
# SF-3
# SF-4
# SF-5
# SF-6
# SF-7
# SF-8
# SF Status with 5 s confirmation (ON and OFF) :
#  the status changes only when the new state lasts 5 s (timer 5)
# =====================================================================
# SA flow (CMH) = VP_FWU_SA Flow Coef (235.751976) x sqrt(SAFLOW DP) x SAF VA-2
#  - SF stopped or DP < 5 Pa : 0
# =====================================================================
# =====================================================================
# Local / Remote selection (REMOTE SELECTION DI)
#  - Remote (1) : BMS command (VP_FWU_Command) is used, copied to Command-HMI
#  - Local  (0) : touch screen command (VP_FWU_Command-HMI) is used, copied to Command
# =====================================================================
# SF Max RPM = Design RPM x Max RPM Ratio (110 %), limited to the fan rated max (1920 rpm)

```

## PICV Control.py

```text

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
# PICV control

```

## Remote Shutdown.py

```text

# =====================================================================
# FWU-F8-ATS : Remote Shutdown  (rev. 2026-11-11)
#  - Fire alarm (smoke detector in the return air, FWU_FIRE ALARM DI)
#    ON for 3 s -> VP_FWU_Fire Alarm = 1 (OFF : reset at once)
#  - Smoke shutdown (QTS 143, field configurable with VP_FWU_Smoke Action) :
#      0 = continue running (default, alarm only)
#      1 = shutdown, same path as the Remote Shutdown below
#  - Shutdown = Remote Shutdown Command = 1, or Fire Alarm = 1 with
#    Smoke Action = 1 (Local or Remote mode) :
#      Command / Command-HMI = 0 (P11)
#      PICV 0 %, SF analog speed 0, SF-1~8 Target RPM 0 (P2)
#      SF-1~8 Run Command 0 (P2)
#      SAD-1~4 close (P2) after the SF has stopped
#      PICV, SF Speed Value, SAD command : kept value (P11) 0 as well, so
#      that nothing restarts in manual mode when the shutdown is released
#  - No shutdown : release P2
#    (Command stays 0, the operator restarts the FWU)
#  - rev. 2026-11-11 (QTS) : fire alarm point and smoke shutdown option added,
#      SF-1~8 Run Command 0 (P2) during the shutdown (a fan Run Command no
#      longer stays 1 when the Command is written at a higher priority)
#
# Timers (SECTIMER)
#  0 : Fire alarm confirmation (3 s)
# =====================================================================
# =====================================================================
# Fire alarm (smoke detector) : 3 s confirmation
# =====================================================================
# =====================================================================
# Shutdown : Remote Shutdown Command, or smoke shutdown (Smoke Action = 1)
# =====================================================================

```

## SF Control.py

```text

# =====================================================================
# FWU-F8-ATS : SF Control  (rev. 2026-11-13)
#  - CZT / RDP PV and Delta T PV are made in Initialization (read here)
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
#           comm fault  : analog AO SF-1_4 / SF-5_8 (% of VP_FWU_SF Rated Max RPM),
#                         Modbus Target RPM = 0
#  - rev. 2026-10-28 (CRAH pattern) :
#      SF stop when all SAD are closed (was done by Alarm with P3 / P11)
#      SF Run Command added
#      speed output switched by the SF comm fault summary (any fan) instead
#      of "all 4 fans in comm fault", Target RPM limited to SF Max RPM,
#      interval 10 s -> 5 s
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
#  - rev. 2026-11-12 : adjacent zone compensation removed (upper control item).
#      RDP / CZT loops use VP_FWU_RDP PV / VP_FWU_CZT PV (was RDP / CZT Comp PV)
#  - rev. 2026-11-12 (2) : backup operation removed (upper control item : the
#      upper control can use SF Control Select / Speed SP / PICV SAT SP;
#      VP_FWU_Backup Operation stays defined, not used here). Unused HZT gain
#      reads and the duplicate Delta T PV calculation (made in Initialization,
#      which runs before this logic) removed
#  - rev. 2026-11-13 : analog speed scale 1920 rpm -> VP_FWU_SF Rated Max RPM
#      (setting point, default 1920)
#
# Timers (SECTIMER)
#  1 : Speed output interval (5 s)
# =====================================================================
# HZT / CZT / RDP PV selection is made in Initialization
# Fixed value control : SF Control Select 0, or the control PV is not available
#  (CZT / RDP : all sensors failed) -> Speed SP
#  (BMS PLC comm fault : BMS_FAIL below, not the fixed value)
# BMS PLC comm fault (QTS 129~131) : BMS_FAIL = 1 for the control modes that
# use values written by the BMS
#  - RDP (2) / CZT (4) : zone sensors written by the BMS PLC (Local or Remote)
#  - Fixed value (0)   : Speed SP written by the BMS (Remote only; in Local
#                        the Speed SP is set on the touch screen)
#  BMS_FAIL = 1 takes the place of the fixed value control of RDP / CZT
# Delta T PV (RAT - SAT) is made in Initialization
# SF PI gains
# SF control
# =====================================================================
# SF Run Command (SF-1~8)
# =====================================================================
# =====================================================================
# Speed output every 5 s (Timer 1)
#  - Switched by the SF comm fault summary (VP_FWU_SF Comm Fault = 1 when any
#    one of SF-1~8 is in comm fault) :
#      comm normal : Modbus Target RPM = Speed Value x Max RPM / 100
#                    (limited to Max RPM), analog AO = 0
#      comm fault  : analog AO (0-10 V) = Speed Value x Max RPM / Rated Max RPM
#                    for both groups (SF-1_4, SF-5_8), Modbus Target RPM = 0
# =====================================================================

```