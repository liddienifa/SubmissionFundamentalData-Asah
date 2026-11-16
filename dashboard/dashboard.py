from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Brazilian E-Commerce Analytics Dashboard | Liddieni Hanifa",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")


@st.cache_data
def load_main_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent / "main_data.csv"
    df = pd.read_csv(
        data_path,
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    return df


main_df = load_main_data()

# ==============================================================================
# SIDEBAR FILTERS
# ==============================================================================
with st.sidebar:
    st.title("🛒 E-Commerce Analytics")
    st.markdown(
        "**Disusun oleh:**  \n"
        "👤 **Liddieni Hanifa**  \n"
        "📧 `hi.liddienihanifa@gmail.com`  \n"
        "🆔 ID Dicoding: `Liddieni Hanifa`"
    )
    st.divider()
    st.subheader("⚙️ Filter Rentang Waktu & Wilayah")

    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()

    date_selection = st.date_input(
        label="Rentang Tanggal Pembelian",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )
    if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
        start_date, end_date = date_selection
    else:
        start_date, end_date = min_date, max_date

    all_states = sorted(main_df["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect(
        label="Pilih Negara Bagian (Kosongkan = Semua)",
        options=all_states,
        default=[],
    )

    delivery_filter = st.selectbox(
        label="Status Ketepatan Pengiriman",
        options=["Semua Pesanan", "On-Time (Tepat Waktu)", "Delayed (Terlambat)"],
        index=0,
    )

# Apply filters
filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date)
    & (main_df["order_purchase_timestamp"].dt.date <= end_date)
].copy()

if selected_states:
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]

if delivery_filter != "Semua Pesanan":
    filtered_df = filtered_df[filtered_df["delivery_status_label"] == delivery_filter]

# Order-level aggregation for accurate order/review/SLA metrics
order_level_df = (
    filtered_df.groupby("order_id", as_index=False)
    .agg(
        customer_unique_id=("customer_unique_id", "first"),
        order_purchase_timestamp=("order_purchase_timestamp", "first"),
        order_year_month=("order_year_month", "first"),
        customer_state=("customer_state", "first"),
        total_order_value=("total_item_value", "sum"),
        total_price=("price", "sum"),
        delivery_days=("delivery_days", "first"),
        delay_days=("delay_days", "first"),
        is_late=("is_late", "first"),
        delivery_status_label=("delivery_status_label", "first"),
        review_score=("review_score", "first"),
    )
)

# ==============================================================================
# HEADER & KEY PERFORMANCE INDICATORS (KPI)
# ==============================================================================
st.title("📊 Brazilian E-Commerce Public Dataset Dashboard")
st.caption(
    f"Periode Data Terfilter: **{start_date.strftime('%d %b %Y')}** s/d **{end_date.strftime('%d %b %Y')}** "
    f"| Menampilkan **{order_level_df['order_id'].nunique():,}** pesanan unik (**{len(filtered_df):,}** unit item)"
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_orders = order_level_df["order_id"].nunique()
total_revenue = filtered_df["price"].sum()
total_gmv = filtered_df["total_item_value"].sum()
avg_review = order_level_df["review_score"].mean() if total_orders > 0 else 0.0
ontime_rate = (1.0 - order_level_df["is_late"].mean()) * 100 if total_orders > 0 else 0.0

kpi1.metric("Total Pesanan (Delivered)", f"{total_orders:,}")
kpi2.metric("Total Revenue Produk", f"BRL {total_revenue:,.2f}", f"GMV: BRL {total_gmv:,.2f}")
kpi3.metric("Rata-rata Review Score", f"{avg_review:.2f} / 5.00")
kpi4.metric("Tingkat Pengiriman Tepat Waktu", f"{ontime_rate:.2f}%", f"Terlambat: {100 - ontime_rate:.2f}%")

st.divider()

# ==============================================================================
# NAVIGATION TABS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🏆 Kinerja Kategori Produk & Tren (Pertanyaan 1)",
    "🚚 SLA Logistik & Kepuasan Pelanggan (Pertanyaan 2)",
    "🔬 Analisis Lanjutan (RFM, Geospasial & Clustering)",
])

# ------------------------------------------------------------------------------
# TAB 1: PRODUCT CATEGORY PERFORMANCE & MONTHLY TREND
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("1. Perbandingan Top 5 vs Bottom 5 Kategori Produk Berdasarkan Total Revenue (BRL)")
    cat_perf = (
        filtered_df[filtered_df["product_category_name_english"] != "unknown"]
        .groupby("product_category_name_english", as_index=False)
        .agg(
            total_revenue=("price", "sum"),
            total_gmv=("total_item_value", "sum"),
            items_sold=("order_item_id", "count"),
            unique_orders=("order_id", "nunique"),
            avg_review=("review_score", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
    )

    if not cat_perf.empty:
        fig_cat, axes_cat = plt.subplots(1, 2, figsize=(16, 6))

        top5_c = cat_perf.head(5)
        sns.barplot(
            data=top5_c,
            x="total_revenue",
            y="product_category_name_english",
            palette=["#0B6E4F"] + ["#74A57F"] * (len(top5_c) - 1),
            ax=axes_cat[0],
        )
        axes_cat[0].set_title("Top 5 Kategori Produk (Revenue Tertinggi)", fontweight="bold")
        axes_cat[0].set_xlabel("Total Revenue (BRL)")
        axes_cat[0].set_ylabel("Kategori Produk")
        axes_cat[0].set_xlim(0, top5_c["total_revenue"].max() * 1.25)
        for i, r in enumerate(top5_c.itertuples()):
            axes_cat[0].text(
                r.total_revenue * 1.02,
                i,
                f"BRL {r.total_revenue:,.0f} ({r.items_sold:,} unit)",
                va="center",
                fontsize=9.5,
                fontweight="bold" if i == 0 else "normal",
            )
        sns.despine(ax=axes_cat[0])

        bot5_c = cat_perf.tail(5).sort_values("total_revenue", ascending=True)
        sns.barplot(
            data=bot5_c,
            x="total_revenue",
            y="product_category_name_english",
            palette=["#C0392B"] + ["#D98880"] * (len(bot5_c) - 1),
            ax=axes_cat[1],
        )
        axes_cat[1].set_title("Bottom 5 Kategori Produk (Revenue Terendah)", fontweight="bold")
        axes_cat[1].set_xlabel("Total Revenue (BRL)")
        axes_cat[1].set_ylabel("")
        axes_cat[1].set_xlim(0, max(bot5_c["total_revenue"].max() * 1.28, 10))
        for i, r in enumerate(bot5_c.itertuples()):
            axes_cat[1].text(
                r.total_revenue * 1.02,
                i,
                f"BRL {r.total_revenue:,.2f} ({r.items_sold:,} unit)",
                va="center",
                fontsize=9.5,
                fontweight="bold" if i == 0 else "normal",
            )
        sns.despine(ax=axes_cat[1])

        plt.tight_layout()
        st.pyplot(fig_cat)
        plt.close(fig_cat)

    st.subheader("2. Tren Pertumbuhan Bulanan GMV & Pesanan")
    monthly_df = (
        filtered_df.groupby("order_year_month", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("price", "sum"),
            total_gmv=("total_item_value", "sum"),
        )
        .sort_values("order_year_month")
    )
    if not monthly_df.empty:
        fig_m, ax_m = plt.subplots(figsize=(14, 4.8))
        ax_m.plot(
            monthly_df["order_year_month"],
            monthly_df["total_gmv"] / 1e6,
            marker="o",
            linewidth=2.5,
            color="#0B6E4F",
        )
        ax_m.fill_between(
            range(len(monthly_df)),
            monthly_df["total_gmv"] / 1e6,
            color="#0B6E4F",
            alpha=0.12,
        )
        ax_m.set_title("Tren Bulanan Gross Merchandise Value (Juta BRL)", fontweight="bold")
        ax_m.set_xlabel("Periode Bulan")
        ax_m.set_ylabel("Total GMV (Juta BRL)")
        ax_m.tick_params(axis="x", rotation=45)
        sns.despine(ax=ax_m)
        plt.tight_layout()
        st.pyplot(fig_m)
        plt.close(fig_m)

# ------------------------------------------------------------------------------
# TAB 2: LOGISTICS SLA & CUSTOMER SATISFACTION
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Evaluasi Keterlambatan Pengiriman & Dampaknya terhadap Review Score di Top 5 Negara Bagian")
    if not order_level_df.empty:
        top_states = order_level_df["customer_state"].value_counts().head(5).index.tolist()
        st_sla = (
            order_level_df[order_level_df["customer_state"].isin(top_states)]
            .groupby("customer_state", as_index=False)
            .agg(
                total_orders=("order_id", "count"),
                late_rate_pct=("is_late", lambda x: x.mean() * 100),
                avg_delivery_days=("delivery_days", "mean"),
                avg_review_score=("review_score", "mean"),
            )
            .sort_values("late_rate_pct", ascending=False)
        )

        fig_sla, axes_sla = plt.subplots(1, 2, figsize=(16, 5.8))

        colors_st = ["#C0392B" if i == 0 else "#5D6D7E" for i in range(len(st_sla))]
        sns.barplot(
            data=st_sla,
            x="customer_state",
            y="late_rate_pct",
            palette=colors_st,
            ax=axes_sla[0],
        )
        axes_sla[0].set_title("Tingkat Keterlambatan Pengiriman (%) di Top 5 Negara Bagian", fontweight="bold")
        axes_sla[0].set_xlabel("Negara Bagian (State)")
        axes_sla[0].set_ylabel("Persentase Terlambat (%)")
        axes_sla[0].set_ylim(0, max(st_sla["late_rate_pct"].max() * 1.25, 5))
        for i, r in enumerate(st_sla.itertuples()):
            axes_sla[0].text(
                i,
                r.late_rate_pct + 0.3,
                f"{r.late_rate_pct:.2f}%\n({r.avg_delivery_days:.1f} hr)",
                ha="center",
                fontsize=9,
                fontweight="bold" if i == 0 else "normal",
            )
        sns.despine(ax=axes_sla[0])

        st_rev_grp = (
            order_level_df[order_level_df["customer_state"].isin(top_states)]
            .groupby(["customer_state", "delivery_status_label"], as_index=False)
            .agg(avg_review_score=("review_score", "mean"))
        )
        sns.barplot(
            data=st_rev_grp,
            x="customer_state",
            y="avg_review_score",
            hue="delivery_status_label",
            order=st_sla["customer_state"].tolist(),
            palette={"On-Time (Tepat Waktu)": "#0B6E4F", "Delayed (Terlambat)": "#C0392B"},
            ax=axes_sla[1],
        )
        axes_sla[1].set_title("Rata-rata Review Score: Tepat Waktu vs Terlambat", fontweight="bold")
        axes_sla[1].set_xlabel("Negara Bagian (State)")
        axes_sla[1].set_ylabel("Rata-rata Review Score (1 - 5)")
        axes_sla[1].set_ylim(0, 5.3)
        for container in axes_sla[1].containers:
            axes_sla[1].bar_label(container, fmt="%.2f", padding=3, fontsize=9)
        sns.despine(ax=axes_sla[1])

        plt.tight_layout()
        st.pyplot(fig_sla)
        plt.close(fig_sla)

        st.dataframe(st_sla, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: ADVANCED ANALYTICS (RFM, GEOSPATIAL, BINNING CLUSTERING)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("1. RFM Analysis (Recency, Frequency, Monetary)")
    if not order_level_df.empty:
        ref_date = order_level_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
        rfm = (
            order_level_df.groupby("customer_unique_id", as_index=False)
            .agg(
                last_purchase=("order_purchase_timestamp", "max"),
                frequency=("order_id", "nunique"),
                monetary=("total_order_value", "sum"),
            )
        )
        rfm["recency"] = (ref_date - rfm["last_purchase"]).dt.days

        c1, c2, c3 = st.columns(3)
        c1.metric("Rata-rata Recency", f"{rfm['recency'].mean():.1f} Hari")
        c2.metric("Rata-rata Frequency", f"{rfm['frequency'].mean():.2f} Pesanan")
        c3.metric("Rata-rata Monetary", f"BRL {rfm['monetary'].mean():,.2f}")

        rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
        rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        def map_seg(row):
            if row["r_score"] >= 4 and row["m_score"] >= 4:
                return "Champions / High Value Recent"
            elif row["frequency"] >= 2 and row["m_score"] >= 3:
                return "Loyal Repeat Buyers"
            elif row["r_score"] >= 4 and row["m_score"] <= 3:
                return "Recent Promising Customers"
            elif row["r_score"] == 3:
                return "Need Attention (Cooling Down)"
            elif row["r_score"] <= 2 and row["m_score"] >= 4:
                return "At Risk High Spenders"
            return "Hibernating / Lost Customers"

        rfm["customer_segment"] = rfm.apply(map_seg, axis=1)
        seg_df = (
            rfm.groupby("customer_segment", as_index=False)
            .agg(
                customers=("customer_unique_id", "count"),
                total_monetary=("monetary", "sum"),
            )
            .sort_values("total_monetary", ascending=False)
        )

        fig_rfm, axes_rfm = plt.subplots(1, 2, figsize=(15, 5))
        sns.barplot(data=seg_df, x="customers", y="customer_segment", palette="crest", ax=axes_rfm[0])
        axes_rfm[0].set_title("Jumlah Pelanggan per Segmen RFM", fontweight="bold")
        axes_rfm[0].set_xlabel("Jumlah Pelanggan Unik")
        axes_rfm[0].set_ylabel("Segmen RFM")
        sns.despine(ax=axes_rfm[0])

        sns.barplot(data=seg_df, x="total_monetary", y="customer_segment", palette="viridis", ax=axes_rfm[1])
        axes_rfm[1].set_title("Total Nilai Transaksi (BRL) per Segmen RFM", fontweight="bold")
        axes_rfm[1].set_xlabel("Total Monetary (BRL)")
        axes_rfm[1].set_ylabel("")
        sns.despine(ax=axes_rfm[1])

        plt.tight_layout()
        st.pyplot(fig_rfm)
        plt.close(fig_rfm)

    st.subheader("2. Geospatial Analysis & Manual Grouping (Delivery Speed Tier)")
    col_geo, col_bin = st.columns(2)
    with col_geo:
        geo_pts = filtered_df[["geolocation_lat", "geolocation_lng"]].dropna().rename(
            columns={"geolocation_lat": "lat", "geolocation_lng": "lon"}
        )
        if not geo_pts.empty:
            st.map(geo_pts.sample(n=min(10000, len(geo_pts)), random_state=42), zoom=3)

    with col_bin:
        order_level_df["delivery_speed_tier"] = pd.cut(
            order_level_df["delivery_days"],
            bins=[-1, 7, 14, 21, 1000],
            labels=[
                "1. Cepat (<= 7 Hari)",
                "2. Normal (8 - 14 Hari)",
                "3. Lambat (15 - 21 Hari)",
                "4. Sangat Lambat (> 21 Hari)",
            ],
        )
        bin_df = (
            order_level_df.groupby("delivery_speed_tier", observed=False, as_index=False)
            .agg(
                total_orders=("order_id", "count"),
                avg_review_score=("review_score", "mean"),
            )
        )
        fig_bin, ax_bin = plt.subplots(figsize=(7, 5))
        sns.barplot(
            data=bin_df,
            x="delivery_speed_tier",
            y="avg_review_score",
            palette=["#0B6E4F", "#2E8B57", "#E67E22", "#C0392B"],
            ax=ax_bin,
        )
        ax_bin.set_title("Rata-rata Review Score per Kelompok Kecepatan Kirim", fontweight="bold")
        ax_bin.set_xlabel("Kelompok Kecepatan Pengiriman")
        ax_bin.set_ylabel("Rata-rata Review Score (1 - 5)")
        ax_bin.set_ylim(0, 5.2)
        ax_bin.tick_params(axis="x", rotation=15)
        for container in ax_bin.containers:
            ax_bin.bar_label(container, fmt="%.2f", padding=3, fontweight="bold")
        sns.despine(ax=ax_bin)
        plt.tight_layout()
        st.pyplot(fig_bin)
        plt.close(fig_bin)

st.caption("© 2026 Liddieni Hanifa — Proyek Akhir Belajar Analisis Data dengan Python (Dicoding Indonesia)")
