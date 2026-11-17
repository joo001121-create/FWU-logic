# LJH[2026.1117]네 밸브 공통 냉방 명령: S ----
PICV_LOOP = 1
# AO3 공통 명령을 네 밸브에 전달한다. 개도·유량·온도는 RS485로 각각 수신.
# 유량 모드에서 100%는 설정 최대 유량 요구이며 실제 개도 100%와 다르다.
# SAT 고장 시 100% 요구 유지. 복구 후 PI 누적 상태에 따른 출력·온도 변동 확인.
# Command=1이고 팬 정지 상태이면 기존 명령 유지. 비상 P1·원격 P2는 별도 우선.
# 수동 Command=0은 자동 닫힘 아님. 무풍 중 냉수 공급에 대한 HMI 안내 검토.
# AO 단선·전원 상실 시 위치는 제조사 확인 후 대응 기능 적용 여부 결정.
engine = ddc_logic()

picv_p = engine.READPOINT("VP_FWU_PICV_PGain")
picv_i = engine.READPOINT("VP_FWU_PICV_IGain")

if engine.READPOINT("FWU_EMERGENCY") == 0 :
    engine.RELEASE_PRI("FWU_PICV_CONTROL", 1)
    if engine.READPOINT("VP_FWU_Operation_Mode") == 1:
        if engine.READPOINT("VP_FWU_Command") == 1 and engine.READPOINT("VP_FWU_SF_Status") == 1 :
            if engine.READPOINT("VP_FWU_SAT_Failure_Alarm") == 1 :
                engine.WRITEPOINT("FWU_PICV_CONTROL", 100)
            else :
                engine.LOOP2(1, "FWU_SAT", "FWU_PICV_CONTROL", "VP_FWU_PICV_SAT_SP", picv_p, picv_i, 0, 1, 100, engine.READPOINT("VP_FWU_PICV_MinSP"), 100, PICV_LOOP, 0)
        if engine.READPOINT("VP_FWU_Command") == 0 :
            engine.LOOP2_INIT(PICV_LOOP)
            engine.WRITEPOINT("FWU_PICV_CONTROL", 0)
        engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", engine.READPOINT("FWU_PICV_CONTROL"), 11)
    else:
        engine.LOOP2_INIT(PICV_LOOP)
        engine.RELEASE_PRI("FWU_PICV_CONTROL", 5)
else:
    engine.LOOP2_INIT(PICV_LOOP)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 1)
    engine.WRITEPOINT_PRI("FWU_PICV_CONTROL", 0, 11)
# LJH[2026.1117]네 밸브 공통 냉방 명령: E ----
