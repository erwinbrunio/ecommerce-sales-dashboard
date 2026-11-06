# 💼 Commercial E-Commerce Sales & Performance Dashboard

An end-to-end analytics engineering and interactive dashboard solution that consolidates seven relational e-commerce tables into an audited star-schema fact model (`fact_sales.parquet`), visualized through a high-performance **Streamlit** executive web application.

---

## 📌 Executive Summary

* **Net Realized Revenue:** Generated **₱6,823,900.13** across **15,000** distinct orders (37,501 verified line items).
* **Basket Efficiency:** Enterprise Average Order Value (AOV) settled at **₱454.93**, averaging 2.50 units per transaction.
* **Operating Profitability:** Maintained an aggregate gross profit of **₱2,005,627.07**, representing a **29.39% gross margin**.
* **Omnichannel Revenue Parity:** Revenue split evenly across **Web (33.63%)**, **Marketplace (33.29%)**, and **Mobile App (33.07%)**.
* **Channel Cart Variance:** Web drives the highest cart spend at **₱461.97 AOV** compared to Mobile App (₱452.75) and Marketplace (₱450.14).
* **Core Department Leaders:** **Toys** (₱952.4K / 30.3% margin) and **Electronics** (₱927.5K / 31.0% margin) anchor company margins.
* **Geographic Balance:** Demand is distributed across 6 Philippine administrative regions, led by **Central Luzon** (₱1.17M) and **Central Visayas** (₱1.15M).
* **Customer Retention:** An **84.14% repeat purchase rate** (4,001 repeat buyers out of 4,755 customers) confirms strong brand engagement.
* **Operational Order Friction:** 1,235 orders were cancelled (8.23%) and 578 were returned (3.85%), totaling **12.09% post-purchase attrition**.
* **Root-Cause Returns:** **84.83% of all return incidents** stem from merchant-controllable issues (defects, missing parts, picking errors, sizing mismatch).
* **Promotional Discipline:** Median discount applied was restricted to **6.00%**, preventing bottom-line margin erosion.

---

## 📂 Repository Architecture

```text
ecommerce-sales-dashboard/
├── data/                            # Raw and cleaned data artifacts
├── notebooks/                       # Data engineering & cleaning code
├── src/                             # Core ETL scripts
├── app/                             # Streamlit dashboard application files
├── LICENSE                          # Project license
└── README.md                        # Project documentation