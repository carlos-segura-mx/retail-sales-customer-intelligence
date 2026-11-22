
import pandas as pd
from src.pipeline import classify,abc,rfm
def sample():
    return pd.DataFrame({"Invoice":["100","100","C101","102"],"StockCode":["A","A","A","B"],
      "Description":["a","a","a","b"],"Quantity":[2,2,-1,3],
      "InvoiceDate":pd.to_datetime(["2010-01-01"]*4),"Price":[5,5,5,10],
      "Customer ID":[1,1,1,2],"Country":["UK"]*4})
def test_no_deduplication():
    x=classify(sample());assert len(x)==4
    assert x.gross_positive_gbp.sum()==50
    assert x.returns_gbp.sum()==5
    assert x.net_gbp.sum()==45
def test_cancellation():
    x=classify(sample());assert x.status.tolist()==["positive_sale","positive_sale","cancellation","positive_sale"]
def test_abc():
    z=abc(pd.DataFrame({"product_id":["a","b","c"],"revenue_gbp":[80,15,5]}))
    assert z.abc.tolist()==["A","B","C"]
    assert abs(z.share.sum()-1)<1e-10
def test_rfm():
    z=rfm(classify(sample()))
    assert len(z)==2 and z.frequency.sum()==2
