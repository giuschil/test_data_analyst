import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -- Prima brand colors --
PURPLE_DARK = '#4A1D8A'
PURPLE_MAIN = '#6B21A8'
PURPLE_MID = '#7C3AED'
PURPLE_LIGHT = '#A78BFA'
PURPLE_PALE = '#EDE9FE'
GRAY_TEXT = '#4B5563'
GRAY_LIGHT = '#F9FAFB'

# -- page config --
st.set_page_config(page_title="Insurance Data Analysis", page_icon="📊", layout="wide")

# -- custom CSS --
st.markdown(f"""
<style>
    .stApp {{ background-color: {GRAY_LIGHT}; }}
    [data-testid="stSidebar"] {{
        background-color: #F9FAFB;
        border-right: 2px solid {PURPLE_MAIN};
    }}
    [data-testid="stSidebar"] * {{ color: {PURPLE_DARK} !important; }}
    .stMetric {{
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 4px solid {PURPLE_MAIN};
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    h1, h2, h3 {{ color: {PURPLE_DARK} !important; }}
    .answer-box {{
        background-color: {PURPLE_PALE}; border-left: 4px solid {PURPLE_MAIN};
        padding: 12px 18px; border-radius: 6px; margin: 10px 0; color: {GRAY_TEXT};
    }}
</style>
""", unsafe_allow_html=True)


# -- password gate --
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown(f"""
        <div style="display:flex;justify-content:center;align-items:center;height:60vh;flex-direction:column;">
            <h1 style="color:{PURPLE_MAIN};">Insurance Data Analysis</h1>
            <p style="color:{GRAY_TEXT};">Enter the password to access the dashboard</p>
        </div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            pwd = st.text_input("Password", type="password",
                                label_visibility="collapsed", placeholder="Enter password")
            if pwd:
                if pwd == st.secrets["password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong password")
        st.stop()

check_password()


# -- load data --
@st.cache_data
def load_data():
    quotes = pd.read_csv('data/quotes.csv')
    vehicles = pd.read_csv('data/vehicles.csv')
    prices = pd.read_csv('data/prices.csv')
    policies = pd.read_csv('data/policies.csv')
    quotes['date'] = pd.to_datetime(quotes['date'])
    policies['date'] = pd.to_datetime(policies['date'])
    prices_clean = prices.drop_duplicates()
    prices_clean = prices_clean[prices_clean['premium'].notna()]
    prices_clean = prices_clean[prices_clean['product_type'] != 'none']
    return quotes, vehicles, prices, prices_clean, policies

quotes, vehicles, prices_raw, prices, policies = load_data()
pol_pr = policies.merge(prices, left_on='price_id', right_on='id', suffixes=('_pol', '_pr'))


def styled_fig(fig, height=420):
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', color=GRAY_TEXT),
        title_font=dict(color=PURPLE_DARK, size=16),
        height=height, margin=dict(t=50, b=40, l=50, r=30),
        legend=dict(bgcolor='rgba(255,255,255,0.8)')
    )
    fig.update_xaxes(gridcolor='#F3F4F6', linecolor='#E5E7EB')
    fig.update_yaxes(gridcolor='#F3F4F6', linecolor='#E5E7EB')
    return fig

COLORS_3 = [PURPLE_MAIN, '#EC4899', '#F59E0B']

# -- sidebar --
st.sidebar.image('logo.jpg', width=160)
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Analyst Test**")
st.sidebar.markdown("Giuseppe Schillaci")
st.sidebar.markdown("---")
section = st.sidebar.radio("Navigate", [
    "Overview", "Q0 - Data Quality", "Q1 - Most Quoted Vehicles",
    "Q2 - Average Premium", "Q3 - Cart Size", "Q4 - Customer Growth",
    "Q5 - Net Revenue", "Q6 - Conversion Rate", "Q7 - Cross-sell",
    "Q8 - Purchase Timing"
])


# ============================================================
if section == "Overview":
    st.title("Insurance Data Analysis")
    st.markdown("Interactive dashboard for the motor insurance data analyst test.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quotes", f"{len(quotes):,}")
    c2.metric("Vehicles", f"{len(vehicles):,}")
    c3.metric("Price Records", f"{len(prices):,}")
    c4.metric("Policies Sold", f"{len(policies):,}")
    st.markdown("---")

    monthly_q = quotes.groupby(quotes['date'].dt.to_period('M')).size().reset_index(name='count')
    monthly_q['date'] = monthly_q['date'].astype(str)
    fig = px.bar(monthly_q, x='date', y='count', color_discrete_sequence=[PURPLE_MAIN])
    fig.update_layout(xaxis_title='Month', yaxis_title='Quotes')
    st.plotly_chart(styled_fig(fig, 350), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        vtype = vehicles['vehicle_type'].value_counts()
        fig = px.pie(values=vtype.values, names=vtype.index, title='Vehicle Type',
                     color_discrete_sequence=COLORS_3)
        st.plotly_chart(styled_fig(fig, 320), use_container_width=True)
    with col2:
        city = vehicles['city'].value_counts()
        fig = px.pie(values=city.values, names=city.index, title='Registration City',
                     color_discrete_sequence=[PURPLE_DARK, PURPLE_MAIN, PURPLE_MID, PURPLE_LIGHT])
        st.plotly_chart(styled_fig(fig, 320), use_container_width=True)


# ============================================================
elif section == "Q0 - Data Quality":
    st.title("Q0 — Data Quality Check")
    st.markdown("**Which table contains data with issues?**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate Rows", 88)
    c2.metric("Null Premiums", 42)
    c3.metric("Invalid product_type", 13)
    st.markdown(f"""<div class="answer-box">
        <strong>Answer:</strong> The <strong>PRICES</strong> table has 3 issues:<br>
        1. 88 fully duplicated rows<br>2. 42 rows with null premium<br>
        3. 13 rows with product_type = 'none'<br><br>
        Clean dataset: <strong>{len(prices):,}</strong> rows (removed {len(prices_raw)-len(prices)}).
    </div>""", unsafe_allow_html=True)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Before Cleaning", "After Cleaning"))
    before = prices_raw['product_type'].value_counts()
    after = prices['product_type'].value_counts()
    fig.add_trace(go.Bar(x=before.index, y=before.values, marker_color=PURPLE_LIGHT), row=1, col=1)
    fig.add_trace(go.Bar(x=after.index, y=after.values, marker_color=PURPLE_MAIN), row=1, col=2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(styled_fig(fig, 350), use_container_width=True)


# ============================================================
elif section == "Q1 - Most Quoted Vehicles":
    st.title("Q1 — Most Quoted Vehicles in H2 2021")
    h2 = quotes[(quotes['date'] >= '2021-07-01') & (quotes['date'] <= '2021-12-31')]
    top_vid = h2['vehicle_id'].value_counts().head(1)
    h2_v = h2.merge(vehicles, left_on='vehicle_id', right_on='id', suffixes=('', '_v'))
    top_vtype = h2_v['vehicle_type'].value_counts()

    c1, c2 = st.columns(2)
    c1.metric("Most Quoted vehicle_id", f"{top_vid.index[0]}", f"{top_vid.values[0]} quotes")
    c2.metric("Most Quoted vehicle_type", top_vtype.index[0], f"{top_vtype.values[0]:,} quotes")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(values=top_vtype.values, names=top_vtype.index,
                     title='Vehicle Type — H2 2021', color_discrete_sequence=COLORS_3)
        st.plotly_chart(styled_fig(fig, 350), use_container_width=True)
    with col2:
        top10 = h2['vehicle_id'].value_counts().head(10).reset_index()
        top10.columns = ['vehicle_id', 'quotes']
        top10['vehicle_id'] = top10['vehicle_id'].astype(str)
        fig = px.bar(top10, x='vehicle_id', y='quotes', title='Top 10 vehicle_id',
                     color_discrete_sequence=[PURPLE_MID])
        st.plotly_chart(styled_fig(fig, 350), use_container_width=True)


# ============================================================
elif section == "Q2 - Average Premium":
    st.title("Q2 — Average Total Premium")
    st.markdown("Total premium = sum of all product premiums within a single quote.")
    premium_per_quote = prices.groupby('quote_id')['premium'].sum()
    avg = premium_per_quote.mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("Average", f"{avg:.2f} EUR")
    c2.metric("Median", f"{premium_per_quote.median():.2f} EUR")
    c3.metric("Std Dev", f"{premium_per_quote.std():.2f} EUR")
    fig = px.histogram(premium_per_quote, nbins=60, title='Premium Distribution',
                       color_discrete_sequence=[PURPLE_MAIN])
    fig.update_layout(xaxis_title='Total Premium (EUR)', yaxis_title='Count')
    st.plotly_chart(styled_fig(fig), use_container_width=True)


# ============================================================
elif section == "Q3 - Cart Size":
    st.title("Q3 — Average Cart Size")
    cart = pol_pr.groupby('quote_id')['product_type'].count()
    avg_cart = cart.mean()
    c1, c2 = st.columns(2)
    c1.metric("Average Cart Size", f"{avg_cart:.2f} products")
    c2.metric("Total Purchasing Quotes", f"{len(cart):,}")
    cart_dist = cart.value_counts().sort_index().reset_index()
    cart_dist.columns = ['products', 'count']
    fig = px.bar(cart_dist, x='products', y='count', title='Cart Size Distribution',
                 color_discrete_sequence=[PURPLE_MAIN])
    fig.update_layout(xaxis_title='# Products', yaxis_title='# Quotes')
    st.plotly_chart(styled_fig(fig, 350), use_container_width=True)


# ============================================================
elif section == "Q4 - Customer Growth":
    st.title("Q4 — Monthly Unique Quoting Customers")
    monthly = quotes.groupby(quotes['date'].dt.to_period('M'))['email'].nunique().reset_index()
    monthly.columns = ['month', 'unique_customers']
    monthly['change'] = monthly['unique_customers'].diff()
    monthly['month'] = monthly['month'].astype(str)
    best = monthly.loc[monthly['change'].idxmax()]
    st.metric("Highest MoM Increase", str(best['month']), f"+{int(best['change'])} customers")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=monthly['month'], y=monthly['unique_customers'],
                         name='Unique Customers', marker_color=PURPLE_MAIN, opacity=0.7),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly['month'], y=monthly['change'],
                             name='MoM Change', line=dict(color='#EC4899', width=2.5),
                             mode='lines+markers'), secondary_y=True)
    fig.update_yaxes(title_text='Unique Customers', secondary_y=False)
    fig.update_yaxes(title_text='MoM Change', secondary_y=True)
    st.plotly_chart(styled_fig(fig), use_container_width=True)
    st.dataframe(monthly, use_container_width=True)


# ============================================================
elif section == "Q5 - Net Revenue":
    st.title("Q5 — Net Revenue by City and Product Type")
    rev = pol_pr.merge(quotes[['id', 'vehicle_id']], left_on='quote_id',
                       right_on='id', suffixes=('', '_q'))
    rev = rev.merge(vehicles, left_on='vehicle_id', right_on='id', suffixes=('', '_v'))
    rev['net_revenue'] = rev['premium'] - rev['taxes']
    st.metric("Grand Total", f"{rev['net_revenue'].sum():,.2f} EUR")

    pivot = rev.groupby(['city', 'product_type'])['net_revenue'].sum().reset_index()
    fig = px.bar(pivot, x='city', y='net_revenue', color='product_type',
                 barmode='group', color_discrete_sequence=COLORS_3)
    fig.update_layout(yaxis_title='Net Revenue (EUR)')
    st.plotly_chart(styled_fig(fig), use_container_width=True)

    table = rev.groupby(['city', 'product_type'])['net_revenue'].sum().unstack().round(2)
    table['Total'] = table.sum(axis=1)
    st.dataframe(table.style.format("{:,.2f}"), use_container_width=True)


# ============================================================
elif section == "Q6 - Conversion Rate":
    st.title("Q6 — Conversion Rate by Product Type")
    quoted = prices.groupby('product_type').size()
    purchased = pol_pr.groupby('product_type').size()
    conv = pd.DataFrame({'quoted': quoted, 'purchased': purchased})
    conv['conversion_%'] = (conv['purchased'] / conv['quoted'] * 100).round(2)
    best_conv = conv['conversion_%'].idxmax()
    st.metric("Highest Conversion", best_conv, f"{conv.loc[best_conv, 'conversion_%']}%")

    fig = px.bar(conv.reset_index(), x='product_type', y='conversion_%',
                 color='product_type', text='conversion_%', color_discrete_sequence=COLORS_3)
    fig.update_layout(yaxis_title='Conversion %', showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(styled_fig(fig, 380), use_container_width=True)
    st.dataframe(conv, use_container_width=True)


# ============================================================
elif section == "Q7 - Cross-sell":
    st.title("Q7 — Cross-sell Among Full Product Buyers")
    full_quotes = set(pol_pr[pol_pr['product_type'] == 'full']['quote_id'])
    n_full = len(full_quotes)
    also_legal = pol_pr[(pol_pr['product_type'] == 'legal') & (pol_pr['quote_id'].isin(full_quotes))]
    also_break = pol_pr[(pol_pr['product_type'] == 'breakdown') & (pol_pr['quote_id'].isin(full_quotes))]
    pct_legal = len(also_legal['quote_id'].unique()) / n_full * 100
    pct_break = len(also_break['quote_id'].unique()) / n_full * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Full Buyers", f"{n_full:,}")
    c2.metric("Also Bought Legal", f"{pct_legal:.1f}%")
    c3.metric("Also Bought Breakdown", f"{pct_break:.1f}%")

    cross = pd.DataFrame({'product': ['Legal', 'Breakdown'], 'percentage': [pct_legal, pct_break]})
    fig = px.bar(cross, x='percentage', y='product', orientation='h',
                 text='percentage', color_discrete_sequence=[PURPLE_MAIN])
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_title='% of Full Buyers', yaxis_title='', xaxis_range=[0, 100])
    st.plotly_chart(styled_fig(fig, 300), use_container_width=True)


# ============================================================
elif section == "Q8 - Purchase Timing":
    st.title("Q8 — Purchase Timing Analysis")

    pq = policies.merge(prices[['id', 'quote_id']],
                        left_on='price_id', right_on='id', suffixes=('_pol', '_pr'))
    pq = pq.merge(quotes[['id', 'date']], left_on='quote_id', right_on='id', suffixes=('', '_quote'))
    pq.rename(columns={'date': 'purchase_date', 'date_quote': 'quote_date'}, inplace=True)
    pq['days'] = (pq['purchase_date'] - pq['quote_date']).dt.days

    n_week = len(pq[pq['days'] <= 7])
    n_month = len(pq[pq['days'] <= 30])

    c1, c2 = st.columns(2)
    c1.metric("Within 1 Week", f"{n_week:,}")
    c2.metric("Within 1 Month", f"{n_month:,}")

    # weekly conversion by quoting month
    week_df = pq[pq['days'] <= 7].copy()
    week_df['quote_month'] = week_df['quote_date'].dt.to_period('M')
    quotes_monthly = quotes.groupby(quotes['date'].dt.to_period('M')).size()
    week_purch = week_df.groupby('quote_month')['quote_id'].nunique()

    conv_wk = pd.concat([quotes_monthly.rename('total_quotes'),
                         week_purch.rename('within_week')], axis=1).fillna(0)
    conv_wk['rate_%'] = (conv_wk['within_week'] / conv_wk['total_quotes'] * 100).round(2)
    conv_plot = conv_wk.reset_index()
    conv_plot.columns = ['month', 'total_quotes', 'within_week', 'rate_%']
    conv_plot['month'] = conv_plot['month'].astype(str)

    best_wk = conv_wk['rate_%'].idxmax()
    st.metric("Best Weekly Conversion Month", str(best_wk), f"{conv_wk.loc[best_wk, 'rate_%']}%")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=conv_plot['month'], y=conv_plot['within_week'],
                         name='Purchases (1 week)', marker_color=PURPLE_MAIN, opacity=0.7),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=conv_plot['month'], y=conv_plot['rate_%'],
                             name='Conversion %', line=dict(color='#EC4899', width=2.5),
                             mode='lines+markers'), secondary_y=True)
    fig.update_yaxes(title_text='# Purchases', secondary_y=False)
    fig.update_yaxes(title_text='Conversion %', secondary_y=True)
    fig.update_layout(title='Weekly Conversion Rate by Quoting Month')
    st.plotly_chart(styled_fig(fig, 450), use_container_width=True)
    st.dataframe(conv_plot, use_container_width=True)