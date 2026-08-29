import sys,os,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..'))
from app.engine import calc_chart,nak_info,dasha_timeline,varga_sign
class T(unittest.TestCase):
 def setUp(self): self.p={'name':'T','date':'1990-01-01','time':'12:00','lat':22.3039,'lon':70.8022,'tz':5.5,'ayanamsa':'Lahiri'}
 def test_chart(self):
  c=calc_chart(self.p); self.assertIn('Sun',c['planets']); self.assertEqual(len(c['houses']),12); self.assertTrue(0<=c['ascendant']['longitude']<360)
 def test_nak(self): self.assertEqual(nak_info(0)['name'],'Ashwini'); self.assertEqual(nak_info(0)['pada'],1)
 def test_dasha(self): c=calc_chart(self.p); d=dasha_timeline(c,self.p['date']); self.assertEqual(len(d),9)
 def test_varga(self): self.assertTrue(0<=varga_sign(123.4,9)<12)
if __name__=='__main__': unittest.main()
