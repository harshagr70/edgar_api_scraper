---
title: "📊 Edgar Financial Statement Analyzer"
output: html_document
---

## 🧠 What is this?
A Python tool that automatically downloads and normalizes **multi-year financial statements** from **SEC Edgar**, solving the problem of inconsistent line-item labels across years.

---

## 🚨 The Problem
Companies often change how they label items between years:

| Year | Label Example |
|------|----------------|
| 1 | Research & Development |
| 2 | R&D |
| 3 | R&D Expenses |

These all refer to the *same* item but appear as separate rows when merged naively.

---

## 💡 The Solution
This tool intelligently matches items across years using:

- **GAAP codes** (official accounting standard identifiers)  
- **Label matching** (normalized text comparison)  
- **Value matching** (if values match, they’re likely the same item)  
- **AI matching** (GPT-4 detects semantic equivalence)

---

## 🎁 What You Get

**Input:**  
- Ticker symbol (e.g., `AAPL`)  
- Number of years to analyze  

**Output:**  
- Unified financial statements with **aligned line items**

✅ Fetches data directly from **SEC Edgar API** — no manual downloads  
✅ Merges 3 + years into a single, consistent view  
✅ Interactive **Streamlit web UI**  
✅ Excel export with clean formatting  

---

## 💼 Use Cases

| User | Purpose |
|------|----------|
| **Investors** | Quick multi-year performance analysis |
| **Analysts** | Ready-to-use data for financial models |
| **Researchers** | Structured data extraction for empirical work |

---

## 🧾 Bottom Line
Enter a **ticker symbol**, and get **perfectly aligned multi-year financial statements** in seconds —  
no more manual PDF wrangling required!

