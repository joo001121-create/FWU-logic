# LJH[2026.1117]네 밸브 공통 냉방 명령: S ----
# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, if-else 짝 맞춤, 주석): S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0

## DEC/INC는 LOOP2 제어 방향 (DEC: 현재값을 내리는 제어, INC: 현재값을 올리는 제어)
PICV_LOOP = 1     ## 이 로직의 LOOP2 번호 (같은 출력점에는 같은 번호를 쓴다)
PICV_PGAIN = engine.READPOINT("VP_FWU_PICV_PGain")    ## SAT 기준 냉수밸브 PI 제어의 P 게인
PICV_IGAIN = engine.READPOINT("VP_FWU_PICV_IGain")    ## 같은 제어의 I 게인

## 타이머 정의: 이 로직은 타이머를 쓰지 않는다

# AO3(FWU_PICV_CONTROL) 공통 명령을 네 밸브에 전달한다. 개도·유량·온도는 RS485로 각각 수신.
# 유량 모드에서 100%는 설정 최대 유량 요구이며 실제 개도 100%와 다르다.
# SAT 고장 시 100% 요구 유지. 복구 후 PI 누적 상태에 따른 출력·온도 변동 확인.
# Command=1이고 팬 정지 상태이면 기존 명령 유지. 비상 P1·원격 P2는 별도 우선.
# 수동 Command=0은 자동 닫힘 아님. 무풍 중 냉수 공급에 대한 HMI 안내 검토.
# AO 단선·전원 상실 시 위치는 제조사 확인 후 대응 기능 적용 여부 결정. (단선 시 0%로 돌아가는 밸브는 사용X 해야함)

## 비상정지가 아닐 때: 자동이면 SAT 기준으로 밸브를 제어하고, 수동이면 로직 출력을 내려놓는다
if engine.READPOINT("FWU_EMERGENCY") == FALSE:
    engine.RELEASE_PRI("FWU_PICV_CONTROL", 1)   ## 비상정지 때 걸어 둔 P1 해제

    if engine.READPOINT("VP_FWU_Operation_Mode") == TRUE:   ## Operation_Mode 1 = 자동, 0 = 수동
        ## 운전 명령이 있고 팬이 돌 때만 SAT 기준으로 제어한다
        if engine.READPOINT("VP_FWU_Command") == ON and engine.READPOINT("VP_FWU_SF_Status") == ON:
            if engine.READPOINT("VP_FWU_SAT_Failure_Alarm") == TRUE:
                engine.WRITEPOINT("FWU_PICV_CONTROL", 100)   ## SAT를 믿을 수 없으면 냉방이 모자라지 않게 100%
            else:
                ## LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)
                engine.LOOP2(DEC, "FWU_SAT", "FWU_PICV_CONTROL", "VP_FWU_PICV_SAT_SP", PICV_PGAIN, PICV_IGAIN, 0, 1, 100, engine.READPOINT("VP_FWU_PICV_MinSP"), 100, PICV_LOOP, 0)
        else:
            pass  ## do_nothing (명령은 있는데 팬이 아직 안 돌면 직전 출력을 그대로 둔다)

        ## 운전 명령이 꺼지면 PI 누적값을 지우고 밸브를 닫는다
        if engine.READPOINT("VP_FWU_Command") == OFF:
            engine.LOOP2_INIT(PICV_LOOP)
            engine.WRITEPOINT("FWU_PICV_CONTROL", 0)
        else:
            pass  ## do_nothing
        engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", engine.READPOINT("FWU_PICV_CONTROL"), 11)
    else:
        ## 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다
        engine.LOOP2_INIT(PICV_LOOP)
        engine.RELEASE_PRI("FWU_PICV_CONTROL", 5)
else:
    ## 비상정지: 밸브를 P1으로 닫는다
    engine.LOOP2_INIT(PICV_LOOP)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 11)

# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]네 밸브 공통 냉방 명령: E ----
