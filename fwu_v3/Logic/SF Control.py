# LJH[2026.1117]온도 센서 고장 시 대체운전, 네 밸브 닫힘과 팬 정지 연계: S ----
# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석): S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0

## DEC/INC는 LOOP2 제어 방향 (DEC: 현재값을 내리는 제어, INC: 현재값을 올리는 제어)
RAT_LOOP = 1                ## LOOP2 번호: RAT 기준 제어
RDP_LOOP = 2                ## LOOP2 번호: RDP 기준 제어
DELTA_T_LOOP = 3            ## LOOP2 번호: ΔT(RAT-SAT) 기준 제어
CZT_LOOP = 4                ## LOOP2 번호: CZT 기준 제어
SF_CONTROL_SELECT = engine.READPOINT("VP_FWU_SF_Control_Select")    ## 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT
RAT_PGAIN = engine.READPOINT("VP_FWU_SF_RAT_PGain")                 ## RAT 기준 팬 제어 P 게인
RAT_IGAIN = engine.READPOINT("VP_FWU_SF_RAT_IGain")                 ## RAT 기준 팬 제어 I 게인
RDP_PGAIN = engine.READPOINT("VP_FWU_SF_RDP_PGain")                 ## RDP 기준 팬 제어 P 게인
RDP_IGAIN = engine.READPOINT("VP_FWU_SF_RDP_IGain")                 ## RDP 기준 팬 제어 I 게인
DELTAT_PGAIN = engine.READPOINT("VP_FWU_SF_DeltaT_PGain")           ## ΔT 기준 팬 제어 P 게인
DELTAT_IGAIN = engine.READPOINT("VP_FWU_SF_DeltaT_IGain")           ## ΔT 기준 팬 제어 I 게인
CZT_PGAIN = engine.READPOINT("VP_FWU_SF_CZT_PGain")                 ## CZT 기준 팬 제어 P 게인
CZT_IGAIN = engine.READPOINT("VP_FWU_SF_CZT_IGain")                 ## CZT 기준 팬 제어 I 게인

## 타이머 정의
SPEED_OUTPUT_TIMER = 1      ## 팬 속도를 마지막으로 내보낸 뒤 지난 시간

## 전역변수 선언
mbFixed = FALSE      ## TRUE면 PI 제어 대신 고정속도(Speed_SP)로 돈다
mbBMSFail = FALSE    ## TRUE면 상위 통신이 끊겨 Comm_Fail_Mode 설정대로 돈다

# 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.
# 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.
# HMI에서 최소 <= 최대를 확인할 것. 최소 30% 유지, QTS 20%는 코드 리뷰시 확인 필요.
# ΔT 목표 -2℃는 SMX01 기준 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.
# 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.
# 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.

## 고정속도로 돌릴지 판단
## 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다
if 0 <= SF_CONTROL_SELECT < 1:
    mbFixed = TRUE
else:
    pass  ## do_nothing

if 2 <= SF_CONTROL_SELECT < 3 and engine.READPOINT("VP_FWU_RDP_PV_Valid") != TRUE:
    mbFixed = TRUE
else:
    pass  ## do_nothing

if 4 <= SF_CONTROL_SELECT < 5 and engine.READPOINT("VP_FWU_CZT_PV_Valid") != TRUE:
    mbFixed = TRUE
else:
    pass  ## do_nothing

## 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도
if 1 <= SF_CONTROL_SELECT < 2 and engine.READPOINT("VP_FWU_RAT_Failure_Alarm") == TRUE:
    mbFixed = TRUE
else:
    pass  ## do_nothing

if 3 <= SF_CONTROL_SELECT < 4 and (engine.READPOINT("VP_FWU_RAT_Failure_Alarm") == TRUE or engine.READPOINT("VP_FWU_SAT_Failure_Alarm") == TRUE):
    mbFixed = TRUE
else:
    pass  ## do_nothing

## 상위(BMS/PLC) 통신이 끊겼을 때
## 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다
if engine.READPOINT("VP_FWU_Upper_Comm_Enable") == TRUE and engine.READPOINT("VP_FWU_BMS_PLC_Comm_Fault") == TRUE:
    if 2 <= SF_CONTROL_SELECT < 3 or 4 <= SF_CONTROL_SELECT < 5:
        mbBMSFail = TRUE
    else:
        pass  ## do_nothing
    if 0 <= SF_CONTROL_SELECT < 1 and engine.READPOINT("REMOTE_SELECTION") == TRUE:
        mbBMSFail = TRUE
    else:
        pass  ## do_nothing
else:
    pass  ## do_nothing

if mbBMSFail == TRUE:
    mbFixed = FALSE
else:
    pass  ## do_nothing

## 비상정지가 아닐 때
if engine.READPOINT("FWU_EMERGENCY") == FALSE:
    ## 비상정지 때 걸어 둔 P1 해제
    engine.RELEASE_PRI("FWU_SF-1_4_SPEED_CONTROL", 1)       #FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨 (기존 배선이 1~4, 5~8로 나뉘어 있음)
    engine.RELEASE_PRI("FWU_SF-5_8_SPEED_CONTROL", 1)
    engine.RELEASE_PRI("FWU_SF-1.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-2.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-3.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-4.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-5.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-6.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-7.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SF-8.Target_RPM_Set", 1)
    engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 1)

    if engine.READPOINT("VP_FWU_Operation_Mode") == TRUE:   ## Operation_Mode 1 = 자동, 0 = 수동
        if engine.READPOINT("VP_FWU_Command") == ON:
            ## 운전: 댐퍼부터 열고, 네 댐퍼가 모두 열린 뒤에 팬 속도를 정한다
            engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", ON)
            if engine.READPOINT("FWU_SAD-1_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-2_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-3_OPEN_STATUS") == TRUE and engine.READPOINT("FWU_SAD-4_OPEN_STATUS") == TRUE:
                ## 고정속도: Speed_SP를 최소~최대 속도 안으로 맞춰서 쓴다
                if mbFixed == TRUE:
                    Speed = engine.MAX(engine.READPOINT("VP_FWU_Speed_SP"), engine.READPOINT("VP_FWU_SF_Speed_Min"))
                    Speed = engine.MIN(Speed, engine.READPOINT("VP_FWU_SF_Speed_Max"))
                    engine.WRITEPOINT("VP_FWU_SF_Speed_Value", Speed)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                else:
                    pass  ## do_nothing

                ## LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)
                ## RAT 기준: RAT가 목표보다 높으면 팬을 올린다 (DEC)
                if mbFixed == FALSE and 1 <= SF_CONTROL_SELECT < 2:
                    engine.LOOP2(DEC,"FWU_RAT","VP_FWU_SF_Speed_Value","VP_FWU_RAT_SP",RAT_PGAIN,RAT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),RAT_LOOP,0)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                else:
                    pass  ## do_nothing

                ## RDP 기준: 차압이 목표보다 낮으면 팬을 올린다 (INC)
                if mbFixed == FALSE and mbBMSFail == FALSE and 2 <= SF_CONTROL_SELECT < 3:
                    engine.LOOP2(INC,"VP_FWU_RDP_PV","VP_FWU_SF_Speed_Value","VP_FWU_RDP_SP",RDP_PGAIN,RDP_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),RDP_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                else:
                    pass  ## do_nothing

                ## ΔT 기준
                if mbFixed == FALSE and 3 <= SF_CONTROL_SELECT < 4:
                    engine.LOOP2(DEC,"VP_FWU_DeltaT_PV","VP_FWU_SF_Speed_Value","VP_FWU_DeltaT_SP",DELTAT_PGAIN,DELTAT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),DELTA_T_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                else:
                    pass  ## do_nothing

                ## CZT 기준: 존 온도가 목표보다 높으면 팬을 올린다 (DEC)
                if mbFixed == FALSE and mbBMSFail == FALSE and 4 <= SF_CONTROL_SELECT < 5:
                    engine.LOOP2(DEC,"VP_FWU_CZT_PV","VP_FWU_SF_Speed_Value","VP_FWU_CZT_SP",CZT_PGAIN,CZT_IGAIN,0,0,60,engine.READPOINT("VP_FWU_SF_Speed_Min"),engine.READPOINT("VP_FWU_SF_Speed_Max"),CZT_LOOP,0)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                else:
                    pass  ## do_nothing

                ## 상위 통신 끊김: 설정이 '최대 속도'이거나 지금 속도가 최소보다 낮으면 최대 속도로 올린다
                if mbBMSFail == TRUE:
                    if engine.READPOINT("VP_FWU_BMS_Comm_Fail_Mode") == TRUE or engine.READPOINT("VP_FWU_SF_Speed_Value") < engine.READPOINT("VP_FWU_SF_Speed_Min"):   ## Comm_Fail_Mode 1 = 최대 속도, 0 = 마지막 속도 유지
                        engine.WRITEPOINT("VP_FWU_SF_Speed_Value", engine.READPOINT("VP_FWU_SF_Speed_Max"))
                    else:
                        pass  ## do_nothing (마지막 팬 속도 유지)
                    engine.LOOP2_INIT(RAT_LOOP)
                    engine.LOOP2_INIT(RDP_LOOP)
                    engine.LOOP2_INIT(DELTA_T_LOOP)
                    engine.LOOP2_INIT(CZT_LOOP)
                else:
                    pass  ## do_nothing
            else:
                pass  ## do_nothing (댐퍼가 다 열릴 때까지 팬 속도는 그대로 둔다)

            ## 운전 명령 중인데 네 댐퍼가 모두 닫혀 있으면 PI를 초기화하고 속도를 0으로
            if engine.READPOINT("FWU_SAD-1_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-2_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-3_CLOSE_STATUS") == TRUE and engine.READPOINT("FWU_SAD-4_CLOSE_STATUS") == TRUE:
                engine.LOOP2_INIT(RAT_LOOP)
                engine.LOOP2_INIT(RDP_LOOP)
                engine.LOOP2_INIT(DELTA_T_LOOP)
                engine.LOOP2_INIT(CZT_LOOP)
                engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)
            else:
                pass  ## do_nothing

        else:
            ## 정지 명령: 밸브가 다 닫힌 뒤 팬을 세우고, 팬이 멈춘 뒤 댐퍼를 닫는다
            engine.LOOP2_INIT(RAT_LOOP)
            engine.LOOP2_INIT(RDP_LOOP)
            engine.LOOP2_INIT(DELTA_T_LOOP)
            engine.LOOP2_INIT(CZT_LOOP)
            if engine.READPOINT("VP_FWU_PICV_All_Closed") == TRUE:
                engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)
            else:
                pass  ## do_nothing
            if engine.READPOINT("VP_FWU_SF_Status") == OFF:
                engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", OFF)
            else:
                pass  ## do_nothing
        engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", engine.READPOINT("VP_FWU_SF_Speed_Value"), 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", engine.READPOINT("FWU_SAD-1_4_COMMAND"), 11)
    else:
        ## 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다
        engine.LOOP2_INIT(RAT_LOOP)
        engine.LOOP2_INIT(RDP_LOOP)
        engine.LOOP2_INIT(DELTA_T_LOOP)
        engine.LOOP2_INIT(CZT_LOOP)
        engine.RELEASE_PRI("VP_FWU_SF_Speed_Value", 5)
        engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 5)
else:
    ## 비상정지: 운전 명령을 끄고 팬 출력을 P1으로 0으로 누른다. 댐퍼는 팬이 멈춘 뒤 닫는다
    engine.WRITEPOINT_PRI("VP_FWU_Command", OFF, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command_HMI", OFF, 11)
    engine.LOOP2_INIT(RAT_LOOP)
    engine.LOOP2_INIT(RDP_LOOP)
    engine.LOOP2_INIT(DELTA_T_LOOP)
    engine.LOOP2_INIT(CZT_LOOP)
    engine.WRITEPOINT("VP_FWU_SF_Speed_Value", 0)
    engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", 0, 11)
    if engine.READPOINT("VP_FWU_SF_Status") == OFF:
        engine.WRITEPOINT("FWU_SAD-1_4_COMMAND", OFF)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", OFF, 11)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", OFF, 1)
    else:
        pass  ## do_nothing
    engine.WRITEPOINT_PRI("FWU_SF-1_4_SPEED_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-5_8_SPEED_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-1.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-2.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-3.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-4.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-5.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-6.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-7.Target_RPM_Set", 0, 1)
    engine.WRITEPOINT_PRI("FWU_SF-8.Target_RPM_Set", 0, 1)

## 팬 운전 명령: 속도 값이 있으면 8대 모두 운전
if engine.READPOINT("VP_FWU_SF_Speed_Value") > 0:
    engine.WRITEPOINT("FWU_SF-1.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-2.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-3.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-4.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-5.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-6.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-7.Run_Command", ON)
    engine.WRITEPOINT("FWU_SF-8.Run_Command", ON)
else:
    engine.WRITEPOINT("FWU_SF-1.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-2.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-3.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-4.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-5.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-6.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-7.Run_Command", OFF)
    engine.WRITEPOINT("FWU_SF-8.Run_Command", OFF)

## 팬 속도 출력 (5초마다)
## 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다
if engine.SECTIMER(SPEED_OUTPUT_TIMER, TMR_READ) > 5:   ## 5초
    SFSpeed = engine.READPOINT("VP_FWU_SF_Speed_Value")
    SFMaxRPM = engine.READPOINT("VP_FWU_SF_Max_RPM")   ## Initialization이 설계 RPM과 비율로 계산해 둔 값
    SFRPMSet = engine.MIN(SFSpeed * SFMaxRPM / 100, SFMaxRPM)
    SFAOSet = SFSpeed * SFMaxRPM / engine.MAX(engine.READPOINT("VP_FWU_SF_Rated_Max_RPM"), 1)

    if engine.READPOINT("VP_FWU_SF_Comm_Fault") == TRUE:
        engine.WRITEPOINT("FWU_SF-1_4_SPEED_CONTROL", SFAOSet)
        engine.WRITEPOINT("FWU_SF-5_8_SPEED_CONTROL", SFAOSet)
        engine.WRITEPOINT("FWU_SF-1.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-2.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-3.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-4.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-5.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-6.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-7.Target_RPM_Set", 0)
        engine.WRITEPOINT("FWU_SF-8.Target_RPM_Set", 0)
    else:
        engine.WRITEPOINT("FWU_SF-1_4_SPEED_CONTROL", 0)
        engine.WRITEPOINT("FWU_SF-5_8_SPEED_CONTROL", 0)
        engine.WRITEPOINT("FWU_SF-1.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-2.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-3.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-4.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-5.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-6.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-7.Target_RPM_Set", SFRPMSet)
        engine.WRITEPOINT("FWU_SF-8.Target_RPM_Set", SFRPMSet)

    engine.SECTIMER(SPEED_OUTPUT_TIMER, TMR_CLEAR)
else:
    pass  ## do_nothing

# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]온도 고장 대체운전과 네 밸브 정지 연계: E ----
