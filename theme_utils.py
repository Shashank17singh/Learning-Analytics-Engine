"""
Design system styling utilities for Learning-Analytics-Engine.
Implements UI/UX Pro Max and Hallmark-compliant modern-minimal dark theme.
"""

import streamlit as st


THEME_CSS = """
<style>
/* Hallmark & UI-UX-Pro-Max Design System · Data-Dense Dashboard
 * Theme: Modern Dark Slate with Electric Royal Accent
 * Accessibility: WCAG AA compliant contrast (>= 4.5:1), visible focus rings
 */
:root {
  --bg-canvas: #0d1117;
  --bg-surface: #161b22;
  --bg-surface-elevated: #21262d;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-default: #30363d;
  --border-focus: #3b82f6;
  --text-primary: #f0f6fc;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --accent-primary: #3b82f6;
  --accent-hover: #2563eb;
  --accent-active: #1d4ed8;
  --accent-success: #10b981;
  --accent-warning: #f59e0b;
  --accent-danger: #ef4444;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

/* App container */
.stApp {
  background-color: var(--bg-canvas) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
}

[data-testid="stHeader"] {
  background: transparent !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  letter-spacing: -0.02em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default) !important;
  padding-bottom: 0px;
}

.stTabs [data-baseweb="tab"] {
  height: 42px;
  background-color: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0px !important;
  color: var(--text-secondary) !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  padding: 0 16px !important;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-primary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  color: var(--accent-primary) !important;
  border-bottom: 2px solid var(--accent-primary) !important;
  font-weight: 600 !important;
}

/* Forms & Containers (Cards) */
[data-testid="stForm"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
  padding: 1.5rem !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
}

/* Metrics */
[data-testid="stMetric"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
  padding: 1rem 1.25rem !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
}

[data-testid="stMetricLabel"] {
  color: var(--text-secondary) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}

[data-testid="stMetricValue"] {
  color: var(--text-primary) !important;
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
}

/* Buttons */
.stButton > button, button[data-testid="baseButton-secondary"] {
  background-color: var(--bg-surface) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  padding: 0.45rem 1rem !important;
  transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.05s ease !important;
}

.stButton > button:hover, button[data-testid="baseButton-secondary"]:hover {
  background-color: var(--bg-surface-elevated) !important;
  border-color: var(--text-secondary) !important;
}

.stButton > button:active, button[data-testid="baseButton-secondary"]:active {
  transform: translateY(1px);
}

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"], button[data-testid="baseButton-primary"] {
  background-color: var(--accent-primary) !important;
  color: #ffffff !important;
  border: 1px solid var(--accent-primary) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
  transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.05s ease !important;
}

.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
  background-color: var(--accent-hover) !important;
  border-color: var(--accent-hover) !important;
}

.stButton > button[kind="primary"]:active, .stFormSubmitButton > button[kind="primary"]:active, button[data-testid="baseButton-primary"]:active {
  background-color: var(--accent-active) !important;
  transform: translateY(1px);
}

/* Inputs, Selectboxes & TextAreas */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
[data-baseweb="select"] > div {
  background-color: var(--bg-canvas) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-size: 0.925rem !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
[data-baseweb="select"]:focus-within > div {
  border-color: var(--border-focus) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
}

/* Select dropdown menu */
[data-baseweb="popover"], [data-baseweb="menu"] {
  background-color: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
}

[data-baseweb="menu"] li {
  color: var(--text-primary) !important;
}

[data-baseweb="menu"] li:hover, [data-baseweb="menu"] li[aria-selected="true"] {
  background-color: var(--bg-surface-elevated) !important;
  color: var(--accent-primary) !important;
}

/* Sliders */
[data-testid="stSlider"] [role="slider"] {
  background-color: var(--accent-primary) !important;
  border: 2px solid var(--text-primary) !important;
  box-shadow: 0 0 6px rgba(59, 130, 246, 0.5) !important;
}

[data-testid="stSlider"] div[data-baseweb="slider"] div {
  color: var(--text-secondary) !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
  color: var(--text-primary) !important;
  font-size: 0.925rem !important;
}

/* Cards & Section Panels */
.analytics-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.portal-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-top: 1rem;
}
.portal-badge {
  display: inline-block;
  background-color: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  margin-bottom: 0.75rem;
}
.portal-title {
  font-size: 2.2rem !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
  margin: 0 0 0.5rem 0 !important;
  letter-spacing: -0.03em;
}
.portal-subtitle {
  color: var(--text-secondary) !important;
  font-size: 0.975rem !important;
  max-width: 580px;
  margin: 0 auto;
}
.info-callout {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid var(--accent-primary);
  border-radius: var(--radius-sm);
  padding: 0.75rem 1rem;
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}
.info-callout strong {
  color: var(--text-primary);
}
.info-callout code {
  background-color: var(--bg-surface-elevated);
  border: 1px solid var(--border-subtle);
  color: #93c5fd;
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>
"""


def inject_custom_theme() -> None:
    """Injects the Hallmark-grade dark theme CSS into the Streamlit session."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def configure_matplotlib_dark() -> None:
    """Applies modern dark palette settings to matplotlib rcParams."""
    try:
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "figure.facecolor": "#161b22",
                "axes.facecolor": "#161b22",
                "axes.edgecolor": "#30363d",
                "axes.labelcolor": "#8b949e",
                "axes.titlecolor": "#f0f6fc",
                "text.color": "#f0f6fc",
                "xtick.color": "#8b949e",
                "ytick.color": "#8b949e",
                "grid.color": "#21262d",
                "grid.alpha": 0.7,
                "legend.facecolor": "#161b22",
                "legend.edgecolor": "#30363d",
                "figure.autolayout": True,
            }
        )
    except ImportError:
        pass
