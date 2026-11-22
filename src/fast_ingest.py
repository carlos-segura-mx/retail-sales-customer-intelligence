import zipfile, re
from lxml import etree
import pandas as pd
import numpy as np
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def load_fast(path):
    with zipfile.ZipFile(path) as z:
        with z.open('xl/sharedStrings.xml') as f:
            root=etree.parse(f).getroot()
            strings=[''.join(t.text or '' for t in si.iter(NS+'t')) for si in root]
        del root
        frames=[]
        for idx, name in enumerate(['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml']):
            data=[]
            with z.open(name) as f:
                for _,row in etree.iterparse(f,events=('end',),tag=NS+'row'):
                    vals=[None]*8
                    for cell in row.iterchildren(NS+'c'):
                        ref=cell.get('r'); m=re.match(r'([A-H])',ref)
                        if not m:continue
                        col=ord(m.group(1))-65
                        v=cell.find(NS+'v')
                        if v is None:
                            inline=cell.find(NS+'is')
                            val=''.join(t.text or '' for t in inline.iter(NS+'t')) if inline is not None else None
                        else:
                            val=v.text
                            if cell.get('t')=='s':val=strings[int(val)]
                            elif cell.get('t') in ('n',None):
                                try:val=float(val)
                                except (ValueError,TypeError):pass
                        vals[col]=val
                    if row.get('r')!='1':data.append(vals)
                    row.clear()
                    while row.getprevious() is not None:del row.getparent()[0]
            df=pd.DataFrame(data,columns=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country'])
            df['InvoiceDate']=pd.to_datetime(pd.to_numeric(df['InvoiceDate'],errors='coerce'),unit='D',origin='1899-12-30',errors='coerce')
            df['source_sheet']=['Year 2009-2010','Year 2010-2011'][idx]
            df['source_row']=np.arange(2,len(df)+2)
            frames.append(df)
            print('parsed',name,len(df),flush=True)
    return pd.concat(frames,ignore_index=True)
