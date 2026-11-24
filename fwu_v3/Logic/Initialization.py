# LJH[2026.1117]상위 감시와 외부 센서 집계: S ----
# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석): S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
FAIL_RPM = engine.READPOINT("VP_FWU_SF_Failure_RPM_Set")   ## 팬 RPM이 이 값 이상이면 도는 것으로 봄
RUN_DP = engine.READPOINT("VP_FWU_SF_Run_DP_Set")          ## 팬 통신이 끊겼을 때 급기 차압이 이 값보다 높으면 도는 것으로 봄

## 타이머 정의
SF_STATUS_TIMER = 5          ## 팬 운전 판단이 VP_FWU_SF_Status와 다르게 이어진 시간
UPPER_HEARTBEAT_TIMER = 6    ## 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간
UPPER_RESET_TIMER = 7        ## 상위 통신 Reset 입력이 켜져 있던 시간

## 전역변수 선언
mbUpperEnabled = engine.READPOINT("VP_FWU_Upper_Comm_Enable") == TRUE   ## 상위(BMS/PLC) 통신 감시를 쓰는지 (HMI 설정)
mHeartbeat = engine.READPOINT("VP_FWU_BMS_PLC_Heartbeat")               ## 상위가 주기적으로 바꿔 주는 값
mbHBOk = FALSE        ## 이번 실행에서 heartbeat가 살아 있다고 확인되면 TRUE
mbUpperOk = FALSE     ## 상위 통신이 정상이라 외부 센서값을 써도 되면 TRUE (heartbeat 확인 뒤에 계산)

## 외부 센서 집계값. 최대·최소는 어떤 센서값보다도 작게/크게 잡고 시작한다
mCZTCount = 0
mCZTSum = 0
mCZTMax = -1000
mCZTMin = 1000
mHZTCount = 0
mHZTSum = 0
mHZTMax = -1000
mHZTMin = 1000
mRDPCount = 0
mRDPSum = 0
mRDPMax = -1000
mRDPMin = 1000
mCZHCount = 0
mCZHSum = 0
mCZHMax = -1000
mCZHMin = 1000

## 팬 8대의 통신 이상 상태 (Comm Fault Alarm이 판단해 둔 값)
mbSF1CommFault = engine.READPOINT("VP_FWU_SF-1_Comm_Fault")
mbSF2CommFault = engine.READPOINT("VP_FWU_SF-2_Comm_Fault")
mbSF3CommFault = engine.READPOINT("VP_FWU_SF-3_Comm_Fault")
mbSF4CommFault = engine.READPOINT("VP_FWU_SF-4_Comm_Fault")
mbSF5CommFault = engine.READPOINT("VP_FWU_SF-5_Comm_Fault")
mbSF6CommFault = engine.READPOINT("VP_FWU_SF-6_Comm_Fault")
mbSF7CommFault = engine.READPOINT("VP_FWU_SF-7_Comm_Fault")
mbSF8CommFault = engine.READPOINT("VP_FWU_SF-8_Comm_Fault")

mSAFlowDP = engine.READPOINT("FWU_SAFLOW_DP")   ## 급기 차압(Pa)
mbSFRun = FALSE       ## 팬이 한 대라도 돌고 있다고 판단되면 TRUE

# 상위가 없는 모델은 감시를 끄고 고정속도/RAT/ΔT를 사용한다.
# 감시를 끄면 외부 온도·차압은 제어 입력으로 쓰지 않는다.

## 상위 통신(heartbeat) 감시
## 상위가 heartbeat 값을 계속 바꿔 주는지 본다. Upper_Comm_Timeout 동안 그대로면 통신 이상으로 잡아 둔다
if mbUpperEnabled == TRUE:
    ## 감시를 막 켰으면(이전 실행에서는 꺼져 있었으면) 지금 값을 기준으로 새로 잰다
    if engine.READPOINT("VP_FWU_Upper_Comm_Enable_Prev") == TRUE:
        pass  ## do_nothing (이전 실행에서도 켜져 있었음. 하던 대로 잰다)
    else:
        engine.SECTIMER(UPPER_HEARTBEAT_TIMER, TMR_CLEAR)
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", mHeartbeat)
    if mHeartbeat == engine.READPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev"):   ## 값이 그대로면 Timeout을 넘었는지 본다
        if engine.SECTIMER(UPPER_HEARTBEAT_TIMER, TMR_READ) > engine.READPOINT("VP_FWU_Upper_Comm_Timeout"):
            engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", TRUE)
        else:
            mbHBOk = TRUE
    else:
        ## 값이 바뀌었으면 살아 있는 것. 기준값을 새로 남기고 시간을 다시 잰다
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", mHeartbeat)
        engine.SECTIMER(UPPER_HEARTBEAT_TIMER, TMR_CLEAR)
        mbHBOk = TRUE
else:
    ## 감시를 안 쓰면 타이머와 통신 이상을 풀어 둔다
    engine.SECTIMER(UPPER_HEARTBEAT_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_BMS_PLC_Heartbeat_Prev", mHeartbeat)
    engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", FALSE)

## 다음 실행에서 '감시를 막 켰는지' 알 수 있도록 지금 상태를 남긴다
engine.WRITEPOINT("VP_FWU_Upper_Comm_Enable_Prev", mbUpperEnabled)

## 통신 이상 Reset: heartbeat가 살아 있을 때만 알람을 풀고, Reset 입력은 5초 뒤 스스로 되돌린다
if engine.READPOINT("VP_FWU_BMS_PLC_Comm_Reset") == TRUE:
    if mbHBOk == TRUE:
        engine.WRITEPOINT("VP_FWU_BMS_PLC_Comm_Fault", FALSE)
    else:
        pass  ## do_nothing
    if engine.SECTIMER(UPPER_RESET_TIMER, TMR_READ) > 5:   ## 5초
        engine.WRITEPOINT_PRI("VP_FWU_BMS_PLC_Comm_Reset", FALSE, 11)
        engine.SECTIMER(UPPER_RESET_TIMER, TMR_CLEAR)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(UPPER_RESET_TIMER, TMR_CLEAR)

## 상위 통신이 정상일 때만 외부 센서(CZT/HZT/RDP)값을 쓴다
mbUpperOk = mbUpperEnabled == TRUE and engine.READPOINT("VP_FWU_BMS_PLC_Comm_Fault") == FALSE

## CZT(냉복도 온도) 집계
## 사용 개수(CZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다
## 사용 개수는 0~10 정수. 상위에서 대표값 하나만 받으면 사용 개수를 1로 설정한다
if engine.READPOINT("VP_FWU_CZT_Count") >= 1 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-1_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-1")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 2 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-2_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-2")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 3 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-3_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-3")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 4 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-4_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-4")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 5 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-5_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-5")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 6 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-6_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-6")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 7 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-7_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-7")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 8 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-8_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-8")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 9 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-9_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-9")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZT_Count") >= 10 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_CZT-10_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_CZT-10")
    mCZTCount = mCZTCount + 1
    mCZTSum = mCZTSum + SensorValue
    mCZTMax = engine.MAX(mCZTMax, SensorValue)
    mCZTMin = engine.MIN(mCZTMin, SensorValue)
else:
    pass  ## do_nothing

## 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시
if mCZTCount > 0:
    engine.WRITEPOINT("VP_FWU_CZT_Avg", mCZTSum / mCZTCount)
    engine.WRITEPOINT("VP_FWU_CZT_Max", mCZTMax)
    engine.WRITEPOINT("VP_FWU_CZT_Min", mCZTMin)
    engine.WRITEPOINT("VP_FWU_CZT_PV_Valid", TRUE)
else:
    engine.WRITEPOINT("VP_FWU_CZT_Avg", 0)
    engine.WRITEPOINT("VP_FWU_CZT_Max", 0)
    engine.WRITEPOINT("VP_FWU_CZT_Min", 0)
    engine.WRITEPOINT("VP_FWU_CZT_PV_Valid", FALSE)

## 제어에 쓸 CZT 값 (Select 0 = 평균, 1 = 최대)
if engine.READPOINT("VP_FWU_CZT_PV_Valid") == TRUE:
    if engine.READPOINT("VP_FWU_CZT_Select") == FALSE:
        engine.WRITEPOINT("VP_FWU_CZT_PV", engine.READPOINT("VP_FWU_CZT_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_CZT_PV", engine.READPOINT("VP_FWU_CZT_Max"))
else:
    engine.WRITEPOINT("VP_FWU_CZT_PV", 0)

## HZT(열복도 온도) 집계
## 사용 개수(HZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다
if engine.READPOINT("VP_FWU_HZT_Count") >= 1 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-1_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-1")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 2 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-2_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-2")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 3 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-3_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-3")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 4 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-4_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-4")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 5 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-5_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-5")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 6 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-6_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-6")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 7 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-7_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-7")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 8 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-8_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-8")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 9 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-9_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-9")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_HZT_Count") >= 10 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_HZT-10_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_HZT-10")
    mHZTCount = mHZTCount + 1
    mHZTSum = mHZTSum + SensorValue
    mHZTMax = engine.MAX(mHZTMax, SensorValue)
    mHZTMin = engine.MIN(mHZTMin, SensorValue)
else:
    pass  ## do_nothing

## 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시
if mHZTCount > 0:
    engine.WRITEPOINT("VP_FWU_HZT_Avg", mHZTSum / mHZTCount)
    engine.WRITEPOINT("VP_FWU_HZT_Max", mHZTMax)
    engine.WRITEPOINT("VP_FWU_HZT_Min", mHZTMin)
    engine.WRITEPOINT("VP_FWU_HZT_PV_Valid", TRUE)
else:
    engine.WRITEPOINT("VP_FWU_HZT_Avg", 0)
    engine.WRITEPOINT("VP_FWU_HZT_Max", 0)
    engine.WRITEPOINT("VP_FWU_HZT_Min", 0)
    engine.WRITEPOINT("VP_FWU_HZT_PV_Valid", FALSE)

## 제어에 쓸 HZT 값 (Select 0 = 평균, 1 = 최대)
if engine.READPOINT("VP_FWU_HZT_PV_Valid") == TRUE:
    if engine.READPOINT("VP_FWU_HZT_Select") == FALSE:
        engine.WRITEPOINT("VP_FWU_HZT_PV", engine.READPOINT("VP_FWU_HZT_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_HZT_PV", engine.READPOINT("VP_FWU_HZT_Max"))
else:
    engine.WRITEPOINT("VP_FWU_HZT_PV", 0)

## RDP(룸 차압) 집계
## 사용 개수(RDP_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다
if engine.READPOINT("VP_FWU_RDP_Count") >= 1 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-1_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-1")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 2 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-2_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-2")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 3 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-3_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-3")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 4 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-4_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-4")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 5 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-5_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-5")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 6 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-6_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-6")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 7 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-7_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-7")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 8 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-8_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-8")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 9 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-9_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-9")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_RDP_Count") >= 10 and mbUpperOk == TRUE and engine.READPOINT("VP_FWU_RDP-10_Failure_Alarm") == FALSE:
    SensorValue = engine.READPOINT("VP_FWU_RDP-10")
    mRDPCount = mRDPCount + 1
    mRDPSum = mRDPSum + SensorValue
    mRDPMax = engine.MAX(mRDPMax, SensorValue)
    mRDPMin = engine.MIN(mRDPMin, SensorValue)
else:
    pass  ## do_nothing

## 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시
if mRDPCount > 0:
    engine.WRITEPOINT("VP_FWU_RDP_Avg", mRDPSum / mRDPCount)
    engine.WRITEPOINT("VP_FWU_RDP_Max", mRDPMax)
    engine.WRITEPOINT("VP_FWU_RDP_Min", mRDPMin)
    engine.WRITEPOINT("VP_FWU_RDP_PV_Valid", TRUE)
else:
    engine.WRITEPOINT("VP_FWU_RDP_Avg", 0)
    engine.WRITEPOINT("VP_FWU_RDP_Max", 0)
    engine.WRITEPOINT("VP_FWU_RDP_Min", 0)
    engine.WRITEPOINT("VP_FWU_RDP_PV_Valid", FALSE)

## 제어에 쓸 RDP 값 (Select 0 = 평균, 1 = 최소)
if engine.READPOINT("VP_FWU_RDP_PV_Valid") == TRUE:
    if engine.READPOINT("VP_FWU_RDP_Select") == FALSE:
        engine.WRITEPOINT("VP_FWU_RDP_PV", engine.READPOINT("VP_FWU_RDP_Avg"))
    else:
        engine.WRITEPOINT("VP_FWU_RDP_PV", engine.READPOINT("VP_FWU_RDP_Min"))
else:
    engine.WRITEPOINT("VP_FWU_RDP_PV", 0)

## CZH(냉복도 습도) 집계: 표시용이라 상위 통신·고장 조건 없이 사용 개수만 본다
if engine.READPOINT("VP_FWU_CZH_Count") >= 1:
    SensorValue = engine.READPOINT("VP_FWU_CZH-1")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 2:
    SensorValue = engine.READPOINT("VP_FWU_CZH-2")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 3:
    SensorValue = engine.READPOINT("VP_FWU_CZH-3")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 4:
    SensorValue = engine.READPOINT("VP_FWU_CZH-4")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 5:
    SensorValue = engine.READPOINT("VP_FWU_CZH-5")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 6:
    SensorValue = engine.READPOINT("VP_FWU_CZH-6")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 7:
    SensorValue = engine.READPOINT("VP_FWU_CZH-7")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 8:
    SensorValue = engine.READPOINT("VP_FWU_CZH-8")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 9:
    SensorValue = engine.READPOINT("VP_FWU_CZH-9")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_CZH_Count") >= 10:
    SensorValue = engine.READPOINT("VP_FWU_CZH-10")
    mCZHCount = mCZHCount + 1
    mCZHSum = mCZHSum + SensorValue
    mCZHMax = engine.MAX(mCZHMax, SensorValue)
    mCZHMin = engine.MIN(mCZHMin, SensorValue)
else:
    pass  ## do_nothing

if mCZHCount > 0:
    engine.WRITEPOINT("VP_FWU_CZH_Avg", mCZHSum / mCZHCount)
    engine.WRITEPOINT("VP_FWU_CZH_Max", mCZHMax)
    engine.WRITEPOINT("VP_FWU_CZH_Min", mCZHMin)
else:
    engine.WRITEPOINT("VP_FWU_CZH_Avg", 0)
    engine.WRITEPOINT("VP_FWU_CZH_Max", 0)
    engine.WRITEPOINT("VP_FWU_CZH_Min", 0)

# 팬 수는 F8 기준 고정. F4/F6는 팬별 입출력과 고장 집계를 함께 변경한다.
# 풍량 계수·정격 RPM·운전 차압은 새 팬 제원으로 팬 개발팀 확인 필요.
# FMS 1대로 개별 팬 풍량은 확인할 수 없다. QTS 수준은 팬별 감지 입력 추가 검토.
# 공통 차압 대체 판정은 다른 팬이 만든 차압으로 정지 팬을 구분하지 못할 수 있다.

## ΔT = RAT - SAT (SF Control의 ΔT 모드에서 쓴다)
engine.WRITEPOINT("VP_FWU_DeltaT_PV", engine.READPOINT("FWU_RAT") - engine.READPOINT("FWU_SAT"))

## 팬 운전 판단: 한 대라도 돌고 있으면 운전 중으로 본다
## 통신이 되는 팬은 RPM으로, 통신이 끊긴 팬은 급기 차압으로 판단한다
if mbSF1CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-1.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF2CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-2.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF3CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-3.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF4CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-4.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF5CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-5.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF6CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-6.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF7CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-7.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

if mbSF8CommFault == TRUE:
    if mSAFlowDP > RUN_DP:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing
else:
    if engine.READPOINT("FWU_SF-8.Current_RPM") >= FAIL_RPM:
        mbSFRun = TRUE
    else:
        pass  ## do_nothing

## 판단이 바뀐 채로 5초가 지나야 VP_FWU_SF_Status에 반영한다 (순간적인 흔들림 무시)
if mbSFRun == engine.READPOINT("VP_FWU_SF_Status"):
    engine.SECTIMER(SF_STATUS_TIMER, TMR_CLEAR)   ## 판단이 지금 상태와 같으면 시간을 다시 잰다
else:
    if engine.SECTIMER(SF_STATUS_TIMER, TMR_READ) > 5:   ## 5초
        engine.WRITEPOINT("VP_FWU_SF_Status", mbSFRun)
        engine.SECTIMER(SF_STATUS_TIMER, TMR_CLEAR)
    else:
        pass  ## do_nothing

## 급기 풍량 계산: 팬이 돌고 차압이 5Pa 이상일 때만 계산한다
## 차압은 위에서 읽어 둔 mSAFlowDP를 쓴다 (FWU_SAFLOW_DP를 다시 읽는 것과 같은 값)
## VP_FWU_SAF_VA-2(기본값 9)가 어떤 값인지는 아직 확인하지 못했다
if engine.READPOINT("VP_FWU_SF_Status") == ON and mSAFlowDP >= 5:
    SAFlow = engine.READPOINT("VP_FWU_SA_Flow_Coef") * mSAFlowDP ** 0.5 * engine.READPOINT("VP_FWU_SAF_VA-2")
    engine.WRITEPOINT("VP_FWU_SA_Flow", SAFlow)
else:
    engine.WRITEPOINT("VP_FWU_SA_Flow", 0)

## 운전 명령 맞추기: 원격(BMS) 선택이면 BMS 명령을 HMI 쪽에, 로컬이면 HMI 명령을 BMS 쪽에 따라 쓴다
if engine.READPOINT("REMOTE_SELECTION") == TRUE:
    engine.RELEASE_PRI("VP_FWU_Command", 5)
    engine.WRITEPOINT("VP_FWU_Command_HMI", engine.READPOINT("VP_FWU_Command"))
    engine.WRITEPOINT_PRI("VP_FWU_Command_HMI", engine.READPOINT("VP_FWU_Command"), 11)
else:
    engine.RELEASE_PRI("VP_FWU_Command_HMI", 5)
    engine.WRITEPOINT("VP_FWU_Command", engine.READPOINT("VP_FWU_Command_HMI"))
    engine.WRITEPOINT_PRI("VP_FWU_Command", engine.READPOINT("VP_FWU_Command_HMI"), 11)

## 팬 최대 RPM = 설계 RPM × 비율(%). 단 정격 최대 RPM은 넘지 않게 한다 (SF Control이 이 값을 쓴다)
engine.WRITEPOINT("VP_FWU_SF_Max_RPM", engine.MIN(engine.READPOINT("VP_FWU_SF_Design_RPM") * engine.READPOINT("VP_FWU_SF_Max_RPM_Ratio") / 100, engine.READPOINT("VP_FWU_SF_Rated_Max_RPM")))

# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]상위 감시와 외부 센서 집계: E ----
