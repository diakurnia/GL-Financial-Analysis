import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.db import run_sql_file, run_query

st.set_page_config(
    page_title="GL Financial Analysis",
    page_icon="📒",
    layout="wide",
)

# ── Minimalist white + Slate Blue palette ─────────────────────────────────────
SLATE   = "#4A6FA5"
SLATE_L = "#7B9EC7"
SLATE_XL= "#EEF2F7"
GREEN   = "#57A773"
RED     = "#C0392B"
ORANGE  = "#E8A838"
GRAY_D  = "#2D2D2D"
GRAY_M  = "#6B7280"
GRAY_L  = "#E5E7EB"
WHITE   = "#FFFFFF"

CHART_PALETTE = [SLATE, SLATE_L, "#B8CDE4", "#D4E4F0", "#90B4D5", "#3A5A8A", "#2B4A7A"]

st.markdown(f"""
<style>
    /* Global white background */
    .stApp {{ background-color: {WHITE}; }}
    [data-testid="stSidebar"] {{ background-color: #FAFAFA; }}

    /* KPI cards — white box with thin shadow */
    .kpi {{
        background: {WHITE};
        border: 1px solid {GRAY_L};
        border-radius: 8px;
        padding: 20px 24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
        margin-bottom: 8px;
    }}
    .kpi-label {{
        font-size: 11px;
        color: {GRAY_M};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        color: {GRAY_D};
        margin: 6px 0 3px;
        font-variant-numeric: tabular-nums;
    }}
    .kpi-value.accent {{ color: {SLATE}; }}
    .kpi-value.pos    {{ color: {GREEN}; }}
    .kpi-value.neg    {{ color: {RED};   }}
    .kpi-value.warn   {{ color: {ORANGE}; }}
    .kpi-sub {{
        font-size: 11px;
        color: {GRAY_M};
    }}

    /* Insight / warning boxes */
    .finding {{
        background: {SLATE_XL};
        border-left: 3px solid {SLATE};
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: {GRAY_D};
        line-height: 1.6;
        margin-top: 16px;
    }}
    .finding strong {{ color: {SLATE}; }}
    .warn {{
        background: #FEF9EE;
        border-left: 3px solid {ORANGE};
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: {GRAY_D};
        line-height: 1.6;
        margin-top: 16px;
    }}
    .warn strong {{ color: {ORANGE}; }}

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {{
        font-size: 13px;
        font-weight: 600;
        color: {GRAY_M};
    }}
    .stTabs [aria-selected="true"] {{
        color: {SLATE} !important;
        border-bottom: 2px solid {SLATE} !important;
    }}

    /* Section headers */
    h3 {{ color: {GRAY_D} !important; font-weight: 600 !important; }}
    .section-desc {{ font-size: 13px; color: {GRAY_M}; margin-bottom: 20px; }}

    /* Divider */
    hr {{ border-color: {GRAY_L}; }}
</style>
""", unsafe_allow_html=True)


def kpi(label, value, sub="", tone=""):
    cls = {"pos":"pos","neg":"neg","warn":"warn","accent":"accent"}.get(tone,"")
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {cls}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def finding(text):
    st.markdown(f'<div class="finding"><strong>Key Finding &nbsp;—</strong> {text}</div>',
                unsafe_allow_html=True)

def warn(text):
    st.markdown(f'<div class="warn"><strong>⚠ Data Quality Issue &nbsp;—</strong> {text}</div>',
                unsafe_allow_html=True)

def chart_layout(fig, title="", height=320):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=GRAY_D), x=0),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=GRAY_M, size=11),
        height=height,
        margin=dict(t=40, b=40, l=40, r=20),
        xaxis=dict(gridcolor=GRAY_L, linecolor=GRAY_L, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRAY_L, linecolor=GRAY_L, tickfont=dict(size=10)),
        legend=dict(font=dict(size=11), bgcolor=WHITE,
                    bordercolor=GRAY_L, borderwidth=1),
    )
    return fig


@st.cache_data
def load_all():
    return {
        "tb":  run_sql_file("trial_balance.sql"),
        "pnl": run_sql_file("pnl_statement.sql"),
        "ar":  run_sql_file("ar_analysis.sql"),
        "ap":  run_sql_file("ap_analysis.sql"),
        "bv":  run_sql_file("budget_variance.sql"),
    }

data = load_all()
tb, pnl, ar, ap, bv = data["tb"], data["pnl"], data["ar"], data["ap"], data["bv"]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"<h2 style='color:{GRAY_D};font-weight:700;margin-bottom:4px'>GL Financial Analysis Suite</h2>",
            unsafe_allow_html=True)
st.markdown(f"<p style='color:{GRAY_M};font-size:13px;margin-bottom:24px'>"
            "Financial analysis built from General Ledger, AR, AP, and Budget data — "
            "simulating the core reporting a Data & Reporting Analyst delivers to SMB clients.</p>",
            unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Trial Balance",
    "P&L Statement",
    "AR Analysis",
    "AP Analysis",
    "Budget Variance",
])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — TRIAL BALANCE
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Trial Balance")
    st.markdown('<p class="section-desc">Debits and credits per account per currency. '
                'A balanced GL requires total debits = total credits per currency.</p>',
                unsafe_allow_html=True)

    currencies = ["All"] + sorted(tb["Currency"].unique().tolist())
    sel = st.selectbox("Currency", currencies, label_visibility="collapsed")
    tb_f = tb if sel == "All" else tb[tb["Currency"] == sel]

    imbalanced   = tb_f[tb_f["BalanceStatus"] == "IMBALANCED"]["Currency"].nunique()
    total_debit  = tb_f["TotalDebit"].sum()
    total_credit = tb_f["TotalCredit"].sum()

    c1, c2, c3 = st.columns(3)
    with c1: kpi("Total Debit",            f"${total_debit:,.0f}",  "Across selected currencies")
    with c2: kpi("Total Credit",           f"${total_credit:,.0f}", "Across selected currencies")
    with c3: kpi("Imbalanced Currencies",  str(imbalanced),
                 "Should be 0 for a clean GL", "neg" if imbalanced > 0 else "pos")

    fig = px.bar(tb_f, x="AccountName", y=["TotalDebit","TotalCredit"],
                 barmode="group", facet_col="Currency", facet_col_wrap=3,
                 color_discrete_map={"TotalDebit": SLATE, "TotalCredit": GREEN})
    chart_layout(fig, "Debit vs Credit by Account and Currency", height=360)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        tb_f.rename(columns={"AccountNumber":"Account No","AccountName":"Account",
                              "TotalDebit":"Total Debit","TotalCredit":"Total Credit",
                              "NetBalance":"Net Balance","TxnCount":"Transactions",
                              "BalanceStatus":"Status"}),
        use_container_width=True, hide_index=True
    )
    warn(f"All 5 currencies show IMBALANCED — total debits (${total_debit:,.0f}) ≠ "
         f"total credits (${total_credit:,.0f}). Asset and liability accounts (bank, equity) "
         "are missing from the dataset, causing the imbalance. In a complete double-entry system, "
         "every transaction must have equal debits and credits.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — P&L STATEMENT
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Profit & Loss Statement")
    st.markdown('<p class="section-desc">USD entries only. '
                'Revenue (4xxx) vs COGS (5000) vs Operating Expenses (5010, 6000).</p>',
                unsafe_allow_html=True)

    years  = sorted(pnl["Year"].unique().tolist())
    sel_yr = st.multiselect("Year", years, default=years, label_visibility="collapsed")
    pnl_f  = pnl[pnl["Year"].isin(sel_yr)]

    tot_rev = pnl_f["Revenue"].sum()
    tot_gp  = pnl_f["GrossProfit"].sum()
    tot_np  = pnl_f["NetProfit"].sum()
    avg_gm  = round(tot_gp / tot_rev * 100, 1) if tot_rev else 0
    avg_nm  = round(tot_np / tot_rev * 100, 1) if tot_rev else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Total Revenue",     f"${tot_rev:,.0f}",  "USD only",       "accent")
    with c2: kpi("Total Gross Profit",f"${tot_gp:,.0f}",   f"Margin {avg_gm}%")
    with c3: kpi("Total Net Profit",  f"${tot_np:,.0f}",   f"Margin {avg_nm}%",
                 "pos" if tot_np > 0 else "neg")
    with c4: kpi("Avg Gross Margin",  f"{avg_gm}%",        "Revenue − COGS")
    with c5: kpi("Avg Net Margin",    f"{avg_nm}%",        "After all expenses")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Gross Profit", x=pnl_f["YearMonth"],
                          y=pnl_f["GrossProfit"], marker_color=SLATE_XL,
                          marker_line_color=SLATE_L, marker_line_width=1))
    fig2.add_trace(go.Bar(name="OpEx", x=pnl_f["YearMonth"],
                          y=pnl_f["OpEx"], marker_color=GRAY_L,
                          marker_line_color="#C5C9D0", marker_line_width=1))
    fig2.add_trace(go.Scatter(name="Net Profit", x=pnl_f["YearMonth"],
                              y=pnl_f["NetProfit"], mode="lines+markers",
                              line=dict(color=SLATE, width=2),
                              marker=dict(size=4), yaxis="y2"))
    fig2.update_layout(
        barmode="stack", plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        title=dict(text="Monthly P&L — Gross Profit vs OpEx vs Net Profit",
                   font=dict(size=13, color=GRAY_D), x=0),
        height=340, margin=dict(t=40,b=50,l=40,r=40),
        xaxis=dict(tickangle=45, gridcolor=GRAY_L, linecolor=GRAY_L, tickfont=dict(size=9)),
        yaxis=dict(title="Amount (USD)", gridcolor=GRAY_L, linecolor=GRAY_L, tickfont=dict(size=10)),
        yaxis2=dict(title="Net Profit", overlaying="y", side="right",
                    gridcolor=GRAY_L, tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.08, font=dict(size=11),
                    bgcolor=WHITE, bordercolor=GRAY_L, borderwidth=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=pnl_f["YearMonth"], y=pnl_f["GrossMarginPct"],
                              name="Gross Margin %", line=dict(color=SLATE, width=2),
                              marker=dict(size=3)))
    fig3.add_trace(go.Scatter(x=pnl_f["YearMonth"], y=pnl_f["NetMarginPct"],
                              name="Net Margin %", line=dict(color=SLATE_L, width=2, dash="dot"),
                              marker=dict(size=3)))
    chart_layout(fig3, "Monthly Margin Trend (%)", height=280)
    fig3.update_layout(yaxis_title="Margin %", xaxis=dict(tickangle=45))
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(pnl_f.rename(columns={
        "YearMonth":"Month","GrossMarginPct":"Gross Margin %",
        "NetMarginPct":"Net Margin %","GrossProfit":"Gross Profit","NetProfit":"Net Profit"}),
        use_container_width=True, hide_index=True)

    finding(f"Average Gross Margin {avg_gm}% indicates healthy pricing relative to COGS. "
            f"Net Margin {avg_nm}% shows operating expenses are well-controlled. "
            "Months with negative net profit should be investigated for unusual OpEx spikes.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — AR ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Accounts Receivable Analysis")
    st.markdown('<p class="section-desc">Customer exposure by status (Open, Partial, Received) '
                'with estimated DSO.</p>', unsafe_allow_html=True)

    total_billed    = ar["TotalBilled"].sum()
    total_open      = ar["OpenAmount"].sum()
    total_partial   = ar["PartialAmount"].sum()
    total_collected = ar["CollectedAmount"].sum()
    collection_rate = round(total_collected / total_billed * 100, 1) if total_billed else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Total Billed",    f"${total_billed:,.0f}",  "All invoices")
    with c2: kpi("Open AR",         f"${total_open:,.0f}",    "Unpaid invoices",  "neg")
    with c3: kpi("Partial AR",      f"${total_partial:,.0f}", "Partially paid",   "warn")
    with c4: kpi("Collection Rate", f"{collection_rate}%",    "Fully received",   "pos")

    col_l, col_r = st.columns(2)
    with col_l:
        fig4 = px.bar(ar.sort_values("OpenAmount", ascending=False),
                      x="Customer", y=["OpenAmount","PartialAmount","CollectedAmount"],
                      barmode="stack",
                      color_discrete_map={"OpenAmount": RED,
                                          "PartialAmount": ORANGE,
                                          "CollectedAmount": GREEN})
        chart_layout(fig4, "AR Exposure by Customer")
        fig4.update_traces(marker_line_width=0)
        fig4.update_layout(yaxis_title="Amount", legend_title="Status")
        st.plotly_chart(fig4, use_container_width=True)

    with col_r:
        fig5 = px.bar(ar.sort_values("EstimatedDSO", ascending=False),
                      x="Customer", y="EstimatedDSO",
                      color_discrete_sequence=[SLATE])
        chart_layout(fig5, "Estimated DSO by Customer (days)")
        fig5.update_traces(marker_line_width=0)
        fig5.update_layout(yaxis_title="DSO (days)", showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    st.dataframe(ar.rename(columns={
        "TotalInvoices":"Invoices","TotalBilled":"Total Billed",
        "OpenAmount":"Open","PartialAmount":"Partial","CollectedAmount":"Collected",
        "OpenCount":"Open Inv","PartialCount":"Partial Inv",
        "EstimatedDSO":"Est. DSO","OpenPct":"Open %"}),
        use_container_width=True, hide_index=True)

    finding(f"Total open AR of ${total_open:,.0f} across {ar['OpenCount'].sum()} invoices. "
            f"Partial payments total ${total_partial:,.0f} — these require follow-up to collect the remaining balance. "
            f"Collection rate of {collection_rate}% indicates "
            f"{'healthy' if collection_rate > 30 else 'low'} receivables performance. "
            "DSO estimates are based on Net 45 payment terms.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — AP ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Accounts Payable Analysis")
    st.markdown('<p class="section-desc">Vendor obligations by status (Open, Partial, Paid) '
                'with estimated DPO.</p>', unsafe_allow_html=True)

    total_ap      = ap["TotalAmount"].sum()
    total_ap_open = ap["OpenAmount"].sum()
    total_ap_part = ap["PartialAmount"].sum()
    total_ap_paid = ap["PaidAmount"].sum()
    payment_rate  = round(total_ap_paid / total_ap * 100, 1) if total_ap else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Total AP",       f"${total_ap:,.0f}",      "All vendor invoices")
    with c2: kpi("Open Payables",  f"${total_ap_open:,.0f}", "Unpaid obligations",  "neg")
    with c3: kpi("Partial Paid",   f"${total_ap_part:,.0f}", "Partially settled",   "warn")
    with c4: kpi("Payment Rate",   f"{payment_rate}%",       "Fully paid",          "pos")

    col_l, col_r = st.columns(2)
    with col_l:
        fig6 = px.bar(ap.sort_values("OpenAmount", ascending=False),
                      x="Vendor", y=["OpenAmount","PartialAmount","PaidAmount"],
                      barmode="stack",
                      color_discrete_map={"OpenAmount": RED,
                                          "PartialAmount": ORANGE,
                                          "PaidAmount": GREEN})
        chart_layout(fig6, "AP Exposure by Vendor")
        fig6.update_traces(marker_line_width=0)
        fig6.update_layout(yaxis_title="Amount", legend_title="Status")
        st.plotly_chart(fig6, use_container_width=True)

    with col_r:
        fig7 = px.bar(ap.sort_values("EstimatedDPO", ascending=False),
                      x="Vendor", y="EstimatedDPO",
                      color_discrete_sequence=[SLATE_L])
        chart_layout(fig7, "Estimated DPO by Vendor (days)")
        fig7.update_traces(marker_line_width=0)
        fig7.update_layout(yaxis_title="DPO (days)", showlegend=False)
        st.plotly_chart(fig7, use_container_width=True)

    st.dataframe(ap.rename(columns={
        "TotalInvoices":"Invoices","TotalAmount":"Total",
        "OpenAmount":"Open","PartialAmount":"Partial","PaidAmount":"Paid",
        "OpenCount":"Open Inv","PartialCount":"Partial Inv","PaidCount":"Paid Inv",
        "EstimatedDPO":"Est. DPO","UnpaidPct":"Unpaid %"}),
        use_container_width=True, hide_index=True)

    finding(f"Open AP of ${total_ap_open:,.0f} represents obligations that must be settled. "
            f"Payment rate of {payment_rate}% means {100-payment_rate:.0f}% of vendor invoices "
            "remain open or partial. High partial payment rates may indicate cash flow constraints "
            "or disputed invoices.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — BUDGET VARIANCE
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### Budget Variance Analysis")
    st.markdown('<p class="section-desc">Budget vs Forecast vs Actual per department and quarter. '
                'Risk: HIGH &gt;10%, MEDIUM &gt;5%.</p>', unsafe_allow_html=True)

    years = sorted(bv["FiscalYear"].unique().tolist())
    sel_y = st.selectbox("Fiscal Year", years, label_visibility="collapsed")
    bv_f  = bv[bv["FiscalYear"] == sel_y]

    dept_summary = bv_f.groupby("Dept").agg(
        Budget=("BudgetUSD","sum"),
        Actual=("ActualUSD","sum"),
        Variance=("VarianceUSD","sum")
    ).reset_index()
    dept_summary["VariancePct"] = round(
        dept_summary["Variance"] / dept_summary["Budget"] * 100, 1)

    total_budget   = bv_f["BudgetUSD"].sum()
    total_actual   = bv_f["ActualUSD"].sum()
    total_variance = bv_f["VarianceUSD"].sum()
    high_risk      = bv_f[bv_f["RiskFlag"] == "HIGH"].shape[0]

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Total Budget",        f"${total_budget:,.0f}",   f"FY{sel_y}")
    with c2: kpi("Total Actual",        f"${total_actual:,.0f}",   f"FY{sel_y}")
    with c3: kpi("Total Variance",      f"${total_variance:,.0f}",
                 "Positive = over budget",
                 "neg" if total_variance > 0 else "pos")
    with c4: kpi("High Risk Quarters",  str(high_risk),
                 "Variance > 10%",
                 "neg" if high_risk > 0 else "pos")

    col_l, col_r = st.columns(2)
    with col_l:
        fig8 = go.Figure(go.Bar(
            x=dept_summary["Dept"],
            y=dept_summary["Variance"],
            marker_color=[RED if v > 0 else GREEN for v in dept_summary["Variance"]],
            marker_line_width=0,
            text=[f"${v:,.0f}" for v in dept_summary["Variance"]],
            textposition="outside", textfont=dict(size=10, color=GRAY_M)
        ))
        chart_layout(fig8, f"FY{sel_y} — Variance by Department")
        fig8.update_layout(yaxis_title="Variance (USD)")
        st.plotly_chart(fig8, use_container_width=True)

    with col_r:
        fig9 = go.Figure()
        fig9.add_trace(go.Bar(name="Budget", x=dept_summary["Dept"],
                              y=dept_summary["Budget"],
                              marker_color=SLATE_XL,
                              marker_line_color=SLATE_L, marker_line_width=1))
        fig9.add_trace(go.Bar(name="Actual", x=dept_summary["Dept"],
                              y=dept_summary["Actual"],
                              marker_color=SLATE,
                              marker_line_width=0))
        chart_layout(fig9, f"FY{sel_y} — Budget vs Actual")
        fig9.update_layout(barmode="group", yaxis_title="Amount (USD)")
        st.plotly_chart(fig9, use_container_width=True)

    st.dataframe(
        bv_f[["FiscalYear","Dept","Quarter","BudgetUSD","ForecastUSD","ActualUSD",
              "VarianceUSD","VariancePct","BudgetStatus","RiskFlag"]].rename(columns={
            "FiscalYear":"Year","BudgetUSD":"Budget","ForecastUSD":"Forecast",
            "ActualUSD":"Actual","VarianceUSD":"Variance","VariancePct":"Variance %",
            "BudgetStatus":"Status","RiskFlag":"Risk"}),
        use_container_width=True, hide_index=True
    )

    over  = bv_f[bv_f["BudgetStatus"]=="Over Budget"]["Dept"].unique().tolist()
    under = bv_f[bv_f["BudgetStatus"]=="Under Budget"]["Dept"].unique().tolist()
    finding(f"Departments over budget in FY{sel_y}: {', '.join(over) if over else 'None'}. "
            f"Under budget: {', '.join(under) if under else 'None'}. "
            f"{high_risk} quarter(s) flagged as HIGH risk (variance >10%). "
            "Budget vs Actual comparison helps management identify where spending controls need tightening.")


st.divider()
st.markdown(
    f"<p style='font-size:11px;color:{GRAY_M};text-align:center'>"
    "Built by Dia Kurnia Dewi &nbsp;·&nbsp; "
    "Dataset: Excelx.com Finance & Accounting Sample Data &nbsp;·&nbsp; "
    "Stack: Python · SQLite · Streamlit · Plotly</p>",
    unsafe_allow_html=True
)
