"""DDC API test double; does not validate actual firmware, PI dynamics or wiring."""
import ast
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Engine:
    def __init__(self):
        self.defaults={p.get('name'):float(p.get('relinguishDefault') or 0) for f in (ROOT/'ControlPoint').glob('*.xml') for p in ET.parse(f).iter() if p.get('name') and p.get('id')}
        # Existing unresolved DI; synthetic input only, not a fabricated physical address.
        self.defaults['FWU_LEAK_DETECT']=0
        self.point_alarms={};self.writes=[];self.values={};self.time=0;self.timers={};self.block='';self.loops=[];self.resets=[]
        # Synthetic unbound inputs. Alarm=8 is a TEST setup, not an assertion
        # about actual firmware behavior before its first Modbus response.
        for i in range(1, 5):
            for quantity in ('Position', 'Flow', 'Temperature'):
                point = f'FWU_PICV-{i}.{quantity}'
                assert point in self.defaults  # Required in delivered Modbus XML
                self.point_alarms[point] = 8
    def set(self,p,v,priority=16):
        if p not in self.defaults:raise KeyError(p)
        self.values.setdefault(p,{})[priority]=v
    def READPOINT(self,p):
        if p not in self.defaults:raise KeyError(p)
        v=self.values.get(p,{})
        return v[min(v)] if v else self.defaults[p]
    def WRITEPOINT(self,p,v):self.READPOINT(p);self.set(p,v,5)
    def WRITEPOINT_PRI(self,p,v,n):self.READPOINT(p);self.set(p,v,n);self.writes.append((p,v,n))
    def RELEASE_PRI(self,p,n):self.values.get(p,{}).pop(n,None)
    def READPOINT_ALARM(self,p):self.READPOINT(p);return self.point_alarms.get(p,0)
    def SECTIMER(self,i,opt):
        assert 0<=i<=9
        key=(self.block,i)
        if opt==0:self.timers[key]=self.time;return 0
        return self.time-self.timers.setdefault(key,self.time)
    def MAX(self,*a):assert len(a)<=5;return max(a)
    def MIN(self,*a):assert len(a)<=5;return min(a)
    def LOOP2(self,*a):
        assert len(a)==13
        self.loops.append((self.block,a));self.WRITEPOINT(a[2],a[8])
    def LOOP2_INIT(self,i):self.resets.append((self.block,i))
    def run(self,name):
        self.block=name
        exec(compile((ROOT/'Logic'/f'{name}.py').read_text(),name,'exec'),{'ddc_logic':lambda:self})
    def tick(self,n):self.time+=n
class ControlTests(unittest.TestCase):
    def setUp(self):self.e=Engine()
    def set(self,p,v):self.e.set(p,v)
    def get(self,p):return self.e.READPOINT(p)
    def running(self,mode=0):
        for p,v in [('VP_FWU_Operation_Mode',1),('VP_FWU_Command',1),('VP_FWU_SF_Status',1),('VP_FWU_SF_Control_Select',mode),('VP_FWU_Speed_SP',65),('VP_FWU_SF_Speed_Min',30),('VP_FWU_SF_Speed_Max',95)]:self.set(p,v)
        for i in range(1,5):self.set(f'FWU_SAD-{i}_OPEN_STATUS',1);self.set(f'FWU_SAD-{i}_CLOSE_STATUS',0)
    def test_all_blocks_no_new_missing_reads(self):
        for name in [x.get('name') for x in ET.parse(ROOT/'DDC.xml').findall('logicInfo')]:self.e.run(name)
    def test_upper_timeout_latch_reset_and_disable(self):
        self.set('VP_FWU_Upper_Comm_Enable',1);self.e.run('Initialization')
        self.e.tick(31);self.e.run('Initialization');self.assertEqual(self.get('VP_FWU_BMS_PLC_Comm_Fault'),1)
        self.set('VP_FWU_BMS_PLC_Heartbeat',1);self.e.run('Initialization');self.assertEqual(self.get('VP_FWU_BMS_PLC_Comm_Fault'),1)
        self.set('VP_FWU_BMS_PLC_Comm_Reset',1);self.e.run('Initialization');self.assertEqual(self.get('VP_FWU_BMS_PLC_Comm_Fault'),0)
        self.set('VP_FWU_Upper_Comm_Enable',0);self.e.tick(100);self.e.run('Initialization');self.assertEqual(self.get('VP_FWU_BMS_PLC_Comm_Fault'),0)
        self.assertEqual(self.get('VP_FWU_CZT_PV_Valid'),0)
    def test_sensor_counts_zero_one_ten_and_unused_outlier(self):
        self.set('VP_FWU_Upper_Comm_Enable',1)
        for kind in ['CZT','HZT','RDP','CZH']:
            for i in range(1,11):self.set(f'VP_FWU_{kind}-{i}',i*2)
            for count,avg in [(0,0),(1,2),(10,11)]:
                self.set(f'VP_FWU_{kind}_Count',count);self.e.run('Initialization')
                self.assertEqual(self.get(f'VP_FWU_{kind}_Avg'),avg)
    def test_independent_sensor_failure_and_recovery(self):
        self.set('VP_FWU_Upper_Comm_Enable',1)
        for kind in ['CZT','HZT','RDP']:
            self.set(f'VP_FWU_{kind}_Count',10)
            for i in range(1,11):self.set(f'VP_FWU_{kind}-{i}',-1)
            self.e.run('Zone '+kind+' Alarm')
        self.e.tick(21)
        for kind in ['CZT','HZT','RDP']:
            self.e.run('Zone '+kind+' Alarm')
            for i in range(1,11):self.assertEqual(self.get(f'VP_FWU_{kind}-{i}_Failure_Alarm'),1)
            self.set(f'VP_FWU_{kind}-10',20);self.e.run('Zone '+kind+' Alarm');self.assertEqual(self.get(f'VP_FWU_{kind}-10_Failure_Alarm'),0)
        self.e.run('Initialization');self.assertEqual(self.get('VP_FWU_CZT_Avg'),20)
        self.set('VP_FWU_CZT_Count',0);self.e.run('Zone CZT Alarm');self.assertEqual(self.get('VP_FWU_CZT-1_Failure_Alarm'),0)
    def test_internal_sensor_fallback_only_for_relevant_mode(self):
        for mode,fail,expect_pi in [(1,'RAT',False),(3,'RAT',False),(3,'SAT',False),(1,'SAT',True)]:
            self.e=Engine();self.running(mode);self.set('VP_FWU_'+fail+'_Failure_Alarm',1);self.e.run('SF Control')
            self.assertEqual(bool(self.e.loops),expect_pi)
            if not expect_pi:self.assertEqual(self.get('VP_FWU_SF_Speed_Value'),65)
    def test_upper_fail_hold_max_and_local_exclusion(self):
        for mode,remote,policy,expected in [(2,0,0,65),(4,0,1,95),(0,1,1,95),(0,0,1,65)]:
            self.e=Engine();self.running(mode);self.set('REMOTE_SELECTION',remote);self.set('VP_FWU_Upper_Comm_Enable',1)
            self.set('VP_FWU_BMS_PLC_Comm_Fault',1);self.set('VP_FWU_BMS_Comm_Fail_Mode',policy);self.set('VP_FWU_SF_Speed_Value',65)
            self.e.run('SF Control');self.assertEqual(self.get('VP_FWU_SF_Speed_Value'),expected)
    def test_damper_delays_independent_and_clear(self):
        self.running();self.set('FWU_SAD-1_OPEN_STATUS',0);self.set('FWU_SAD-1_CLOSE_STATUS',0)
        self.set('FWU_SAD-2_CLOSE_STATUS',1);self.set('FWU_SAD-1_4_COMMAND',1)
        self.e.run('Damper Signal Alarm');self.e.tick(6);self.e.run('Damper Signal Alarm')
        self.assertEqual(self.get('VP_FWU_SAD-2_Signal_Conflict_Alarm'),1);self.assertEqual(self.get('VP_FWU_SAD-1_Position_Unknown_Alarm'),0)
        self.e.tick(115);self.e.run('Damper Signal Alarm');self.assertEqual(self.get('VP_FWU_SAD-1_Position_Unknown_Alarm'),1)
        self.set('FWU_SAD-1_OPEN_STATUS',1);self.e.run('Damper Signal Alarm');self.assertEqual(self.get('VP_FWU_SAD-1_Position_Unknown_Alarm'),0)
    def receive(self):
        self.set('VP_FWU_PICV_Input_Enable',1)
        for i in range(1,5):
            for quantity in ('Position','Flow','Temperature'):
                point=f'FWU_PICV-{i}.{quantity}'
                self.set(point,0)
                self.e.point_alarms[point]=0
        self.e.run('PICV Feedback')
    def test_disabled_and_driver_fault_are_not_closed(self):
        self.e.run('PICV Feedback');self.assertEqual(self.get('VP_FWU_PICV_All_Closed'),0)
        self.receive();self.assertEqual(self.get('VP_FWU_PICV_All_Closed'),1)
        self.e.point_alarms['FWU_PICV-1.Position']=8
        self.e.run('PICV Feedback');self.assertEqual(self.get('VP_FWU_PICV_All_Closed'),0)
        self.receive();self.assertEqual(self.get('VP_FWU_PICV_All_Closed'),1)
    def test_stop_needs_all_four_valid_and_below_five(self):
        self.running();self.set('VP_FWU_Command',0);self.set('VP_FWU_SF_Speed_Value',65)
        self.receive();self.set('FWU_PICV-4.Position',5);self.e.run('PICV Feedback');self.e.run('SF Control');self.assertEqual(self.get('VP_FWU_SF_Speed_Value'),65)
        self.set('FWU_PICV-4.Position',4);self.e.run('PICV Feedback');self.e.run('SF Control');self.assertEqual(self.get('VP_FWU_SF_Speed_Value'),0)
    def test_position_comparison_not_used_in_flow_mode(self):
        self.receive();self.set('VP_FWU_PICV_Control_Mode',2);self.set('FWU_PICV_CONTROL',100)
        self.e.run('PICV Feedback');self.e.tick(41);self.receive()
        self.assertEqual(self.get('VP_FWU_PICV-1_Alarm'),0)
        self.set('VP_FWU_PICV_Control_Mode',1);self.e.run('PICV Feedback');self.e.tick(41);self.receive()
        self.assertEqual(self.get('VP_FWU_PICV-1_Alarm'),1)
    def test_picv_sat_failure_manual_and_emergency_priorities(self):
        self.running();self.set('VP_FWU_SAT_Failure_Alarm',1);self.e.run('PICV Control');self.assertEqual(self.get('FWU_PICV_CONTROL'),100)
        self.set('FWU_EMERGENCY',1);self.e.run('PICV Control');self.assertEqual(self.get('FWU_PICV_CONTROL'),0)
        self.set('FWU_EMERGENCY',0);self.set('VP_FWU_Operation_Mode',0);self.e.run('PICV Control');self.assertEqual(self.get('FWU_PICV_CONTROL'),0)
    def test_remote_priority_wins_over_picv_and_fan(self):
        self.running();self.set('VP_FWU_Remote_Shutdown_Command',1)
        self.e.run('PICV Control');self.e.run('SF Control');self.e.run('Remote Shutdown')
        self.assertEqual(self.get('FWU_PICV_CONTROL'),0)
        for i in range(1,9):self.assertEqual(self.get(f'FWU_SF-{i}.Run_Command'),0)
    def test_f8_failure_threshold_ignores_count_vp(self):
        self.running();self.set('VP_FWU_SF_Speed_Value',65);self.set('VP_FWU_SF_Count',4)
        for i in range(1,9):self.set(f'FWU_SF-{i}.Current_RPM',1000 if i>3 else 0)
        self.e.run('Sensor Limit Alarm');self.e.run('Fan Damper Alarm');self.e.tick(61);self.e.run('Sensor Limit Alarm');self.e.run('Fan Damper Alarm');self.assertEqual(self.get('VP_FWU_SF_Failure_Alarm'),0)
        self.set('FWU_SF-4.Current_RPM',0);self.e.run('Sensor Limit Alarm');self.e.run('Fan Damper Alarm');self.assertEqual(self.get('VP_FWU_SF_Failure_Alarm'),1)
if __name__=='__main__':unittest.main()
