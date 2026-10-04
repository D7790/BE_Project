"""Generate an IEEE-style local draft PDF and editable Markdown from the same record."""
from pathlib import Path
import hashlib, html, json, re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, KeepTogether, Table, TableStyle, FrameBreak
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'paper'; OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((P/'src/manuscript.json').read_text(encoding='utf-8'))
fp=json.loads((P/'figures/figure-provenance.json').read_text(encoding='utf-8'))
figs={x['figure_id'].split('_',1)[1]:x for x in fp['figures']}
for name,f in [('TNR','times.ttf'),('TNR-B','timesbd.ttf'),('TNR-I','timesi.ttf'),('TNR-BI','timesbi.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/f)))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-B',italic='TNR-I',boldItalic='TNR-BI')
W,H=612,792; M=45; GAP=18; FULL=W-2*M; COL=(FULL-GAP)/2; BOTTOM=42; TOP=754
styles={
 'body':ParagraphStyle('body',fontName='TNR',fontSize=10,leading=11.8,alignment=TA_JUSTIFY,spaceAfter=4.6,allowWidows=0,allowOrphans=0),
 'h1':ParagraphStyle('h1',fontName='TNR',fontSize=10.4,leading=12.4,alignment=TA_CENTER,spaceBefore=10,spaceAfter=5,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='TNR-I',fontSize=10,leading=11.8,spaceBefore=6,spaceAfter=4,keepWithNext=True),
 'caption':ParagraphStyle('caption',fontName='TNR',fontSize=8.3,leading=9.6,spaceAfter=7),
 'table':ParagraphStyle('table',fontName='TNR',fontSize=8.1,leading=9.6),
 'ref':ParagraphStyle('ref',fontName='TNR',fontSize=8.8,leading=10.2,leftIndent=13,firstLineIndent=-13,spaceAfter=5),
 'eq':ParagraphStyle('eq',fontName='TNR-I',fontSize=9.5,leading=12,alignment=TA_CENTER,spaceBefore=4,spaceAfter=7),
 'title':ParagraphStyle('title',fontName='TNR',fontSize=21,leading=23.5,alignment=TA_CENTER),
 'author':ParagraphStyle('author',fontName='TNR',fontSize=11,leading=13,alignment=TA_CENTER),
 'status':ParagraphStyle('status',fontName='TNR-I',fontSize=8.3,leading=10,alignment=TA_CENTER)
}
def clean(s):
    s=s.replace('\u2013','-').replace('\u2014','-').replace('\u2011','-')
    for a,b in [('E_hat','E<sub>est</sub>'),('T_hat','T<sub>est</sub>'),('I_eff','I<sub>eff</sub>'),('V_nom','V<sub>nom</sub>'),('s_res','s<sub>res</sub>'),('P_U2','P<sub>U2</sub>'),('T_min','T<sub>min</sub>'),('I_src','I<sub>src</sub>'),('I_lim','I<sub>lim</sub>'),('V_reg','V<sub>reg</sub>'),('t_r','t<sub>r</sub>')]: s=s.replace(a,b)
    s=s.replace('sqrt(', '√(').replace('10^-8','10<super>-8</super>')
    s=s.replace('<sub>','<sub rise="2.1" size="7">').replace('<super>','<super rise="3" size="7">')
    return s
def para(s,style='body'): return Paragraph(clean(s),styles[style])
def drawing(key,width):
    path=ROOT/next(x for x in figs[key]['files'] if x.endswith('.svg'))
    d=svg2rlg(str(path)); factor=width/d.width; d.scale(factor,factor);d.width*=factor;d.height*=factor
    return d
def caption(key):
    i=next(i+1 for i,x in enumerate(fp['figures']) if x==figs[key])
    return para(f'Fig. {i}. '+html.escape(figs[key]['caption']),'caption')
big={key:drawing(key,FULL) for key in ['architecture','control_flow']}
reserved={1:117}
for page,key in [(2,'architecture'),(3,'control_flow')]:
    cap=caption(key);ch=cap.wrap(FULL,1000)[1]
    reserved[page]=big[key].height+ch+18
def header(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(colors.black)
    if doc.page==1:
        y=TOP
        for text,style,gap in [(m['title'],'title',10),(', '.join(m['authors']),'author',7),(m['status'],'status',0)]:
            p=para(html.escape(text),style);ht=p.wrap(FULL,200)[1];p.drawOn(canvas,M,y-ht);y-=ht+gap
    if doc.page in [2,3]:
        key={2:'architecture',3:'control_flow'}[doc.page];d=big[key]
        renderPDF.draw(d,canvas,M,TOP-d.height)
        cap=caption(key);ch=cap.wrap(FULL,1000)[1];cap.drawOn(canvas,M,TOP-d.height-5-ch)
    canvas.restoreState()
def page_furniture(canvas,doc):
    canvas.saveState()
    canvas.setFont('TNR-I',7.4);canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(M,774,'WATTSENSE | DESIGN AND SIMULATION STUDY | WORKING DRAFT')
    canvas.setFont('TNR',8);canvas.drawCentredString(W/2,25,str(doc.page))
    canvas.restoreState()
templates=[]
for n in [1,2,3,4]:
    top=TOP-reserved.get(n,0)
    frames=[Frame(M+i*(COL+GAP),BOTTOM,COL,top-BOTTOM,id=f'c{i}',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0) for i in [0,1]]
    templates.append(PageTemplate(id=f'p{n}',frames=frames,onPage=header,onPageEnd=page_furniture))
pdfpath=OUT/'wattsense_research_paper.pdf'
class PaperDoc(BaseDocTemplate):
    def handle_pageBegin(self):
        # Select frames before BaseDocTemplate places the first item on each page.
        self.pageTemplate=self.pageTemplates[min(self.page,3)]
        super().handle_pageBegin()
doc=PaperDoc(str(pdfpath),pagesize=(W,H),leftMargin=M,rightMargin=M,topMargin=38,bottomMargin=BOTTOM,title=m['title'],author=', '.join(m['authors']),pageCompression=1)
doc.addPageTemplates(templates)
story=[para('<b><i>Abstract - </i>'+html.escape(m['abstract'])+'</b>'),para('<b><i>Index Terms - </i></b><i>'+html.escape(m['keywords'])+'</i>'),Spacer(1,3)]
md=['# '+m['title'],'',', '.join(m['authors']),'',m['status'],'','## Abstract','',m['abstract'],'','**Index Terms:** '+m['keywords'],'']
evidence_md=md.copy(); evidence_md[8] += ' [claim:C000] [evidence:E101,E102,E103,E104,E109]'
for b in m['blocks']:
    t=b['type']
    if t in ['h1','h2']:
        story.append(para(html.escape(b['text']),t));md.extend([('## ' if t=='h1' else '### ')+b['text'],'']);evidence_md.extend(md[-2:])
    elif t=='p':
        story.append(para(html.escape(b['text'])));md.extend([b['text'],''])
        evidence_md.extend([b['text']+f" [claim:{b['id']}] [evidence:{','.join(b['evidence'])}]",''])
    elif t=='equation':
        story.append(para(b['text']+f"  ({b['number']})",'eq'))
        line=b['text']+f" ({b['number']})";md.extend([line,'']);evidence_md.extend([line+f" [claim:{b['claim_id']}] [evidence:{','.join(b['evidence'])}]",''])
    elif t=='figure':
        key=b['figure']; f=figs[key]
        if key not in big:
            group=[Spacer(1,5),drawing(key,COL),Spacer(1,4),caption(key)]
            if story and isinstance(story[-1],Paragraph) and story[-1].style.name=='h2': group.insert(0,story.pop())
            story.append(KeepTogether(group))
        rel=Path(next(x for x in f['files'] if x.endswith('.png'))).relative_to('paper').as_posix()
        line=f"![{f['alt_text']}]({rel})";cap=f"Fig. {b['number']}. {f['caption']}"
        md.extend([line,'',cap,'']);evidence_md.extend([line,'',cap+f" [claim:{b['claim_id']}] [evidence:{','.join(b['evidence'])}]",''])
    elif t=='table':
        cap=para(f"TABLE {b['number']}<br/>{html.escape(b['title']).upper()}",'caption');cap.style=ParagraphStyle('tcap',parent=styles['caption'],alignment=TA_CENTER)
        rows=[[para('<b>'+html.escape(str(v))+'</b>','table') for v in b['headers']]]+[[para(html.escape(str(v)),'table') for v in row] for row in b['rows']]
        table=Table(rows,colWidths=[COL*x for x in b['widths']],hAlign='LEFT',repeatRows=1)
        table.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.4,colors.black),('LINEBELOW',(0,-1),(-1,-1),.7,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        story.append(KeepTogether([Spacer(1,4),cap,table,Spacer(1,8)]))
        lines=[f"Table {b['number']}. {b['title']}",'','| '+' | '.join(b['headers'])+' |','| '+' | '.join(['---']*len(b['headers']))+' |']+['| '+' | '.join(row)+' |' for row in b['rows']]+['']
        md.extend(lines);evidence_md.extend(lines+[f"[claim:{b['claim_id']}] [evidence:{','.join(b['evidence'])}]",''])
story.extend([FrameBreak,para('References','h1')]);md.extend(['## References','']);evidence_md.extend(['## References',''])
for r in m['references']:
    label='Data sheet' if r['number'] in [5,6,7] else ('Application note' if r['number']==8 else 'Source')
    text=f"[{r['number']}] {html.escape(r['text'])} <link href='{html.escape(r['url'],quote=True)}' color='#1c4d72'>{label}</link>."
    story.append(para(text,'ref'));line=f"[{r['number']}] {r['text']} [{label}]({r['url']}).";md.extend([line,'']);evidence_md.extend([line,''])
doc.build(story)
(P/'wattsense-manuscript.md').write_text('\n'.join(md),encoding='utf-8')
(P/'evidence/manuscript-with-evidence.md').write_text('\n'.join(evidence_md),encoding='utf-8')
reader=PdfReader(pdfpath)
text='\n\n'.join(p.extract_text() for p in reader.pages)
(P/'evidence/rendered-manuscript.txt').write_text(text,encoding='utf-8')
record=dict(status='RENDERED_AWAITING_VISUAL_QA',pages=len(reader.pages),pdf_sha256=hashlib.sha256(pdfpath.read_bytes()).hexdigest(),body_font='Times New Roman 10 pt',page='US Letter; two columns',source='paper/src/manuscript.json',standalone_figures='SVG vector and 300 dpi PNG',native_pdf_figures='SVG converted to PDF vector drawing',human_review_pending=True)
(P/'evidence/build-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
