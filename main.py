"""Analyze real UCI Online Retail line items; report sales and returns separately."""
from pathlib import Path
import json
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
OUT = BASE / 'outputs'


def load_data():
    return pd.read_csv(BASE / 'data' / 'online_retail.csv.gz', dtype={'InvoiceNo': str, 'StockCode': str, 'CustomerID': str}, parse_dates=['InvoiceDate'])


def clean_data(raw):
    """Conservative policy: exact duplicate lines removed; no invoice-level dedupe."""
    frame = raw.drop_duplicates().copy()
    # Nonpositive prices are free items or adjustments, excluded from this sales view.
    frame = frame.loc[frame.UnitPrice.gt(0) & frame.Quantity.ne(0)].copy()
    frame['Description'] = frame.Description.fillna('Unknown product')
    frame['Country'] = frame.Country.fillna('Unknown country')
    frame['line_value_gbp'] = frame.Quantity * frame.UnitPrice
    # Cancellations and negative quantities are counted as return/credit lines.
    frame['is_return'] = frame.InvoiceNo.str.upper().str.startswith('C') | frame.Quantity.lt(0)
    # Rare positive cancellation lines are treated as credit magnitude, not sales.
    frame['return_value_gbp'] = np.where(frame.is_return, frame.line_value_gbp.abs(), 0.)
    frame['sales_value_gbp'] = np.where(~frame.is_return & frame.Quantity.gt(0), frame.line_value_gbp, 0.)
    frame['net_value_gbp'] = frame.sales_value_gbp - frame.return_value_gbp
    frame['month'] = frame.InvoiceDate.dt.to_period('M').astype(str)
    return frame


def summarize(frame):
    sales = frame.loc[~frame.is_return]
    gross = float(frame.sales_value_gbp.sum())
    returns = float(frame.return_value_gbp.sum())
    orders = int(sales.InvoiceNo.nunique())
    return {'included_lines': len(frame), 'sales_invoices': orders,
            'identified_customers': int(frame.CustomerID.nunique()),
            'gross_sales_gbp': round(gross, 2), 'returns_gbp': round(returns, 2),
            'net_sales_gbp': round(gross - returns, 2),
            'gross_aov_gbp': round(gross / orders, 2) if orders else 0,
            'credit_value_as_pct_of_gross_sales': round(returns / gross * 100, 2) if gross else 0}


def main():
    OUT.mkdir(exist_ok=True)
    raw = load_data()
    frame = clean_data(raw)
    result = summarize(frame)
    result.update(raw_lines=len(raw), exact_duplicates_removed=int(raw.duplicated().sum()),
                  nonpositive_price_or_zero_quantity_excluded=int(((raw.drop_duplicates().UnitPrice <= 0) | (raw.drop_duplicates().Quantity == 0)).sum()),
                  missing_customer_lines=int(frame.CustomerID.isna().sum()),
                  first_timestamp=str(frame.InvoiceDate.min()), last_timestamp=str(frame.InvoiceDate.max()))
    value_cols = ['sales_value_gbp', 'return_value_gbp', 'net_value_gbp']
    monthly = frame.groupby('month')[value_cols].sum()
    countries = frame.groupby('Country')[value_cols].sum().sort_values('net_value_gbp', ascending=False)
    products = frame.groupby('StockCode').agg(description=('Description', 'first'), net_sales_gbp=('net_value_gbp', 'sum'), gross_sales_gbp=('sales_value_gbp', 'sum'), return_value_gbp=('return_value_gbp', 'sum'))
    for name, table in [('monthly', monthly), ('countries', countries), ('products', products)]:
        table.to_csv(OUT / f'{name}.csv')
    # SQL/pandas cross-check of real net line-value aggregation.
    with sqlite3.connect(':memory:') as con:
        frame[['Country', 'net_value_gbp']].to_sql('retail', con, index=False)
        sql_result = pd.read_sql_query((BASE / 'analysis.sql').read_text(), con).set_index('Country')
    assert np.allclose(sql_result.sort_index().net_sales_gbp, countries.sort_index().net_value_gbp)
    assert np.isclose(result['net_sales_gbp'], result['gross_sales_gbp'] - result['returns_gbp'])
    (OUT / 'results.json').write_text(json.dumps(result, indent=2))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    monthly.rename(columns={'sales_value_gbp': 'Gross sales', 'return_value_gbp': 'Credits', 'net_value_gbp': 'Net sales'}).plot(ax=axes[0], color=['#176b87', '#df8f2d', '#5c9768'], marker='o')
    axes[0].set(title='Monthly transaction value', ylabel='GBP', xlabel='Month (Dec 2011 is partial)')
    axes[0].tick_params(axis='x', rotation=45)
    countries.head(8).net_value_gbp.sort_values().plot.barh(ax=axes[1], color='#176b87')
    axes[1].set(title='Top countries by net sales', xlabel='GBP', ylabel='')
    fig.tight_layout()
    fig.savefig(OUT / 'sales_dashboard.png', dpi=150)
    plt.close(fig)
    (OUT / 'report.md').write_text(f'''# Online Retail findings

- Raw lines: {len(raw):,}; analyzed lines: {len(frame):,}.
- Gross sales: GBP {result['gross_sales_gbp']:,.2f}; credits: GBP {result['returns_gbp']:,.2f}.
- Net sales: GBP {result['net_sales_gbp']:,.2f} across {result['sales_invoices']:,} sales invoices.
- Gross average order value: GBP {result['gross_aov_gbp']:,.2f}.
- Top net-sales country: {countries.index[0]}.

These are transaction values, not profit: there is no cost-of-goods data.
Credits in this date window can relate to earlier purchases, so credits divided by sales
is a value ratio, not an order-return probability. Missing CustomerID does not mean zero sales;
those lines remain in revenue totals and are excluded only from customer-specific analysis.
Exact duplicate lines are removed under a stated ingestion-cleaning assumption, although
some identical lines could be legitimate repeated purchases. No invoice-level deduplication.
The final month ends on 9 December 2011, so it is not comparable with a full month.
Data are historical UK transactions in GBP, not current Egyptian market data.

![Transaction overview](sales_dashboard.png)
''')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
