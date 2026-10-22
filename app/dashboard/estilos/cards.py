CSS_CARDS = """
.v14-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 4px;
    animation: v14FadeUp 0.35s ease-out both;
}

.v14-greeting-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.95rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.15 !important;
}

.v14-greeting-sub {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: 0;
    font-weight: 400;
}

.v14-header-pills {
    display: flex;
    align-items: center;
    gap: 10px;
}

.v14-sync-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.command-hero {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 22px 26px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    animation: v14FadeUp 0.35s ease-out both;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(16, 185, 129, 0.1);
    color: #34D399;
    padding: 4px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
    border: 1px solid rgba(16, 185, 129, 0.24);
    margin-bottom: 8px;
}

.hero-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 8px #10B981;
}

.hero-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.025em !important;
    line-height: 1.15 !important;
}

.hero-subtitle {
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin: 0;
}

.hero-right {
    text-align: right;
    background: #0A101A;
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 12px 18px;
}

.v14-overview-grid {
    display: grid;
    grid-template-columns: 1.15fr 1fr 1.25fr;
    gap: 16px;
    margin-bottom: 22px;
    animation: v14FadeUp 0.45s ease-out both;
}

.v14-balance-card {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
    position: relative;
    overflow: hidden;
}

.v14-card-label {
    font-size: 0.84rem;
    color: var(--text-secondary);
    font-weight: 500;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.v14-big-number {
    font-family: 'Outfit', sans-serif;
    font-variant-numeric: tabular-nums;
    font-size: 2.75rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin: 12px 0 8px 0;
}

.v14-trend-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.14);
    color: #34D399;
}

.v14-action-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 18px;
}

.v14-btn-dark {
    background: #172336;
    color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
}

.v14-btn-emerald {
    background: #10B981;
    color: #06281E;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
}

.v14-stat-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 12px;
}

.v14-mini-stat {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.v14-mini-stat:hover {
    transform: translateY(-2px);
    border-color: rgba(16, 185, 129, 0.35);
}

.v14-mini-stat.featured {
    background: linear-gradient(145deg, #10B981 0%, #059669 100%);
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 12px 28px rgba(16, 185, 129, 0.25);
}

.v14-mini-stat.featured .v14-mini-label {
    color: rgba(255, 255, 255, 0.88);
}

.v14-mini-stat.featured .v14-mini-val {
    color: #FFFFFF;
}

.v14-mini-stat.featured .v14-mini-sub {
    color: rgba(255, 255, 255, 0.82);
}

.v14-mini-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.v14-mini-val {
    font-family: 'Outfit', sans-serif;
    font-variant-numeric: tabular-nums;
    font-size: 1.65rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 6px 0 2px 0;
    line-height: 1.1;
}

.v14-mini-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
}

.v14-chart-card {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 22px 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
}

.v14-bars-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    height: 126px;
    padding-top: 18px;
    margin-top: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 10px;
}

.v14-bar-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
    justify-content: flex-end;
    gap: 6px;
}

.v14-bar-pair {
    display: flex;
    align-items: flex-end;
    gap: 4px;
    height: 92px;
    width: 100%;
    justify-content: center;
}

.v14-bar-pill {
    width: 12px;
    border-radius: 6px 6px 3px 3px;
    transition: height 0.3s ease;
}

.v14-bar-lbl {
    font-size: 0.7rem;
    color: var(--text-secondary);
    max-width: 64px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-align: center;
}

.v14-goals-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}

.v14-goal-card {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 16px 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.v14-goal-card:hover {
    transform: translateY(-2px);
    border-color: rgba(16, 185, 129, 0.3);
}

.v14-ring {
    width: 68px;
    height: 68px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 10px 0;
    position: relative;
}

.v14-ring-inner {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: #0F1724;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #FFFFFF;
}

.v14-asset-pass {
    background: linear-gradient(135deg, #162235 0%, #090F1A 60%, #0D1F22 100%);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 22px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    margin-bottom: 14px;
}

.v14-asset-pass::after {
    content: "";
    position: absolute;
    right: -30px;
    bottom: -40px;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, transparent 70%);
    pointer-events: none;
}

.bento-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
    animation: v14FadeUp 0.4s ease-out both;
}

.bento-kpi-card {
    background: #0F1724;
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.bento-kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(16, 185, 129, 0.35);
}

.bento-kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.bento-kpi-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.bento-kpi-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}

.bento-kpi-icon.emerald {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34D399;
}

.bento-kpi-icon.cyan {
    background: rgba(14, 165, 233, 0.12);
    border: 1px solid rgba(14, 165, 233, 0.25);
    color: #38BDF8;
}

.bento-kpi-icon.amber {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
}

.bento-kpi-icon.rose {
    background: rgba(244, 63, 94, 0.12);
    border: 1px solid rgba(244, 63, 94, 0.25);
    color: #FB7185;
}

.bento-kpi-value {
    font-family: 'Outfit', sans-serif;
    font-variant-numeric: tabular-nums;
    font-size: 1.95rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.1;
    margin-bottom: 10px;
}

.bento-kpi-bar {
    width: 100%;
    height: 5px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 8px;
}

.bento-kpi-bar-fill {
    height: 100%;
    border-radius: 999px;
}

.bento-kpi-sub {
    font-size: 0.76rem;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
"""
