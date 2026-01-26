import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

# -----------------------------
# 基本設定
# -----------------------------
st.set_page_config(page_title="物価と家計支出の関係", layout="wide")

st.title("📊 消費者物価指数と家計消費支出の関係分析")

st.markdown("""
本アプリは e-Stat の  
**消費者物価指数（CPI）** と **世帯の消費支出データ** を用いて、  
物価と家計支出の関係を可視化・分析するものである。
""")

# -----------------------------
# データ読み込み
# -----------------------------
df = pd.read_excel("支出.xlsx")
df["年度_num"] = df["年度"].str.replace("年度", "").astype(int)

# -----------------------------
# サイドバーUI
# -----------------------------
with st.sidebar:
    st.header("🔧 表示設定")

    min_year = int(df["年度_num"].min())
    max_year = int(df["年度_num"].max())

    year_range = st.slider(
        "表示する年度範囲",
        min_year, max_year,
        (min_year, max_year)
    )

    graph_type = st.radio(
        "表示形式",
        ["折れ線グラフ", "散布図"]
    )

    show_table = st.checkbox("データ表を表示する")

# -----------------------------
# データ抽出
# -----------------------------
filtered = df[
    (df["年度_num"] >= year_range[0]) &
    (df["年度_num"] <= year_range[1])
]

# -----------------------------
# データ概要
# -----------------------------
st.subheader("📄 データ概要")

col1, col2, col3 = st.columns(3)
col1.metric("開始年", filtered["年度_num"].min())
col2.metric("終了年", filtered["年度_num"].max())
col3.metric("データ件数", len(filtered))

if show_table:
    st.dataframe(filtered[["年度", "消費支出", "指数"]], use_container_width=True)

# -----------------------------
# グラフ表示
# -----------------------------
st.subheader("📈 可視化結果")

if graph_type == "折れ線グラフ":
    st.markdown("### 年度別 CPI と 消費支出の推移")
else:
    st.markdown("### CPI と 消費支出の関係（回帰分析）")

fig, ax = plt.subplots(figsize=(8, 5))

# ---- 折れ線 ----
if graph_type == "折れ線グラフ":
    ax2 = ax.twinx()

    l1 = ax.plot(
        filtered["年度_num"],
        filtered["指数"],
        marker="o",
        color="tab:blue",
        label="CPI"
    )

    l2 = ax2.plot(
        filtered["年度_num"],
        filtered["消費支出"],
        marker="o",
        linestyle="--",
        color="tab:red",
        label="Spending"
    )

    lines = l1 + l2
    labels = [line.get_label() for line in lines]
    ax.legend(lines, labels, loc="upper left")

    ax2.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

    st.caption("左軸：消費者物価指数（CPI） ／ 右軸：世帯の消費支出（円）")

# ---- 散布図 + 回帰 ----
else:
    x = filtered["指数"]
    y = filtered["消費支出"]

    ax.scatter(x, y, label="Data")

    a, b = np.polyfit(x, y, 1)
    y_pred = a * x + b
    ax.plot(x, y_pred, linestyle="--", label="Regression")

    ax.legend()
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

    r = np.corrcoef(x, y)[0, 1]
    r2 = r ** 2

    st.write(f"相関係数 r = {r:.3f}")
    st.write(f"決定係数 R² = {r2:.3f}")
    st.write(f"回帰式 : 消費支出 = {a:.2f} × 指数 + {b:.2f}")

    st.caption("横軸：消費者物価指数（CPI） ／ 縦軸：世帯の消費支出（円）")

plt.tight_layout()
st.pyplot(fig)

# -----------------------------
# 解釈
# -----------------------------
with st.expander("📝 グラフから読み取れること"):
    st.write("""
本分析より、消費者物価指数（CPI）が上昇するにつれて、
世帯の消費支出も増加する傾向が確認できる。

これは物価が上昇すると、同じ商品・サービスを購入するために
より多くの支出が必要になるためである。

ただし、すべての年度で比例的に増加しているわけではなく、
家計の節約行動や所得の変化など、他の要因も影響していると考えられる。

このことから、物価は家計支出に影響を与える重要な要因であるが、
単独ではなく複数の要素と組み合わさって家計行動が決まっているといえる。
""")
