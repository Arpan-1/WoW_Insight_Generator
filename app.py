"""
Telstra WoW Intelligence Tool
A Streamlit app for Week-on-Week traffic & order analysis.
"""

import streamlit as st
import pandas as pd
from stage1 import calculate_wow_changes, format_pct
from stage2 import run_stage2
from utils import fmt_pct, fmt_number, pct_color_class, summarise_gsc

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Telstra WoW Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* ── Brand Header ── */
.brand-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 32px;
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
}
.brand-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,122,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.brand-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}
.brand-subtitle {
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem;
    margin-top: 6px;
    font-family: 'DM Mono', monospace;
}
.telstra-badge {
    display: inline-block;
    background: #007AFF;
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* ── Stage Cards ── */
.stage-card {
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.stage-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #007AFF;
    margin-bottom: 6px;
    font-family: 'DM Mono', monospace;
}
.stage-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0d0d0d;
    margin-bottom: 4px;
}

/* ── KPI Metrics ── */
.metric-row {
    display: flex;
    gap: 16px;
    margin-top: 20px;
    flex-wrap: wrap;
}
.metric-box {
    flex: 1;
    min-width: 140px;
    background: #f7f9fc;
    border-radius: 12px;
    padding: 18px 20px;
    border: 1px solid #eaeef3;
}
.metric-label {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0d0d0d;
    line-height: 1;
    font-family: 'DM Mono', monospace;
}
.metric-change-pos {
    font-size: 0.85rem;
    color: #10b981;
    font-weight: 600;
    margin-top: 4px;
}
.metric-change-neg {
    font-size: 0.85rem;
    color: #ef4444;
    font-weight: 600;
    margin-top: 4px;
}

/* ── Section Tabs ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 16px;
}
.section-chip {
    background: linear-gradient(135deg, #007AFF, #0055d4);
    color: white;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.section-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0d0d0d;
}

/* ── News Cards ── */
.news-card {
    background: #f7f9fc;
    border-left: 3px solid #007AFF;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.news-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0d0d0d;
    margin-bottom: 4px;
}
.news-meta {
    font-size: 0.78rem;
    color: #6b7280;
    font-family: 'DM Mono', monospace;
}
.news-snippet {
    font-size: 0.85rem;
    color: #374151;
    margin-top: 6px;
    line-height: 1.5;
}

/* ── Price Table ── */
.price-highlight {
    background: #ecfdf5;
    border: 1px solid #d1fae5;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.85rem;
    color: #065f46;
    font-weight: 500;
    margin-bottom: 10px;
    display: inline-block;
}

/* ── Report Box ── */
.ai-report {
    background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
    border: 1px solid #c7d7fe;
    border-radius: 14px;
    padding: 28px 32px;
    font-size: 0.92rem;
    line-height: 1.75;
    color: #1e293b;
    white-space: pre-wrap;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #e8ecf0;
    margin: 28px 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1117;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Load API Keys from st.secrets ────────────────────────────────────────────
def load_secrets():
    missing = []
    openai_key = st.secrets.get("OPENAI_API_KEY", "")
    serpapi_key = st.secrets.get("SERPAPI_KEY", "")
    if not openai_key:
        missing.append("OPENAI_API_KEY")
    if not serpapi_key:
        missing.append("SERPAPI_KEY")
    return openai_key, serpapi_key, missing

openai_key, serpapi_key, missing_keys = load_secrets()

# ── Sidebar: Info only ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 WoW Intelligence")
    st.markdown("---")

    # API key status indicator
    if missing_keys:
        st.error(f"⚠️ Missing secrets: `{'`, `'.join(missing_keys)}`\n\nAdd them to `.streamlit/secrets.toml` locally, or via the Streamlit Cloud dashboard.")
    else:
        st.success("✅ API keys loaded")

    st.markdown("---")
    st.markdown("""
**About this tool**

Analyses Week-on-Week changes in Traffic & Orders for Telstra.com categories, powered by:
- 🔍 SerpAPI — Price & News intelligence
- 🤖 OpenAI GPT-4o — Root cause synthesis
    """)
    st.markdown("---")
    st.markdown("**Sections covered**")
    st.markdown("📺 Streaming\n\n📱 Tablet")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div class="telstra-badge">Telstra.com</div>
    <div class="brand-title">📡 WoW Intelligence Tool</div>
    <div class="brand-subtitle">Week-on-Week Performance Analysis · Traffic · Orders · Search Console</div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Stage 1 — WoW Summary", "🔍 Stage 2 — Root Cause Analysis"])


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="stage-card">
        <div class="stage-label">Stage 1</div>
        <div class="stage-title">Traffic & Orders — Week on Week Input</div>
        <p style="color:#6b7280;font-size:0.9rem;margin-top:4px;">Enter traffic and order data for each section across both weeks.</p>
    </div>
    """, unsafe_allow_html=True)

    sections = ["Streaming", "Tablet"]
    sections_data = {}

    for section in sections:
        st.markdown(f"""
        <div class="section-header">
            <span class="section-chip">Section</span>
            <span class="section-name">{section}</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Week 1**")
            w1_traffic = st.number_input(f"Traffic W1 — {section}", min_value=0, value=0, key=f"w1_t_{section}", step=1)
            w1_orders = st.number_input(f"Orders W1 — {section}", min_value=0, value=0, key=f"w1_o_{section}", step=1)
        with col2:
            st.markdown("**Week 2**")
            w2_traffic = st.number_input(f"Traffic W2 — {section}", min_value=0, value=0, key=f"w2_t_{section}", step=1)
            w2_orders = st.number_input(f"Orders W2 — {section}", min_value=0, value=0, key=f"w2_o_{section}", step=1)

        sections_data[section] = {
            "week1": {"traffic": w1_traffic, "orders": w1_orders},
            "week2": {"traffic": w2_traffic, "orders": w2_orders},
        }

        if section != sections[-1]:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶ Calculate WoW Changes", type="primary", use_container_width=True):
        results = calculate_wow_changes(sections_data)
        st.session_state["stage1_results"] = results
        st.session_state["sections_data"] = sections_data

    if "stage1_results" in st.session_state:
        results = st.session_state["stage1_results"]
        st.markdown("---")
        st.markdown("### 📈 Results")

        # Summary table
        table_rows = []
        for section, r in results.items():
            table_rows.append({
                "Section": section,
                "Traffic W1": fmt_number(r["week1_traffic"]),
                "Traffic W2": fmt_number(r["week2_traffic"]),
                "Traffic Δ%": fmt_pct(r["traffic_change_pct"]),
                "Orders W1": fmt_number(r["week1_orders"]),
                "Orders W2": fmt_number(r["week2_orders"]),
                "Orders Δ%": fmt_pct(r["orders_change_pct"]),
            })

        df = pd.DataFrame(table_rows).set_index("Section")
        st.dataframe(df, use_container_width=True)

        # Visual metric cards per section
        for section, r in results.items():
            st.markdown(f"""
            <div class="section-header">
                <span class="section-chip">Section</span>
                <span class="section-name">{section}</span>
            </div>
            """, unsafe_allow_html=True)

            t_pct = r["traffic_change_pct"]
            o_pct = r["orders_change_pct"]

            t_label = fmt_pct(t_pct)
            o_label = fmt_pct(o_pct)
            t_cls = pct_color_class(t_pct)
            o_cls = pct_color_class(o_pct)

            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-label">Traffic — W1</div>
                    <div class="metric-value">{fmt_number(r['week1_traffic'])}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Traffic — W2</div>
                    <div class="metric-value">{fmt_number(r['week2_traffic'])}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Traffic Change</div>
                    <div class="metric-value" style="font-size:1.3rem;">—</div>
                    <div class="{t_cls}">{t_label}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Orders — W1</div>
                    <div class="metric-value">{fmt_number(r['week1_orders'])}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Orders — W2</div>
                    <div class="metric-value">{fmt_number(r['week2_orders'])}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Orders Change</div>
                    <div class="metric-value" style="font-size:1.3rem;">—</div>
                    <div class="{o_cls}">{o_label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="stage-card">
        <div class="stage-label">Stage 2</div>
        <div class="stage-title">Dominating Products & GSC Metrics</div>
        <p style="color:#6b7280;font-size:0.9rem;margin-top:4px;">
            Provide the dominating product for traffic & orders per section, along with Google Search Console metrics.
            The tool will then fetch price comparisons, news, and synthesize the root cause using AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "stage1_results" not in st.session_state:
        st.info("⬅️ Please complete Stage 1 first before running Stage 2.", icon="ℹ️")
    else:
        stage2_inputs = {}
        sections = ["Streaming", "Tablet"]

        for section in sections:
            st.markdown(f"""
            <div class="section-header">
                <span class="section-chip">Section</span>
                <span class="section-name">{section}</span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                prod_traffic = st.text_input(
                    f"Dominating Product (Traffic) — {section}",
                    placeholder="e.g. Apple iPad Pro 13-inch",
                    key=f"prod_t_{section}"
                )
            with col2:
                prod_orders = st.text_input(
                    f"Dominating Product (Orders) — {section}",
                    placeholder="e.g. Samsung Galaxy Tab S9",
                    key=f"prod_o_{section}"
                )

            st.markdown("**Google Search Console Metrics**")
            gsc_col1, gsc_col2, gsc_col3 = st.columns(3)
            with gsc_col1:
                clicks_w1 = st.number_input(f"Clicks W1 — {section}", min_value=0, value=0, key=f"cl_w1_{section}")
                clicks_w2 = st.number_input(f"Clicks W2 — {section}", min_value=0, value=0, key=f"cl_w2_{section}")
            with gsc_col2:
                imp_w1 = st.number_input(f"Impressions W1 — {section}", min_value=0, value=0, key=f"imp_w1_{section}")
                imp_w2 = st.number_input(f"Impressions W2 — {section}", min_value=0, value=0, key=f"imp_w2_{section}")
            with gsc_col3:
                kw_w1 = st.number_input(f"Keywords W1 — {section}", min_value=0, value=0, key=f"kw_w1_{section}")
                kw_w2 = st.number_input(f"Keywords W2 — {section}", min_value=0, value=0, key=f"kw_w2_{section}")

            stage2_inputs[section] = {
                "product_traffic": prod_traffic,
                "product_orders": prod_orders,
                "gsc": {
                    "clicks_w1": clicks_w1, "clicks_w2": clicks_w2,
                    "impressions_w1": imp_w1, "impressions_w2": imp_w2,
                    "keywords_w1": kw_w1, "keywords_w2": kw_w2,
                },
            }

            if section != sections[-1]:
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Run Root Cause Analysis", type="primary", use_container_width=True)

        if run_btn:
            if missing_keys:
                st.error(f"⚠️ Cannot run — missing API keys: `{'`, `'.join(missing_keys)}`. Add them to `.streamlit/secrets.toml` and restart the app.")
            else:
                stage2_results = {}
                progress = st.progress(0, text="Starting analysis...")

                for i, section in enumerate(sections):
                    inp = stage2_inputs[section]
                    wow = st.session_state["stage1_results"][section]

                    progress.progress((i * 2) / (len(sections) * 2 + 1), text=f"🔍 Fetching data for {section}...")

                    with st.spinner(f"Analysing {section}..."):
                        result = run_stage2(
                            section=section,
                            product_traffic=inp["product_traffic"] or f"{section} top product",
                            product_orders=inp["product_orders"] or f"{section} top product",
                            gsc_metrics=inp["gsc"],
                            wow_changes=wow,
                            serpapi_key=serpapi_key,
                            openai_key=openai_key,
                        )
                        stage2_results[section] = result

                    progress.progress((i * 2 + 2) / (len(sections) * 2 + 1), text=f"✅ {section} done.")

                progress.progress(1.0, text="✅ Analysis complete!")
                st.session_state["stage2_results"] = stage2_results

        # ── Display Stage 2 Results ──────────────────────────────────────────
        if "stage2_results" in st.session_state:
            st.markdown("---")
            st.markdown("### 🧠 Analysis Reports")

            for section, res in st.session_state["stage2_results"].items():
                st.markdown(f"""
                <div class="section-header">
                    <span class="section-chip">Section</span>
                    <span class="section-name">{section}</span>
                </div>
                """, unsafe_allow_html=True)

                inner_tabs = st.tabs(["🤖 AI Report", "💰 Price Comparison", "📰 News Intelligence"])

                with inner_tabs[0]:
                    st.markdown(f'<div class="ai-report">{res["ai_report"]}</div>', unsafe_allow_html=True)

                with inner_tabs[1]:
                    col_t, col_o = st.columns(2)
                    with col_t:
                        st.markdown("**Traffic-Dominating Product**")
                        price_data = res["price_comparison_traffic"]
                        if price_data and "error" not in price_data[0]:
                            price_df = pd.DataFrame([
                                {"Source": p["source"], "Title": p["title"][:40] + "..." if len(p["title"]) > 40 else p["title"], "Price": p["price"]}
                                for p in price_data
                            ])
                            st.dataframe(price_df, use_container_width=True, hide_index=True)
                        else:
                            st.warning("No price data found or error occurred.")

                    with col_o:
                        st.markdown("**Orders-Dominating Product**")
                        price_data_o = res["price_comparison_orders"]
                        if price_data_o and "error" not in price_data_o[0]:
                            price_df_o = pd.DataFrame([
                                {"Source": p["source"], "Title": p["title"][:40] + "..." if len(p["title"]) > 40 else p["title"], "Price": p["price"]}
                                for p in price_data_o
                            ])
                            st.dataframe(price_df_o, use_container_width=True, hide_index=True)
                        else:
                            st.warning("No price data found or error occurred.")

                with inner_tabs[2]:
                    col_n1, col_n2 = st.columns(2)
                    with col_n1:
                        st.markdown("**Traffic Product News**")
                        for article in res["news_traffic"]:
                            if "error" not in article:
                                st.markdown(f"""
                                <div class="news-card">
                                    <div class="news-title">{article['title']}</div>
                                    <div class="news-meta">{article['source']} · {article['date']}</div>
                                    <div class="news-snippet">{article['snippet']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.warning("News fetch error.")
                                break

                    with col_n2:
                        st.markdown("**Orders Product News**")
                        for article in res["news_orders"]:
                            if "error" not in article:
                                st.markdown(f"""
                                <div class="news-card">
                                    <div class="news-title">{article['title']}</div>
                                    <div class="news-meta">{article['source']} · {article['date']}</div>
                                    <div class="news-snippet">{article['snippet']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.warning("News fetch error.")
                                break

                st.markdown("<br>", unsafe_allow_html=True)