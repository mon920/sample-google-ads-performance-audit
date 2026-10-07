import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Google Ads Performance Audit",
    page_icon="📊",
    layout="wide"
)

st.title("Google Ads Performance Audit")

df = pd.read_csv("audit_results.csv")

total_spend = df["spend"].sum()
total_opened_accounts = df["opened_accounts"].sum()
overall_cpa = total_spend / total_opened_accounts

col1, col2, col3 = st.columns(3)

col1.metric("Inversión total", f"${total_spend:,.0f}")
col2.metric("Cuentas aperturadas", f"{total_opened_accounts:,.0f}")
col3.metric("CPA general", f"${overall_cpa:,.2f}")

st.subheader("Resumen ejecutivo")

requires_attention = df[
    df["calculated_performance_status"] == "Requiere atención"
]["campaign"].tolist()

monitor = df[
    df["calculated_performance_status"] == "Monitorear"
]["campaign"].tolist()

meets_target = df[
    df["calculated_performance_status"] == "Cumple"
]["campaign"].tolist()

if requires_attention:
    st.error(
        "Requieren atención: " + ", ".join(requires_attention)
    )

if monitor:
    st.warning(
        "Monitorear: " + ", ".join(monitor)
    )

if meets_target:
    st.success(
        "Cumplen el objetivo: " + ", ".join(meets_target)
    )

st.subheader("CPA real vs CPA objetivo")

chart_data = df.set_index("campaign")[[
    "calculated_cpa",
    "target_cpa"
]].rename(columns={
    "calculated_cpa": "CPA real",
    "target_cpa": "CPA objetivo"
})

st.bar_chart(chart_data, stack=False)

st.subheader("Resultados por campaña")
summary_table = df[[
    "campaign",
    "campaign_type",
    "spend",
    "opened_accounts",
    "calculated_cpa",
    "target_cpa",
    "calculated_cpa_vs_target",
    "calculated_performance_status"
]].copy()

summary_table["calculated_cpa_vs_target"] = (
    summary_table["calculated_cpa_vs_target"] * 100
)

summary_table = summary_table.rename(columns={
    "campaign": "Campaña",
    "campaign_type": "Tipo",
    "spend": "Inversión",
    "opened_accounts": "Cuentas aperturadas",
    "calculated_cpa": "CPA real",
    "target_cpa": "CPA objetivo",
    "calculated_cpa_vs_target": "CPA vs objetivo",
    "calculated_performance_status": "Estatus"
})

def colorear_estatus(valor):
    colores = {
        "Cumple": "background-color: #C6EFCE; color: #006100;",
        "Monitorear": "background-color: #FFEB9C; color: #9C6500;",
        "Requiere atención": "background-color: #FFC7CE; color: #9C0006;"
    }
    return colores.get(valor, "")

tabla_estilizada = summary_table.style.map(
    colorear_estatus,
    subset=["Estatus"]
)
st.dataframe(
    tabla_estilizada,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Inversión": st.column_config.NumberColumn(format="$%.0f"),
        "CPA real": st.column_config.NumberColumn(format="$%.2f"),
        "CPA objetivo": st.column_config.NumberColumn(format="$%.2f"),
        "CPA vs objetivo": st.column_config.NumberColumn(format="%.1f%%")
    }
)

st.subheader("Recomendaciones por campaña")

for _, row in df.iterrows():
    with st.expander(
        f'{row["campaign"]} — {row["calculated_performance_status"]}'
    ):
        st.write(row["calculated_recommendation"])