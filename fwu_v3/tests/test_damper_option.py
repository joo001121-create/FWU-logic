"""댐퍼 설치 여부(VP_FWU_SAD_Installed) 옵션 동작 (JSY 2026-11-24). 0 = 댐퍼 없음(기본), 1 = 댐퍼 있음(기존 동작)."""
import unittest
import xml.etree.ElementTree as ET
from test_control import Engine, ROOT

ORDER = [x.get('name') for x in ET.parse(ROOT / 'DDC.xml').findall('logicInfo') if (ROOT / 'Logic' / f"{x.get('name')}.py").exists()]
DAMPER_ALARMS = ('VP_FWU_SAD_Partial_Close_Alarm', 'VP_FWU_SAD_Full_Close_Alarm', 'VP_FWU_SAD_Not_Open_Alarm', 'VP_FWU_SAD_Not_Close_Alarm')


class DamperOptionTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def contacts(self, opened, closed):
        for i in range(1, 5):
            self.e.set(f'FWU_SAD-{i}_OPEN_STATUS', opened)
            self.e.set(f'FWU_SAD-{i}_CLOSE_STATUS', closed)

    def test_default_is_not_installed(self):
        self.assertEqual(self.e.READPOINT('VP_FWU_SAD_Installed'), 0)

    def test_not_installed_fans_start_without_damper_contacts(self):
        # 댐퍼 접점이 하나도 안 들어와도(배선 없음) 바로 팬 속도를 정하고, 댐퍼 명령은 내지 않는다
        self.contacts(0, 0)
        self.e.run('SF Control')
        self.assertEqual(self.e.READPOINT('VP_FWU_SF_Speed_Value'), 50)   # 고정속도 기본 Speed_SP 50
        self.assertEqual(self.e.READPOINT('FWU_SAD-1_4_COMMAND'), 0)
        self.assertEqual(self.e.READPOINT('FWU_SF-1.Run_Command'), 1)

    def test_installed_waits_until_all_dampers_open(self):
        # 기존 동작: 네 댐퍼가 닫혀 있으면 댐퍼만 열고 팬 속도는 0, 다 열리면 팬 속도를 정한다
        self.e.set('VP_FWU_SAD_Installed', 1)
        self.contacts(0, 1)
        self.e.run('SF Control')
        self.assertEqual(self.e.READPOINT('FWU_SAD-1_4_COMMAND'), 1)
        self.assertEqual(self.e.READPOINT('VP_FWU_SF_Speed_Value'), 0)
        self.contacts(1, 0)
        self.e.run('SF Control')
        self.assertEqual(self.e.READPOINT('VP_FWU_SF_Speed_Value'), 50)

    def run_damper_alarm_cases(self, installed):
        e = self.e
        e.set('VP_FWU_SAD_Installed', installed)
        result = {}
        # 일부 닫힘: 팬이 도는데 1번만 닫힘
        e.set('VP_FWU_SF_Status', 1); self.contacts(1, 0); e.set('FWU_SAD-1_CLOSE_STATUS', 1)
        e.run('Fan Damper Alarm'); result['VP_FWU_SAD_Partial_Close_Alarm'] = e.READPOINT('VP_FWU_SAD_Partial_Close_Alarm')
        # 전폐: 열림 명령인데 네 개 모두 닫힘, 팬 운전 중
        e.set('FWU_SAD-1_4_COMMAND', 1, 5); self.contacts(0, 1)
        e.run('Fan Damper Alarm'); result['VP_FWU_SAD_Full_Close_Alarm'] = e.READPOINT('VP_FWU_SAD_Full_Close_Alarm')
        # 미개방: 열림 명령, 팬 정지, 120초가 지나도 안 열림
        e.set('VP_FWU_SF_Status', 0); self.contacts(0, 0)
        e.run('Fan Damper Alarm'); e.tick(121); e.run('Fan Damper Alarm')
        result['VP_FWU_SAD_Not_Open_Alarm'] = e.READPOINT('VP_FWU_SAD_Not_Open_Alarm')
        # 미폐쇄: 닫힘 명령 뒤 120초가 지나도 안 닫힘
        e.set('FWU_SAD-1_4_COMMAND', 0, 5)
        e.run('Fan Damper Alarm'); e.tick(121); e.run('Fan Damper Alarm')
        result['VP_FWU_SAD_Not_Close_Alarm'] = e.READPOINT('VP_FWU_SAD_Not_Close_Alarm')
        return result

    def test_damper_alarms_only_when_installed(self):
        self.assertEqual(self.run_damper_alarm_cases(1), {p: 1 for p in DAMPER_ALARMS})
        self.setUp()
        self.assertEqual(self.run_damper_alarm_cases(0), {p: 0 for p in DAMPER_ALARMS})

    def test_not_installed_full_scan_no_damper_or_failover_alarm(self):
        # 댐퍼 없이 팬이 돌고 접점 배선이 없어도(0) 댐퍼 알람, 예제 Damper Signal Alarm 알람, Failover가 걸리지 않는다
        e = self.e
        self.contacts(0, 0)
        for i in range(1, 9):
            e.set(f'FWU_SF-{i}.Current_RPM', 800)
        for _ in range(200):
            e.tick(1)
            for block in ORDER:
                e.run(block)
        self.assertEqual(e.READPOINT('VP_FWU_SF_Status'), 1)
        self.assertEqual(e.READPOINT('FWU_SAD-1_4_COMMAND'), 0)
        for p in DAMPER_ALARMS:
            self.assertEqual(e.READPOINT(p), 0, p)
        for i in range(1, 5):
            self.assertEqual(e.READPOINT(f'VP_FWU_SAD-{i}_Position_Unknown_Alarm'), 0)
            self.assertEqual(e.READPOINT(f'VP_FWU_SAD-{i}_Signal_Conflict_Alarm'), 0)
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 0)


if __name__ == '__main__':
    unittest.main()
