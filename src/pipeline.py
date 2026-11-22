
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

COLUMNS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
def load_source(path):
    if str(path).lower().endswith(".csv"):
        return pd.read_csv(path, dtype={"Invoice":"string","StockCode":"string","Customer ID":"string"}, low_memory=False)
    from src.fast_ingest import load_fast
    return load_fast(path)

def classify(df):
    x=df.copy()
    x["invoice_id"]=x["Invoice"].astype("string").str.strip()
    x["product_id"]=x["StockCode"].astype("string").str.strip()
    x["customer_id"]=x["Customer ID"].astype("string").str.replace(r"\.0$","",regex=True)
    x["invoice_date"]=pd.to_datetime(x["InvoiceDate"],errors="coerce")
    x["quantity"]=pd.to_numeric(x["Quantity"],errors="coerce")
    x["unit_price"]=pd.to_numeric(x["Price"],errors="coerce")
    x["country"]=x["Country"].astype("string").str.strip()
    x["description"]=x["Description"].astype("string").str.strip()
    x["line_value_gbp"]=(x["quantity"]*x["unit_price"]).round(2)
    cancellation=x["invoice_id"].str.upper().str.startswith("C",na=False)
    bad=x["invoice_date"].isna()|x["quantity"].isna()|x["unit_price"].isna()|x["invoice_id"].isna()
    x["status"]=np.select(
      [bad,x["unit_price"]<0,x["quantity"]==0,x["unit_price"]==0,cancellation & (x["quantity"]<0),cancellation,x["quantity"]<0],
      ["invalid","negative_price","zero_quantity","zero_price","cancellation","cancellation_review","negative_adjustment_review"],
      default="positive_sale")
    x["gross_positive_gbp"]=np.where(x["status"]=="positive_sale",x["line_value_gbp"],0)
    x["returns_gbp"]=np.where(x["status"]=="cancellation",-x["line_value_gbp"],0)
    x["net_gbp"]=x["gross_positive_gbp"]-x["returns_gbp"]
    return x

def abc(products, a=.8,b=.95):
    if not 0<a<b<1: raise ValueError("ABC thresholds invalid")
    z=products.sort_values(["revenue_gbp","product_id"],ascending=[False,True]).copy()
    total=z["revenue_gbp"].sum()
    z["share"]=z["revenue_gbp"]/total if total>0 else 0
    z["cumulative_share"]=z["share"].cumsum()
    before=z["cumulative_share"]-z["share"]
    z["abc"]=np.select([before<a,before<b],["A","B"],default="C")
    return z

def rfm(lines):
    valid=lines[(lines.status=="positive_sale") & lines.customer_id.notna()].copy()
    if valid.empty: return pd.DataFrame()
    orders=valid.groupby(["customer_id","invoice_id"],as_index=False).agg(
        date=("invoice_date","min"),amount=("line_value_gbp","sum"))
    cutoff=valid.invoice_date.max().normalize()+pd.Timedelta(days=1)
    out=orders.groupby("customer_id").agg(last=("date","max"),frequency=("invoice_id","nunique"),monetary=("amount","sum")).reset_index()
    out["recency_days"]=(cutoff-out["last"]).dt.days
    out["r_score"]=pd.qcut(out.recency_days.rank(method="first"),5,labels=[5,4,3,2,1]).astype(int)
    out["f_score"]=pd.qcut(out.frequency.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    out["m_score"]=pd.qcut(out.monetary.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    out["segment"]=np.select([(out.r_score>=4)&(out.f_score>=4),
        (out.r_score<=2)&(out.m_score>=4),out.f_score>=4],
        ["active_frequent","high_value_inactive_observed","frequent"],default="other")
    return out

def run(source,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    raw=load_source(source);x=classify(raw)
    x.to_csv(out/"classified_lines.csv.gz",index=False,compression="gzip")
    quality=x.groupby("status",dropna=False).agg(lines=("invoice_id","size"),signed_value_gbp=("line_value_gbp","sum")).reset_index()
    quality.to_csv(out/"quality_summary.csv",index=False)
    sales=x[x.status=="positive_sale"].copy()
    sales["month"]=sales.invoice_date.dt.to_period("M").astype(str)
    monthly=sales.groupby("month").agg(revenue_gbp=("line_value_gbp","sum"),units=("quantity","sum"),orders=("invoice_id","nunique")).reset_index()
    monthly["average_order_value_gbp"]=monthly.revenue_gbp/monthly.orders
    monthly.to_csv(out/"monthly.csv",index=False)
    products=sales.groupby("product_id").agg(revenue_gbp=("line_value_gbp","sum"),units=("quantity","sum")).reset_index()
    abc(products).to_csv(out/"products_abc.csv",index=False)
    customers=rfm(x);customers.to_csv(out/"customers_rfm.csv",index=False)
    country=sales.groupby("country").agg(revenue_gbp=("line_value_gbp","sum"),orders=("invoice_id","nunique")).reset_index()
    country.to_csv(out/"country.csv",index=False)
    # BI tables: stable source-line surrogate keys; preserve original rows without value-based deduplication.
    x["line_key"]=np.arange(1,len(x)+1)
    x["date_key"]=x.invoice_date.dt.strftime("%Y%m%d")
    x[["line_key","invoice_id","product_id","customer_id","country","date_key","quantity","unit_price","line_value_gbp","gross_positive_gbp","returns_gbp","net_gbp","status"]].to_csv(out/"fact_transaction.csv.gz",index=False,compression="gzip")
    for name,cols in [("dim_product",["product_id","description"]),("dim_customer",["customer_id"]),("dim_country",["country"])]:
        x[cols].dropna(subset=[cols[0]]).drop_duplicates(subset=[cols[0]]).to_csv(out/f"{name}.csv",index=False)
    dates=pd.DataFrame({"date":pd.date_range(x.invoice_date.min().normalize(),x.invoice_date.max().normalize())})
    dates["date_key"]=dates.date.dt.strftime("%Y%m%d")
    dates["year"]=dates.date.dt.year;dates["month"]=dates.date.dt.month
    dates.to_csv(out/"dim_date.csv",index=False)
    summary={"source_rows":len(x),"positive_sales_gbp":round(float(x.gross_positive_gbp.sum()),2),
      "cancellations_gbp":round(float(x.returns_gbp.sum()),2),"net_convention_gbp":round(float(x.net_gbp.sum()),2),
      "identified_customers":int(x.customer_id.nunique()),"positive_invoices":int(sales.invoice_id.nunique()),
      "note":"Net convention excludes negative adjustments under review and zero-price rows; not audited accounting revenue."}
    (out/"metrics.json").write_text(json.dumps(summary,indent=2))
    assert np.isclose(summary["net_convention_gbp"],summary["positive_sales_gbp"]-summary["cancellations_gbp"],atol=.011)
    assert np.isclose(monthly.revenue_gbp.sum(),sales.line_value_gbp.sum(),atol=.01)
    assert np.isclose(country.revenue_gbp.sum(),sales.line_value_gbp.sum(),atol=.01)
    return summary

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--output",default="outputs")
    a=ap.parse_args();print(json.dumps(run(a.source,a.output),indent=2))
