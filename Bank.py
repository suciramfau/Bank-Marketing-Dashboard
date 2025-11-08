import streamlit as st
import pandas as pd
import plotly.express as px

# ---- LOAD & CLEANING DATASET ----#
@st.cache_data
def load_data():
    df = pd.read_csv("Data/bank-additional-full.csv", sep=';')

    # Pastikan semua kolom lowercase
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Ubah kolom target jadi kapital
    df['y'] = df['y'].str.capitalize()

    # Konversi numerik jika perlu
    numeric_cols = ['age', 'duration', 'campaign', 'pdays', 'previous',
                    'emp.var.rate', 'cons.price.idx', 'cons.conf.idx', 'euribor3m', 'nr.employed']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Load dataset
df_bank = load_data()

# ----- SETUP DASHBOARD ----#
st.set_page_config(page_title="🏦 Bank Marketing Dashboard", layout="wide")
st.title("🏦 Bank Marketing Campaign Dashboard")
st.caption("Analisis lengkap data kampanye marketing untuk produk deposito berjangka di Portugal (Bank Marketing Dataset).")

# ----- KPI Utama ----#
col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Nasabah", f"{len(df_bank):,}")
col2.metric("Rata-rata Umur", f"{df_bank['age'].mean():.1f}")
col3.metric("Durasi Kontak Rata-rata", f"{df_bank['duration'].mean():.0f} detik")
col4.metric("Rasio Langganan", f"{(df_bank['y'].str.lower() == 'yes').mean() * 100:.2f}%")

with st.expander("📄 Lihat 5 Baris Pertama Data"):
    st.dataframe(df_bank.head())

# ----- Sidebar Filter ----#
st.sidebar.header("🎛️ Filter Data")

job_list = ['All'] + sorted(df_bank['job'].unique())
job_filter = st.sidebar.selectbox("Pilih Pekerjaan", job_list)

edu_list = ['All'] + sorted(df_bank['education'].unique())
edu_filter = st.sidebar.selectbox("Pilih Pendidikan", edu_list)

month_list = ['All'] + sorted(df_bank['month'].unique())
month_filter = st.sidebar.selectbox("Pilih Bulan Kontak", month_list)

filtered_df = df_bank.copy()
if job_filter != 'All':
    filtered_df = filtered_df[filtered_df['job'] == job_filter]
if edu_filter != 'All':
    filtered_df = filtered_df[filtered_df['education'] == edu_filter]
if month_filter != 'All':
    filtered_df = filtered_df[filtered_df['month'] == month_filter]


# ----- KPI Berdasarkan Filter ----#
success_rate = (filtered_df['y'].str.lower() == 'yes').mean() * 100
avg_duration = filtered_df['duration'].mean()
avg_emp_rate = filtered_df['emp.var.rate'].mean()
avg_conf_idx = filtered_df['cons.conf.idx'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📈 Success Rate", f"{success_rate:.2f}%")
col2.metric("⏱️ Durasi Rata-rata", f"{avg_duration:.0f} detik")
col3.metric("💼 Employment Var. Rate", f"{avg_emp_rate:.2f}")
col4.metric("📉 Consumer Confidence", f"{avg_conf_idx:.1f}")

# ----- Visualisasi Data ----#
#  Distribusi Umur
st.subheader("👥 Distribusi Umur Berdasarkan Status Langganan")
fig_age = px.histogram(
    filtered_df, x='age', color='y', nbins=20,
    title="Distribusi Umur Nasabah",
    color_discrete_sequence=['#636EFA', '#EF553B']
)
st.plotly_chart(fig_age, use_container_width=True)

# Durasi vs Keputusan Langganan
st.subheader("⏱️ Durasi Kontak vs Keputusan Langganan")
fig_dur = px.box(
    filtered_df, x='y', y='duration', color='y',
    title="Perbandingan Durasi Kontak Nasabah (detik)",
    color_discrete_sequence=['#EF553B', '#00CC96']
)
st.plotly_chart(fig_dur, use_container_width=True)

# Rasio Langganan per Pekerjaan
st.subheader("🏢 Rasio Keberhasilan Kampanye per Pekerjaan")
job_success = (
    filtered_df.groupby('job')['y']
    .apply(lambda x: (x == 'Yes').mean() * 100)
    .reset_index(name='success_rate')
    .sort_values(by='success_rate', ascending=False)
)
fig_job = px.bar(
    job_success, x='job', y='success_rate', color='job',
    title="Persentase Nasabah Berlangganan per Pekerjaan",
    color_discrete_sequence=px.colors.qualitative.Bold
)
st.plotly_chart(fig_job, use_container_width=True)

# Distribusi Pendidikan
st.subheader("Distribusi Pendidikan Nasabah")
fig_edu = px.pie(
    filtered_df, names='education',
    title="Proporsi Pendidikan Nasabah",
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_edu, use_container_width=True)

#  Aktivitas Kampanye per Bulan
st.subheader("📆 Aktivitas Kampanye per Bulan")
month_counts = (
    filtered_df.groupby('month')['y']
    .value_counts(normalize=True)
    .rename('rate')
    .mul(100)
    .reset_index()
)
fig_month = px.bar(
    month_counts, x='month', y='rate', color='y',
    barmode='group',
    title="Rasio Langganan per Bulan",
    color_discrete_sequence=['#FFA15A', '#19D3F3']
)
st.plotly_chart(fig_month, use_container_width=True)

#  Hubungan Indikator Ekonomi
st.subheader("💹 Hubungan Indikator Ekonomi terhadap Keputusan Langganan")
fig_scatter = px.scatter(
    filtered_df,
    x='emp.var.rate',
    y='euribor3m',
    color='y',
    title="Hubungan Employment Var. Rate dan Euribor 3M",
    color_discrete_sequence=['#AB63FA', '#00CC96']
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ----- Insight ----#
st.markdown("""
### 💡 Insight Tambahan:
- Peluang langganan meningkat saat **durasi panggilan lebih lama**.
- Bulan seperti **March–May** cenderung punya tingkat keberhasilan lebih tinggi.
- Faktor ekonomi makro (`emp.var.rate`, `euribor3m`) berkorelasi kuat dengan keputusan nasabah.
- Pendidikan tinggi cenderung memiliki tingkat langganan yang lebih tinggi dibandingkan tingkat dasar.

---
📊 Dataset: *Bank Marketing Dataset (UCI Machine Learning Repository)*
""")