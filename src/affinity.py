"""CASE-03: observed merchandise customer concentration and basket affinity; no causal claims."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import pandas as pd, numpy as np, json
BASE=Path(__file__).resolve().parents[1]; OUT=BASE/'outputs'
def run():
    audit=pd.read_csv(OUT/'product_classification_audit.csv',dtype={'product_id':str})
    eligible=set(audit.loc[audit.merchandise_status=='MERCHANDISE_CANDIDATE','product_id'])
    cols=['invoice_id','product_id','customer_id','invoice_date','gross_positive_gbp','quantity','status']
    chunks=[]
    for ch in pd.read_csv(OUT/'classified_lines.csv.gz',usecols=cols,dtype={'product_id':str,'customer_id':str,'invoice_id':str},chunksize=200000):
        ch=ch[(ch.status=='positive_sale')&ch.product_id.isin(eligible)].copy()
        chunks.append(ch.drop(columns='status'))
    df=pd.concat(chunks,ignore_index=True);del chunks
    expected=float(audit.loc[audit.product_id.isin(eligible),'revenue_gbp'].sum())
    assert abs(df.gross_positive_gbp.sum()-expected)<.05
    identified=df[df.customer_id.notna()].copy()
    # Product customer concentration. Missing customer IDs explicitly excluded.
    pc=identified.groupby(['product_id','customer_id'],sort=False).agg(revenue=('gross_positive_gbp','sum'),orders=('invoice_id','nunique')).reset_index()
    product=pc.groupby('product_id').agg(identified_sales_gbp=('revenue','sum'),unique_buyers=('customer_id','size'),repeat_buyers=('orders',lambda s:int((s>=2).sum())),buyer_orders=('orders','sum'),top_buyer_gbp=('revenue','max')).reset_index()
    top5=pc.sort_values('revenue',ascending=False).groupby('product_id').head(5).groupby('product_id').revenue.sum().rename('top5_buyer_gbp')
    product=product.join(top5,on='product_id');product['repeat_buyer_rate_pct']=100*product.repeat_buyers/product.unique_buyers
    product['top1_buyer_share_pct']=100*product.top_buyer_gbp/product.identified_sales_gbp
    product['top5_buyer_share_pct']=100*product.top5_buyer_gbp/product.identified_sales_gbp
    product=product.merge(audit[['product_id','primary_description','revenue_gbp']],on='product_id',how='left',validate='one_to_one')
    product['unidentified_sales_gbp']=(product.revenue_gbp-product.identified_sales_gbp).clip(lower=0)
    product['identified_coverage_pct']=100*product.identified_sales_gbp/product.revenue_gbp
    product['priority_signal']=np.select([(product.unique_buyers>=10)&(product.top1_buyer_share_pct>=40),(product.unique_buyers>=10)&(product.repeat_buyer_rate_pct>=40)],['Customer concentration: validate dependency','Repeat-purchase signal: investigate replenishment'],default='Exploratory: validate buyer coverage and commercial context')
    product.sort_values('revenue_gbp',ascending=False).to_csv(OUT/'product_customer_concentration.csv',index=False)
    # Repeat purchasing across identified customers, with distinct invoices.
    ci=identified.groupby(['customer_id','invoice_id'],sort=False).agg(order_date=('invoice_date','min'),merchandise_spend_gbp=('gross_positive_gbp','sum')).reset_index()
    customer=ci.groupby('customer_id').agg(orders=('invoice_id','size'),spend_gbp=('merchandise_spend_gbp','sum'),first_order=('order_date','min'),last_order=('order_date','max')).reset_index()
    customer['repeat_customer']=customer.orders>=2
    # Public outputs are aggregate only; no customer-level extract in release.
    repeat=pd.DataFrame([{'identified_customers':len(customer),'repeat_customers':int(customer.repeat_customer.sum()),'repeat_customer_share_pct':round(100*customer.repeat_customer.mean(),2),'identified_orders':len(ci),'identified_merchandise_sales_gbp':round(float(customer.spend_gbp.sum()),2),'unidentified_merchandise_sales_gbp':round(float(df.gross_positive_gbp.sum()-customer.spend_gbp.sum()),2)}]);repeat.to_csv(OUT/'merchandise_repeat_summary.csv',index=False)
    # Market basket: a single invoice is a basket; top 100 candidate SKUs by observed positive sales.
    top=set(audit[audit.product_id.isin(eligible)].nlargest(100,'revenue_gbp').product_id)
    baskets=df[df.product_id.isin(top)].groupby('invoice_id',sort=False).product_id.unique()
    basket_count=len(baskets);item_count=Counter();pair_count=Counter()
    for items in baskets:
        unique=sorted(set(items));item_count.update(unique);pair_count.update(combinations(unique,2))
    pairs=[]
    for (a,b),n in pair_count.items():
        if n<20:continue
        pa=item_count[a]/basket_count;pb=item_count[b]/basket_count; pab=n/basket_count
        pairs.append({'product_a':a,'product_b':b,'co_baskets':n,'basket_universe':basket_count,'support_pct':100*pab,'confidence_a_to_b_pct':100*n/item_count[a],'confidence_b_to_a_pct':100*n/item_count[b],'lift':pab/(pa*pb),'a_baskets':item_count[a],'b_baskets':item_count[b]})
    affinity=pd.DataFrame(pairs)
    if not affinity.empty:
        affinity=affinity.merge(audit[['product_id','primary_description']].rename(columns={'product_id':'product_a','primary_description':'description_a'}),on='product_a',how='left').merge(audit[['product_id','primary_description']].rename(columns={'product_id':'product_b','primary_description':'description_b'}),on='product_b',how='left')
        affinity.sort_values(['lift','co_baskets'],ascending=False).to_csv(OUT/'basket_affinity_top100.csv',index=False)
    # Action shortlist: transparent screening, not causal intervention.
    shortlisted=product[(product.unique_buyers>=10)&(product.identified_coverage_pct>=50)].copy()
    shortlisted['action_hypothesis']=np.where(shortlisted.top1_buyer_share_pct>=40,'Diversify demand; investigate dependence on top buyer',np.where(shortlisted.repeat_buyer_rate_pct>=40,'Test replenishment reminders on eligible customers','Test complementary assortment placement; validate margin'))
    shortlisted.sort_values(['revenue_gbp','unique_buyers'],ascending=False).head(100).to_csv(OUT/'merchandise_action_shortlist.csv',index=False)
    result={'candidate_sales_gbp':round(expected,2),'identified_candidate_sales_gbp':round(float(identified.gross_positive_gbp.sum()),2),'identified_sales_coverage_pct':round(100*identified.gross_positive_gbp.sum()/expected,2),'products_with_identified_buyers':len(product),'identified_customers':len(customer),'repeat_customers':int(customer.repeat_customer.sum()),'repeat_customer_share_pct':round(100*customer.repeat_customer.mean(),2),'top_sku_basket_universe':basket_count,'top_sku_pairs_min_20_baskets':len(affinity),'shortlist_rows':min(100,len(shortlisted)),'methodology':'Positive merchandise-candidate lines; unique invoices per customer; top-100 SKUs selected on positive sales; pair universe invoices containing at least one top-100 SKU; associations not causal; returns excluded.'}
    (OUT/'affinity_metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':run()
