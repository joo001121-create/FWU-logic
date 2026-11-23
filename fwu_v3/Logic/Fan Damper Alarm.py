# JSY[2026.1123]Alarm-1에서 팬 운전 고장 알람과 댐퍼 보호 알람을 떼어 만듦, Coding Rule 적용: S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
FAN_COUNT = 8                    ## 팬 대수 (F8 모델 기준)
FAN_FAIL_CONFIRM_SECONDS = 60    ## 운전 명령 후 60초가 지나야 팬 고장을 본다
DAMPER_TRAVEL_SECONDS = 120      ## 댐퍼가 끝까지 움직이는 데 주는 시간
FAIL_RPM = engine.READPOINT("VP_FWU_SF_Failure_RPM_Set")   ## 팬 RPM이 이 값보다 낮으면 고장 후보로 봄
# F4/F6는 개별 팬 판정과 입출력을 함께 변경. Count VP로 모델을 전환하지 않는다.

## 타이머 정의 (번호는 Alarm-1에서 쓰던 그대로)
FAN_FAIL_TIMER = 1     ## 운전 명령이 들어간 뒤 지난 시간 (팬 고장 판단 시작 지연)
SAD_OPEN_TIMER = 7     ## 댐퍼 열림 명령 뒤 지난 시간
SAD_CLOSE_TIMER = 8    ## 댐퍼 닫힘 명령 뒤 지난 시간

## 전역변수 선언: 댐퍼 닫힘 접점 상태
mbSADAllClose = engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == TRUE   ## 네 댐퍼가 모두 닫힘
mbSADAnyClose = engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == TRUE or engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == TRUE or engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == TRUE or engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == TRUE   ## 하나라도 닫힘

## 팬 운전 고장: 운전 명령이 있고 속도가 최소 이상인데 60초가 지나도 안 돌면 고장
if engine.READPOINT("VP_FWU_Command") == ON and engine.READPOINT("VP_FWU_SF_Speed_Value") >= engine.READPOINT("VP_FWU_SF_Speed_Min"):
    if engine.SECTIMER(FAN_FAIL_TIMER, TMR_READ) > FAN_FAIL_CONFIRM_SECONDS:
        bSFDPLow = engine.READPOINT("FWU_SAFLOW_DP") <= engine.READPOINT("VP_FWU_SF_Run_DP_Set")   ## 급기 차압이 운전 기준 이하

        ## 통신이 되는 팬은 RPM으로, 통신이 끊긴 팬은 급기 차압으로 판단한다
        if engine.READPOINT("VP_FWU_SF-1_Comm_Fault") == FALSE:
            bSF1Fail = engine.READPOINT("FWU_SF-1.Current_RPM") < FAIL_RPM
        else:
            bSF1Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-2_Comm_Fault") == FALSE:
            bSF2Fail = engine.READPOINT("FWU_SF-2.Current_RPM") < FAIL_RPM
        else:
            bSF2Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-3_Comm_Fault") == FALSE:
            bSF3Fail = engine.READPOINT("FWU_SF-3.Current_RPM") < FAIL_RPM
        else:
            bSF3Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-4_Comm_Fault") == FALSE:
            bSF4Fail = engine.READPOINT("FWU_SF-4.Current_RPM") < FAIL_RPM
        else:
            bSF4Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-5_Comm_Fault") == FALSE:
            bSF5Fail = engine.READPOINT("FWU_SF-5.Current_RPM") < FAIL_RPM
        else:
            bSF5Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-6_Comm_Fault") == FALSE:
            bSF6Fail = engine.READPOINT("FWU_SF-6.Current_RPM") < FAIL_RPM
        else:
            bSF6Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-7_Comm_Fault") == FALSE:
            bSF7Fail = engine.READPOINT("FWU_SF-7.Current_RPM") < FAIL_RPM
        else:
            bSF7Fail = bSFDPLow

        if engine.READPOINT("VP_FWU_SF-8_Comm_Fault") == FALSE:
            bSF8Fail = engine.READPOINT("FWU_SF-8.Current_RPM") < FAIL_RPM
        else:
            bSF8Fail = bSFDPLow

        ## 팬별 알람을 내고 고장 대수를 센다
        SFFailCount = 0
        if bSF1Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", FALSE)
        if bSF2Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", FALSE)
        if bSF3Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", FALSE)
        if bSF4Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", FALSE)
        if bSF5Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", FALSE)
        if bSF6Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", FALSE)
        if bSF7Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", FALSE)
        if bSF8Fail == TRUE:
            SFFailCount = SFFailCount + 1
            engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", FALSE)

        # 종합 팬 고장 기준은 SMX01의 절반 이상 고장을 임시로 유지한다.
        # 신규 팬의 정압-풍량 곡선과 허용 최대속도를 기준으로, 팬 고장 시에도
        # 요구 정압에서 목표 풍량을 확보할 수 있는 고장 허용 대수를 확인할 것.
        # 확인 결과에 맞춰 아래 종합 고장 대수 기준과 Failover 정지 연계를 재검토한다.
        if SFFailCount * 2 >= FAN_COUNT:   ## 절반 이상 고장이면 종합 알람 (팬·모델이 바뀌면 기준을 다시 정해야 할 수 있음)
            engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", FALSE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(FAN_FAIL_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_SF_Failure_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-1_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-2_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-3_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-4_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-5_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-6_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-7_Run_Fail_Alarm", FALSE)
    engine.WRITEPOINT("VP_FWU_SF-8_Run_Fail_Alarm", FALSE)

## 댐퍼 일부 닫힘: 팬이 도는데 네 댐퍼 중 일부만 닫혀 있음
if engine.READPOINT("VP_FWU_SF_Status") == ON:
    if mbSADAnyClose == TRUE and mbSADAllClose == FALSE:
        engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", TRUE)
    else:
        engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", FALSE)
else:
    engine.WRITEPOINT("VP_FWU_SAD_Partial_Close_Alarm", FALSE)

## 댐퍼 전폐: 열림 명령인데 네 댐퍼가 모두 닫혀 있음. 팬이 서도 한 번 걸린 알람은 닫힘이 풀릴 때까지 유지
if mbSADAllClose == TRUE and engine.READPOINT("FWU_SAD-1_4_COMMAND") == ON and (engine.READPOINT("VP_FWU_SF_Status") == ON or engine.READPOINT("VP_FWU_SAD_Full_Close_Alarm") == TRUE):
    engine.WRITEPOINT("VP_FWU_SAD_Full_Close_Alarm", TRUE)
else:
    engine.WRITEPOINT("VP_FWU_SAD_Full_Close_Alarm", FALSE)

## 댐퍼 미개방: 열림 명령을 내고 팬이 아직 안 돌 때, 120초가 지나도 네 댐퍼가 다 안 열리면 알람
if engine.READPOINT("FWU_SAD-1_4_COMMAND") == ON and engine.READPOINT("VP_FWU_SF_Status") == OFF:
    engine.SECTIMER(SAD_CLOSE_TIMER, TMR_CLEAR)
    if engine.SECTIMER(SAD_OPEN_TIMER, TMR_READ) > DAMPER_TRAVEL_SECONDS:
        if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") != TRUE or engine.READPOINT("FWU_SAD-2_OPEN_STATUS") != TRUE or engine.READPOINT("FWU_SAD-3_OPEN_STATUS") != TRUE or engine.READPOINT("FWU_SAD-4_OPEN_STATUS") != TRUE:
            engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", FALSE)
    else:
        engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", FALSE)
else:
    engine.WRITEPOINT("VP_FWU_SAD_Not_Open_Alarm", FALSE)
    engine.SECTIMER(SAD_OPEN_TIMER, TMR_CLEAR)

## 댐퍼 미폐쇄: 닫힘 명령 뒤 120초가 지나도 네 댐퍼가 다 안 닫히면 알람
if engine.READPOINT("FWU_SAD-1_4_COMMAND") == OFF:
    engine.SECTIMER(SAD_OPEN_TIMER, TMR_CLEAR)
    if engine.SECTIMER(SAD_CLOSE_TIMER, TMR_READ) > DAMPER_TRAVEL_SECONDS:
        if engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") != TRUE or engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") != TRUE or engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") != TRUE or engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") != TRUE:
            engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", TRUE)
        else:
            engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", FALSE)
    else:
        engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", FALSE)
else:
    engine.WRITEPOINT("VP_FWU_SAD_Not_Close_Alarm", FALSE)
    engine.SECTIMER(SAD_CLOSE_TIMER, TMR_CLEAR)

# JSY[2026.1123]Alarm-1에서 팬 운전 고장 알람과 댐퍼 보호 알람을 떼어 만듦, Coding Rule 적용: E ----
# LJH[2026.1117]내부 센서 유효성 및 팬·댐퍼 알람
