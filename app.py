"""CASE-03 public Streamlit dashboard. Aggregate-only Online Retail II case."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"

st.set_page_config(page_title="Retail Sales & Customer Intelligence | CS Intelligence", page_icon="📈", layout="wide")

language = st.sidebar.radio("Idioma / Language", ["Español", "English"], horizontal=True)
ES = language == "Español"

def T(es: str, en: str) -> str:
    return es if ES else en

@st.cache_data(show_spinner=False)
def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)

@st.cache_data(show_spinner=False)
def metric(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))

def pounds(value: float) -> str:
    return f"£{value / 1_000_000:,.2f} M"

def csv_export(frame: pd.DataFrame, filename: str, label_es: str, label_en: str) -> None:
    st.download_button(T(label_es, label_en), frame.to_csv(index=False).encode("utf-8-sig"),
                       filename, mime="text/csv", key=f"download_{filename}")

def fmt_frame(frame: pd.DataFrame, cols: dict[str, str], numeric: int = 2) -> pd.DataFrame:
    view = frame[list(cols)].copy()
    return view.round(numeric).rename(columns=cols)

try:
    core = metric("metrics.json")
    merchandise = metric("merchandise_metrics.json")
    validation = metric("temporal_validation_metrics.json")
    monthly = csv("monthly.csv")
    countries = csv("country.csv")
    bridge = csv("classification_bridge.csv")
    quality = csv("quality_summary.csv")
    abc_sum = csv("merchandise_abc_summary.csv")
    abc = csv("merchandise_candidate_abc.csv")
    rfm = csv("rfm_segment_summary.csv")
    repeat = csv("merchandise_repeat_summary.csv").iloc[0]
    concentration = csv("product_customer_concentration.csv")
    screened_pairs = csv("basket_temporal_validation.csv")
    actions = csv("merchandise_action_shortlist.csv")
except (FileNotFoundError, KeyError, ValueError, pd.errors.ParserError) as exc:
    st.error(T("Faltan datos agregados necesarios. Comprueba la carpeta outputs/.",
               "Required aggregate data are missing. Check the outputs/ directory."))
    st.code(str(exc))
    st.stop()

st.title(T("Inteligencia de ventas y clientes", "Retail Sales & Customer Intelligence"))
st.caption(T(
    "CS Intelligence | Online Retail II (UCI) | GBP | Datos históricos de 2009 a 2011",
    "CS Intelligence | Online Retail II (UCI) | GBP | Historical data from 2009 to 2011"
))
st.write(T(
    "**¿Qué productos y clientes merecen atención, y qué decisiones comerciales pueden evaluarse con los datos disponibles?**",
    "**Which products and customers deserve attention, and what commercial decisions can the available data support?**"
))
st.caption(T(
    "Caso independiente sobre datos públicos. Los resultados son descriptivos, no estimaciones causales ni contabilidad auditada.",
    "Independent public-data case. Findings are descriptive, not causal estimates or audited accounting results."
))

labels = [
    T("Panorama", "Overview"), T("Productos", "Products"),
    T("Clientes", "Customers"), T("Afinidad", "Affinity"),
    T("Decisiones", "Decisions"), T("Metodología", "Methods")
]
tabs = st.tabs(labels)

with tabs[0]:
    st.subheader(T("¿Qué sabemos de las ventas registradas?", "What do the recorded sales tell us?"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("Ventas positivas", "Positive sales"), pounds(core["positive_sales_gbp"]))
    c2.metric(T("Mercancía candidata", "Candidate merchandise"), pounds(merchandise["merchandise_candidate_gbp"]))
    c3.metric(T("Cancelaciones", "Cancellation value"), pounds(core["cancellations_gbp"]))
    c4.metric(T("Clientes identificados", "Identified buyers"), f"{core['identified_customers_with_positive_sale']:,}")
    st.caption(T(
        "Las ventas positivas son valores de líneas clasificadas como ventas; las cancelaciones no están vinculadas a su factura original. El total neto analítico no equivale a ingresos contables auditados.",
        "Positive sales are values from lines classified as sales; cancellations have not been linked to originating orders. The analytical net total is not audited accounting revenue."
    ))

    subset = st.radio(T("Periodo del gráfico", "Chart period"),
                      ["full", "all"], horizontal=True,
                      format_func=lambda v: T("Meses completos", "Full months") if v == "full"
                      else T("Todos, incluidos parciales", "All, including partial months"),
                      key="monthly_period")
    displayed_monthly = monthly.iloc[1:-1].copy() if subset == "full" else monthly.copy()
    graph = px.line(displayed_monthly, x="month", y="revenue_gbp", markers=True,
                    labels={"month": T("Mes", "Month"), "revenue_gbp": T("Ventas positivas (GBP)", "Positive sales (GBP)")},
                    title=T("Evolución de ventas positivas", "Positive sales over time"))
    graph.update_layout(margin=dict(l=15, r=10, t=45, b=20))
    st.plotly_chart(graph, use_container_width=True)
    st.caption(T(
        "El primer y el último mes del archivo son parciales. El filtro predeterminado los excluye del gráfico, pero los totales del encabezado abarcan todo el dataset.",
        "The dataset's first and last calendar months are partial. The chart hides them by default; the KPI totals always use the full dataset."
    ))
    left, right = st.columns(2)
    with left:
        st.markdown(T("**Distribución por país**", "**Country mix**"))
        top_countries = countries.sort_values("revenue_gbp", ascending=False).head(12)
        fig = px.bar(top_countries.iloc[::-1], x="revenue_gbp", y="country", orientation="h",
                     labels={"country": T("País", "Country"), "revenue_gbp": "GBP"})
        fig.update_layout(height=425, margin=dict(l=10, r=10, t=15, b=15))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown(T("**Calidad y clasificación**", "**Quality and classification**"))
        q = quality[["status", "lines", "signed_value_gbp"]].copy()
        translations = {"positive_sale": "Venta positiva", "cancellation": "Cancelación",
                        "cancellation_review": "Cancelación por revisar", "zero_price": "Precio cero",
                        "negative_price": "Precio negativo"}
        if ES:
            q["status"] = q.status.map(lambda x: translations.get(x, x))
        st.dataframe(fmt_frame(q, {"status": T("Clasificación", "Classification"),
                                   "lines": T("Líneas", "Lines"),
                                   "signed_value_gbp": T("Importe firmado (GBP)", "Signed amount (GBP)")}),
                     hide_index=True, use_container_width=True)
        st.caption(T("Los ajustes de precio negativo requieren revisión, no se suman automáticamente a las cancelaciones.",
                     "Negative-price adjustments require review and are not automatically added to cancellations."))

with tabs[1]:
    st.subheader(T("¿Qué parte del surtido concentra las ventas?", "Which products account for most sales?"))
    st.caption(T(
        "La clasificación ABC corresponde a códigos candidatos a mercancía; no es un catálogo maestro validado ni un análisis de rentabilidad.",
        "ABC covers merchandise-candidate codes, not verified stock-master items or profitability."
    ))
    abc_cols = st.columns(3)
    for i, klass in enumerate(["A", "B", "C"]):
        row = abc_sum.loc[abc_sum.abc.eq(klass)].iloc[0]
        abc_cols[i].metric(T(f"Clase {klass}", f"Class {klass}"),
                           f"{int(row.product_codes):,} {T('códigos', 'codes')}",
                           f"{row.share_of_candidate_sales_pct:.1f}% {T('de ventas candidatas', 'of candidate sales')}",
                           delta_color="off")
    fig = px.bar(abc_sum, x="abc", y="positive_sales_gbp", text="share_of_candidate_sales_pct",
                 labels={"abc": T("Clase ABC", "ABC class"), "positive_sales_gbp": "GBP"},
                 title=T("Concentración de ventas por clase", "Sales concentration by class"))
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    a, b = st.columns([1, 2])
    with a:
        klass = st.multiselect(T("Clases", "Classes"), ["A", "B", "C"], default=["A", "B", "C"])
    with b:
        term = st.text_input(T("Buscar código o descripción", "Search code or description"), key="product_query")
    filtered = abc.loc[abc.abc.isin(klass)].copy()
    if term.strip():
        mask = filtered.product_id.astype(str).str.contains(term.strip(), regex=False, case=False)
        mask |= filtered.primary_description.fillna("").str.contains(term.strip(), regex=False, case=False)
        filtered = filtered.loc[mask]
    st.caption(T(f"{len(filtered):,} códigos encontrados", f"{len(filtered):,} matching codes"))
    fields = {"product_id": T("SKU", "SKU"), "primary_description": T("Descripción", "Description"),
              "abc": "ABC", "revenue_gbp": T("Ventas (GBP)", "Sales (GBP)"),
              "units": T("Unidades", "Units"), "cumulative_share": T("Participación acumulada", "Cumulative share")}
    view = filtered[list(fields)].copy()
    view["cumulative_share"] = (view.cumulative_share * 100).round(2)
    cols = fields.copy(); cols["cumulative_share"] = T("Acumulado (%)", "Cumulative (%)")
    st.dataframe(view.round(2).rename(columns=cols).head(100), hide_index=True, use_container_width=True)
    csv_export(filtered, "case03_candidate_products.csv", "Descargar productos filtrados (CSV)", "Download filtered products (CSV)")
    st.caption(T(
        "La clase A agrupa cerca del 80 % de las ventas de mercancía candidata; los códigos de servicios y ajustes se separaron mediante reglas que todavía requieren validación externa.",
        "Class A accounts for about 80% of candidate merchandise sales; service and adjustment codes were separated using rules that still need external verification."
    ))

with tabs[2]:
    st.subheader(T("¿Qué patrones de compra se observan en clientes identificados?", "What patterns emerge among identified buyers?"))
    c1, c2, c3 = st.columns(3)
    c1.metric(T("Compradores de mercancía", "Merchandise buyers"), f"{int(repeat.identified_customers):,}")
    c2.metric(T("Compradores recurrentes", "Repeat buyers"), f"{int(repeat.repeat_customers):,}")
    c3.metric(T("Recompra observada", "Observed repeat share"), f"{repeat.repeat_customer_share_pct:.2f}%")
    st.caption(T(
        "Las métricas de recompra usan únicamente clientes identificados con facturas positivas de mercancía candidata. No incluyen clientes anónimos ni cancelaciones vinculadas.",
        "Repeat metrics include only identified customers with positive candidate-merchandise invoices. Unidentified buyers and matched returns are excluded."
    ))
    groups = {"active_frequent": ("Activos frecuentes", "Active frequent"),
              "frequent": ("Frecuentes", "Frequent"),
              "high_value_inactive_observed": ("Alto gasto, menor recencia", "High spend, less recent"),
              "other": ("Otros", "Other")}
    sg = rfm.copy(); sg["segment"] = sg.segment.map(lambda x: T(*groups.get(x, (x, x))))
    fig = px.bar(sg, x="segment", y="customers", text="customers",
                 title=T("Grupos RFM descriptivos", "Descriptive RFM groups"),
                 labels={"segment": T("Grupo", "Group"), "customers": T("Clientes", "Customers")})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(fmt_frame(sg, {"segment": T("Grupo", "Group"), "customers": T("Clientes", "Customers"),
                                "observed_monetary_gbp": T("Ventas positivas (GBP)", "Positive sales (GBP)")}),
                 hide_index=True, use_container_width=True)
    st.info(T(
        "Los 396 compradores de alto gasto y menor recencia son candidatos a una revisión comercial. El grupo no es una predicción de abandono ni acredita oportunidades de recuperación.",
        "The 396 high-spend, less-recent buyers merit commercial review. This is not a churn prediction or evidence of recoverable sales."
    ))
    st.markdown(T("**Dependencia de compradores por SKU**", "**Buyer concentration by SKU**"))
    buyer_view = concentration.sort_values("identified_sales_gbp", ascending=False).head(40).copy()
    fields = {"product_id": "SKU", "primary_description": T("Descripción", "Description"),
              "unique_buyers": T("Compradores", "Buyers"),
              "identified_sales_gbp": T("Ventas identificadas (GBP)", "Identified sales (GBP)"),
              "top1_buyer_share_pct": T("Principal comprador (%)", "Top buyer share (%)"),
              "identified_coverage_pct": T("Cobertura identificada (%)", "Identified coverage (%)")}
    st.dataframe(fmt_frame(buyer_view, fields), hide_index=True, use_container_width=True)
    st.caption(T("La concentración se mide sobre las ventas atribuibles a compradores identificados, no todas las ventas del SKU.",
                 "Buyer concentration is based on sales attributable to identified buyers, not all SKU sales."))

with tabs[3]:
    st.subheader(T("¿Qué compras conjuntas merecen una prueba comercial?", "Which co-purchases merit a commercial test?"))
    st.caption(T(
        "Los 100 productos de análisis se seleccionaron con información del periodo de entrenamiento. La asociación se volvió a medir en un periodo posterior.",
        "The 100 analyzed products were selected using training-period data only. Associations were measured again in a later holdout period."
    ))
    c1, c2, c3 = st.columns(3)
    c1.metric(T("Facturas entrenamiento", "Training invoices"), f"{validation['train_invoices']:,}")
    c2.metric(T("Facturas evaluación", "Holdout invoices"), f"{validation['holdout_invoices']:,}")
    c3.metric(T("Pares que pasan filtro", "Pairs passing screen"), f"{validation['holdout_screen_pairs']:,}")
    st.caption(T("Corte temporal: 1 de junio de 2011. El filtro es exploratorio, no una prueba de significancia estadística.",
                 "Temporal cutoff: 1 June 2011. The screen is exploratory, not a statistical significance test."))

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        min_lift = st.slider(T("Lift mínimo en evaluación", "Minimum holdout lift"), 1.5, 12.0, 2.0, 0.5)
    with c2:
        min_baskets = st.slider(T("Compras conjuntas mínimas", "Minimum joint invoices"), 20, 200, 30, 10)
    with c3:
        max_rows = st.selectbox(T("Filas visibles", "Visible rows"), [20, 50, 100, 200], index=1)
    selected_pairs = screened_pairs.loc[
        (screened_pairs.meets_holdout_screen.astype(str).str.lower() == "true") &
        (screened_pairs.test_lift >= min_lift) &
        (screened_pairs.test_co_baskets >= min_baskets)
    ].sort_values(["test_co_baskets", "test_lift"], ascending=False)
    st.caption(T(f"{len(selected_pairs):,} pares cumplen los filtros actuales", f"{len(selected_pairs):,} pairs meet these filters"))
    if not selected_pairs.empty:
        fig = px.scatter(selected_pairs.head(500), x="test_co_baskets", y="test_lift",
                         hover_data=["description_a", "description_b"],
                         labels={"test_co_baskets": T("Facturas conjuntas", "Joint invoices"),
                                 "test_lift": T("Lift en evaluación", "Holdout lift")},
                         title=T("Asociación y frecuencia observada", "Observed association and frequency"))
        st.plotly_chart(fig, use_container_width=True)
    fields = {"description_a": T("Producto A", "Product A"), "description_b": T("Producto B", "Product B"),
              "train_co_baskets": T("Facturas entrenamiento", "Training invoices"),
              "test_co_baskets": T("Facturas evaluación", "Holdout invoices"),
              "train_lift": T("Lift entrenamiento", "Training lift"),
              "test_lift": T("Lift evaluación", "Holdout lift")}
    st.dataframe(fmt_frame(selected_pairs.head(max_rows), fields), hide_index=True, use_container_width=True)
    csv_export(selected_pairs, "case03_affinity_filtered.csv", "Descargar asociaciones filtradas (CSV)", "Download filtered associations (CSV)")
    st.warning(T(
        "Un lift alto no demuestra que un paquete promocional aumente las ventas. Primero hay que validar sustitución, inventario, margen y un experimento con grupo de control.",
        "High lift does not prove a bundle will increase sales. First verify substitutability, inventory, margins and a controlled experiment."
    ))

with tabs[4]:
    st.subheader(T("¿Qué decisiones conviene investigar primero?", "Which decisions should be investigated first?"))
    st.write(T(
        "El Centro de decisiones traduce patrones descriptivos en hipótesis para investigar. No ordena compras, no predice pérdidas ni estima resultados causales.",
        "The Decision Center converts descriptive patterns into hypotheses for investigation. It does not issue purchase orders, predict losses or estimate causal outcomes."
    ))
    signal = {
        "Repeat-purchase signal: investigate replenishment": ("Recompra observada", "Observed repeat purchases"),
        "Customer concentration: validate dependency": ("Concentración de compradores", "Buyer concentration"),
        "Exploratory: validate buyer coverage and commercial context": ("Validación comercial", "Commercial review")
    }
    hypothesis = {
        "Test replenishment reminders on eligible customers": ("Probar recordatorios con grupo de control", "Test reminders with a control group"),
        "Diversify demand; investigate dependence on top buyer": ("Revisar dependencia del principal comprador", "Review reliance on top buyer"),
        "Test complementary assortment placement; validate margin": ("Evaluar ubicación complementaria y margen", "Review complementary placement and margin")
    }
    categories = ["all"] + sorted(actions.priority_signal.unique().tolist())
    chosen = st.selectbox(T("Motivo de revisión", "Review reason"), categories,
                          format_func=lambda x: T("Todos", "All") if x == "all" else T(*signal.get(x, (x, x))))
    ac = actions if chosen == "all" else actions.loc[actions.priority_signal.eq(chosen)]
    ac = ac.copy()
    ac["priority_signal"] = ac.priority_signal.map(lambda x: T(*signal.get(x, (x, x))))
    ac["action_hypothesis"] = ac.action_hypothesis.map(lambda x: T(*hypothesis.get(x, (x, x))))
    st.metric(T("Productos en revisión", "Products under review"), len(ac))
    fields = {"product_id": "SKU", "primary_description": T("Descripción", "Description"),
              "revenue_gbp": T("Ventas positivas (GBP)", "Positive sales (GBP)"),
              "unique_buyers": T("Compradores", "Buyers"),
              "top1_buyer_share_pct": T("Mayor comprador (%)", "Top buyer (%)"),
              "priority_signal": T("Motivo", "Reason")}
    st.dataframe(fmt_frame(ac, fields), hide_index=True, use_container_width=True)
    csv_export(ac, "case03_sku_review.csv", "Descargar revisión de productos (CSV)", "Download product review (CSV)")
    if not ac.empty:
        product = st.selectbox(T("Ver detalle de un SKU", "View SKU details"), ac.product_id.astype(str).tolist())
        current = ac.loc[ac.product_id.astype(str).eq(product)].iloc[0]
        st.markdown(f"**{current['primary_description']}**")
        st.write(f"**{T('Motivo', 'Reason')}:** {current['priority_signal']}")
        st.write(f"**{T('Próxima revisión', 'Next review')}:** {current['action_hypothesis']}")
    st.info(T(
        "Secuencia sugerida: validar catálogo y cobertura de clientes; comprobar costos, disponibilidad y política comercial; diseñar un experimento con control; evaluar contribución incremental.",
        "Suggested sequence: verify catalog and customer coverage; check costs, availability and commercial policy; design a controlled test; evaluate incremental contribution."
    ))

with tabs[5]:
    st.subheader(T("Cómo interpretar los resultados", "How to interpret the results"))
    st.markdown(T(
        """**Origen y alcance.** Online Retail II, UCI Machine Learning Repository, Chen (2012), [DOI 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), licencia CC BY 4.0. Dos hojas originales, 1,067,371 líneas y 25 meses, incluidos dos meses parciales.

**Ventas.** Las ventas positivas provienen de líneas con valores positivos. Las cancelaciones se registran por separado. No se vincularon todas las cancelaciones con las compras originales, por lo que el neto analítico no equivale a un cierre contable.

**Mercancía.** La clasificación se realizó mediante reglas sobre códigos y descripciones. La categoría de mercancía candidata y sus clases ABC requieren cotejo contra un catálogo maestro.

**Clientes.** Los grupos RFM describen compras observadas de clientes identificados. No son probabilidades de abandono, potencial de compra futuro ni campañas evaluadas.

**Afinidad.** El universo de 100 SKU se seleccionó antes del periodo de evaluación, usando ventas del entrenamiento. Los pares se filtraron por frecuencia y lift en ambos periodos, pero la validación no es un experimento ni demuestra efectos incrementales.

**Datos faltantes.** No existen costos de productos, márgenes, inventarios, desabastos, tratamientos promocionales ni resultados experimentales verificables. Por eso no se estiman rentabilidad, elasticidades, canibalización ni ganancias atribuibles a acciones.

**Privacidad y publicación.** El paquete público incluye resultados agregados por producto, grupo o periodo. No incluye el Excel original, líneas de factura ni identificadores individuales de clientes.""",
        """**Source and scope.** Online Retail II, UCI Machine Learning Repository, Chen (2012), [DOI 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), CC BY 4.0. Two original worksheets, 1,067,371 lines and 25 calendar months including two partial months.

**Sales.** Positive sales represent positive-valued sale lines. Cancellations are reported separately and have not all been matched to originating orders. Analytical net is not an accounting close.

**Merchandise.** Stock codes and descriptions were classified using rules. Candidate merchandise and its ABC classes still require validation against an actual stock master.

**Customers.** RFM groups describe observed purchases by identified customers. They are not churn probabilities, future purchasing potential or evaluated campaigns.

**Affinity.** The top 100 SKU universe was selected before the evaluation period using training sales only. Pairs were screened for co-purchase counts and lift in both periods, but the screen is not an experiment or proof of incremental effects.

**Missing data.** No verified product costs, margins, inventory, stockouts, promotional treatments or experiment outcomes are available. Thus profitability, elasticity, cannibalization and action-attributable gains are not estimated.

**Privacy and publication.** The public package contains aggregated outcomes by product, group or period. It does not contain original Excel files, invoice lines or individual customer identifiers."""
    ))
    st.markdown(T("**Conciliación de ventas positivas**", "**Positive-sales reconciliation**"))
    st.dataframe(fmt_frame(bridge, {
        "merchandise_status": T("Estado", "Status"), "reason": T("Regla", "Rule"),
        "positive_sales_gbp": T("Ventas (GBP)", "Sales (GBP)"),
        "share_of_total_positive_sales_pct": T("Participación (%)", "Share (%)")
    }), hide_index=True, use_container_width=True)
    st.caption(T("Los detalles de los métodos, las validaciones y los resultados están documentados en el repositorio.",
                 "Method definitions, validation and findings are documented in the repository."))

st.sidebar.caption(T(
    "Demostración histórica y descriptiva. Solo datos agregados autorizados.",
    "Historical, descriptive demonstration. Authorized aggregate data only."
))
