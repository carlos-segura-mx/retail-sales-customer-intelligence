import zipfile,csv,re
from lxml import etree
from datetime import datetime,timedelta
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
p='/mnt/data/case03/data/source_lines.csv'
with open(p,'rb+') as f:
 f.seek(-1000,2);data=f.read();last=data.rfind(b'\r\n');f.seek(-(len(data)-last-2),2);f.truncate()
with zipfile.ZipFile('/mnt/data/online_retail_II.xlsx') as z:
 shared=[]
 with z.open('xl/sharedStrings.xml') as f:
  for _,e in etree.iterparse(f,events=('end',),tag=NS+'si'):
   shared.append(''.join(e.itertext()));e.clear()
 with open(p,'a',newline='',encoding='utf8') as dest,z.open('xl/worksheets/sheet2.xml') as f:
  w=csv.writer(dest)
  for _,el in etree.iterparse(f,events=('end',),tag=NS+'row'):
   r=int(el.get('r'))
   if r>=374245:
    vals=['']*8
    for cell in el:
     if cell.tag!=NS+'c':continue
     match=re.match('[A-Z]+',cell.get('r',''))
     if not match:continue
     col=0
     for ch in match.group():col=col*26+ord(ch)-64
     if col>8:continue
     v=cell.find(NS+'v')
     if v is None:continue
     value=v.text or ''
     if cell.get('t')=='s':value=shared[int(value)]
     if col==5 and value:value=(datetime(1899,12,30)+timedelta(days=float(value))).isoformat(sep=' ')
     vals[col-1]=value
    w.writerow(vals+['Year 2010-2011',r])
   el.clear()
   while el.getprevious() is not None:del el.getparent()[0]
print('complete')
