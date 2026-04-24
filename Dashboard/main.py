import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

# Header
st.title("📊 E-Commerce Business Performance Dashboard")
st.markdown("Analisis performa logistik, kepuasan pelanggan, dan finansial pada platform Olist.")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("all_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# Sidebar Filter
st.sidebar.header("Filter Data")
selected_year = st.sidebar.selectbox("Pilih Tahun", [2017, 2018])
df_filtered = df[df['order_purchase_timestamp'].dt.year == selected_year]

# --- TABEL DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["Logistik", "Kepuasan", "Finansial"])

# --- TAB 1: LOGISTIK ---
with tab1:
    st.subheader(f"10 Kategori dengan Delay Tertinggi di Sao Paulo ({selected_year})")
    
    # Filter data khusus SP, Tahun, dan hanya yang terlambat (delay > 0)
    df_sp = df[(df['customer_state'] == 'SP') & 
               (df['order_purchase_timestamp'].dt.year == selected_year) &
               (df['delivery_delay'] > 0)]
    
    top_10_delay = df_sp.groupby('product_category_name_english')['delivery_delay'].mean().sort_values(ascending=False).head(10).reset_index()

    # KODE PLOTLY: Horizontal Bar Chart
    fig1 = px.bar(top_10_delay, 
                  x='delivery_delay', 
                  y='product_category_name_english',
                  orientation='h',
                  labels={'delivery_delay': 'Rata-rata Keterlambatan (Hari)', 'product_category_name_english': 'Kategori Produk'},
                  color='delivery_delay',
                  color_continuous_scale='Reds')
    
    fig1.update_layout(yaxis={'categoryorder':'total ascending'}) # Biar yang tertinggi di atas
    st.plotly_chart(fig1, use_container_width=True)

# --- TAB 2: KEPUASAN ---
with tab2:
    st.subheader("Hubungan Delay Pengiriman vs Skor Ulasan")
    
    # Filter kategori Bed Bath Table
    df_bbt = df[df['product_category_name_english'] == 'bed_bath_table']

    # KODE PLOTLY: Boxplot
    fig2 = px.box(df_bbt, 
                  x='review_score', 
                  y='delivery_delay',
                  color='review_score',
                  labels={'review_score': 'Skor Ulasan', 'delivery_delay': 'Delay Pengiriman (Hari)'},
                  points="outliers") # Menampilkan titik-titik yang sangat terlambat
    
    st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3: FINANSIAL ---
with tab3:
    st.subheader("Tren Pendapatan Bulanan: Credit Card vs Boleto")
    
    # Filter data tahun dan tipe pembayaran
    df_pay = df[(df['order_purchase_timestamp'].dt.year == selected_year) & 
                (df['payment_type'].isin(['credit_card', 'boleto']))]
    
    # Resample data per bulan
    df_trend = df_pay.set_index('order_purchase_timestamp').groupby(['payment_type', pd.DatetimeIndex(df_pay['order_purchase_timestamp']).to_period('M')])['payment_value'].sum().reset_index()
    df_trend['order_purchase_timestamp'] = df_trend['order_purchase_timestamp'].astype(str)

    # KODE PLOTLY: Line Chart
    fig3 = px.line(df_trend, 
                   x='order_purchase_timestamp', 
                   y='payment_value', 
                   color='payment_type',
                   markers=True,
                   labels={'order_purchase_timestamp': 'Bulan', 'payment_value': 'Total Pendapatan (BRL)'})
    
    st.plotly_chart(fig3, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("Developed by Cinta Wardana")
