"""
Stage 2: Reason Analysis
- Price comparison via SerpAPI Google Shopping
- News/information retrieval via SerpAPI News
- Synthesis via OpenAI GPT-4
"""

import os
import json
import requests


# ── SerpAPI helpers ──────────────────────────────────────────────────────────

SERPAPI_BASE = "https://serpapi.com/search"


def _serpapi_get(params: dict, api_key: str) -> dict:
    params["api_key"] = api_key
    resp = requests.get(SERPAPI_BASE, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def get_price_comparison(product_name: str, serpapi_key: str) -> list[dict]:
    """
    Search Google Shopping for the product to find prices across platforms.
    Returns a list of {source, price, link} dicts.
    """
    params = {
        "engine": "google_shopping",
        "q": f"{product_name} site:telstra.com OR site:jbhifi.com.au OR site:harvey-norman.com.au OR site:officeworks.com.au",
        "gl": "au",
        "hl": "en",
        "num": 10,
    }
    try:
        data = _serpapi_get(params, serpapi_key)
        results = []
        for item in data.get("shopping_results", [])[:8]:
            results.append({
                "source": item.get("source", "Unknown"),
                "price": item.get("price", "N/A"),
                "extracted_price": item.get("extracted_price"),
                "title": item.get("title", product_name),
                "link": item.get("link", ""),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def get_news_articles(product_name: str, serpapi_key: str) -> list[dict]:
    """
    Search Google News for recent articles about the product.
    Returns list of {title, source, date, snippet, link}.
    """
    params = {
        "engine": "google_news",
        "q": f"{product_name} Australia deal offer launch",
        "gl": "au",
        "hl": "en",
        "num": 8,
    }
    try:
        data = _serpapi_get(params, serpapi_key)
        results = []
        for item in data.get("news_results", [])[:8]:
            results.append({
                "title": item.get("title", ""),
                "source": item.get("source", {}).get("name", "Unknown") if isinstance(item.get("source"), dict) else item.get("source", "Unknown"),
                "date": item.get("date", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


# ── OpenAI synthesis ─────────────────────────────────────────────────────────

def synthesize_reasons(
    section: str,
    product_traffic: str,
    product_orders: str,
    date_w1: str,
    date_w2: str,
    gsc_metrics: dict,
    wow_changes: dict,
    price_data_traffic: list,
    news_data_traffic: list,
    price_data_orders: list,
    news_data_orders: list,
    openai_key: str,
) -> str:
    """
    Use OpenAI to synthesize a narrative explaining WoW changes.
    """
    import openai

    client = openai.OpenAI(api_key=openai_key)

    prompt = f"""
You are a senior digital analytics consultant analysing Week-on-Week (WoW) performance changes for Telstra.com's "{section}" section.

## Reporting Period
- Week 1 starting: {date_w1}
- Week 2 starting: {date_w2}

## WoW Performance Summary
- Traffic Change: {wow_changes.get('traffic_change_pct', 'N/A'):.2f}% (W1: {wow_changes.get('week1_traffic')} → W2: {wow_changes.get('week2_traffic')})
- Orders Change: {wow_changes.get('orders_change_pct', 'N/A'):.2f}% (W1: {wow_changes.get('week1_orders')} → W2: {wow_changes.get('week2_orders')})
- Conversion Rate W1: {f"{wow_changes.get('week1_cvr'):.2f}%" if wow_changes.get('week1_cvr') else 'N/A'}
- Conversion Rate W2: {f"{wow_changes.get('week2_cvr'):.2f}%" if wow_changes.get('week2_cvr') else 'N/A'}
- CVR Change: {f"{wow_changes.get('cvr_change_pct'):.2f}%" if wow_changes.get('cvr_change_pct') else 'N/A'}

## Google Search Console Metrics
- Clicks W1→W2: {gsc_metrics.get('clicks_w1')} → {gsc_metrics.get('clicks_w2')}
- Impressions W1→W2: {gsc_metrics.get('impressions_w1')} → {gsc_metrics.get('impressions_w2')}
- Keywords W1→W2: {gsc_metrics.get('keywords_w1')} → {gsc_metrics.get('keywords_w2')}

## Dominating Products
- Traffic: {product_traffic}
- Orders: {product_orders}

## Price Comparison Data (Traffic-dominating product: {product_traffic})
{json.dumps(price_data_traffic, indent=2)}

## News & Market Intelligence (Traffic-dominating product: {product_traffic})
{json.dumps(news_data_traffic, indent=2)}

## Price Comparison Data (Orders-dominating product: {product_orders})
{json.dumps(price_data_orders, indent=2)}

## News & Market Intelligence (Orders-dominating product: {product_orders})
{json.dumps(news_data_orders, indent=2)}

---

Please write a structured analysis report with the following sections:

### 1. Executive Summary
2-3 sentences summarising the WoW shift for the period {date_w1} vs {date_w2}.

### 2. Traffic Analysis
Explain the traffic change. Connect GSC metrics (clicks, impressions, keywords) to the traffic movement. Identify whether organic search is driving or limiting traffic.

### 3. Orders & Conversion Analysis
Explain the order change. Analyse the conversion rate shift — did more or fewer visitors convert? Is the change driven by traffic volume or conversion efficiency?

### 4. Price & Competitive Intelligence
Based on the price comparison data, assess whether pricing differences or promotions on Telstra.com vs competitors could explain the change. Be specific about price gaps found.

### 5. News & Market Context
Summarise relevant news. Did any product launch, deal, announcement, or external event likely influence the WoW change during this period?

### 6. Root Cause Assessment
Provide a prioritised list of likely root causes (most likely first) with confidence level (High / Medium / Low).

### 7. Recommendations
3-5 actionable recommendations for the team.

Write in a professional, data-driven tone. Be specific, not generic.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1800,
    )
    return response.choices[0].message.content


# ── Main Stage 2 runner ──────────────────────────────────────────────────────

def run_stage2(
    section: str,
    product_traffic: str,
    product_orders: str,
    date_w1: str,
    date_w2: str,
    gsc_metrics: dict,
    wow_changes: dict,
    serpapi_key: str,
    openai_key: str,
) -> dict:
    """
    Orchestrates Stage 2 for a single section.
    Returns a dict with all raw data and the synthesized report.
    """
    # Price comparison
    price_traffic = get_price_comparison(product_traffic, serpapi_key)
    price_orders = get_price_comparison(product_orders, serpapi_key) if product_orders != product_traffic else price_traffic

    # News
    news_traffic = get_news_articles(product_traffic, serpapi_key)
    news_orders = get_news_articles(product_orders, serpapi_key) if product_orders != product_traffic else news_traffic

    # Synthesis
    report = synthesize_reasons(
        section=section,
        product_traffic=product_traffic,
        product_orders=product_orders,
        date_w1=date_w1,
        date_w2=date_w2,
        gsc_metrics=gsc_metrics,
        wow_changes=wow_changes,
        price_data_traffic=price_traffic,
        news_data_traffic=news_traffic,
        price_data_orders=price_orders,
        news_data_orders=news_orders,
        openai_key=openai_key,
    )

    return {
        "section": section,
        "price_comparison_traffic": price_traffic,
        "price_comparison_orders": price_orders,
        "news_traffic": news_traffic,
        "news_orders": news_orders,
        "ai_report": report,
    }