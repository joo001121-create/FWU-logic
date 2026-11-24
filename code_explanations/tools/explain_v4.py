# fwu_v3 로직 14개 파일의 줄별 해설 문서(code_explanations/fwu_v3/*해석.md)를 자동으로 만든다.
#
# 사용법 (저장소 맨 위 폴더에서 실행):
#   python code_explanations/tools/explain_v4.py
#   python code_explanations/tools/explain_v4.py <로직 폴더> <출력 폴더> "<기준 표시 문구>"
# 인자를 생략하면 fwu_v3/Logic을 읽어 code_explanations/fwu_v3에 덮어쓴다.
#
# 코드를 고친 뒤 이 스크립트를 다시 돌리면 행 번호와 설명이 새 코드에 맞게 다시 만들어진다.
# 새 관제점·변수를 쓰면 아래 SINGLE(관제점 쉬운 이름), BIN_MEANING(0/1 뜻), VARDESC(변수 뜻)에 한 줄씩 추가한다.
# 새 로직 파일을 만들면 맨 아래 ORDER 목록과 INTRO(파일 소개)에 추가한다.
# (JSY 2026-11-24 작성. 코드를 바꾸지 않고 읽기만 한다)
import ast, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOGIC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "fwu_v3" / "Logic"
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "code_explanations" / "fwu_v3"
BASE = sys.argv[3] if len(sys.argv) > 3 else "sy 브랜치 2026-11-24 (댐퍼 설치 여부 설정 반영)"
EXAMPLES = {"PICV Feedback", "Zone CZT Alarm", "Zone HZT Alarm", "Zone RDP Alarm", "Damper Signal Alarm"}

SENS = {"CZT": "냉복도 온도", "HZT": "열복도 온도", "RDP": "룸 차압", "CZH": "냉복도 습도",
        "RAT": "환기 온도(RAT)", "RAH": "환기 습도(RAH)", "SAT": "급기 온도(SAT)", "SAH": "급기 습도(SAH)"}
SUFFIX = {"Avg": "평균", "Max": "최대값", "Min": "최소값", "Count": "사용 센서 수 설정", "PV": "제어용 값(PV)",
          "PV_Valid": "제어용 값 유효 표시", "Select": "제어값 선택 설정", "SP": "목표값"}
SINGLE = {
    "FWU_ATS.Current_Power": "ATS 현재 전원 통신점", "FWU_EMERGENCY": "비상정지 입력(DI)",
    "FWU_FILTER_ALARM": "필터 차압 스위치 입력(DI)", "FWU_FIRE_ALARM": "연기감지기 입력(DI)",
    "FWU_LEAK_DETECT": "누수 감지 입력(DI)", "FWU_PICV_CONTROL": "PICV 공통 개도 명령(AO)",
    "FWU_SAFLOW_DP": "급기 풍량 차압(FMS)", "REMOTE_SELECTION": "원격(BMS) 선택 입력(DI)",
    "FWU_SAD-1_4_COMMAND": "댐퍼 1~4번 개폐 명령(DO)",
    "FWU_SF-1_4_SPEED_CONTROL": "팬 1~4번 속도 AO 출력", "FWU_SF-5_8_SPEED_CONTROL": "팬 5~8번 속도 AO 출력",
    "VP_FWU_ATS_Comm_Fault": "ATS 통신 이상", "VP_FWU_BMS_Comm_Fail_Mode": "상위 통신 끊김 시 운전 방식 설정(1 최대 속도, 0 마지막 속도)",
    "VP_FWU_BMS_PLC_Comm_Fault": "상위(BMS/PLC) 통신 이상", "VP_FWU_BMS_PLC_Comm_Reset": "상위 통신 이상 Reset 입력",
    "VP_FWU_BMS_PLC_Heartbeat": "상위 heartbeat 값", "VP_FWU_BMS_PLC_Heartbeat_Prev": "직전 heartbeat 값(기억용)",
    "VP_FWU_Chilled_Water_Supply_Condition": "냉수 공급 조건 성립 표시", "VP_FWU_Command": "운전 명령(BMS)",
    "VP_FWU_Command_HMI": "운전 명령(HMI)", "VP_FWU_DeltaT_PV": "ΔT(RAT-SAT) 현재값", "VP_FWU_DeltaT_SP": "ΔT 목표값",
    "VP_FWU_Failover_Alarm": "Failover 알람", "VP_FWU_Failover_Reset": "Failover Reset 입력",
    "VP_FWU_Filter_Alarm": "필터 알람", "VP_FWU_Fire_Alarm": "화재 알람", "VP_FWU_Flow_Comm_Fault": "PICV 수신 이상 종합",
    "VP_FWU_Leak_Alarm": "누수 알람", "VP_FWU_Operation_Mode": "운전 모드(1 자동, 0 수동)",
    "VP_FWU_PICV_Alarm": "PICV 알람 종합", "VP_FWU_PICV_All_Closed": "네 밸브 모두 닫힘 표시",
    "VP_FWU_PICV_Control_Mode": "밸브 제어 모드(0 미확정, 1 위치, 2 유량)", "VP_FWU_PICV_Flow_Check_Enable": "밸브 유량 감시 사용 설정",
    "VP_FWU_PICV_IGain": "PICV PI 적분 게인", "VP_FWU_PICV_PGain": "PICV PI 비례 게인",
    "VP_FWU_PICV_Input_Enable": "PICV 통신 입력 사용 설정", "VP_FWU_PICV_Leak_Flow_Set": "누설 판단 유량 설정",
    "VP_FWU_PICV_MinSP": "PICV 최소 개도(출력 하한) 설정", "VP_FWU_PICV_Fail_Mode": "SAT 고장 시 밸브 위치 선택(0 마지막 위치 유지, 1 안전 위치)", "VP_FWU_PICV_Safe_Position": "밸브 안전 위치 개도(%)", "VP_FWU_PICV_PI_Started": "이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐)", "VP_FWU_SAD_Installed": "댐퍼 설치 여부 설정(0 없음, 1 있음)", "VP_FWU_PICV_Monitor_Ready": "밸브 감시 준비 표시",
    "VP_FWU_PICV_No_Flow_Set": "유량 없음 판단 유량 설정", "VP_FWU_PICV_SAT_SP": "급기 온도 목표값(PICV 제어)",
    "VP_FWU_RAT_SP": "환기 온도 목표값", "VP_FWU_Remote_Shutdown_Command": "원격 정지 명령",
    "VP_FWU_SAD_Conflict_Delay": "댐퍼 접점 모순 판정 시간 설정", "VP_FWU_SAD_Unknown_Delay": "댐퍼 위치 미확인 판정 시간 설정",
    "VP_FWU_SAD_Full_Close_Alarm": "댐퍼 전폐 알람", "VP_FWU_SAD_Not_Close_Alarm": "댐퍼 미폐쇄 알람",
    "VP_FWU_SAD_Not_Open_Alarm": "댐퍼 미개방 알람", "VP_FWU_SAD_Partial_Close_Alarm": "댐퍼 일부 닫힘 알람",
    "VP_FWU_SAF_Fail_DP_Set": "FMS 고장 판단 차압 설정", "VP_FWU_SAF_Fail_RPM_Set": "FMS 고장 판단 RPM 설정",
    "VP_FWU_SAF_Failure_Alarm": "FMS(풍량 차압 센서) 고장 알람", "VP_FWU_SA_Flow": "급기 풍량 계산값",
    "VP_FWU_SA_Flow_Coef": "급기 풍량 계수", "VP_FWU_SF_Comm_Fault": "팬 통신 이상 종합",
    "VP_FWU_SF_Control_Select": "팬 제어 기준 선택(0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT)",
    "VP_FWU_SF_Design_RPM": "팬 설계 RPM", "VP_FWU_SF_Failure_Alarm": "팬 종합 고장 알람",
    "VP_FWU_SF_Failure_RPM_Set": "팬 운전 판단 RPM 설정", "VP_FWU_SF_Max_RPM": "팬 최대 RPM(계산값)",
    "VP_FWU_SF_Max_RPM_Ratio": "팬 최대 RPM 비율(%)", "VP_FWU_SF_Rated_Max_RPM": "팬 정격 최대 RPM",
    "VP_FWU_SF_Run_DP_Set": "팬 운전 판단 차압 설정", "VP_FWU_SF_Speed_Max": "팬 최대 속도(%)",
    "VP_FWU_SF_Speed_Min": "팬 최소 속도(%)", "VP_FWU_SF_Speed_Value": "팬 속도 요구값(%)",
    "VP_FWU_SF_Status": "팬 운전 상태", "VP_FWU_Smoke_Action_Set": "화재 시 동작 설정(1 정지, 0 알람만)",
    "VP_FWU_Speed_SP": "고정속도 설정값(%)", "VP_FWU_Upper_Comm_Enable": "상위 통신 감시 사용 설정",
    "VP_FWU_Upper_Comm_Enable_Prev": "직전 감시 사용 상태(기억용)", "VP_FWU_Upper_Comm_Timeout": "상위 통신 끊김 판정 시간 설정(초)",
}
for g, t in (("RAT", "RAT"), ("RDP", "RDP"), ("DeltaT", "ΔT"), ("CZT", "CZT"), ("HZT", "HZT")):
    SINGLE[f"VP_FWU_SF_{g}_PGain"] = f"팬 {t} 기준 제어 P 게인"
    SINGLE[f"VP_FWU_SF_{g}_IGain"] = f"팬 {t} 기준 제어 I 게인"


def pdesc(p):
    if p in SINGLE:
        return SINGLE[p]
    m = re.fullmatch(r"VP_FWU_(CZT|HZT|RDP|CZH)-(\d+)", p)
    if m: return f"{SENS[m[1]]} {m[2]}번 값"
    m = re.fullmatch(r"VP_FWU_(CZT|HZT|RDP)-(\d+)_Failure_Alarm", p)
    if m: return f"{SENS[m[1]]} {m[2]}번 센서 고장 알람"
    m = re.fullmatch(r"VP_FWU_(RAT|RAH|SAT|SAH|CZT|HZT|RDP)_(High|Low)_Alarm(_SP)?", p)
    if m: return f"{SENS[m[1]]} {'상한' if m[2] == 'High' else '하한'} 알람" + (" 설정값" if m[3] else "")
    m = re.fullmatch(r"VP_FWU_(CZT|HZT|RDP|CZH)_(Avg|Max|Min|Count|PV_Valid|PV|Select|SP)", p)
    if m: return f"{SENS[m[1]]} {SUFFIX[m[2]]}"
    m = re.fullmatch(r"VP_FWU_(RAT|RAH|SAT|SAH)_Failure_Alarm", p)
    if m: return f"{SENS[m[1]]} 센서 고장 알람"
    m = re.fullmatch(r"FWU_(RAT|RAH|SAT|SAH)", p)
    if m: return f"{SENS[m[1]]} 센서값"
    m = re.fullmatch(r"FWU_SF-(\d)\.(Current_RPM|Run_Command|Target_RPM_Set)", p)
    if m: return f"팬 {m[1]}번 " + {"Current_RPM": "현재 RPM", "Run_Command": "운전 명령", "Target_RPM_Set": "목표 RPM"}[m[2]]
    m = re.fullmatch(r"VP_FWU_SF-(\d)_(Comm_Fault|Run_Fail_Alarm)", p)
    if m: return f"팬 {m[1]}번 " + ("통신 이상" if m[2] == "Comm_Fault" else "운전 고장 알람")
    m = re.fullmatch(r"FWU_SAD-(\d)_(OPEN|CLOSE)_STATUS", p)
    if m: return f"댐퍼 {m[1]}번 {'열림' if m[2] == 'OPEN' else '닫힘'} 접점"
    m = re.fullmatch(r"VP_FWU_SAD-(\d)_(Position_Unknown_Alarm|Signal_Conflict_Alarm)", p)
    if m: return f"댐퍼 {m[1]}번 " + ("위치 미확인 알람" if m[2].startswith("Position") else "접점 모순 알람")
    m = re.fullmatch(r"FWU_PICV-(\d)\.(Position|Flow|Temperature)", p)
    if m: return f"PICV {m[1]}번 " + {"Position": "개도", "Flow": "유량", "Temperature": "온도"}[m[2]] + " 통신점"
    m = re.fullmatch(r"VP_FWU_PICV-(\d)_(Position|Flow|Temperature|Feedback_Valid|Comm_Fault|Alarm)", p)
    if m: return f"PICV {m[1]}번 " + {"Position": "개도 표시값", "Flow": "유량 표시값", "Temperature": "온도 표시값",
                                      "Feedback_Valid": "수신값 유효 표시", "Comm_Fault": "수신 이상", "Alarm": "밸브 알람"}[m[2]]
    m = re.fullmatch(r"VP_FWU_SAF_VA-(\d)", p)
    if m: return f"급기 풍량 계수 VA-{m[1]}"
    raise KeyError(p)


def point(p):
    return f"{pdesc(p)} (`{p}`)"


MACRO_VAL = {"TMR_READ": 1, "SET": 1, "ON": 1, "TRUE": 1, "DEC": 1,
             "TMR_CLEAR": 0, "CLEAR": 0, "OFF": 0, "FALSE": 0, "INC": 0}
BIN = {ast.Add: "+", ast.Sub: "-", ast.Mult: "×", ast.Div: "÷"}
PRI_ROLE = {"1": "비상정지가 쓰는 칸, 가장 강함", "2": "원격·화재 정지가 쓰는 칸",
            "5": "일반 로직이 쓰는 칸", "11": "값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨"}

BIN_MEANING = {
    "VP_FWU_SF_Status": ("팬이 한 대도 안 돎", "팬이 한 대라도 돌고 있음"),
    "VP_FWU_Operation_Mode": ("수동 운전", "자동 운전"),
    "VP_FWU_Command": ("정지 명령", "운전 명령"),
    "VP_FWU_Command_HMI": ("정지 명령", "운전 명령"),
    "FWU_EMERGENCY": ("정상, 비상정지 아님", "비상정지 눌림"),
    "REMOTE_SELECTION": ("로컬(HMI) 선택", "원격(BMS) 선택"),
    "FWU_SAD-1_4_COMMAND": ("댐퍼 닫힘 명령", "댐퍼 열림 명령"),
    "VP_FWU_Upper_Comm_Enable": ("상위 통신 감시 안 함", "상위 통신 감시 사용"),
    "VP_FWU_Upper_Comm_Enable_Prev": ("직전 실행에서는 감시가 꺼져 있었음", "직전 실행에서도 감시가 켜져 있었음"),
    "VP_FWU_BMS_Comm_Fail_Mode": ("마지막 속도 유지", "최대 속도"),
    "VP_FWU_Smoke_Action_Set": ("알람만 냄", "정지함"),
    "VP_FWU_PICV_Fail_Mode": ("마지막 위치 유지", "안전 위치"),
    "VP_FWU_PICV_PI_Started": ("이번 운전에서 PI가 아직 안 돌았음", "이번 운전에서 PI가 돈 적 있음"),
    "VP_FWU_SAD_Installed": ("댐퍼 없음", "댐퍼 있음"),
    "VP_FWU_CZT_Select": ("평균값을 제어에 사용", "최대값을 제어에 사용"),
    "VP_FWU_HZT_Select": ("평균값을 제어에 사용", "최대값을 제어에 사용"),
    "VP_FWU_RDP_Select": ("평균값을 제어에 사용", "최소값을 제어에 사용"),
    "VP_FWU_Remote_Shutdown_Command": ("원격 정지 요청 없음", "원격 정지 요청"),
    "VP_FWU_BMS_PLC_Comm_Reset": ("Reset 안 누름", "Reset 누름"),
    "VP_FWU_Failover_Reset": ("Reset 안 누름", "Reset 누름"),
    "VP_FWU_PICV_Input_Enable": ("PICV 통신 입력 안 씀", "PICV 통신 입력 씀"),
    "VP_FWU_PICV_Flow_Check_Enable": ("유량 감시 안 함", "유량 감시 함"),
    "VP_FWU_Chilled_Water_Supply_Condition": ("냉수 공급 비정상", "냉수 공급 정상"),
    "VP_FWU_PICV_All_Closed": ("닫히지 않은 밸브가 있음", "네 밸브 모두 닫힘"),
    "VP_FWU_PICV_Monitor_Ready": ("밸브 감시 준비 안 됨", "밸브 감시 준비됨"),
    "FWU_FIRE_ALARM": ("연기 감지 안 됨", "연기 감지"),
    "FWU_FILTER_ALARM": ("필터 정상", "필터 차압 스위치 작동(필터 막힘)"),
    "FWU_LEAK_DETECT": ("누수 없음", "누수 감지"),
}


def bin_meaning(p, v):
    if p in BIN_MEANING:
        return BIN_MEANING[p][v]
    if p.endswith("Comm_Fault"):
        return ("통신 정상", "통신 이상")[v]
    if re.search(r"(Alarm|Fault)$", p):
        return ("알람 없음", "알람 걸림")[v]
    if p.endswith("Valid"):
        return ("무효, 쓸 수 없음", "유효, 쓸 수 있음")[v]
    m = re.fullmatch(r"FWU_SAD-\d_(OPEN|CLOSE)_STATUS", p)
    if m:
        return (("열림 신호 없음", "열림 확인") if m[1] == "OPEN" else ("닫힘 신호 없음", "닫힘 확인"))[v]
    if p.endswith("Run_Command"):
        return ("정지", "운전")[v]
    return None


VARDESC = {
    "mbUpperEnabled": "상위 통신 감시를 쓰는지, TRUE면 씀", "mHeartbeat": "이번에 읽은 상위 heartbeat 값",
    "mbHBOk": "heartbeat가 살아 있는지, TRUE면 정상", "mbUpperOk": "상위 통신이 정상이라 외부 센서값을 써도 되는지, TRUE면 씀",
    "mSAFlowDP": "급기 풍량 차압(Pa)", "mbSFRun": "팬이 한 대라도 돈다고 판단했는지, TRUE면 운전 중",
    "SensorValue": "방금 읽은 센서 값(임시)", "SAFlow": "계산한 급기 풍량(임시)",
    "mbFixed": "PI 대신 고정속도로 돌릴지, TRUE면 고정속도", "mbBMSFail": "상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함",
    "Speed": "고정속도로 쓸 팬 속도(임시, %)", "SFSpeed": "팬 속도 요구값(임시, %)", "SFMaxRPM": "팬 최대 RPM(임시)",
    "SFRPMSet": "팬에 보낼 목표 RPM(임시)", "SFAOSet": "팬 AO로 보낼 값(임시, %)",
    "bSADReady": "팬 속도를 정해도 되는지, 댐퍼가 없거나 네 댐퍼가 모두 열렸으면 TRUE",
    "mbRATValid": "RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위", "mbRAHValid": "RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위",
    "mbSATValid": "SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위", "mbSAHValid": "SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위",
    "mbSADAllClose": "네 댐퍼가 모두 닫혔는지, TRUE면 모두 닫힘", "mbSADAnyClose": "댐퍼가 하나라도 닫혔는지, TRUE면 하나 이상 닫힘",
    "bSFDPLow": "급기 차압이 운전 기준 이하인지, TRUE면 낮음", "SFFailCount": "고장으로 판단한 팬 대수",
    "mbShutdown": "강제 정지할지, 원격 정지나 화재 정지면 TRUE", "mbFailTotal": "Failover 원인이 하나라도 있는지, TRUE면 있음",
    "mbAllClosed": "네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘", "mbMonitorReady": "밸브 감시가 준비됐는지, TRUE면 준비됨",
    "mbAnyFault": "밸브 알람이 하나라도 있는지, TRUE면 있음", "mbAnyCommFault": "밸브 수신 이상이 하나라도 있는지, TRUE면 있음",
    "mbPICVValid": "지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효", "mbPICVInputEnable": "PICV 통신 입력을 쓰는지, TRUE면 씀",
    "mbPICVFlowChkEnable": "밸브 유량 감시를 하는지, TRUE면 함", "mbCHWSCondi": "냉수 공급이 정상인지, TRUE면 정상",
    "mPICVCurrPos": "지금 보는 밸브의 현재 개도(%)", "bValveFault": "지금 보는 밸브를 고장으로 볼지, TRUE면 고장",
    "PICVCurrFlow": "지금 보는 밸브의 현재 유량", "mbSFstat": "팬이 돌고 있는지(팬 운전 상태가 1이면 TRUE)",
    "mbSADcmd": "댐퍼 열림 명령 중인지(댐퍼 명령이 1이면 TRUE)",
}


def vdesc(n):
    if n in VARDESC:
        return VARDESC[n]
    m = re.fullmatch(r"m(CZT|HZT|RDP|CZH)(Count|Sum|Max|Min)", n)
    if m:
        return f"{SENS[m[1]]} 집계용 " + {"Count": "쓸 수 있는 센서 개수", "Sum": "합계", "Max": "최대값", "Min": "최소값"}[m[2]]
    m = re.fullmatch(r"mbSF(\d)CommFault", n)
    if m:
        return f"팬 {m[1]}번 통신 이상 여부, TRUE면 이상"
    m = re.fullmatch(r"bSF(\d)Fail", n)
    if m:
        return f"팬 {m[1]}번을 고장으로 볼지, TRUE면 고장"
    return None


def timer_name_desc(name):
    m = re.fullmatch(r"SAD_(\d)_(UNKNOWN|CONFLICT)_TIMER", name)
    if m: return f"댐퍼 {m[1]}번 {'위치 미확인' if m[2] == 'UNKNOWN' else '접점 모순'} 상태가 이어진 시간"
    m = re.fullmatch(r"(CZT|HZT|RDP)_(\d+)_FAIL_TIMER", name)
    if m: return f"{SENS[m[1]]} {m[2]}번 센서값이 고장 범위에 있던 시간"
    m = re.fullmatch(r"PICV_(\d)_DEVIATION_TIMER", name)
    if m: return f"PICV {m[1]}번 명령과 실제 개도가 크게 다른 상태가 이어진 시간"
    return name


class Ctx:
    def __init__(self):
        self.consts = {}    # name -> (값 문자열, 주석, 읽는 관제점)
        self.timers = {}    # name -> (번호, 설명)
        self.declared = set()

    @staticmethod
    def num(v):
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        return str(v)

    def macro(self, n):
        return f"{n}({MACRO_VAL[n]})"

    def name(self, n):
        if n in MACRO_VAL:
            return self.macro(n)
        if n in self.timers:
            return f"`{n}`(타이머 {self.timers[n][0]}번)"
        if n in self.consts:
            val, com, pt = self.consts[n]
            if pt:
                return f"`{n}`({com or pdesc(pt)} 설정값)" if not com else f"`{n}`(설정값: {com})"
            return f"`{n}`(= {val}" + (f", {com})" if com else ")")
        d = vdesc(n)
        return f"`{n}`({d})" if d else f"`{n}`"

    def timer(self, node):
        if isinstance(node, ast.Name) and node.id in self.timers:
            n, d = self.timers[node.id]
            return f"타이머 {n}번 `{node.id}`({d})"
        return f"타이머 {self.r(node)}번"

    def r(self, node):
        if isinstance(node, ast.Constant):
            return f'"{node.value}"' if isinstance(node.value, str) else self.num(node.value)
        if isinstance(node, ast.Name):
            return self.name(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return "-" + self.r(node.operand)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            f, a = node.func.attr, node.args
            if f == "READPOINT":
                return point(a[0].value)
            if f == "READPOINT_ALARM":
                return f"{point(a[0].value)}의 알람 코드"
            if f == "SECTIMER":
                return f"{self.timer(a[0])}으로 잰 시간(초)"
            if f in ("MAX", "MIN"):
                return f"[{', '.join(self.r(x) for x in a)}] 중 {'가장 큰 값' if f == 'MAX' else '가장 작은 값'}"
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant) and node.right.value == 0.5:
                return f"√({self.r(node.left)})"
            mul = isinstance(node.op, (ast.Mult, ast.Div))
            return f"{self.wrap(node.left, mul)} {BIN.get(type(node.op), '?')} {self.wrap(node.right, mul)}"
        if isinstance(node, (ast.Compare, ast.BoolOp)):
            return self.cond(node)
        return ast.unparse(node)

    def wrap(self, node, parent_mul=False):
        s = self.r(node)
        low = isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))
        return f"({s})" if (low and parent_mul) else s

    def binval(self, node):
        if isinstance(node, ast.Name) and node.id in MACRO_VAL:
            return MACRO_VAL[node.id]
        if isinstance(node, ast.Constant) and node.value in (0, 1) and not isinstance(node.value, bool):
            return int(node.value)
        return None

    def ptname(self, node):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "READPOINT":
            return node.args[0].value
        return None

    def atom(self, node):
        """조건 하나를 '…값이 [x]임' 꼴의 문장으로"""
        if isinstance(node, ast.Name) and node.id not in MACRO_VAL:
            return f"{self.name(node.id)} 값이 [TRUE(1)]임"
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return f"({self.cond(node.operand)})이 아님"
        if isinstance(node, ast.BoolOp):
            j = " **그리고** " if isinstance(node.op, ast.And) else " **또는** "
            return "(" + j.join(self.atom(v) for v in node.values) + ")"
        if not isinstance(node, ast.Compare):
            return self.r(node)
        ops, items = node.ops, [node.left] + node.comparators
        if len(ops) == 2:
            lo, mid, hi = items
            first = {ast.Lt: "보다 크고", ast.LtE: " 이상이고"}.get(type(ops[0]), "?")
            second = {ast.Lt: "보다 작음", ast.LtE: " 이하"}.get(type(ops[1]), "?")
            return f"{self.subj(mid)} 값이 [{self.r(lo)}]{first} [{self.r(hi)}]{second}"
        left, right, op = items[0], items[1], ops[0]
        is_timer = isinstance(left, ast.Call) and getattr(left.func, "attr", "") == "SECTIMER"
        R = self.r(right)
        if isinstance(op, ast.Eq):
            pt, bv = self.ptname(left), self.binval(right)
            if pt and bv is not None and bin_meaning(pt, bv):
                return f"{point(pt)} 값이 [{R}]임 (= {bin_meaning(pt, bv)})"
            if isinstance(left, ast.Name) and left.id in self.consts and self.consts[left.id][2] and bv is not None:
                m = bin_meaning(self.consts[left.id][2], bv)
                if m:
                    return f"{self.name(left.id)} 값이 [{R}]임 (= {m})"
            is_alarm = isinstance(left, ast.Call) and getattr(left.func, "attr", "") == "READPOINT_ALARM"
            if is_alarm and isinstance(right, ast.Name) and right.id == "COMM_FAULT_CODE":
                return f"{self.r(left)}가 [`COMM_FAULT_CODE`(= 8)]임 (= 통신 경보, 통신이 끊긴 상태)"
            if is_alarm and isinstance(right, ast.Constant) and right.value == 0:
                return f"{self.r(left)}가 [0]임 (= 알람 없음, 정상 수신)"
            simple = isinstance(right, ast.Constant) or (isinstance(right, ast.Name) and (right.id in MACRO_VAL or right.id in self.consts))
            if not simple:
                return f"{self.subj(left)} 값과 {R} 값이 같음"
            return f"{self.subj(left)} 값이 [{R}]임"
        if is_timer:
            return f"{self.r(left)}이 [{R}]초보다 " + {ast.Gt: "김", ast.GtE: "같거나 김", ast.Lt: "짧음", ast.LtE: "같거나 짧음"}[type(op)]
        tail = {ast.Gt: "보다 큼", ast.GtE: " 이상", ast.Lt: "보다 작음", ast.LtE: " 이하", ast.NotEq: "와 다름"}[type(op)]
        return f"{self.subj(left)} 값이 [{R}]{tail}"

    def subj(self, node):
        return self.r(node)

    def natom(self, node):
        """조건 하나의 '반대 상황'을 문장으로"""
        if isinstance(node, ast.Name) and node.id not in MACRO_VAL:
            return f"{self.name(node.id)} 값이 [FALSE(0)]임"
        if isinstance(node, ast.BoolOp):
            j = " **또는** " if isinstance(node.op, ast.And) else " **그리고** "
            return "(" + j.join(self.natom(v) for v in node.values) + ")"
        if not isinstance(node, ast.Compare):
            return f"({self.r(node)})이 아님"
        ops, items = node.ops, [node.left] + node.comparators
        if len(ops) == 2:
            lo, mid, hi = items
            return f"{self.subj(mid)} 값이 [{self.r(lo)}]~[{self.r(hi)}] 범위 밖임"
        left, right, op = items[0], items[1], ops[0]
        is_timer = isinstance(left, ast.Call) and getattr(left.func, "attr", "") == "SECTIMER"
        R = self.r(right)
        if isinstance(op, ast.Eq):
            pt, bv = self.ptname(left), self.binval(right)
            if pt and bv is not None and bin_meaning(pt, bv):
                return f"{point(pt)} 값이 [{R}]이 아님 (= {bin_meaning(pt, 1 - bv)})"
            if isinstance(left, ast.Name) and left.id in self.consts and self.consts[left.id][2] and bv is not None:
                m = bin_meaning(self.consts[left.id][2], 1 - bv)
                if m:
                    return f"{self.name(left.id)} 값이 [{R}]이 아님 (= {m})"
            is_alarm = isinstance(left, ast.Call) and getattr(left.func, "attr", "") == "READPOINT_ALARM"
            if is_alarm and isinstance(right, ast.Name) and right.id == "COMM_FAULT_CODE":
                return f"{self.r(left)}가 [`COMM_FAULT_CODE`(= 8)]이 아님 (= 통신 경보 없음, 통신 정상)"
            if is_alarm and isinstance(right, ast.Constant) and right.value == 0:
                return f"{self.r(left)}가 [0]이 아님 (= 알람이 있음, 수신 이상)"
            simple = isinstance(right, ast.Constant) or (isinstance(right, ast.Name) and (right.id in MACRO_VAL or right.id in self.consts))
            if not simple:
                return f"{self.subj(left)} 값과 {R} 값이 다름"
            return f"{self.subj(left)} 값이 [{R}]이 아님"
        if is_timer:
            return f"{self.r(left)}이 아직 [{R}]초를 " + {ast.Gt: "넘지 않음", ast.GtE: "채우지 못함", ast.Lt: "넘음(같거나 김)", ast.LtE: "넘음"}[type(op)]
        tail = {ast.Gt: " 이하", ast.GtE: "보다 작음", ast.Lt: " 이상", ast.LtE: "보다 큼", ast.NotEq: "와 같음"}[type(op)]
        return f"{self.subj(left)} 값이 [{R}]{tail}"

    def ncond(self, node):
        if isinstance(node, ast.BoolOp) and len(node.values) >= 2:
            circ = "①②③④⑤⑥⑦⑧⑨⑩"
            if isinstance(node.op, ast.And):
                head = "아래 조건 중 **하나라도 맞지 않음**"
                items = [self.atom(v) for v in node.values]
            else:
                head = "아래가 **모두** 맞음 (원래 조건이 하나도 맞지 않음)"
                items = [self.natom(v) for v in node.values]
            return f"{head}<br>" + "<br>".join(f"{circ[i]} {t}" for i, t in enumerate(items))
        return self.natom(node)

    def cond(self, node):
        if isinstance(node, ast.BoolOp) and len(node.values) >= 2:
            items = [self.atom(v) for v in node.values]
            circ = "①②③④⑤⑥⑦⑧⑨⑩"
            body = "<br>".join(f"{circ[i]} {t}" for i, t in enumerate(items))
            head = "다음이 **모두** 맞음" if isinstance(node.op, ast.And) else "다음 중 **하나라도** 맞음"
            return f"{head}<br>{body}"
        return self.atom(node)


def collect(lines, ctx):
    for raw in lines:
        if raw[:1].isspace():
            continue
        code, com = split_comment(raw)
        m = re.fullmatch(r"([A-Z][A-Z0-9_]*)\s*=\s*(.+)", code.strip())
        if not m:
            continue
        name, val = m[1], m[2]
        if name.endswith("_TIMER") and re.fullmatch(r"\d+", val):
            ctx.timers[name] = (val, com or timer_name_desc(name))
        elif re.fullmatch(r"-?[\d.]+", val):
            ctx.consts[name] = (val, com, None)
        else:
            pm = re.search(r'READPOINT\("([^"]+)"\)', val)
            ctx.consts[name] = ("설정값", com, pm[1] if pm else None)


def write_phrase(ctx, p, v):
    """관제점 p에 값 v를 쓰는 일을 말로"""
    if isinstance(v, ast.Call) and getattr(v.func, "attr", "") == "READPOINT":
        src = v.args[0].value
        if src == p:
            return f"{point(p)}의 지금 값을 그대로 다시 적는다"
        return f"{point(p)} 값을 {point(src)}의 지금 값과 똑같이 맞춘다"
    bv = ctx.binval(v)
    meaning = bin_meaning(p, bv) if bv is not None else None
    if meaning and re.search(r"(Alarm|Fault)$", p) and not p.endswith("Comm_Fault"):
        return f"{point(p)}을 {'켠다' if bv else '끈다'} — 값 [{ctx.r(v)}] (= {meaning})"
    if isinstance(v, (ast.BinOp, ast.Call)):
        return f"{point(p)} 값을 다음 계산값으로 바꾼다: {ctx.r(v)}"
    return f"{point(p)} 값을 [{ctx.r(v)}]로 바꾼다" + (f" (= {meaning})" if meaning else "")


def pri_text(n):
    return f"우선순위 {n} 칸({PRI_ROLE.get(n, '')})"


def explain_stmt(code, ctx, level=0):
    if code == "engine = ddc_logic()":
        return "DDC 로직 엔진을 불러온다. 이 아래에서 `engine.READPOINT`(관제점 읽기), `engine.WRITEPOINT`(관제점 쓰기) 같은 기능을 이 이름으로 쓴다"
    node = ast.parse(code).body[0]
    if isinstance(node, ast.Assign):
        t, v = node.targets[0], node.value
        if isinstance(t, ast.Tuple):
            names = [e.id for e in t.elts]
            one = ctx.r(v.elts[0]) == "1"
            why = ("타이머 읽기·켜짐·참·DEC 방향처럼 '긍정' 또는 1을 뜻하는 인자" if one else
                   "타이머 초기화·꺼짐·거짓·INC 방향처럼 '부정' 또는 0을 뜻하는 인자")
            return (f"매크로 상수 정의: {', '.join(names)}를 모두 숫자 {1 if one else 0}으로 정한다. "
                    f"코드에서 숫자 {1 if one else 0} 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 ({why})")
        n = t.id
        if n.endswith("_TIMER") and n in ctx.timers:
            num, d = ctx.timers[n]
            return f"타이머 번호에 이름 붙이기: `{n}` = 타이머 {num}번. 이 타이머로 '{d}'을 잰다 (한 로직에서 타이머는 0~9번 10개까지)"
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", n):
            val, com, pt = ctx.consts.get(n, (None, "", None))
            if isinstance(v, ast.Call) and getattr(v.func, "attr", "") == "READPOINT":
                return (f"설정값 상수 `{n}`: {point(v.args[0].value)} 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다"
                        + (f". 뜻: {com}" if com else ""))
            if n.endswith("_LOOP"):
                return f"PI 루프 번호에 이름 붙이기: `{n}` = {ctx.r(v)}번" + (f". {com}" if com else "")
            return f"상수 `{n}` = {ctx.r(v)}" + (f". 뜻: {com}" if com else "")
        d = vdesc(n)
        label = f"`{n}`({d})" if d else f"`{n}`"
        decl = level == 0 and n.startswith("m") and n not in ctx.declared
        ctx.declared.add(n)
        if decl and (isinstance(v, ast.Constant) or (isinstance(v, ast.Name) and v.id in MACRO_VAL) or isinstance(v, ast.UnaryOp)):
            first = ctx.r(v)
            hint = ""
            if first in ("-1000", "1000"):
                hint = " (최대·최소를 찾을 때 어떤 센서값보다도 작은/큰 값에서 시작하기 위한 값)"
            return f"전역변수 {label}를 만들고 처음 값을 [{first}]로 둔다{hint}. 이 로직이 실행될 때마다 이 값에서 다시 시작한다"
        if isinstance(v, (ast.Compare, ast.BoolOp)) or (isinstance(v, ast.Name) and v.id not in MACRO_VAL and v.id not in ctx.consts):
            return f"{label}에 판단 결과를 넣는다: {ctx.cond(v)}<br>→ 맞으면 TRUE(1), 아니면 FALSE(0)"
        if isinstance(v, ast.Call) and getattr(v.func, "attr", "") == "READPOINT":
            return f"{label}에 {point(v.args[0].value)} 값을 읽어 넣는다"
        if isinstance(v, ast.BinOp) and isinstance(v.left, ast.Name) and v.left.id == n and isinstance(v.op, ast.Add):
            if isinstance(v.right, ast.Constant) and v.right.value == 1:
                return f"{label}를 1 늘린다 (하나 더 센다)"
            return f"{label}에 {ctx.r(v.right)}를 더한다"
        if isinstance(v, ast.Constant) or (isinstance(v, ast.Name) and v.id in MACRO_VAL):
            return f"{label} 값을 [{ctx.r(v)}]로 바꾼다"
        return f"{label}에 다음 계산값을 넣는다: {ctx.r(v)}"
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        c = node.value
        f, a = c.func.attr, c.args
        if f == "WRITEPOINT":
            return f"{write_phrase(ctx, a[0].value, a[1])} — {pri_text('5')}"
        if f == "WRITEPOINT_PRI":
            pr = ctx.r(a[2])
            if isinstance(a[1], ast.Call) and getattr(a[1].func, "attr", "") == "READPOINT" and a[1].args[0].value == a[0].value:
                return (f"{point(a[0].value)}의 지금 값을 {pri_text(pr)}에도 똑같이 적어 둔다. "
                        "자동 운전에서 계산한 값을 보관해 두어, 수동으로 바꾸거나 다시 시작할 때 이 값부터 이어가게 한다")
            return f"{write_phrase(ctx, a[0].value, a[1])} — {pri_text(pr)}에 쓴다"
        if f == "RELEASE_PRI":
            pr = ctx.r(a[1])
            return (f"{point(a[0].value)}의 {pri_text(pr)}에 써 둔 값을 지운다. "
                    "그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다")
        if f == "SECTIMER":
            return f"{ctx.timer(a[0])}를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다"
        if f == "LOOP2_INIT":
            n = a[0].id if isinstance(a[0], ast.Name) else None
            d = ctx.consts.get(n, ("", "", None))[1] if n else ""
            return (f"PI 루프 {ctx.r(a[0])}의 누적값(I 적분값)을 지운다" + (f" ({d})" if d else "")
                    + ". 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다")
        if f == "LOOP2":
            dec = ctx.r(a[0]).startswith("DEC")
            pv = point(a[1].value) if isinstance(a[1], ast.Constant) else ctx.r(a[1])
            return ("**PI 자동 제어 실행**: " + f"{pv}이(가) {point(a[3].value)}에 가까워지도록 {point(a[2].value)}을 계산해서 쓴다 — {pri_text('5')}<br>"
                    + ("· 방향 DEC: 현재값이 목표보다 **높으면 출력을 올린다** (예: 온도가 높으면 더 세게)<br>" if dec else
                       "· 방향 INC: 현재값이 목표보다 **낮으면 출력을 올린다** (예: 차압이 낮으면 더 세게)<br>")
                    + f"· 비례 게인 P = {ctx.r(a[4])}, 적분 게인 I = {ctx.r(a[5])}, 미분 D = {ctx.r(a[6])} (0이면 안 씀)<br>"
                    + f"· 계산 주기 = {ctx.r(a[7])}초 (0이면 기본 1초)<br>"
                    + f"· 처음 시작할 때 출력 = {ctx.r(a[8])}<br>"
                    + f"· 출력 범위 = {ctx.r(a[9])} ~ {ctx.r(a[10])} (이 범위 밖으로는 내보내지 않음)<br>"
                    + f"· 루프 번호 = {ctx.r(a[11])} (LOOP2_INIT으로 이 제어를 초기화할 때 쓰는 번호)<br>"
                    + f"· 데드밴드 = {ctx.r(a[12])} (0이면 없음)")
    return f"`{code}`"


def split_comment(line):
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q: q = None
        elif ch in "\"'":
            q = ch
        elif ch == "#":
            return line[:i].rstrip(), line[i:].lstrip("#").strip()
    return line.rstrip(), ""


TAG = re.compile(r"#\s*([A-Z]{2,4})\[(\d{4})\.(\d{2})(\d{2})\](.*?)(?::\s*([SE])\s*-+)?\s*$")


def comment_text(raw):
    m = TAG.match(raw.strip())
    if m:
        who, y, mo, d, topic, se = m.groups()
        topic = topic.strip()
        kind = {"S": "수정 구간 시작", "E": "수정 구간 끝"}.get(se, "수정 표시")
        return f"*[주석] {who} {y}-{mo}-{d} {kind}. 주제 = {topic}*"
    return f"*[주석] {raw.strip().lstrip('#').strip()}*"


def explain_file(path):
    name = path.stem
    raw = path.read_text(encoding="utf-8").split("\n")
    if raw and raw[-1] == "":
        raw = raw[:-1]
    ctx = Ctx()
    collect(raw, ctx)
    rows, last_if = [], {}
    for no, line in enumerate(raw, 1):
        if not line.strip():
            continue
        exp = line.expandtabs(4)
        level = (len(exp) - len(exp.lstrip(" "))) // 4
        s = exp.strip()
        arrow = ("&emsp;" * level + "→&nbsp;") if level else ""
        if s.startswith("#"):
            rows.append((no, level, s, arrow + comment_text(s)))
            continue
        code, com = split_comment(s)
        if code.startswith("if ") and code.endswith(":"):
            cnode = ast.parse(code[3:-1].strip(), mode='eval').body
            ctext = ctx.cond(cnode)
            last_if[level] = (no, ctx.ncond(cnode))
            text = f"**[조건]** {ctext}<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다"
        elif code == "else:":
            ino, ntext = last_if.get(level, ("?", "?"))
            text = f"**[아니면]** {ino}행 조건의 반대 상황, 즉 {ntext}<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다"
        elif code.startswith("else:") and code[5:].strip().startswith("pass"):
            ino, ntext = last_if.get(level, ("?", "?"))
            text = f"**[아니면]** {ino}행 조건의 반대 상황, 즉 {ntext}<br>→ 이때는 아무것도 하지 않는다"
        elif code == "pass":
            text = "아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing)"
        else:
            text = explain_stmt(code, ctx, level)
        if com.startswith("do_nothing"):
            extra = com[len("do_nothing"):].strip(" ()")
            text += f" — {extra}" if extra else ""
        elif com and com not in text:
            text += f"<br>*[주석] {com}*"
        rows.append((no, level, s, arrow + text))
    # 구간 나누기: 맨 바깥 '## ' 주석 묶음에서 새 구간 시작 (머리말 선언부 제외)
    HEADER = ("## 로직엔진", "## Macro상수", "## 타이머 정의", "## 전역변수", "## 외부 센서 집계값", "## 팬 8대의 통신", "## DEC/INC")
    sections, cur = [], {"title": "머리말 · 로직 엔진, 상수, 타이머, 전역변수", "summary": [], "rows": []}
    collecting = False
    for no, level, s, text in rows:
        is2 = level == 0 and s.startswith("## ")
        after_blank = no == 1 or raw[no - 2].strip() == ""
        if is2 and after_blank and not s.startswith(HEADER) and cur["rows"]:
            sections.append(cur)
            cur = {"title": s[3:].strip(), "summary": [], "rows": []}
            collecting = True
        elif collecting and is2:
            cur["summary"].append(s[3:].strip())
        else:
            collecting = False
        cur["rows"].append((no, level, s, text))
    sections.append(cur)
    return name, raw, sections


INTRO = {
    "Initialization": "상위(BMS/PLC) 통신을 감시하고, 외부 센서(냉복도·열복도 온도, 룸 차압, 냉복도 습도) 값을 모아 평균·최대·최소와 제어용 값을 만든다. 팬 운전 상태 판단, 급기 풍량 계산, 운전 명령 동기화, 팬 최대 RPM 계산도 여기서 한다.",
    "PICV Control": "네 PICV에 공통 개도 명령 하나를 낸다. 자동 운전 중에는 급기 온도(SAT) 기준 PI 제어를 하고, SAT 고장 시에는 사용자 설정에 따라 마지막 위치를 유지하거나 안전 위치로 보낸다. 비상정지 때는 밸브를 닫는다.",
    "SF Control": "팬 제어 기준(고정속도·RAT·RDP·ΔT·CZT)에 따라 팬 속도를 정하고, 댐퍼·밸브와 연계해 기동과 정지를 한다. 5초마다 팬 목표 RPM(팬 통신 이상 시 AO)을 내보낸다.",
    "Sensor Limit Alarm": "내부 센서(RAT·RAH·SAT·SAH)와 외부 센서 집계값(CZT·HZT·RDP)의 상·하한 알람, 내부 센서 고장, FMS 고장을 판단한다. 기존 Alarm-1에서 떼어 만든 파일이다.",
    "Fan Damper Alarm": "팬 8대의 운전 고장과 종합 팬 고장, 댐퍼 보호 알람(일부 닫힘·전폐·미개방·미폐쇄)을 판단한다. 기존 Alarm-1에서 떼어 만든 파일이다.",
    "Leak Filter Alarm": "누수 알람과 필터 알람을 낸다. 기존 Alarm-2에서 이름만 바꾼 파일이다.",
    "Comm Fault Alarm": "팬 8대와 ATS의 통신 이상을 감시한다. 기존 Alarm-3에서 이름만 바꾼 파일이다.",
    "Remote Shutdown": "연기감지기 신호를 확인해 화재 알람을 내고, 원격 정지 명령이 있거나 화재 시 정지 설정이면 운전 명령과 출력을 0으로 누른다.",
    "Failover": "댐퍼 미개방·전폐 또는 팬 종합 고장이 이어지면 Failover 알람을 내고 운전 OFF를 한 번 기록한다. 원인이 없어진 뒤 Reset으로 해제한다.",
    "PICV Feedback": "PICV 4대의 개도·유량·온도 수신값을 확인하고, 닫힘 여부·명령-개도 차이·유량 이상을 판단해 밸브별 알람과 종합 상태를 낸다. refac 예제 원본 파일이다.",
    "Zone CZT Alarm": "사용하도록 설정한 냉복도 온도 센서의 값이 0℃ 미만인 상태가 20초를 넘으면 센서 고장 알람을 낸다. refac 예제 원본 파일이다.",
    "Zone HZT Alarm": "사용하도록 설정한 열복도 온도 센서의 값이 0℃ 미만인 상태가 20초를 넘으면 센서 고장 알람을 낸다. refac 예제 원본 파일이다.",
    "Zone RDP Alarm": "사용하도록 설정한 룸 차압 센서의 값이 0 이하인 상태가 20초를 넘으면 센서 고장 알람을 낸다. refac 예제 원본 파일이다.",
    "Damper Signal Alarm": "댐퍼 4개의 열림·닫힘 접점이 둘 다 꺼져 있거나(위치 미확인) 둘 다 켜져 있는(접점 모순) 상태를 감시한다. refac 예제 원본 파일이다.",
}
NOTE = {
    "PICV Feedback": "**※** 이 파일(refac 예제 원본)은 탭과 스페이스가 섞여 있어 Python에서 TabError가 난다. 원본을 그대로 두었으며, 아래 들여쓰기 단계는 탭을 4칸으로 보고 표시했다.",
    "Zone RDP Alarm": "**※** refac 예제 원본이라 일부 if에 짝이 되는 else가 없다(원본 그대로 해석).",
}


def write_md(name, raw, sections):
    ex = name in EXAMPLES
    nonblank = len(raw)
    out = [f"# {name} 줄별 해석", "",
           f"> **대상 코드** : `fwu_v3/Logic/{name}.py` ({nonblank} 줄{', refac 예제 원본' if ex else ''})  ",
           f"> **기준** : `{BASE}`  ",
           "> **행** = 코드 줄 번호 (빈 줄은 생략)  ",
           "> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점",
           "", INTRO[name], ""]
    if name in NOTE:
        out += [NOTE[name], ""]
    out += ["**목차**", ""]
    for i, sec in enumerate(sections, 1):
        a, b = sec["rows"][0][0], sec["rows"][-1][0]
        sec["range"] = f"{a}~{b}행" if a != b else f"{a}행"
        out.append(f"- [{sec['range']} · {sec['title']}](#section-{i})")
    out += ["", "**※ 읽는 법**", "",
            "- **[조건]** 줄은 조건이 맞을 때만 바로 아래 한 칸 더 들여쓴(→가 하나 더 붙은) 줄들을 실행한다. **[아니면]** 줄은 그 조건이 맞지 않을 때 실행하는 부분이다.",
            "- 값은 [ ] 안에 적었다. TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0 이다. 0/1 값 옆 (= …)은 그 관제점에서 0/1이 뜻하는 상태다.",
            "- **우선순위 칸**: 관제점 하나에 번호가 붙은 여러 칸이 있고, **숫자가 작은 칸의 값이 이긴다**. 1 = 비상정지, 2 = 원격·화재 정지, 5 = 일반 로직(번호 없이 쓰는 `WRITEPOINT`), 11 = 값 보관·정지 요청. 칸을 지우면(해제) 그다음 칸의 값이 적용된다.",
            "- 조건이 맞지 않는다고 관제점이 저절로 0이 되지는 않는다. 그 분기에 쓰는 줄이 없으면 **이전 값이 그대로 남는다**.",
            "- 타이머는 0으로 되돌린 순간부터 흐른 시간(초)을 잰다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일 전체에서 쓰는 변수, 이름에 `b`가 붙은 변수는 TRUE/FALSE 값이다.", ""]
    for i, sec in enumerate(sections, 1):
        out += [f'<a id="section-{i}"></a>', "", f"## {sec['range']} · {sec['title']}", ""]
        if sec["summary"]:
            out += ["> " + " ".join(sec["summary"]), ""]
        out += ["| 행 | 해석 |", "|---:|---|"]
        for no, level, s, text in sec["rows"]:
            out.append(f"| {no} | {text.replace('|', '&#124;')} |")
        out.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name.lower()}해석.md").write_text("\n".join(out), encoding="utf-8")


ORDER = ["PICV Feedback", "Zone CZT Alarm", "Zone HZT Alarm", "Zone RDP Alarm", "Damper Signal Alarm", "Initialization",
         "PICV Control", "SF Control", "Sensor Limit Alarm", "Fan Damper Alarm", "Leak Filter Alarm", "Comm Fault Alarm",
         "Remote Shutdown", "Failover"]
for n in ORDER:
    name, raw, secs = explain_file(LOGIC / f"{n}.py")
    write_md(name, raw, secs)
    print(f"{n}: {len(raw)}줄, 구간 {len(secs)}개")
