# JSY[2026.1123]Alarm-3에서 이름 변경(팬·ATS 통신 이상 알람만 남아 내용에 맞춤), Coding Rule 적용: S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
COMM_FAULT_CODE = 8              ## READPOINT_ALARM 결과 8 = 통신 경보 (LDPL 가이드 4.10)
FAN_COMM_CONFIRM_SECONDS = 10    ## 팬 통신 이상이 10초 넘게 이어지면 알람
ATS_COMM_CONFIRM_SECONDS = 10    ## ATS 통신 이상이 10초 넘게 이어지면 알람

## 타이머 정의 (번호는 Alarm-3에서 쓰던 그대로)
SF_1_COMM_TIMER = 0    ## 팬1 통신 이상이 이어진 시간
SF_2_COMM_TIMER = 1    ## 팬2 통신 이상이 이어진 시간
SF_3_COMM_TIMER = 2    ## 팬3 통신 이상이 이어진 시간
SF_4_COMM_TIMER = 3    ## 팬4 통신 이상이 이어진 시간
SF_5_COMM_TIMER = 4    ## 팬5 통신 이상이 이어진 시간
SF_6_COMM_TIMER = 5    ## 팬6 통신 이상이 이어진 시간
SF_7_COMM_TIMER = 6    ## 팬7 통신 이상이 이어진 시간
SF_8_COMM_TIMER = 7    ## 팬8 통신 이상이 이어진 시간
ATS_COMM_TIMER = 8     ## ATS 통신 이상이 이어진 시간

# ATS는 CH2 RS485 구성으로 연결할 것. DI 입력 표기와 실제 HW 구성을 대조한다.
# 현재 XML 통신 포트 배치는 구형 맵이므로 실장 전에 수정해야 한다.

## 팬 1~8 통신 이상: 각 팬의 Current_RPM 점에 통신 경보(8)가 떠 있는지로 본다
if engine.READPOINT_ALARM("FWU_SF-1.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_1_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-1_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-1_Comm_Fault", FALSE)
    engine.SECTIMER(SF_1_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-2.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_2_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-2_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-2_Comm_Fault", FALSE)
    engine.SECTIMER(SF_2_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-3.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_3_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-3_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-3_Comm_Fault", FALSE)
    engine.SECTIMER(SF_3_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-4.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_4_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-4_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-4_Comm_Fault", FALSE)
    engine.SECTIMER(SF_4_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-5.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_5_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-5_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-5_Comm_Fault", FALSE)
    engine.SECTIMER(SF_5_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-6.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_6_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-6_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-6_Comm_Fault", FALSE)
    engine.SECTIMER(SF_6_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-7.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_7_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-7_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-7_Comm_Fault", FALSE)
    engine.SECTIMER(SF_7_COMM_TIMER, TMR_CLEAR)

if engine.READPOINT_ALARM("FWU_SF-8.Current_RPM") == COMM_FAULT_CODE:
    if engine.SECTIMER(SF_8_COMM_TIMER, TMR_READ) > FAN_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_SF-8_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_SF-8_Comm_Fault", FALSE)
    engine.SECTIMER(SF_8_COMM_TIMER, TMR_CLEAR)

## 팬 통신 종합: 한 대라도 이상이면 TRUE (SF Control이 이 값을 보고 AO 출력으로 바꾼다)
if engine.READPOINT("VP_FWU_SF-1_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-2_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-3_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-4_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-5_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-6_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-7_Comm_Fault") == TRUE or engine.READPOINT("VP_FWU_SF-8_Comm_Fault") == TRUE:
    engine.WRITEPOINT("VP_FWU_SF_Comm_Fault", TRUE)
else:
    engine.WRITEPOINT("VP_FWU_SF_Comm_Fault", FALSE)

## ATS 통신 이상
if engine.READPOINT_ALARM("FWU_ATS.Current_Power") == COMM_FAULT_CODE:
    if engine.SECTIMER(ATS_COMM_TIMER, TMR_READ) > ATS_COMM_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_ATS_Comm_Fault", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.WRITEPOINT("VP_FWU_ATS_Comm_Fault", FALSE)
    engine.SECTIMER(ATS_COMM_TIMER, TMR_CLEAR)

# JSY[2026.1123]Alarm-3에서 이름 변경(팬·ATS 통신 이상 알람만 남아 내용에 맞춤), Coding Rule 적용: E ----
# LJH[2026.1117]기존 단일 유량계 감시 분리
