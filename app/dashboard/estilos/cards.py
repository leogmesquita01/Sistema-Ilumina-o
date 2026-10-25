CSS_CARDS = """
.v14-header{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;margin:0 0 20px;padding:0 0 16px;border-bottom:1px solid var(--rule)}
.v14-greeting-title,.hero-title{font-family:'IBM Plex Sans',sans-serif!important;font-size:1.55rem!important;font-weight:600!important;color:var(--text)!important;letter-spacing:-.035em!important;line-height:1.2!important;margin:0 0 5px!important}
.v14-greeting-sub,.hero-subtitle{font-size:.9rem;color:var(--muted);margin:0;line-height:1.5}
.v14-header-pills{display:flex;align-items:center;gap:8px}
.v14-sync-pill,.hero-badge{display:inline-flex;align-items:center;gap:7px;background:var(--raised);color:var(--muted);padding:5px 9px;border-radius:4px;font-size:.75rem;border:1px solid var(--border)}
.hero-dot{width:7px;height:7px;border-radius:50%;background:#3e7954;display:inline-block}
.command-hero{background:var(--raised);border:1px solid var(--border);border-radius:var(--radius-card);padding:18px 20px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:none}
.hero-right{background:#fff;border:1px solid var(--border);border-radius:6px;padding:10px 14px;text-align:right}
.v14-overview-grid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:20px;margin-bottom:18px}
.v14-balance-card,.v14-chart-card,.v14-mini-stat,.v14-goal-card,.bento-kpi-card,.v14-asset-pass,.panel-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius-card);box-shadow:none}
.v14-balance-card,.v14-chart-card,.panel-card{padding:18px 20px;margin-bottom:14px}
.v14-card-label,.v14-mini-label,.bento-kpi-label{font-size:.82rem;color:var(--muted);font-weight:500}
.v14-big-number,.v14-mini-val,.bento-kpi-value{font-family:'IBM Plex Sans',sans-serif;font-variant-numeric:tabular-nums;font-size:1.75rem;font-weight:500;color:var(--text);letter-spacing:-.025em;line-height:1.15;margin:9px 0 5px}
.v14-mini-sub,.bento-kpi-sub{font-size:.76rem;color:var(--soft)}
.v14-stat-2x2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.v14-mini-stat{padding:14px 15px;display:flex;flex-direction:column;justify-content:center}
.v14-mini-stat.featured{background:#edf3ed;border-color:#d4e0d4}.v14-mini-stat.featured .v14-mini-val{color:var(--accent)}
.v14-goals-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.v14-goal-card{padding:14px;display:flex;flex-direction:column;align-items:center;text-align:center}
.v14-ring{width:62px;height:62px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:10px 0;position:relative}
.v14-ring-inner{width:48px;height:48px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-variant-numeric:tabular-nums;font-size:.82rem;font-weight:600;color:var(--text)}
.v14-bars-wrap{display:flex;align-items:flex-end;justify-content:space-between;gap:10px;height:118px;padding:12px 0 8px;margin-top:8px;border-bottom:1px solid var(--rule)}
.v14-bar-col{flex:1;display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end;gap:6px}.v14-bar-pair{display:flex;align-items:flex-end;gap:3px;height:88px;width:100%;justify-content:center}.v14-bar-pill{width:12px;border-radius:2px 2px 0 0}.v14-bar-lbl{font-size:.7rem;color:var(--muted);max-width:64px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center}
.v14-activity-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--rule);gap:10px}.v14-activity-row:last-child{border-bottom:0}.v14-activity-left{display:flex;align-items:center;gap:10px}.v14-avatar{width:34px;height:34px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-family:'IBM Plex Mono',monospace;font-size:.72rem;font-weight:500;flex-shrink:0}
.v14-action-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}.v14-btn-dark,.v14-btn-emerald{border-radius:5px;padding:9px 12px;font-size:.8rem;font-weight:600;text-align:center}.v14-btn-dark{background:#fff;color:var(--text);border:1px solid var(--control)}.v14-btn-emerald{background:var(--accent);color:#fff;border:1px solid var(--accent)}
.bento-kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:18px}.bento-kpi-card{padding:14px 16px}.bento-kpi-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}.bento-kpi-icon{width:24px;height:24px;display:flex;align-items:center;justify-content:center;color:var(--muted);background:transparent!important;border:0!important}.bento-kpi-icon.emerald{color:var(--positive)}.bento-kpi-icon.amber{color:var(--warning)}.bento-kpi-icon.rose{color:var(--negative)}.bento-kpi-bar{width:100%;height:3px;background:#edf0ed;border-radius:2px;overflow:hidden;margin:8px 0 6px}.bento-kpi-bar-fill{height:100%;border-radius:2px}.v14-asset-pass{padding:16px 18px;margin-bottom:14px;position:relative;overflow:hidden}
@media(max-width:1024px){.v14-overview-grid{grid-template-columns:1fr}.bento-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.v14-goals-grid{grid-template-columns:1fr}.v14-goal-card{flex-direction:row;justify-content:space-between;text-align:left}.v14-ring{margin:0}.v14-overview-grid{gap:12px}}
@media(max-width:560px){.v14-header{align-items:flex-start}.v14-greeting-title,.hero-title{font-size:1.3rem!important}.command-hero{padding:15px}.hero-right{text-align:left}.v14-stat-2x2{grid-template-columns:1fr 1fr}.bento-kpi-grid{gap:8px}.bento-kpi-card{padding:12px}.v14-big-number,.v14-mini-val,.bento-kpi-value{font-size:1.45rem}.panel-card{padding:15px}}
"""
