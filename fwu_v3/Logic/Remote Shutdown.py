# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: S ----
# JSY[2026.1124]Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석): S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
FIRE_CONFIRM_SECONDS = 3   ## 감지기 신호가 잠깐 튀는 걸 화재로 보지 않도록, 3초 넘게 이어질 때만 알람

## 타이머 정의
FIRE_CONFIRM_TIMER = 0     ## 연기감지기 신호가 이어진 시간

## 전역변수 선언
mbShutdown = FALSE         ## 원격 정지나 화재 정지 중 하나라도 걸리면 TRUE

## 연기감지기 신호 확인 → 화재 알람
if engine.READPOINT("FWU_FIRE_ALARM") == TRUE:
    if engine.SECTIMER(FIRE_CONFIRM_TIMER, TMR_READ) > FIRE_CONFIRM_SECONDS:
        engine.WRITEPOINT("VP_FWU_Fire_Alarm", TRUE)
    else:
        pass  ## do_nothing
else:
    engine.SECTIMER(FIRE_CONFIRM_TIMER, TMR_CLEAR)
    engine.WRITEPOINT("VP_FWU_Fire_Alarm", FALSE)

## 정지 조건 확인
## 화재 때 정지할지는 HMI의 Smoke_Action_Set으로 고른다.
## 일반 운전 ON/OFF와 별개인 강제 정지라서 로컬·수동 운전 중에도 걸린다.
## 하드웨어 화재 차단 회로는 이 설정과 상관없이 따로 동작한다.
if engine.READPOINT("VP_FWU_Remote_Shutdown_Command") == TRUE:   ## 사용자(HMI/BMS)가 원격 정지를 걸면 1
    mbShutdown = TRUE
else:
    pass  ## do_nothing

if engine.READPOINT("VP_FWU_Fire_Alarm") == TRUE and engine.READPOINT("VP_FWU_Smoke_Action_Set") == TRUE:   ## Smoke_Action_Set 1 = 정지, 0 = 알람만
    mbShutdown = TRUE
else:
    pass  ## do_nothing

## 강제 정지: 운전 명령과 출력을 0으로 누른다 (P2·P11)
if mbShutdown == TRUE:
    engine.WRITEPOINT_PRI("VP_FWU_Command", OFF, 11)
    engine.WRITEPOINT_PRI("VP_FWU_Command_HMI", OFF, 11)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 11)
    engine.WRITEPOINT_PRI("VP_FWU_SF_Speed_Value", 0, 11)
    engine.WRITEPOINT_PRI("FWU_SF-1_4_SPEED_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5_8_SPEED_CONTROL", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-1.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-2.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-3.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-4.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-6.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-7.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-8.Target_RPM_Set", 0, 2)
    engine.WRITEPOINT_PRI("FWU_SF-1.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-2.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-3.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-4.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-5.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-6.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-7.Run_Command", OFF, 2)
    engine.WRITEPOINT_PRI("FWU_SF-8.Run_Command", OFF, 2)

    ## 댐퍼는 팬이 다 멈춘 걸 확인한 뒤에 닫는다
    if engine.READPOINT("VP_FWU_SF_Status") == OFF:
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", OFF, 2)
        engine.WRITEPOINT_PRI("FWU_SAD-1_4_COMMAND", OFF, 11)
    else:
        pass  ## do_nothing
else:
    ## 정지 해제: P2만 풀어 준다.
    ## P11에 남은 OFF는 재기동을 막는 래치가 아니어서, 더 높은 우선순위에 운전 명령이 남아 있으면 다시 돈다.
    engine.RELEASE_PRI("FWU_PICV_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-1_4_SPEED_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-5_8_SPEED_CONTROL", 2)
    engine.RELEASE_PRI("FWU_SF-1.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-2.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-3.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-4.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-5.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-6.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-7.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-8.Target_RPM_Set", 2)
    engine.RELEASE_PRI("FWU_SF-1.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-2.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-3.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-4.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-5.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-6.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-7.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SF-8.Run_Command", 2)
    engine.RELEASE_PRI("FWU_SAD-1_4_COMMAND", 2)

# JSY[2026.1124]Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]원격 및 연기 정지 우선순위 유지: E ----
