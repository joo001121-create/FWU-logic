"""Project-reference and Modbus request checks; no hardware communication."""
import csv
import unittest
import xml.etree.ElementTree as E
from test_control import ROOT

class ConfigurationTests(unittest.TestCase):
    def test_retired_adapter_points_absent(self):
        names=[n.get('name','') for n in E.parse(ROOT/'ControlPoint/VirtualPoint.xml').iter()]
        for name in names:
            if 'PICV' in name:
                for suffix in ('_Input_OK','_Sample_Seq','_Sample_Prev','_Input_Timeout'):
                    self.assertNotIn(suffix,name)

    def test_port_assignments(self):
        expected={1:[f'FWU SF-{i}' for i in range(1,9)],2:['FWU-ATS'],3:[f'FWU_PICV-{i}' for i in range(1,5)]}
        for port, units in expected.items():
            root=E.parse(ROOT/f'ControlPoint/Modbus{port}.xml').getroot()
            self.assertEqual(root.get('portNumber'),str(port))
            self.assertEqual([n.get('name') for n in root],units)
            stations=[n.get('address') for n in root]
            self.assertEqual(len(stations),len(set(stations)))
            for p in root.iter('modbusPoint'):
                self.assertTrue(p.get('address').startswith(f'R{port}'))

    def test_picv_definitions_and_queries_match_profile(self):
        root=E.parse(ROOT/'ControlPoint/Modbus3.xml').getroot()
        for i,u in enumerate(root,1):
            pts=u.findall('modbusPoint');qs=u.findall('query')
            self.assertEqual(len(pts),3);self.assertEqual(len(qs),3)
            for p,q,(name,reg,fmt,a) in zip(pts,qs,[('Position',4,'UINT16',.01),('Flow',7,'UINT16',.6),('Temperature',21,'INT16',.01)]):
                self.assertEqual(p.get('name'),f'FWU_PICV-{i}.{name}')
                self.assertEqual(p.get('registerNumber'),str(reg))
                self.assertEqual(p.get('dataFormat'),fmt)
                self.assertEqual(float(p.get('scaleFactorA')),a)
                self.assertEqual(p.get('attribute'),'R')
                self.assertEqual(p.get('dataSize'),'16')
                self.assertEqual(q.get('startRegisterNumber'),str(reg))
                self.assertEqual(q.get('endRegisterNumber'),str(reg))
                frame=bytes.fromhex(q.get('queryText'))
                self.assertEqual(frame[:6],bytes([i,3,0,reg,0,1]))

    def test_every_modbus_query_crc_and_station(self):
        for port in (1,2,3):
            for u in E.parse(ROOT/f'ControlPoint/Modbus{port}.xml').getroot():
                for q in u.findall('query'):
                    data=bytes.fromhex(q.get('queryText'))
                    self.assertEqual(data[0],int(u.get('address'),16))
                    crc=65535
                    for byte in data:
                        crc^=byte
                        for _ in range(8):crc=(crc>>1)^0xA001 if crc&1 else crc>>1
                    self.assertEqual(crc,0)

    def test_no_new_unresolved_service_references_and_old_meter_removed(self):
        ids={n.get('id') for p in (ROOT/'ControlPoint').glob('*.xml') for n in E.parse(p).iter() if n.get('id')}
        ids|={n.get('id') for n in E.parse(ROOT/'DDC.xml').iter('logicInfo')}
        expected={(r['file'],r['map_type'],r['point_id'],r['modbus_address'],r['byte_count'])
                  for r in csv.DictReader((ROOT/'INHERITED_EXPORT_REFERENCES.csv').open(encoding='utf-8-sig'))}
        actual=set()
        for p in (ROOT/'ProtocolSerivce').rglob('*.xml'):
            for a in E.parse(p).iter('modbusAddressMap'):
                for n in a:
                    if n.get('pointId') and n.get('pointId') not in ids:
                        actual.add((str(p.relative_to(ROOT)),a.get('addressMapType'),n.get('pointId'),n.get('modbusAddress'),n.get('byteCount')))
        self.assertEqual(actual,expected)
        retired={r['id'] for r in csv.DictReader((ROOT/'RETIRED_POINTS.csv').open(encoding='utf-8-sig'))}
        self.assertTrue(ids.isdisjoint(retired))

    def test_ch3_serial_profile_and_existing_enable_default(self):
        p=next(n for n in E.parse(ROOT/'DDC.xml').iter('portInfo') if n.get('portNumber')=='3')
        self.assertEqual((p.get('baudRate'),p.get('dataBit'),p.get('parity'),p.get('stopBit')),('Rate38400','Bit8','None','Bit2'))
        n=next(n for n in E.parse(ROOT/'ControlPoint/VirtualPoint.xml').iter() if n.get('name')=='VP_FWU_PICV_Input_Enable')
        self.assertEqual(n.get('relinguishDefault'),'0')

if __name__=='__main__':unittest.main()
