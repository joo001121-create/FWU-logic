# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: S ----

## 로직엔진 loading
engine = ddc_logic()

## Macro상수 정의
TMR_READ, SET, ON, TRUE, DEC = 1, 1, 1, 1, 1
TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0, 0, 0, 0, 0
DEV_TIME_OUT = 40   ## deviation timer는 40초 까지
POS_HYST = 30       ## 개도의 히스테리시스는 +/-30% 까지
POS_OPEN = 30       ## 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단
NO_FLOW = engine.READPOINT("VP_FWU_PICV_No_Flow_Set")   ## '유량없음'으로 판단하는 최소 유량
LEAK_FLOW = engine.READPOINT("VP_FWU_PICV_Leak_Flow_Set")   ## leak로 판단하는 유량 (?)

## 타이머 정의: PICV의 현재 개도가 tolerance를 벗어난 경우
PICV_1_DEVIATION_TIMER = 4
PICV_2_DEVIATION_TIMER = 5
PICV_3_DEVIATION_TIMER = 6
PICV_4_DEVIATION_TIMER = 7

# CH3에 FWU_PICV-1~4의 Position, Flow, Temperature 통신점을 등록한 뒤 Input_Enable=1로 설정
# 개도는 %, 유량은 L/min, 온도는 냉수 출구 온도(℃)로 환산

## 전역변수 선언
mbAllClosed = TRUE
mbMonitorReady = TRUE
mbAnyFault = FALSE
mbAnyCommFault = FALSE
mbPICVValid = FALSE
mbPICVInputEnable = engine.READPOINT("VP_FWU_PICV_Input_Enable") == 1
mbPICVFlowChkEnable = engine.READPOINT("VP_FWU_PICV_Flow_Check_Enable") == 1
mbCHWSCondi = engine.READPOINT("VP_FWU_Chilled_Water_Supply_Condition") == 1
mPICVCurrPos = 0    ## PICV의 현재 개도값

## PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)
mbPICVValid = FALSE ## 초기화
if mbPICVInputEnable:
    if engine.READPOINT_ALARM("FWU_PICV-1.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-1.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-1.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-1_Position", engine.READPOINT("FWU_PICV-1.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-1_Flow", engine.READPOINT("FWU_PICV-1.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-1_Temperature", engine.READPOINT("FWU_PICV-1.Temperature"))
        mbPICVValid = TRUE
    else: 
		pass ## do_nothing
	
mPICVCurrPos = engine.READPOINT("VP_FWU_PICV-1_Position")
if (0 <= mPICVCurrPos <= 100): 
	pass ## do_nothing
else: 
	mbPICVValid = FALSE	
engine.WRITEPOINT("VP_FWU_PICV-1_Feedback_Valid", mbPICVValid)

## PICV1(2/2): 개도 및 유량 범위 확인
if mbPICVValid:    
    engine.WRITEPOINT("VP_FWU_PICV-1_Comm_Fault", FALSE)
	
    if mPICVCurrPos >= 5: 
		mbAllClosed = FALSE
    else: 
		pass  ## do_nothing
    
    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    bValveFault = FALSE
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1: ## 좌변이 boolean인가? (?)
        if (mPICVCurrPos - POS_HYST < engine.READPOINT("FWU_PICV_CONTROL") < mPICVCurrPos + POS_HYST):
            engine.SECTIMER(PICV_1_DEVIATION_TIMER, TMR_CLEAR)            
        else:
            if engine.SECTIMER(PICV_1_DEVIATION_TIMER, TMR_READ) > DEV_TIME_OUT: 
				bValveFault = TRUE
            else: 
				pass  ## do_nothing            
    else: 
		engine.SECTIMER(PICV_1_DEVIATION_TIMER, TMR_CLEAR)
    
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if mbPICVFlowChkEnable:
        PICVCurrFlow = engine.READPOINT("VP_FWU_PICV-1_Flow")
        if mbCHWSCondi and mPICVCurrPos > POS_OPEN and PICVCurrFlow < NO_FLOW: 
			bValveFault = TRUE
        else: 
			pass  ## do_nothing
        
        if mPICVCurrPos < 1 and PICVCurrFlow > LEAK_FLOW: 
			bValveFault = TRUE
        else: 
			pass  ## do_nothing
    else: 
		pass  ## do_nothing
        
    engine.WRITEPOINT("VP_FWU_PICV-1_Alarm", bValveFault)
else: 
    mbAllClosed = FALSE
    mbMonitorReady = FALSE
    mbAnyCommFault = TRUE
    engine.WRITEPOINT("VP_FWU_PICV-1_Comm_Fault", TRUE)
    engine.WRITEPOINT("VP_FWU_PICV-1_Alarm", TRUE)
    engine.SECTIMER(PICV_1_DEVIATION_TIMER, TMR_CLEAR)    
    
if engine.READPOINT("VP_FWU_PICV-1_Alarm") == TRUE: 
	mbAnyFault = TRUE
else: 
	pass  ## do_nothing

## PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)
mbPICVValid = FALSE ## 초기화
if mbPICVInputEnable:
    if engine.READPOINT_ALARM("FWU_PICV-2.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-2.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-2.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-2_Position", engine.READPOINT("FWU_PICV-2.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-2_Flow", engine.READPOINT("FWU_PICV-2.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-2_Temperature", engine.READPOINT("FWU_PICV-2.Temperature"))
        mbPICVValid = TRUE
    else: 
		pass ## do_nothing

mPICVCurrPos = engine.READPOINT("VP_FWU_PICV-2_Position")
if (0 <= mPICVCurrPos <= 100):
	pass ## do_nothing
else:
	mbPICVValid = FALSE
engine.WRITEPOINT("VP_FWU_PICV-2_Feedback_Valid", mbPICVValid)	

## PICV2(2/2): 개도 및 유량 범위 확인
if mbPICVValid:
    engine.WRITEPOINT("VP_FWU_PICV-2_Comm_Fault", FALSE)

    if mPICVCurrPos >= 5: 
    	mbAllClosed = FALSE
    else:
    	pass  ## do_nothing

    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    bValveFault = FALSE    
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1: ## 좌변이 boolean인가? (?)
        if (mPICVCurrPos - POS_HYST < engine.READPOINT("FWU_PICV_CONTROL") < mPICVCurrPos + POS_HYST):
            engine.SECTIMER(PICV_2_DEVIATION_TIMER, TMR_CLEAR)
        else:
            if engine.SECTIMER(PICV_2_DEVIATION_TIMER, TMR_READ) > DEV_TIME_OUT:
                bValveFault = TRUE
            else:
                pass  ## do_nothing
    else:
        engine.SECTIMER(PICV_2_DEVIATION_TIMER, TMR_CLEAR)

    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if mbPICVFlowChkEnable:
        PICVCurrFlow = engine.READPOINT("VP_FWU_PICV-2_Flow")
        if mbCHWSCondi and mPICVCurrPos > POS_OPEN and PICVCurrFlow < NO_FLOW: 
            bValveFault = TRUE
        else:
            pass  ## do_nothing	
		
        if mPICVCurrPos < 1 and PICVCurrFlow > LEAK_FLOW:
            bValveFault = TRUE
        else:
            pass  ## do_nothing
    else:
            pass  ## do_nothing
            
    engine.WRITEPOINT("VP_FWU_PICV-2_Alarm", bValveFault)
else:
    mbAllClosed = FALSE
    mbMonitorReady = FALSE
    mbAnyCommFault = TRUE
    engine.WRITEPOINT("VP_FWU_PICV-2_Comm_Fault", TRUE)
    engine.WRITEPOINT("VP_FWU_PICV-2_Alarm", TRUE)
    engine.SECTIMER(PICV_2_DEVIATION_TIMER, TMR_CLEAR)

if engine.READPOINT("VP_FWU_PICV-2_Alarm") == TRUE:
	mbAnyFault = TRUE
else: 
	pass  ## do_nothing
    
## PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)
mbPICVValid = FALSE ## 초기화
if mbPICVInputEnable:
    if engine.READPOINT_ALARM("FWU_PICV-3.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-3.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-3.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-3_Position", engine.READPOINT("FWU_PICV-3.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-3_Flow", engine.READPOINT("FWU_PICV-3.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-3_Temperature", engine.READPOINT("FWU_PICV-3.Temperature"))
        mbPICVValid = TRUE
	else: 
		pass ## do_nothing
		
mPICVCurrPos = engine.READPOINT("VP_FWU_PICV-3_Position")
if (0 <= mPICVCurrPos <= 100):
	pass ## do_nothing
else: 
	mbPICVValid = FALSE	
engine.WRITEPOINT("VP_FWU_PICV-3_Feedback_Valid", mbPICVValid)

## PICV3(2/2): 개도 및 유량 범위 확인
if mbPICVValid:
    engine.WRITEPOINT("VP_FWU_PICV-3_Comm_Fault", FALSE)

    if mPICVCurrPos >= 5:
		mbAllClosed = FALSE
    else: 
		pass  ## do_nothing

   # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    bValveFault = FALSE
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1: ## 좌변이 boolean인가? (?)
        if (mPICVCurrPos - POS_HYST < engine.READPOINT("FWU_PICV_CONTROL") < mPICVCurrPos + POS_HYST):
            engine.SECTIMER(PICV_3_DEVIATION_TIMER, TMR_CLEAR)
		else:
            if engine.SECTIMER(PICV_3_DEVIATION_TIMER, TMR_READ) > DEV_TIME_OUT:
                bValveFault = TRUE
            else: 
				pass  ## do_nothing         
    else:
        engine.SECTIMER(PICV_3_DEVIATION_TIMER, TMR_CLEAR)
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if mbPICVFlowChkEnable:
		PICVCurrFlow = engine.READPOINT("VP_FWU_PICV-3_Flow")
        if mbCHWSCondi and mPICVCurrPos > POS_OPEN and PICVCurrFlow < NO_FLOW: 
			bValveFault = TRUE
        else: 
			pass  ## do_nothing	
				
        if mPICVCurrPos < 1 and PICVCurrFlow > LEAK_FLOW:
			bValveFault = TRUE
        else: 
			pass  ## do_nothing
    else: 
		pass  ## do_nothing
    engine.WRITEPOINT("VP_FWU_PICV-3_Alarm", bValveFault)
else:
    mbAllClosed = FALSE
    mbMonitorReady = FALSE
    mbAnyCommFault = TRUE
    engine.WRITEPOINT("VP_FWU_PICV-3_Comm_Fault", TRUE)
    engine.WRITEPOINT("VP_FWU_PICV-3_Alarm", TRUE)
    engine.SECTIMER(PICV_3_DEVIATION_TIMER, TMR_CLEAR)

if engine.READPOINT("VP_FWU_PICV-3_Alarm") == TRUE:
	mbAnyFault = TRUE
else: 
	pass  ## do_nothing

## PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)
mbPICVValid = FALSE ## 초기화
if mbPICVInputEnable:
    if engine.READPOINT_ALARM("FWU_PICV-4.Position") == 0 and engine.READPOINT_ALARM("FWU_PICV-4.Flow") == 0 and engine.READPOINT_ALARM("FWU_PICV-4.Temperature") == 0:
        engine.WRITEPOINT("VP_FWU_PICV-4_Position", engine.READPOINT("FWU_PICV-4.Position"))
        engine.WRITEPOINT("VP_FWU_PICV-4_Flow", engine.READPOINT("FWU_PICV-4.Flow"))
        engine.WRITEPOINT("VP_FWU_PICV-4_Temperature", engine.READPOINT("FWU_PICV-4.Temperature"))
        mbPICVValid = TRUE
    else: 
		pass ## do_nothing
		
mPICVCurrPos = engine.READPOINT("VP_FWU_PICV-4_Position")
if (0 <= mPICVCurrPos <= 100):
	pass ## do_nothing
else: 
	mbPICVValid = FALSE	
engine.WRITEPOINT("VP_FWU_PICV-4_Feedback_Valid", mbPICVValid)

## PICV4(2/2): 개도 및 유량 범위 확인
if mbPICVValid:
    engine.WRITEPOINT("VP_FWU_PICV-4_Comm_Fault", FALSE)

    if mPICVCurrPos >= 5:
		mbAllClosed = FALSE
    else: 
		pass  ## do_nothing

    # 위치 제어 모드에서만 명령과 실제 개도를 비교한다.
    bValveFault = FALSE
    if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 1: ## 좌변이 boolean인가? (?)
        if (mPICVCurrPos - POS_HYST < engine.READPOINT("FWU_PICV_CONTROL") < mPICVCurrPos + POS_HYST):
            engine.SECTIMER(PICV_4_DEVIATION_TIMER, TMR_CLEAR)
		else:
            if engine.SECTIMER(PICV_4_DEVIATION_TIMER, TMR_READ) > DEV_TIME_OUT:
				bValveFault = TRUE
            else: 
				pass  ## do_nothing            
    else:
        engine.SECTIMER(PICV_4_DEVIATION_TIMER, TMR_CLEAR)
		
    # 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.
    if mbPICVFlowChkEnable:
		PICVCurrFlow = engine.READPOINT("VP_FWU_PICV-4_Flow")
        if mbCHWSCondi and mPICVCurrPos > POS_OPEN and PICVCurrFlow < NO_FLOW: 
			bValveFault = TRUE
        else: 
			pass  ## do_nothing			
		
        if mPICVCurrPos < 1 and PICVCurrFlow > LEAK_FLOW: 
            bValveFault = TRUE
        else: 
			pass  ## do_nothing
    else: 
		pass  ## do_nothing
		
    engine.WRITEPOINT("VP_FWU_PICV-4_Alarm", bValveFault)
else:
    mbAllClosed = FALSE
    mbMonitorReady = FALSE
    mbAnyCommFault = TRUE
    engine.WRITEPOINT("VP_FWU_PICV-4_Comm_Fault", TRUE)
    engine.WRITEPOINT("VP_FWU_PICV-4_Alarm", TRUE)
    engine.SECTIMER(PICV_4_DEVIATION_TIMER, TMR_CLEAR)

if engine.READPOINT("VP_FWU_PICV-4_Alarm") == TRUE:
	mbAnyFault = TRUE
else: 
	pass  ## do_nothing

## 모니터링 flag setting  
if engine.READPOINT("VP_FWU_PICV_Control_Mode") == 0 or mbPICVFlowChkEnable == FALSE: ## 좌변의 첫번째 term이 boolean인가? (?)
    mbMonitorReady = 0
else:
    pass  ## do_nothing
    
## PICV 상태, 유량 등의 정보를 VP_...에 업데이트
engine.WRITEPOINT("VP_FWU_PICV_All_Closed", mbAllClosed)
engine.WRITEPOINT("VP_FWU_PICV_Monitor_Ready", mbMonitorReady)
engine.WRITEPOINT("VP_FWU_PICV_Alarm", mbAnyFault)
engine.WRITEPOINT("VP_FWU_Flow_Comm_Fault", mbAnyCommFault)
# LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: E ----
