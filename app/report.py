from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
import os, datetime

def make_pdf(chart, profile, outpath):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    styles=getSampleStyleSheet(); story=[]
    story += [Paragraph('Celestial Calculus',styles['Title']),Paragraph('Vedic Horoscope Research Report',styles['Heading2']),Spacer(1,8)]
    story += [Paragraph(f"<b>{profile.get('name','')}</b><br/>Birth: {profile.get('date','')} {profile.get('time','')}<br/>Place: {profile.get('place','')}<br/>Coordinates: {profile.get('lat','')}, {profile.get('lon','')} · TZ {profile.get('tz','')}",styles['BodyText']),Spacer(1,12)]
    a=chart['ascendant']; story += [Paragraph(f"<b>Lagna:</b> {a['sign']} {a['degree']:.4f}° · Nakshatra {a['nakshatra']['name']} Pada {a['nakshatra']['pada']}",styles['BodyText']),Spacer(1,10)]
    rows=[['Planet','Longitude','Sign','House','Nakshatra','Pada','Retro']]
    for k,v in chart['planets'].items(): rows.append([k,f"{v['longitude']:.5f}°",f"{v['sign']} {v['degree']:.2f}°",str(v['house']),v['nakshatra']['name'],str(v['nakshatra']['pada']),'Yes' if v['retrograde'] else 'No'])
    t=Table(rows,repeatRows=1,colWidths=[20*mm,25*mm,32*mm,15*mm,32*mm,15*mm,15*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7dfcf')),('GRID',(0,0),(-1,-1),0.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story += [Paragraph('Planetary Positions',styles['Heading2']),t,PageBreak()]
    story += [Paragraph('Nakshatra / Nadi',styles['Heading2'])]
    nrows=[['Point','Nakshatra','Lord','Pada','Nadi','Gana','Yoni']]+[[k,v['nakshatra']['name'],v['nakshatra']['lord'],v['nakshatra']['pada'],v['nakshatra']['nadi'],v['nakshatra']['gana'],v['nakshatra']['yoni']] for k,v in chart['planets'].items()]
    nt=Table(nrows,repeatRows=1); nt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7dfcf')),('GRID',(0,0),(-1,-1),0.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),8)])); story += [nt,Spacer(1,14)]
    story += [Paragraph('Yogas',styles['Heading2'])]
    if chart['yogas']:
        for y in chart['yogas']: story.append(Paragraph(f"<b>{y['name']}</b> — {y['reason']}",styles['BodyText']))
    else: story.append(Paragraph('No conservative yoga rules matched.',styles['BodyText']))
    story += [Spacer(1,12),Paragraph('Methodology',styles['Heading2']),Paragraph(f"Ephemeris: {chart['meta']['ephemeris']}<br/>Ayanamsa: {chart['ayanamsa']}<br/>House model: {chart['meta']['house_model']}<br/>Generated: {datetime.datetime.now().isoformat(timespec='seconds')}",styles['BodyText'])]
    SimpleDocTemplate(outpath,pagesize=A4,rightMargin=14*mm,leftMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm,title='Celestial Calculus Report').build(story)
    return outpath
