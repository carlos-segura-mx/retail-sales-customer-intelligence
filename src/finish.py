from pathlib import Path
import pandas as pd,json,numpy as np
p=Path('/mnt/data/case03/outputs');q=pd.read_csv(p/'quality_summary.csv');m=pd.read_csv(p/'monthly.csv');prod=pd.read_csv(p/'products_abc.csv',dtype={'product_id':str});cust=pd.read_csv(p/'customers_rfm.csv',dtype={'customer_id':str});country=pd.read_csv(p/'country.csv');gross=float(q.loc[q.status=='positive_sale','signed_value_gbp'].sum());returns=-float(q.loc[q.status=='cancellation','signed_value_gbp'].sum());net=gross-returns
summary={'source_rows':1067371,'positive_sales_gbp':round(gross,2),'cancellations_gbp':round(returns,2),'net_convention_gbp':round(net,2),'return_to_gross_pct':round(returns/gross*100,2),'products_positive_sale':len(prod),'identified_customers_with_positive_sale':len(cust),'months':len(m),'quality_status_counts':dict(zip(q.status,q.lines.astype(int))),'source':'Online Retail II, UCI Machine Learning Repository; original Excel, two worksheets','limitations':'Net convention is not audited revenue; returns not linked to originating sales; non-merchandise codes may distort product ABC.'}
(p/'metrics.json').write_text(json.dumps(summary,indent=2))
assert abs(m.revenue_gbp.sum()-gross)<.02
assert abs(country.revenue_gbp.sum()-gross)<.02
assert abs(prod.revenue_gbp.sum()-gross)<.02
assert abs(cust.monetary.sum()-gross)<gross # missing customer IDs
# Separate product category inference, avoid unvalidated merchandising claims.
non_merch={'M','POST','DOT','BANK CHARGES','AMAZONFEE','S','D','CRUK','C2','B','PADS','ADJUST','TEST001','TEST002','gift_0001','GIFT_0001'}
prod['review_flag']=np.where(prod.product_id.str.upper().isin({x.upper() for x in non_merch}),'NON_MERCHANDISE_OR_SERVICE_REVIEW','MERCHANDISE_UNVERIFIED')
prod['opportunity_type']=np.select([(prod.abc=='A') & (prod.review_flag=='MERCHANDISE_UNVERIFIED'),(prod.abc=='B') & (prod.review_flag=='MERCHANDISE_UNVERIFIED'),prod.review_flag!='MERCHANDISE_UNVERIFIED'],['Protect availability; review margin and stockouts','Targeted assortment and cross-sell hypothesis','Exclude from merchandise ranking after code validation'],default='Long-tail rationalization hypothesis')
prod.to_csv(p/'product_action_center.csv',index=False)
cust['opportunity_type']=np.select([cust.segment=='high_value_inactive_observed',cust.segment=='active_frequent',cust.segment=='frequent'],['Prioritize for holdout-tested win-back','Retention and service protection','Cross-sell experiment'],default='Lifecycle profiling; no intervention without test')
cust['risk_notice']='Observed recency is not churn probability; no causal uplift inferred'
cust.to_csv(p/'customer_action_center.csv',index=False)
# Snapshot facts
abc_counts=prod.groupby('abc').agg(products=('product_id','size'),gross_gbp=('revenue_gbp','sum')).reset_index();abc_counts['share_pct']=abc_counts.gross_gbp/gross*100;abc_counts.to_csv(p/'abc_summary.csv',index=False)
seg=cust.groupby('segment').agg(customers=('customer_id','size'),observed_monetary_gbp=('monetary','sum')).reset_index().sort_values('observed_monetary_gbp',ascending=False);seg.to_csv(p/'rfm_segment_summary.csv',index=False)
print(json.dumps(summary,indent=2));print(abc_counts.to_string(index=False));print(seg.to_string(index=False))
