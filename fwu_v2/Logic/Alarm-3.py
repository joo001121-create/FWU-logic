# LJH[2026.1117]기존 단일 유량계 감시 분리: S ----
SF_1_COMM_TIMER = 0
SF_2_COMM_TIMER = 1
SF_3_COMM_TIMER = 2
SF_4_COMM_TIMER = 3
SF_5_COMM_TIMER = 4
SF_6_COMM_TIMER = 5
SF_7_COMM_TIMER = 6
SF_8_COMM_TIMER = 7
ATS_COMM_TIMER = 8
engine = ddc_logic()

if engine.READPOINT_ALARM("FWU SF-1.Current RPM") == 8 :
    if engine.SECTIMER(SF_1_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-1 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-1 Comm Fault", 0)
    engine.SECTIMER(SF_1_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-2.Current RPM") == 8 :
    if engine.SECTIMER(SF_2_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-2 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-2 Comm Fault", 0)
    engine.SECTIMER(SF_2_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-3.Current RPM") == 8 :
    if engine.SECTIMER(SF_3_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-3 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-3 Comm Fault", 0)
    engine.SECTIMER(SF_3_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-4.Current RPM") == 8 :
    if engine.SECTIMER(SF_4_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-4 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-4 Comm Fault", 0)
    engine.SECTIMER(SF_4_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-5.Current RPM") == 8 :
    if engine.SECTIMER(SF_5_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-5 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-5 Comm Fault", 0)
    engine.SECTIMER(SF_5_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-6.Current RPM") == 8 :
    if engine.SECTIMER(SF_6_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-6 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-6 Comm Fault", 0)
    engine.SECTIMER(SF_6_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-7.Current RPM") == 8 :
    if engine.SECTIMER(SF_7_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-7 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-7 Comm Fault", 0)
    engine.SECTIMER(SF_7_COMM_TIMER, 0)

if engine.READPOINT_ALARM("FWU SF-8.Current RPM") == 8 :
    if engine.SECTIMER(SF_8_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_SF-8 Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF-8 Comm Fault", 0)
    engine.SECTIMER(SF_8_COMM_TIMER, 0)

if engine.READPOINT("VP_FWU_SF-1 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-2 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-3 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-4 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-5 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-6 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-7 Comm Fault") == 1 or engine.READPOINT("VP_FWU_SF-8 Comm Fault") == 1 :
    engine.WRITEPOINT("VP_FWU_SF Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_SF Comm Fault", 0)

if engine.READPOINT_ALARM("FWU-ATS.Current Power") == 8 :
    if engine.SECTIMER(ATS_COMM_TIMER, 1) > 10 :
        engine.WRITEPOINT("VP_FWU_ATS Comm Fault", 1)
else :
    engine.WRITEPOINT("VP_FWU_ATS Comm Fault", 0)
    engine.SECTIMER(ATS_COMM_TIMER, 0)

# LJH[2026.1117]기존 단일 유량계 감시 분리: E ----
