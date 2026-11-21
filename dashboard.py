"""Interactive Online Retail explorer. Run: python -m streamlit run dashboard.py"""
from resources import ensure_assets
ensure_assets()

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from main import load_data, clean_data, summarize

st.set_page_config(page_title='Retail Intelligence', page_icon='📊', layout='wide')
from design import setup, header, metrics, section, insight
setup('retail')
header('retail')

@st.cache_data
def prepared():
    raw = load_data()
    return clean_data(raw), {'Raw lines': len(raw), 'Exact duplicates': int(raw.duplicated().sum()), 'Missing customer IDs': int(raw.CustomerID.isna().sum()), 'Nonpositive prices': int(raw.UnitPrice.le(0).sum())}

frame, audit = prepared()
st.sidebar.header('Transaction filters')
period = st.sidebar.date_input('Invoice date range', value=(frame.InvoiceDate.min().date(), frame.InvoiceDate.max().date()), min_value=frame.InvoiceDate.min().date(), max_value=frame.InvoiceDate.max().date())
countries = st.sidebar.multiselect('Countries (empty = all)', sorted(frame.Country.unique()))
query = st.sidebar.text_input('Product description contains')
exclude_uk = st.sidebar.checkbox('Exclude United Kingdom', value=False)
if len(period) != 2:
    st.info('Choose both the start and end date.')
    st.stop()
start, end = period
view = frame.loc[frame.InvoiceDate.ge(pd.Timestamp(start)) & frame.InvoiceDate.lt(pd.Timestamp(end) + pd.Timedelta(days=1))].copy()
if countries:
    view = view.loc[view.Country.isin(countries)]
if exclude_uk:
    view = view.loc[view.Country != 'United Kingdom']
if query:
    view = view.loc[view.Description.str.contains(query, case=False, regex=False)]
if view.empty:
    st.warning('No records match these filters. Broaden the dates, countries or product query.')
    st.stop()
st.caption(f'{len(view):,} line items in view · {start} to {end} · Filters apply to every tab')
m = summarize(view)
metrics(['Gross sales', 'Credits / returns', 'Net sales', 'Sales invoices', 'Gross AOV'],
        [f'£{m["gross_sales_gbp"]/1_000_000:.2f}M', f'£{m["returns_gbp"]/1_000:.2f}K', f'£{m["net_sales_gbp"]/1_000_000:.2f}M', f'{m["sales_invoices"]:,}', f'£{m["gross_aov_gbp"]:,.2f}'],
        ['trend','return','wallet','bag','target'])
st.caption(f"Exact values: gross £{m['gross_sales_gbp']:,.2f} · credits £{m['returns_gbp']:,.2f} · net £{m['net_sales_gbp']:,.2f}")
if start.year <= 2011 <= end.year and end >= pd.Timestamp('2011-12-01').date():
    insight('Reading the trend: December 2011 ends on the 9th. Its lower total does not establish a sales decline versus a full month.')
overview, catalog, customers, quality = st.tabs(['◈  Sales overview', '▦  Products & geography', '◎  Customer segments', '◇  Data & methods'])
with overview:
    section("Revenue performance", "trend")
    monthly = view.groupby('month')[['sales_value_gbp', 'return_value_gbp', 'net_value_gbp']].sum().reset_index()
    monthly = monthly.rename(columns={'sales_value_gbp':'Gross sales','return_value_gbp':'Credits','net_value_gbp':'Net sales'})
    st.plotly_chart(px.line(monthly, x='month', y=['Gross sales', 'Credits', 'Net sales'], markers=True, title='Monthly sales and credits', labels={'value':'GBP', 'month':'Month', 'variable':'Measure'}), width='stretch',theme=None)
    left, right = st.columns(2)
    daily = view.groupby(view.InvoiceDate.dt.day_name()).net_value_gbp.sum().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']).fillna(0).rename_axis('Day').reset_index()
    left.plotly_chart(px.bar(daily, x='Day', y='net_value_gbp', title='Net sales by weekday', labels={'net_value_gbp':'GBP'}), width='stretch',theme=None)
    orders = view.loc[~view.is_return].groupby('InvoiceNo').sales_value_gbp.sum().rename('basket_gbp').reset_index()
    right.plotly_chart(px.histogram(orders, x='basket_gbp', nbins=60, log_y=True, title='Basket values (log count axis)', labels={'basket_gbp':'Gross invoice value, GBP'}), width='stretch',theme=None)
    st.caption('For product-filtered views, AOV is matching sales value per matching invoice, not the full basket value.')
with catalog:
    section("Product & market mix", "globe")
    top_n = st.slider('Top N', 5, 25, 10)
    metric = st.selectbox('Rank by', ['net_value_gbp','sales_value_gbp','return_value_gbp'], format_func=lambda v: {'net_value_gbp':'Net sales · GBP','sales_value_gbp':'Gross sales · GBP','return_value_gbp':'Credits / returns · GBP'}[v])
    products = view.groupby(['StockCode','Description'])[metric].sum().nlargest(top_n).sort_values().reset_index()
    products['label'] = products.Description.str.slice(0,45) + ' [' + products.StockCode + ']'
    st.plotly_chart(px.bar(products, x=metric, y='label', orientation='h', title=f'Top {top_n} products', height=max(400,top_n*28), labels={'label':'Product',metric:'GBP'}), width='stretch',theme=None)
    geo = view.groupby('Country')[metric].sum().nlargest(top_n).sort_values().reset_index()
    st.plotly_chart(px.bar(geo, x=metric, y='Country', orientation='h', title='Country contribution', labels={metric:'GBP'}), width='stretch',theme=None)
with customers:
    section("Customer behavior", "target")
    known = view.loc[view.CustomerID.notna() & ~view.is_return]
    st.caption('RFM-style summary uses identified customers and positive sales only. It does not include anonymous shoppers or subtract returns. Recency is relative to the selected end date.')
    if known.empty:
        st.info('No identified customers have positive sales under these filters.')
    else:
        rfm = known.groupby('CustomerID').agg(last_purchase=('InvoiceDate','max'), frequency=('InvoiceNo','nunique'), monetary_gbp=('sales_value_gbp','sum'))
        rfm['recency_days'] = (pd.Timestamp(end).normalize() + pd.Timedelta(days=1) - rfm.last_purchase.dt.normalize()).dt.days
        rfm['segment'] = 'Occasional'
        rfm.loc[rfm.frequency >= 3, 'segment'] = 'Repeat (3+ invoices)'
        rfm.loc[(rfm.frequency >= 3) & (rfm.recency_days <= 30), 'segment'] = 'Recent repeat'
        chart = rfm.reset_index()
        st.plotly_chart(px.scatter(chart, x='frequency', y='monetary_gbp', color='segment', log_x=True, log_y=True, hover_data=['CustomerID','recency_days'], title='Frequency vs spend, log axes'), width='stretch',theme=None)
        st.dataframe(chart.sort_values('monetary_gbp', ascending=False), hide_index=True)
        st.download_button('Download customer summary', chart.to_csv(index=False), 'customer_segments.csv', 'text/csv')
with quality:
    section("Trust the numbers", "shield")
    st.json(audit)
    st.markdown('''**Cleaning policy:** remove exact duplicate rows; exclude nonpositive prices and zero quantities. Credit invoices (C-prefix) or negative quantities count as credits, not positive sales. Retain missing customer IDs in sales totals. Gross AOV uses positive-sales invoices. Net sales = gross sales minus credit magnitude. No cost data means **no profit claim**. Duplicate removal is an assumption, not a proven correction. See README and source attribution.''')
    st.dataframe(view.head(1000), hide_index=True)
    st.download_button('Download all filtered line items', view.to_csv(index=False).encode('utf-8'), 'filtered_retail.csv', 'text/csv')
    st.markdown('Source: [Chen (2015), UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online). Historical data, December 2010 to December 2011.')
st.caption('Portfolio learning project · Plotly hover, zoom and chart image downloads are enabled · Runs on your local machine by default.')
