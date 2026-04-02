# Branded Recipe Chatbot SaaS

# This README is going to be changing, since the project is **in progress**. Some elements may change, especially the Tech Stack

## 📖 Overview

This repository contains the source code and documentation for my engineering thesis project: a **Software-as-a-Service (SaaS) Recipe Chatbot** designed for the FMCG food industry. 

The chatbot is built to be easily integrated into the websites of various food brands (e.g., Knorr, Winiary, Roleski). It acts as a culinary assistant, providing users with personalized recipe recommendations based on their dietary preferences, meal types, and specific requests (e.g., "I need a low-calorie vegan dinner"). 

The unique value proposition of this SaaS is its **Smart Brand Integration** feature: the bot intelligently substitutes generic ingredients within the recommended recipes with the client's specific branded products (e.g., automatically replacing "mayonnaise" with "Winiary mayonnaise").

## ✨ Key Features

* **Customizable SaaS Solution:** Architecture designed to support multiple brands with distinct product portfolios.
* **Context-Aware Recommendations:** Processes natural language queries to understand dietary restrictions, meal times, and caloric limits.
* **Dynamic Product Placement:** Seamlessly replaces generic concepts with actual client products to drive marketing and sales.
* **Deterministic Pre-filtering:** Ensures strict adherence to user constraints (e.g., zero meat in vegan requests) using rule-based filtering before LLM processing.

## 🧠 System Architecture: Modified RAG

To ensure high accuracy, prevent LLM hallucinations, and maintain strict dietary compliance, the application uses a **Modified Retrieval-Augmented Generation (RAG)** approach.

1.  **Data Storage:** The entire recipe database is stored in a structured `JSON` file.
2.  **Logic & Pre-filtering (Code Level):** When a user submits a prompt, the system extracts the constraints (e.g., "vegan", "dinner"). The backend logic deterministically filters the `JSON` database to exclude any recipes that violate these rules (e.g., filtering out meat dishes or breakfast options).
3.  **Context Injection:** The pre-filtered, highly relevant subset of recipes is passed to the Large Language Model (LLM) as context.
4.  **Selection & Brand Substitution (LLM Level):** The LLM evaluates the subset, selects the top *x* most suitable recipes, formats the output, and applies the targeted product substitutions based on the current client's profile.

## 🛠️ Tech Stack

* **Backend:** [Python]
* **LLM Integration:** [OpenAI API]
* **Database:** [currently local csv, json files]
* **Frontend / Widget:** [~~React]
