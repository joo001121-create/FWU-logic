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
PICV_FAIL_MODE = engine.READPOINT("VP_FWU_PICV_Fail_Mode")            ## SAT 고장 시 밸브 위치 선택. 0 = 마지막 위치 유지, 1 = 안전 위치
PICV_SAFE_POSITION = engine.READPOINT("VP_FWU_PICV_Safe_Position")    ## 안전 위치 개도(%)

## 타이머 정의: 이 로직은 타이머를 쓰지 않는다

# AO3(FWU_PICV_CONTROL) 공통 명령을 네 밸브에 전달한다. 개도·유량·온도는 RS485로 각각 수신.
# 유량 모드에서 100%는 설정 최대 유량 요구이며 실제 개도 100%와 다르다.
# SAT 고장 시 100% 요구 유지. 복구 후 PI 누적 상태에 따른 출력·온도 변동 확인.
# (JSY 2026-11-23) 아래 코드 추가: SAT 센서 고장 시 밸브 위치를 정하는 보호 기능
#   - VP_FWU_PICV_Fail_Mode = 1(기본) : 안전 위치(VP_FWU_PICV_Safe_Position, 기본 100%)로 보낸다. 기존 동작과 같다.
#   - VP_FWU_PICV_Fail_Mode = 0 : 고장 직전 PI 출력(마지막 위치)을 그대로 유지한다.
#     단, 운전을 시작하고 PI 제어가 한 번도 돌기 전에 고장이 나면 '직전 명령'이 없으므로 안전 위치로 보낸다.
#     PI가 돌았는지는 VP_FWU_PICV_PI_Started에 기억하고, 운전 명령 OFF·수동 모드·비상정지·재부팅 때 지운다.
#   - 고장 중에 모드를 1→0으로 바꾸면 고장 전 PI 출력이 아니라 그때 나가던 안전 위치 값이 유지된다.
#   ※ QTS RFP 2.3.E.7(밸브 전원·제어 신호가 끊기거나 DDC가 멈췄을 때 마지막/안전 위치)은 이 코드가 아니라
#     밸브 구동부 설정(하드웨어 사양)으로 충족한다. 그때는 DDC 명령이 밸브에 닿지 않아 코드로는 대응할 수 없다.
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
                # JSY[2026.1123]SAT 센서 고장 시 밸브 마지막/안전 위치 선택 (보호 기능): S ----
                ## SAT를 믿을 수 없어 PI 제어를 멈춘다. 이때 밸브 위치는 HMI 설정(Fail_Mode)으로 고른다
                if PICV_FAIL_MODE == TRUE:   ## 1 = 안전 위치
                    engine.WRITEPOINT("FWU_PICV_CONTROL", PICV_SAFE_POSITION)
                else:
                    ## 0 = 마지막 위치 유지. 단, 이번 운전에서 PI가 한 번도 안 돌았으면 직전 명령이 없으므로 안전 위치
                    if engine.READPOINT("VP_FWU_PICV_PI_Started") == TRUE:
                        pass  ## do_nothing (출력을 새로 쓰지 않아 고장 직전 명령이 그대로 남는다)
                    else:
                        engine.WRITEPOINT("FWU_PICV_CONTROL", PICV_SAFE_POSITION)
                # JSY[2026.1123]SAT 센서 고장 시 밸브 마지막/안전 위치 선택 (보호 기능): E ----
            else:
                ## LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)
                engine.LOOP2(DEC, "FWU_SAT", "FWU_PICV_CONTROL", "VP_FWU_PICV_SAT_SP", PICV_PGAIN, PICV_IGAIN, 0, 1, 100, engine.READPOINT("VP_FWU_PICV_MinSP"), 100, PICV_LOOP, 0)
                engine.WRITEPOINT("VP_FWU_PICV_PI_Started", TRUE)   ## 이번 운전에서 PI가 돌았다는 표시 (마지막 위치 유지 판단에 씀)
        else:
            pass  ## do_nothing (명령은 있는데 팬이 아직 안 돌면 직전 출력을 그대로 둔다)

        ## 운전 명령이 꺼지면 PI 누적값을 지우고 밸브를 닫는다
        if engine.READPOINT("VP_FWU_Command") == OFF:
            engine.LOOP2_INIT(PICV_LOOP)
            engine.WRITEPOINT("VP_FWU_PICV_PI_Started", FALSE)   ## 운전이 끝났으니 PI 실행 기록도 지운다
            engine.WRITEPOINT("FWU_PICV_CONTROL", 0)
        else:
            pass  ## do_nothing
        engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", engine.READPOINT("FWU_PICV_CONTROL"), 11)
    else:
        ## 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다
        engine.LOOP2_INIT(PICV_LOOP)
        engine.WRITEPOINT("VP_FWU_PICV_PI_Started", FALSE)
        engine.RELEASE_PRI("FWU_PICV_CONTROL", 5)
else:
    ## 비상정지: 밸브를 P1으로 닫는다
    engine.LOOP2_INIT(PICV_LOOP)
    engine.WRITEPOINT("VP_FWU_PICV_PI_Started", FALSE)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 11)

# JSY[2026.1123]Coding Rule 적용(매크로 상수, 설정값 상수, if-else 짝 맞춤, 주석): E ----
# LJH[2026.1117]네 밸브 공통 냉방 명령: E ----
