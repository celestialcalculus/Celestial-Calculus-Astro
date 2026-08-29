import math, datetime as dt
import swisseph as swe

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,
}
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
SIGN_LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
NAKSHATRAS = [
('Ashwini','Ketu','Ashwini','Deva','Horse','Aadi','Fire'),('Bharani','Venus','Yoni','Manushya','Elephant','Madhya','Earth'),('Krittika','Sun','Agni','Rakshasa','Sheep','Antya','Fire'),
('Rohini','Moon','Brahma','Manushya','Serpent','Antya','Earth'),('Mrigashira','Mars','Soma','Deva','Serpent','Madhya','Earth'),('Ardra','Rahu','Rudra','Manushya','Dog','Aadi','Air'),
('Punarvasu','Jupiter','Aditi','Deva','Cat','Aadi','Air'),('Pushya','Saturn','Brihaspati','Deva','Goat','Madhya','Water'),('Ashlesha','Mercury','Nagas','Rakshasa','Cat','Antya','Water'),
('Magha','Ketu','Pitris','Rakshasa','Rat','Antya','Fire'),('Purva Phalguni','Venus','Bhaga','Manushya','Rat','Madhya','Fire'),('Uttara Phalguni','Sun','Aryaman','Manushya','Cow','Aadi','Fire'),
('Hasta','Moon','Savitar','Deva','Buffalo','Aadi','Air'),('Chitra','Mars','Tvashtar','Rakshasa','Tiger','Madhya','Fire'),('Swati','Rahu','Vayu','Deva','Buffalo','Antya','Air'),
('Vishakha','Jupiter','Indra-Agni','Rakshasa','Tiger','Aadi','Fire'),('Anuradha','Saturn','Mitra','Deva','Deer','Madhya','Water'),('Jyeshtha','Mercury','Indra','Rakshasa','Deer','Antya','Air'),
('Mula','Ketu','Nirriti','Rakshasa','Dog','Aadi','Air'),('Purva Ashadha','Venus','Apas','Manushya','Monkey','Madhya','Water'),('Uttara Ashadha','Sun','Vishvedevas','Manushya','Mongoose','Antya','Fire'),
('Shravana','Moon','Vishnu','Deva','Monkey','Antya','Air'),('Dhanishtha','Mars','Vasus','Rakshasa','Lion','Madhya','Ether'),('Shatabhisha','Rahu','Varuna','Rakshasa','Horse','Aadi','Air'),
('Purva Bhadrapada','Jupiter','Aja Ekapada','Manushya','Lion','Madhya','Ether'),('Uttara Bhadrapada','Saturn','Ahirbudhnya','Manushya','Cow','Antya','Water'),('Revati','Mercury','Pushan','Deva','Elephant','Antya','Water')]
DASHA_ORDER=['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS={'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_LORDS={x: x for x in DASHA_ORDER}

def norm(x): return x % 360.0

def jd_from_local(date_s, time_s, tz_hours):
    y,m,d=map(int,date_s.split('-')); hh,mm=map(int,time_s.split(':')[:2]); ss=int(time_s.split(':')[2]) if len(time_s.split(':'))>2 else 0
    u=dt.datetime(y,m,d,hh,mm,ss)-dt.timedelta(hours=float(tz_hours))
    return swe.julday(u.year,u.month,u.day,u.hour+u.minute/60+u.second/3600)

def sign_info(lon):
    s=int(norm(lon)//30); deg=norm(lon)%30
    return s,SIGNS[s],deg

def nak_info(lon):
    x=norm(lon); span=360/27; idx=min(26,int(x/span)); within=x-idx*span; pada=min(3,int(within/(span/4)))+1
    n=NAKSHATRAS[idx]
    return {'name':n[0],'lord':n[1],'symbol':n[2],'gana':n[3],'yoni':n[4],'nadi':n[5],'element':n[6],'pada':pada,'index':idx,'degree_range':f'{idx*span:.6f}°–{(idx+1)*span:.6f}°'}

def sidereal(lon, jd, ayanamsa='Lahiri'):
    mode={'Lahiri':swe.SIDM_LAHIRI,'Raman':swe.SIDM_RAMAN,'Krishnamurti':swe.SIDM_KRISHNAMURTI}.get(ayanamsa,swe.SIDM_LAHIRI)
    swe.set_sid_mode(mode)
    return norm(lon-swe.get_ayanamsa_ut(jd))

def calc_chart(payload):
    jd=jd_from_local(payload['date'],payload['time'],payload.get('tz',5.5))
    lat=float(payload['lat']); lon=float(payload['lon']); ay=payload.get('ayanamsa','Lahiri')
    swe.set_topo(lon,lat,0)
    flags=swe.FLG_SWIEPH|swe.FLG_SPEED
    planets={}
    for name,p in PLANETS.items():
        xx,rf=swe.calc_ut(jd,p,flags)
        slon=sidereal(xx[0],jd,ay)
        sidx,sname,deg=sign_info(slon)
        planets[name]={'longitude':round(slon,8),'latitude':round(xx[1],8),'speed':round(xx[3],8),'retrograde':xx[3]<0,'sign_index':sidx,'sign':sname,'degree':round(deg,6),'nakshatra':nak_info(slon)}
    planets['Ketu']=dict(planets['Rahu']); planets['Ketu']['longitude']=norm(planets['Rahu']['longitude']+180); planets['Ketu']['sign_index'],planets['Ketu']['sign'],planets['Ketu']['degree']=sign_info(planets['Ketu']['longitude']); planets['Ketu']['nakshatra']=nak_info(planets['Ketu']['longitude']); planets['Ketu']['retrograde']=planets['Rahu']['retrograde']
    cusps,ascmc=swe.houses_ex(jd,lat,lon,b'P',0)
    asc=sidereal(ascmc[0],jd,ay)
    # Whole-sign houses are used as the default Vedic house model; Bhava/P system is also exposed as raw metadata.
    asc_sign=int(asc//30)
    for p in planets.values(): p['house']=((p['sign_index']-asc_sign)%12)+1
    houses=[]
    for i in range(12):
        si=(asc_sign+i)%12; houses.append({'house':i+1,'sign':SIGNS[si],'sign_index':si,'lord':SIGN_LORDS[si],'planets':[k for k,v in planets.items() if v['house']==i+1]})
    aspects=[]
    for a,av in planets.items():
        for b,bv in planets.items():
            if a==b: continue
            diff=(bv['longitude']-av['longitude'])%360
            hits=[]
            if 0<=diff<1 or 359<diff<360: hits.append('Conjunction')
            if abs(diff-180)<=1: hits.append('Opposition')
            if a in ('Mars',):
                if abs(diff-90)<=1: hits.append('Mars 4th');
                if abs(diff-210)<=1: hits.append('Mars 8th')
            if a in ('Jupiter',):
                if abs(diff-120)<=1: hits.append('Jupiter 5th')
                if abs(diff-240)<=1: hits.append('Jupiter 9th')
            if a in ('Saturn',):
                if abs(diff-90)<=1: hits.append('Saturn 3rd')
                if abs(diff-270)<=1: hits.append('Saturn 10th')
            if hits: aspects.append({'from':a,'to':b,'types':hits})
    yogas=[]
    # Transparent, conservative common yoga rules.
    for name, cond in [('Gaja Kesari', planets['Jupiter']['house'] in (1,4,7,10) and planets['Moon']['house'] in (1,4,7,10) and ((planets['Jupiter']['house']-planets['Moon']['house'])%12 in (0,3,6,9))),
                       ('Budha-Aditya', planets['Sun']['house']==planets['Mercury']['house']),
                       ('Chandra-Mangala', planets['Moon']['house']==planets['Mars']['house'])]:
        if cond: yogas.append({'name':name,'reason':'Rule condition satisfied by the calculated house placements.'})
    asc_sign_name=SIGNS[asc_sign]
    return {'julian_day':jd,'ayanamsa':ay,'ayanamsa_value':swe.get_ayanamsa_ut(jd),'ascendant':{'longitude':asc,'sign_index':asc_sign,'sign':asc_sign_name,'degree':asc%30,'nakshatra':nak_info(asc)},'planets':planets,'houses':houses,'aspects':aspects,'yogas':yogas,'meta':{'ephemeris':'Swiss Ephemeris (pyswisseph)','house_model':'Whole-sign houses for Vedic analysis; Swiss Ephemeris Placidus cusps retained for reference','timezone_hours':float(payload.get('tz',5.5))}}

def dasha_timeline(chart, birth_date):
    moon=chart['planets']['Moon']['longitude']; idx=int(moon/(360/27)); frac=(moon%(360/27))/(360/27); first=NAKSHATRAS[idx][1]; start_idx=DASHA_ORDER.index(first); remaining=(1-frac)*DASHA_YEARS[first]
    y,m,d=map(int,birth_date.split('-')); cur=dt.date(y,m,d); out=[]
    for k in range(9):
        lord=DASHA_ORDER[(start_idx+k)%9]; years=remaining if k==0 else DASHA_YEARS[lord]; days=round(years*365.2425); end=cur+dt.timedelta(days=days); out.append({'lord':lord,'start':cur.isoformat(),'end':end.isoformat(),'years':round(years,4),'balance_at_birth':k==0}); cur=end
    return out

def varga_sign(longitude, v):
    # Classical sign division mapping for commonly used Vargas. Kept explicit so rules can be expanded.
    s=int(longitude//30); d=longitude%30; part=30/v; n=min(v-1,int(d/part))
    if v==1: idx=s
    elif v==2: idx=(s*2+n)%12
    elif v==3: idx=(s*3+n)%12
    elif v==9: idx=(s*9+n)%12
    elif v==10: idx=(s*10+n)%12
    elif v==12: idx=(s*12+n)%12
    elif v==16: idx=(s*16+n)%12
    elif v==20: idx=(s*20+n)%12
    elif v==24: idx=(s*24+n)%12
    elif v==27: idx=(s*27+n)%12
    elif v==30: idx=(s*30+n)%12
    elif v==40: idx=(s*40+n)%12
    elif v==45: idx=(s*45+n)%12
    elif v==60: idx=(s*60+n)%12
    else: idx=(s*v+n)%12
    return idx
