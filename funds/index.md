# VC OS — Fund Index

## Overview

| Region | Funds | Countries Covered |
|---|---|---|
| [Europe](europe/index.md) | 8 | 1 of 31 |
| [USA](usa/index.md) | 0 | 0 of 5 hubs |
| **Total** | **8** | |

---

## Routing

Each fund lives in exactly one folder — the country of its primary presence:

```
funds/
├── europe/
│   ├── index.md               ← all European funds + cross-geography routing
│   ├── denmark/
│   │   ├── index.md
│   │   └── <fund-slug>/
│   ├── united-kingdom/
│   │   ├── index.md
│   │   └── <fund-slug>/
│   └── ... (31 countries)
└── usa/
    ├── index.md               ← all USA funds
    ├── bay-area/
    ├── new-york/
    ├── boston/
    ├── los-angeles/
    └── other/
```

If a fund invests across multiple geographies, its `profile.md` lists `secondary_geographies`. Those country `index.md` files carry a cross-reference row in their **Based Elsewhere, Actively Investing Here** section — linking back to the fund's primary folder. No data is duplicated.
