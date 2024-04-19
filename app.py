import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

# Streamlitアプリのタイトルを設定
st.title("フリーランスエージェント案件数比較")

# 比較する項目を入力するテキストボックスを作成
selected_item = st.text_input("比較する項目を入力してください", "利用者平均年収")

# 比較するサービス数を選択するセレクトボックスを作成
num_services = st.number_input("比較するサービス数を選択してください", min_value=1, max_value=10, value=5, step=1)

# サービスデータを入力するフォームを作成
services = []
for i in range(num_services):
    service_name = st.text_input(f"サービス名 {i+1}", key=f"service_name_{i}")
    item_value = st.number_input(f"{selected_item} {i+1}", min_value=0, key=f"item_value_{i}")
    services.append([service_name, item_value])

# 入力されたデータをDataFrameに変換
df = pd.DataFrame(services, columns=["サービス名", selected_item])

# 選択された項目でデータをソート
sorted_df = df.sort_values(by=selected_item, ascending=False)
sorted_df["順位"] = range(1, len(sorted_df) + 1)

# 選択された項目の平均を計算
average_value = sorted_df[selected_item].mean()

# 選択された項目のランキングをヒストグラムで表示
chart = alt.Chart(sorted_df).mark_bar().encode(
    x=alt.X("サービス名:N", sort=alt.EncodingSortField(field="順位", order="ascending"), title=None),
    y=alt.Y(selected_item, title=selected_item),
    color=alt.condition(
        alt.datum[selected_item] >= average_value,
        alt.value("lightblue"),
        alt.value("lightgray")
    ),
    tooltip=["サービス名", selected_item, "順位"]
).properties(
    width=500,
    height=300,
    title=f"{selected_item}ランキング"
)


# 平均を表す横線を追加
average_line = alt.Chart(pd.DataFrame({'average': [average_value]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='average:Q')

# 数値を表示するテキストを追加
value_text = chart.mark_text(
    align='center',
    baseline='bottom',
    dy=-10  # バーの上部から10ピクセル下にテキストを配置
).encode(
    text=alt.condition(
        alt.datum[selected_item] > 0,  # 条件：数値が0より大きい
        alt.Text(selected_item, type='quantitative'),  # 数値フィールドとして型を明示
        alt.value('')  # 条件が偽のときに表示しない
    ),
    x=alt.X('サービス名:N', sort=alt.EncodingSortField(field="順位", order="ascending")),  # X軸のソートを順位の昇順に設定
    y=alt.Y(selected_item, type='quantitative')
)

# ランキング図形と平均線、数値のテキストを表示
ranking_chart = (chart + average_line + value_text).configure_view(strokeWidth=0).configure_axis(
    labelFontSize=14,
    titleFontSize=16
).configure_title(
    fontSize=18
).properties(
    title=f"{selected_item}ランキング"
).configure_legend(
    titleFontSize=14,
    labelFontSize=12
)
# ヒストグラムを中央寄せで表示
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.altair_chart(ranking_chart, use_container_width=True)

# AltairチャートをHTML、JavaScript、CSSコードに変換
html_code = ranking_chart.to_html()

# コードを表示
st.subheader("HTML、JavaScript、CSSコード")
code_expander = st.expander("コードを表示")
with code_expander:
    st.code(html_code, language="html")

# コードをダウンロード
code_bytes = StringIO(html_code).getvalue().encode("utf-8")
st.download_button(
    label="コードをダウンロード",
    data=code_bytes,
    file_name="agent_ranking.html",
    mime="text/html"
)