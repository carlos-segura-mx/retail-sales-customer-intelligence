"""Release checks on precomputed CASE-03 analytical outputs."""
from pathlib import Path
import json, pandas as pd
R=Path(__file__).resolve().parent; O=R/'outputs'
core=json.loads((O/'metrics.json').read_text());m=json.loads((O/'merchandise_metrics.json').read_text());t=json.loads((O/'temporal_validation_metrics.json').read_text())
monthly=pd.read_csv(O/'monthly.csv');country=pd.read_csv(O/'country.csv'); bridge=pd.read_csv(O/'classification_bridge.csv');abc=pd.read_csv(O/'merchandise_abc_summary.csv');quality=pd.read_csv(O/'quality_summary.csv');aff=pd.read_csv(O/'basket_temporal_validation.csv');short=pd.read_csv(O/'validated_affinity_shortlist.csv')
checks={
 'source line count':int(quality.lines.sum())==core['source_rows'],
 'positive sales = monthly':abs(monthly.revenue_gbp.sum()-core['positive_sales_gbp'])<.01,
 'positive sales = country':abs(country.revenue_gbp.sum()-core['positive_sales_gbp'])<.01,
 'positive sales = classification bridge':abs(bridge.positive_sales_gbp.sum()-core['positive_sales_gbp'])<.01,
 'candidate sales = ABC':abs(abc.positive_sales_gbp.sum()-m['merchandise_candidate_gbp'])<.01,
 'candidate sales = temporal partitions':abs(t['train_positive_merchandise_sales_gbp']+t['holdout_positive_merchandise_sales_gbp']-m['merchandise_candidate_gbp'])<.01,
 'ABC shares = 100%':abs(abc.share_of_candidate_sales_pct.sum()-100)<.01,
 'net convention = gross minus cancellations':abs(core['positive_sales_gbp']-core['cancellations_gbp']-core['net_convention_gbp'])<.01,
 'holdout-screened count':int(aff.meets_holdout_screen.astype(str).str.lower().eq('true').sum())==t['holdout_screen_pairs'],
 'prioritized shortlist max 100':0<len(short)<=100,
 'no repeated SKU pairs in shortlist':not short.duplicated(['product_a','product_b']).any(),
 'holdout screen thresholds':bool(((short.train_co_baskets>=30)&(short.test_co_baskets>=20)&(short.train_lift>=1.5)&(short.test_lift>=1.5)).all()),
 'train/holdout basket counts positive':t['train_invoices']>0 and t['holdout_invoices']>0,
}
lines=['CASE-03 RELEASE QA (computed aggregate outputs)']+[('PASS' if v else 'FAIL')+' | '+k for k,v in checks.items()]
(R/'RELEASE_QA.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines));assert all(checks.values()),'Release QA failed'
