"""Reproducible, conservative merchandise classification using observed source descriptions.
This is an analytical rule set, NOT an authoritative stock-master classification.
"""
from pathlib import Path
import pandas as pd, numpy as np, json, re
BASE=Path(__file__).resolve().parents[1]
SPECIAL={
'M':'MANUAL_ADJUSTMENT','DOT':'DOTCOM_POSTAGE','POST':'POSTAGE','C2':'CARRIAGE','BANK CHARGES':'BANK_FEES',
'AMAZONFEE':'MARKETPLACE_FEES','S':'SAMPLES_OR_SERVICE','D':'DISCOUNT','CRUK':'COMMISSION_OR_CREDIT',
'B':'ADJUSTMENT_OR_SERVICE','PADS':'PADS_ADJUSTMENT','ADJUST':'MANUAL_ADJUSTMENT',
'TEST001':'TEST_ITEM','TEST002':'TEST_ITEM','GIFT_0001':'GIFT_VOUCHER','DCGS0003':'GIFT_VOUCHER',
'DCGS0004':'GIFT_VOUCHER','DCGS0055':'GIFT_VOUCHER','DCGS0057':'GIFT_VOUCHER',
'DCGS0060':'GIFT_VOUCHER','DCGS0062':'GIFT_VOUCHER','DCGS0066':'GIFT_VOUCHER',
'DCGS0067':'GIFT_VOUCHER','DCGS0068':'GIFT_VOUCHER','DCGS0069':'GIFT_VOUCHER',
'DCGS0070':'GIFT_VOUCHER','DCGS0071':'GIFT_VOUCHER','DCGS0072':'GIFT_VOUCHER',
'DCGS0073':'GIFT_VOUCHER','DCGS0074':'GIFT_VOUCHER','DCGS0075':'GIFT_VOUCHER',
'DCGS0076':'GIFT_VOUCHER','DCGS0077':'GIFT_VOUCHER','DCGS0078':'GIFT_VOUCHER',
'DCGS0079':'GIFT_VOUCHER','DCGS0080':'GIFT_VOUCHER','DCGS0081':'GIFT_VOUCHER',
'DCGS0082':'GIFT_VOUCHER','DCGS0083':'GIFT_VOUCHER','DCGS0084':'GIFT_VOUCHER',
'DCGS0085':'GIFT_VOUCHER','DCGS0086':'GIFT_VOUCHER','DCGS0087':'GIFT_VOUCHER',
'DCGS0088':'GIFT_VOUCHER','DCGS0089':'GIFT_VOUCHER','DCGS0090':'GIFT_VOUCHER',
'DCGS0091':'GIFT_VOUCHER','DCGS0092':'GIFT_VOUCHER','DCGS0093':'GIFT_VOUCHER',
'DCGS0094':'GIFT_VOUCHER','DCGS0095':'GIFT_VOUCHER','DCGS0096':'GIFT_VOUCHER',
'DCGS0097':'GIFT_VOUCHER','DCGS0098':'GIFT_VOUCHER','DCGS0099':'GIFT_VOUCHER',
}
DESC_RE=re.compile(r'\b(POSTAGE|BANK CHARGES|AMAZON FEE|AMAZONFEE|MANUAL|ADJUSTMENT|DISCOUNT|DOTCOM POSTAGE|GIFT VOUCHER|GIFT CERTIFICATE|COMMISSION)\b',re.I)
def classify(code, descriptions):
    code=str(code).strip().upper()
    ds=[str(s).strip().upper() for s in descriptions if pd.notna(s)]
    if code.startswith('DCGS'):
        return 'REVIEW_REQUIRED','DCGS_MIXED_CATALOG','PREFIX_REQUIRES_DESCRIPTION_REVIEW'
    if code in SPECIAL:return 'NON_MERCHANDISE_CONFIRMED_RULE',SPECIAL[code], 'EXACT_CODE_RULE'
    if code.startswith('GIFT_'):
        return 'NON_MERCHANDISE_CONFIRMED_RULE','GIFT_VOUCHER','CODE_PREFIX_RULE'
    if code.startswith('DCGS'):
        return 'REVIEW_REQUIRED','DCGS_MIXED_CATALOG','PREFIX_REQUIRES_DESCRIPTION_REVIEW'
    if not ds:return 'REVIEW_REQUIRED','MISSING_DESCRIPTION','MISSING_DESCRIPTION'
    matches=[s for s in ds if DESC_RE.search(s)]
    if matches:
        return 'REVIEW_REQUIRED','SERVICE_LIKE_DESCRIPTION','DESCRIPTION_KEYWORD_RULE'
    if any('NEXT DAY CARRIAGE' in v or v.strip()=='CARRIAGE' for v in ds):
        return 'REVIEW_REQUIRED','SHIPPING_SERVICE_DESCRIPTION','DESCRIPTION_EXACT_RULE'
    if code.isdigit() or re.fullmatch(r'\d{4,6}[A-Z]{1,3}',code):
        return 'MERCHANDISE_CANDIDATE','REGULAR_STOCK_CODE','CODE_PATTERN_AND_DESCRIPTION'
    return 'REVIEW_REQUIRED','UNUSUAL_STOCK_CODE','UNUSUAL_CODE_RULE'
def abc(t):
    t=t.sort_values(['revenue_gbp','product_id'],ascending=[False,True]).copy()
    total=t.revenue_gbp.sum();t['share']=t.revenue_gbp/total
    before=t.revenue_gbp.cumsum().shift(fill_value=0)/total
    t['abc']=np.select([before<.8,before<.95],['A','B'],default='C')
    t['cumulative_share']=t.share.cumsum()
    return t

def run():
    p=BASE/'outputs'; grouped={}; n=0
    for ch in pd.read_csv(p/'classified_lines.csv.gz',chunksize=125000,dtype={'product_id':str},usecols=['product_id','description','status','gross_positive_gbp','quantity']):
        s=ch[ch.status=='positive_sale'];n+=len(s)
        for (code,desc),g in s.groupby(['product_id','description'],dropna=False,sort=False):
            key=(str(code),str(desc)); val=(float(g.gross_positive_gbp.sum()),int(g.quantity.sum()),len(g))
            prev=grouped.get(key,(0.,0,0));grouped[key]=(prev[0]+val[0],prev[1]+val[1],prev[2]+val[2])
    rows=[(k[0],k[1],*v) for k,v in grouped.items()]
    d=pd.DataFrame(rows,columns=['product_id','description','revenue_gbp','units','lines'])
    agg=d.groupby('product_id',sort=False).agg(revenue_gbp=('revenue_gbp','sum'),units=('units','sum'),lines=('lines','sum'),distinct_descriptions=('description','nunique')).reset_index()
    desc=d.sort_values(['revenue_gbp','lines'],ascending=False).drop_duplicates('product_id')[['product_id','description']].rename(columns={'description':'primary_description'})
    agg=agg.merge(desc,on='product_id',validate='one_to_one')
    ds=d.groupby('product_id')['description'].apply(list).to_dict()
    cats=[classify(k,ds.get(k,[])) for k in agg.product_id]
    agg[['merchandise_status','reason','evidence_rule']]=pd.DataFrame(cats,index=agg.index)
    agg=agg.sort_values('revenue_gbp',ascending=False)
    agg.to_csv(p/'product_classification_audit.csv',index=False)
    d.to_csv(p/'product_description_evidence.csv',index=False)
    candidates=agg[agg.merchandise_status=='MERCHANDISE_CANDIDATE'].copy()
    clean=abc(candidates)
    clean.to_csv(p/'merchandise_candidate_abc.csv',index=False)
    summary=agg.groupby(['merchandise_status','reason'],as_index=False).agg(product_codes=('product_id','size'),positive_sales_gbp=('revenue_gbp','sum'))
    summary['share_of_total_positive_sales_pct']=100*summary.positive_sales_gbp/agg.revenue_gbp.sum()
    summary.to_csv(p/'classification_bridge.csv',index=False)
    a=clean.groupby('abc',as_index=False).agg(product_codes=('product_id','size'),positive_sales_gbp=('revenue_gbp','sum'))
    a['share_of_candidate_sales_pct']=100*a.positive_sales_gbp/clean.revenue_gbp.sum()
    a.to_csv(p/'merchandise_abc_summary.csv',index=False)
    review=agg[agg.merchandise_status!='MERCHANDISE_CANDIDATE'].head(100)
    review.to_csv(p/'classification_review_queue.csv',index=False)
    total=float(agg.revenue_gbp.sum());bridge=float(summary.positive_sales_gbp.sum());candidate=float(clean.revenue_gbp.sum())
    assert abs(total-bridge)<.01
    assert abs(total-20972594.55)<.03,(total,'gross reconciliation')
    assert abs(candidate-float(a.positive_sales_gbp.sum()))<.01
    assert len(agg)==4916
    assert n==1041670
    metrics={'positive_sales_gbp':round(total,2),'merchandise_candidate_gbp':round(candidate,2),'merchandise_candidate_share_pct':round(100*candidate/total,2),'non_merchandise_rule_gbp':round(float(agg.loc[agg.merchandise_status=='NON_MERCHANDISE_CONFIRMED_RULE','revenue_gbp'].sum()),2),'review_required_gbp':round(float(agg.loc[agg.merchandise_status=='REVIEW_REQUIRED','revenue_gbp'].sum()),2),'candidate_codes':len(clean),'review_codes':int((agg.merchandise_status=='REVIEW_REQUIRED').sum()),'non_merchandise_rule_codes':int((agg.merchandise_status=='NON_MERCHANDISE_CONFIRMED_RULE').sum()),'classification_rule_version':'v1.0 conservative heuristic, unverified stock master','caveat':'Candidate is not confirmed physical merchandise; flagged codes require manual validation; financial gross unchanged.'}
    (p/'merchandise_metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2));print(a.to_string(index=False));print(summary.sort_values('positive_sales_gbp',ascending=False).head(20).to_string(index=False))
if __name__=='__main__':run()
