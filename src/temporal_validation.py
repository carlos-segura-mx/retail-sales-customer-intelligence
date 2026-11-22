"""Out-of-time basket association validation; descriptive, not causal."""
from pathlib import Path
from collections import Counter
from itertools import combinations
import json
import pandas as pd
import numpy as np
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs'

def count_pairs(baskets, selected):
    items=Counter();pairs=Counter();n=0
    for b in baskets:
        n+=1
        subset=sorted(set(b)&selected)
        items.update(subset)
        pairs.update(combinations(subset,2))
    return n,items,pairs

def run():
    audit=pd.read_csv(OUT/'product_classification_audit.csv',dtype={'product_id':str})
    eligible=set(audit.loc[audit.merchandise_status=='MERCHANDISE_CANDIDATE','product_id'])
    cols=['invoice_id','product_id','invoice_date','gross_positive_gbp','status']
    parts=[]
    for ch in pd.read_csv(OUT/'classified_lines.csv.gz',usecols=cols,dtype={'product_id':str,'invoice_id':str},chunksize=250000):
        ch=ch.loc[(ch.status=='positive_sale')&ch.product_id.isin(eligible)].copy()
        parts.append(ch.drop(columns='status'))
    df=pd.concat(parts,ignore_index=True);del parts
    df['invoice_date']=pd.to_datetime(df.invoice_date,errors='coerce')
    df=df.dropna(subset=['invoice_date','invoice_id'])
    # Assign invoice to one period using its earliest positive merchandise date.
    invoice_dates=df.groupby('invoice_id').invoice_date.min()
    cutoff=pd.Timestamp('2011-06-01')
    train_ids=set(invoice_dates.index[invoice_dates<cutoff]);test_ids=set(invoice_dates.index[invoice_dates>=cutoff])
    assert train_ids.isdisjoint(test_ids)
    train=df[df.invoice_id.isin(train_ids)]
    test=df[df.invoice_id.isin(test_ids)]
    top=set(train.groupby('product_id').gross_positive_gbp.sum().nlargest(100).index)
    def stats(frame):
        baskets=frame.groupby('invoice_id').product_id.unique()
        return count_pairs(baskets,top)
    ntr,itr,ptr=stats(train);nte,ite,pte=stats(test)
    records=[]
    for (a,b),c in ptr.items():
        if c<30:continue
        ct=pte.get((a,b),0)
        atr,btr=itr[a],itr[b];ate,bte=ite[a],ite[b]
        train_lift=(c*ntr)/(atr*btr)
        test_lift=(ct*nte)/(ate*bte) if ate and bte else np.nan
        records.append({'product_a':a,'product_b':b,'train_co_baskets':c,'test_co_baskets':ct,'train_baskets':ntr,'test_baskets':nte,'train_lift':train_lift,'test_lift':test_lift,'train_support_pct':100*c/ntr,'test_support_pct':100*ct/nte,'train_confidence_a_to_b_pct':100*c/atr,'test_confidence_a_to_b_pct':100*ct/ate if ate else np.nan,'train_confidence_b_to_a_pct':100*c/btr,'test_confidence_b_to_a_pct':100*ct/bte if bte else np.nan,'meets_holdout_screen':bool(ct>=20 and test_lift>=1.5 and train_lift>=1.5),'lift_ratio_holdout_to_train':test_lift/train_lift if np.isfinite(test_lift) else np.nan})
    result=pd.DataFrame(records)
    descriptions=audit[['product_id','primary_description']]
    result=result.merge(descriptions.rename(columns={'product_id':'product_a','primary_description':'description_a'}),on='product_a',how='left').merge(descriptions.rename(columns={'product_id':'product_b','primary_description':'description_b'}),on='product_b',how='left')
    result=result.sort_values(['meets_holdout_screen','test_co_baskets','test_lift'],ascending=False)
    result.to_csv(OUT/'basket_temporal_validation.csv',index=False)
    stable=result[result.meets_holdout_screen].copy()
    stable.sort_values(['test_co_baskets','test_lift'],ascending=False).head(100).to_csv(OUT/'validated_affinity_shortlist.csv',index=False)
    metrics={'cutoff':'2011-06-01','train_invoices':ntr,'holdout_invoices':nte,'top_skus_selected_from_train':len(top),'train_pairs_min_30_baskets':len(result),'holdout_screen_pairs':int(result.meets_holdout_screen.sum()),'holdout_screen_rate_pct':round(100*result.meets_holdout_screen.mean(),2),'holdout_screen':'Train co-occurrence >=30, holdout co-occurrence >=20, train and holdout lift >=1.5. Exploratory screen, not statistical significance or causal uplift.','basket_universe':'All positive merchandise-candidate invoices in each period; SKU universe top 100 selected exclusively in training.','invoice_period_assignment':'Earliest positive merchandise line date per invoice.','train_positive_merchandise_sales_gbp':round(float(train.gross_positive_gbp.sum()),2),'holdout_positive_merchandise_sales_gbp':round(float(test.gross_positive_gbp.sum()),2),'caveat':'Temporal holdout shares the same retailer and changing assortment; no inventory, prices, margins or treatment outcomes.'}
    assert abs(metrics['train_positive_merchandise_sales_gbp']+metrics['holdout_positive_merchandise_sales_gbp']-df.gross_positive_gbp.sum())<.1
    (OUT/'temporal_validation_metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2));print(result.head(5)[['product_a','product_b','train_co_baskets','test_co_baskets','train_lift','test_lift']].to_string(index=False))
if __name__=='__main__':run()
