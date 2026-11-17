# LJH[2026.1117]F8 고정 집계와 기존 PICV 알람 분리: S ----
LIMIT_TIMER = 0
FAN_FAIL_TIMER = 1
SAT_FAIL_TIMER = 2
SAH_FAIL_TIMER = 3
RAT_FAIL_TIMER = 4
RAH_FAIL_TIMER = 5
SAF_FAIL_TIMER = 6
SAD_OPEN_TIMER = 7
SAD_CLOSE_TIMER = 8
FAN_COUNT = 8
# F4/F6는 개별 팬 판정과 입출력을 함께 변경. Count VP로 모델을 전환하지 않는다.
engine = ddc_logic()

if engine.READPOINT("VP_FWU_SF Status") == 1 and engine.SECTIMER(LIMIT_TIMER, 1) > 300 :
    if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT High Alarm SP") :
        engine.WRITEPOINT("VP_FWU_RAT High Alarm", 1)
    if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT High Alarm SP") - 0.5 :
        engine.WRITEPOINT("VP_FWU_RAT High Alarm", 0)

    if engine.READPOINT("FWU_RAT") < engine.READPOINT("VP_FWU_RAT Low Alarm SP") :
        engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 1)
    if engine.READPOINT("FWU_RAT") > engine.READPOINT("VP_FWU_RAT Low Alarm SP") + 0.5 :
        engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 0)

    if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH High Alarm SP") :
        engine.WRITEPOINT("VP_FWU_RAH High Alarm", 1)
    if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH High Alarm SP") - 5 :
        engine.WRITEPOINT("VP_FWU_RAH High Alarm", 0)

    if engine.READPOINT("FWU_RAH") < engine.READPOINT("VP_FWU_RAH Low Alarm SP") :
        engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 1)
    if engine.READPOINT("FWU_RAH") > engine.READPOINT("VP_FWU_RAH Low Alarm SP") + 5 :
        engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 0)

    if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT High Alarm SP") :
        engine.WRITEPOINT("VP_FWU_SAT High Alarm", 1)
    if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT High Alarm SP") - 0.5 :
        engine.WRITEPOINT("VP_FWU_SAT High Alarm", 0)

    if engine.READPOINT("FWU_SAT") < engine.READPOINT("VP_FWU_SAT Low Alarm SP") :
        engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 1)
    if engine.READPOINT("FWU_SAT") > engine.READPOINT("VP_FWU_SAT Low Alarm SP") + 0.5 :
        engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 0)

    if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH High Alarm SP") :
        engine.WRITEPOINT("VP_FWU_SAH High Alarm", 1)
    if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH High Alarm SP") - 5 :
        engine.WRITEPOINT("VP_FWU_SAH High Alarm", 0)

    if engine.READPOINT("FWU_SAH") < engine.READPOINT("VP_FWU_SAH Low Alarm SP") :
        engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 1)
    if engine.READPOINT("FWU_SAH") > engine.READPOINT("VP_FWU_SAH Low Alarm SP") + 5 :
        engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 0)

    if engine.READPOINT("VP_FWU_CZT PV Valid") == 1 :
        if engine.READPOINT("VP_FWU_CZT Max") > engine.READPOINT("VP_FWU_CZT High Alarm SP") :
            engine.WRITEPOINT("VP_FWU_CZT High Alarm", 1)
        if engine.READPOINT("VP_FWU_CZT Max") < engine.READPOINT("VP_FWU_CZT High Alarm SP") - 0.5 :
            engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
        if engine.READPOINT("VP_FWU_CZT Min") < engine.READPOINT("VP_FWU_CZT Low Alarm SP") :
            engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 1)
        if engine.READPOINT("VP_FWU_CZT Min") > engine.READPOINT("VP_FWU_CZT Low Alarm SP") + 0.5 :
            engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
        engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)

    if engine.READPOINT("VP_FWU_HZT PV Valid") == 1 :
        if engine.READPOINT("VP_FWU_HZT Max") > engine.READPOINT("VP_FWU_HZT High Alarm SP") :
            engine.WRITEPOINT("VP_FWU_HZT High Alarm", 1)
        if engine.READPOINT("VP_FWU_HZT Max") < engine.READPOINT("VP_FWU_HZT High Alarm SP") - 0.5 :
            engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
        if engine.READPOINT("VP_FWU_HZT Min") < engine.READPOINT("VP_FWU_HZT Low Alarm SP") :
            engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 1)
        if engine.READPOINT("VP_FWU_HZT Min") > engine.READPOINT("VP_FWU_HZT Low Alarm SP") + 0.5 :
            engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
        engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)

    if engine.READPOINT("VP_FWU_RDP PV Valid") == 1 :
        if engine.READPOINT("VP_FWU_RDP Max") > engine.READPOINT("VP_FWU_RDP High Alarm SP") :
            engine.WRITEPOINT("VP_FWU_RDP High Alarm", 1)
        if engine.READPOINT("VP_FWU_RDP Max") < engine.READPOINT("VP_FWU_RDP High Alarm SP") - 0.5 :
            engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
        if engine.READPOINT("VP_FWU_RDP Min") < engine.READPOINT("VP_FWU_RDP Low Alarm SP") :
            engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 1)
        if engine.READPOINT("VP_FWU_RDP Min") > engine.READPOINT("VP_FWU_RDP Low Alarm SP") + 0.5 :
            engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
        engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)

if engine.READPOINT("VP_FWU_SF Status") == 0 :
    engine.SECTIMER(LIMIT_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAT High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAT Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAH High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RAH Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAT High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAT Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAH High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SAH Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_CZT High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_CZT Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_HZT High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_HZT Low Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RDP High Alarm", 0)
    engine.WRITEPOINT("VP_FWU_RDP Low Alarm", 0)

if engine.READPOINT("VP_FWU_Command") == 1 and engine.READPOINT("VP_FWU_SF Speed Value") >= engine.READPOINT("VP_FWU_SF Speed Min") :
    if engine.SECTIMER(FAN_FAIL_TIMER, 1) > 60 :
        fail_rpm = engine.READPOINT("VP_FWU_SF Failure RPM Set")
        b_sf_dp_low = engine.READPOINT("FWU_SAFLOW DP") <= engine.READPOINT("VP_FWU_SF Run DP Set")

        if engine.READPOINT("VP_FWU_SF-1 Comm Fault") == 0 :
            b_sf_1_fail = engine.READPOINT("FWU SF-1.Current RPM") < fail_rpm
        else :
            b_sf_1_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-2 Comm Fault") == 0 :
            b_sf_2_fail = engine.READPOINT("FWU SF-2.Current RPM") < fail_rpm
        else :
            b_sf_2_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-3 Comm Fault") == 0 :
            b_sf_3_fail = engine.READPOINT("FWU SF-3.Current RPM") < fail_rpm
        else :
            b_sf_3_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-4 Comm Fault") == 0 :
            b_sf_4_fail = engine.READPOINT("FWU SF-4.Current RPM") < fail_rpm
        else :
            b_sf_4_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-5 Comm Fault") == 0 :
            b_sf_5_fail = engine.READPOINT("FWU SF-5.Current RPM") < fail_rpm
        else :
            b_sf_5_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-6 Comm Fault") == 0 :
            b_sf_6_fail = engine.READPOINT("FWU SF-6.Current RPM") < fail_rpm
        else :
            b_sf_6_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-7 Comm Fault") == 0 :
            b_sf_7_fail = engine.READPOINT("FWU SF-7.Current RPM") < fail_rpm
        else :
            b_sf_7_fail = b_sf_dp_low

        if engine.READPOINT("VP_FWU_SF-8 Comm Fault") == 0 :
            b_sf_8_fail = engine.READPOINT("FWU SF-8.Current RPM") < fail_rpm
        else :
            b_sf_8_fail = b_sf_dp_low

        sf_fail_count = 0
        if b_sf_1_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-1 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-1 Run Fail Alarm", 0)
        if b_sf_2_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-2 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-2 Run Fail Alarm", 0)
        if b_sf_3_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-3 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-3 Run Fail Alarm", 0)
        if b_sf_4_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-4 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-4 Run Fail Alarm", 0)
        if b_sf_5_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-5 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-5 Run Fail Alarm", 0)
        if b_sf_6_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-6 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-6 Run Fail Alarm", 0)
        if b_sf_7_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-7 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-7 Run Fail Alarm", 0)
        if b_sf_8_fail :
            sf_fail_count = sf_fail_count + 1
            engine.WRITEPOINT("VP_FWU_SF-8 Run Fail Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF-8 Run Fail Alarm", 0)

        if sf_fail_count * 2 >= FAN_COUNT :
            engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 0)
else :
    engine.SECTIMER(FAN_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SF Failure Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-1 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-2 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-3 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-4 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-5 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-6 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-7 Run Fail Alarm", 0)
    engine.WRITEPOINT("VP_FWU_SF-8 Run Fail Alarm", 0)

if engine.READPOINT("FWU_SAT") < 0 :
    if engine.SECTIMER(SAT_FAIL_TIMER, 1) > 20 :
        engine.WRITEPOINT("VP_FWU_SAT Failure Alarm", 1)
else :
    engine.SECTIMER(SAT_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAT Failure Alarm", 0)

if engine.READPOINT("FWU_SAH") < 5 :
    if engine.SECTIMER(SAH_FAIL_TIMER, 1) > 20 :
        engine.WRITEPOINT("VP_FWU_SAH Failure Alarm", 1)
else :
    engine.SECTIMER(SAH_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAH Failure Alarm", 0)

if engine.READPOINT("FWU_RAT") < 0 :
    if engine.SECTIMER(RAT_FAIL_TIMER, 1) > 20 :
        engine.WRITEPOINT("VP_FWU_RAT Failure Alarm", 1)
else :
    engine.SECTIMER(RAT_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAT Failure Alarm", 0)

if engine.READPOINT("FWU_RAH") < 5 :
    if engine.SECTIMER(RAH_FAIL_TIMER, 1) > 20 :
        engine.WRITEPOINT("VP_FWU_RAH Failure Alarm", 1)
else :
    engine.SECTIMER(RAH_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_RAH Failure Alarm", 0)

if engine.READPOINT("FWU_SAFLOW DP") < engine.READPOINT("VP_FWU_SAF Fail DP Set") and engine.MAX(engine.MAX(engine.READPOINT("FWU SF-1.Current RPM"), engine.READPOINT("FWU SF-2.Current RPM"), engine.READPOINT("FWU SF-3.Current RPM"), engine.READPOINT("FWU SF-4.Current RPM")), engine.MAX(engine.READPOINT("FWU SF-5.Current RPM"), engine.READPOINT("FWU SF-6.Current RPM"), engine.READPOINT("FWU SF-7.Current RPM"), engine.READPOINT("FWU SF-8.Current RPM"))) > engine.READPOINT("VP_FWU_SAF Fail RPM Set") :
    if engine.SECTIMER(SAF_FAIL_TIMER, 1) > 20 :
        engine.WRITEPOINT("VP_FWU_SAF Failure Alarm", 1)
else :
    engine.SECTIMER(SAF_FAIL_TIMER, 0)
    engine.WRITEPOINT("VP_FWU_SAF Failure Alarm", 0)

b_sad_all_close = engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 and engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1
b_sad_any_close = engine.READPOINT("FWU_SAD-1 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-2 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-3 CLOSE STATUS") == 1 or engine.READPOINT("FWU_SAD-4 CLOSE STATUS") == 1
if engine.READPOINT("VP_FWU_SF Status") == 1 :
    if b_sad_any_close and not b_sad_all_close :
        engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 1)
    else :
        engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD Partial Close Alarm", 0)

if b_sad_all_close and engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and (engine.READPOINT("VP_FWU_SF Status") == 1 or engine.READPOINT("VP_FWU_SAD Full Close Alarm") == 1) :
    engine.WRITEPOINT("VP_FWU_SAD Full Close Alarm", 1)
else :
    engine.WRITEPOINT("VP_FWU_SAD Full Close Alarm", 0)

if engine.READPOINT("FWU_SAD-1_4 COMMAND") == 1 and engine.READPOINT("VP_FWU_SF Status") == 0 :
    engine.SECTIMER(SAD_CLOSE_TIMER, 0)
    if engine.SECTIMER(SAD_OPEN_TIMER, 1) > 120 :
        if engine.READPOINT("FWU_SAD-1 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-2 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-3 OPEN STATUS") != 1 or engine.READPOINT("FWU_SAD-4 OPEN STATUS") != 1 :
            engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD Not Open Alarm", 0)
    engine.SECTIMER(SAD_OPEN_TIMER, 0)

if engine.READPOINT("FWU_SAD-1_4 COMMAND") == 0 :
    engine.SECTIMER(SAD_OPEN_TIMER, 0)
    if engine.SECTIMER(SAD_CLOSE_TIMER, 1) > 120 :
        if engine.READPOINT("FWU_SAD-1 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-2 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-3 CLOSE STATUS") != 1 or engine.READPOINT("FWU_SAD-4 CLOSE STATUS") != 1 :
            engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 1)
        else :
            engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
    else :
        engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
else :
    engine.WRITEPOINT("VP_FWU_SAD Not Close Alarm", 0)
    engine.SECTIMER(SAD_CLOSE_TIMER, 0)

# LJH[2026.1117]F8 고정 집계와 기존 PICV 알람 분리: E ----
