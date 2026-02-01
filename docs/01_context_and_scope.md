# Context and Scope

## Purpose
This project simulates the end-to-end delivery of an analytics foundation for a SaaS product (Time Doctor-like). The goal is to design a realistic data model that supports time-based analysis (trends, cohorts, engagement), includes common edge cases (late-arriving events, missing values, outliers), and can be consumed by BI tooling for standardized reporting.

## Audience
- Data & Analytics stakeholders (Director of Data, Analytics/BI team)
- Data Engineering (pipeline + transformation readiness)
- Product and Business stakeholders (metrics, adoption, usage patterns)
- Solutions / Customer-facing teams (account health and usage views)

## Scope (What we will model)
We will model product usage through an event-driven dataset with:
- Accounts (customer organizations/teams)
- Users (members of accounts)
- Events (product interactions and work tracking signals)

The model will support:
- Daily/weekly usage trends
- Engagement metrics (DAU/WAU/MAU-style patterns)
- Retention proxies (activity-based)
- Productivity/output proxies (work session durations, tasks completed)

## Out of Scope
To keep the model realistic but not overly complex, we intentionally exclude:
- Financial/billing/revenue indicators
- Complex project/task hierarchies (beyond minimal task identifiers)

## Data Layers (Conceptual)
This assignment will follow a layered approach:
- Raw: generated source tables (accounts, users, events)
- Intermediate: cleaned/standardized events and derived session/activity logic
- Analytics-ready marts: curated datasets for BI and self-service

