# -*- coding: utf-8 -*-

def get_custom_css(theme=None):
    # Use Streamlit's native CSS variables to automatically adapt to any Streamlit theme
    bg_color = "var(--background-color)"
    text_color = "var(--text-color)"
    muted_text = "var(--text-color)"
    card_bg = "var(--secondary-background-color)"
    sidebar_bg = "var(--secondary-background-color)"
    form_bg = "var(--secondary-background-color)"
    border_color = "rgba(128, 128, 128, 0.15)"
    input_bg = "var(--background-color)"
    tab_bg = "var(--secondary-background-color)"
    chat_bg = "var(--secondary-background-color)"
    success_bg = "rgba(46, 204, 113, 0.1)"
    error_bg = "rgba(231, 76, 60, 0.1)"
    success_border = "#2ecc71"
    error_border = "#e74c3c"
    text_on_light_success = "var(--text-color)"
    text_on_light_error = "var(--text-color)"
    hover_bg = "rgba(128, 128, 128, 0.1)"
    hover_text = "var(--text-color)"

    return f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@200;300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Background and Colors */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"], .main, .stApp {{
        font-family: 'Kanit', 'Outfit', sans-serif;
    }}

    /* General text overrides */
    p, li, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{
        color: {text_color} !important;
        opacity: 0.8 !important;
    }}


    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', 'Kanit', sans-serif;
        color: {text_color} !important;
    }}

    /* Force Sidebar Background and Text */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebarNav"] {{
        border-right: 1px solid {border_color} !important;
    }}

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{
        color: {text_color} !important;
    }}
    /* Sidebar spans: exclude badge spans that have their own background-color */
    [data-testid="stSidebar"] span:not([style*="background-color"]) {{
        color: {text_color} !important;
    }}

    /* Navigation menu headers */
    .sidebar-title {{
        font-family: 'Outfit', sans-serif;
        color: {text_color} !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }}

    /* Glassmorphic Cards for Dashboard and Lessons */
    .dashboard-card {{
        background: linear-gradient(145deg, {card_bg}, rgba(255,255,255,0.02)) !important;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid {border_color} !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .dashboard-card:hover {{
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 12px 30px rgba(0, 75, 135, 0.25);
        border: 1px solid #FFCD00 !important;
    }}

    /* Match Game Card Style */
    .match-card {{
        background-color: {card_bg} !important;
        border: 2px solid {border_color} !important;
        border-radius: 12px;
        padding: 25px 15px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
        color: {text_color} !important;
    }}

    /* Sweden accent badge */
    .sweden-badge {{
        background-color: #004B87 !important;
        color: #FFCD00 !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 10px;
    }}

    /* Thai helper badge */
    .thai-badge {{
        background-color: #E21833 !important;
        color: white !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 10px;
        margin-left: 5px;
    }}

    /* Lesson content cards */
    .lesson-section {{
        background-color: {card_bg} !important;
        border-left: 5px solid #004B87 !important;
        padding: 20px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-top: 1px solid {border_color} !important;
        border-right: 1px solid {border_color} !important;
        border-bottom: 1px solid {border_color} !important;
    }}

    /* Form container styles */
    [data-testid="stForm"] {{
        background-color: {form_bg} !important;
        background: {form_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 12px;
        padding: 20px;
    }}

    /* Widget Labels */
    label[data-testid="stWidgetLabel"] p, label, .stWidgetLabel p {{
        color: {text_color} !important;
    }}

    /* Inputs and text fields styling */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="input"] input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease-in-out;
    }}

    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus, [data-baseweb="input"] input:focus {{
        border-color: #FFCD00 !important;
        box-shadow: 0 0 8px rgba(255, 205, 0, 0.2) !important;
    }}

    /* Selectboxes and dropdowns styling */
    [data-baseweb="select"], [data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}

    [data-baseweb="select"] * {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}

    /* Dropdown menu items and lists inside portals */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], li[role="option"] {{
        background-color: {sidebar_bg} !important;
        color: {text_color} !important;
        background: {sidebar_bg} !important;
    }}

    /* Sub-options text color */
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] * {{
        background-color: transparent !important;
        color: {text_color} !important;
    }}

    /* Hover effect on dropdown menu items */
    li[role="option"]:hover, [data-baseweb="menu"] li:hover, [role="option"][aria-selected="true"] {{
        background-color: {hover_bg} !important;
        color: {hover_text} !important;
    }}

    /* Ensure sub-options inherit the hover color */
    li[role="option"]:hover *, [data-baseweb="menu"] li:hover *, [role="option"][aria-selected="true"] * {{
        color: {hover_text} !important;
    }}

    /* Tabs Styling */
    [data-baseweb="tab-list"] {{
        background-color: {sidebar_bg} !important;
        border-radius: 8px 8px 0 0 !important;
        border-bottom: 2px solid {border_color} !important;
    }}
    [data-baseweb="tab"] {{
        color: {text_color} !important;
        opacity: 0.7 !important;
        background-color: transparent !important;
    }}
    [data-baseweb="tab"][aria-selected="true"] {{
        color: var(--primary-color) !important;
        opacity: 1 !important;
        font-weight: bold !important;
        border-bottom-color: var(--primary-color) !important;
    }}

    /* Radio button containers */
    [data-testid="stRadio"] label, [data-testid="stRadio"] div, [data-testid="stRadio"] p {{
        color: {text_color} !important;
    }}

    /* Custom Streamlit button adjustments */
    div.stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        padding: 8px 16px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    div.stButton > button:hover {{
        background-color: #004B87 !important;
        color: #ffffff !important;
        border-color: #004B87 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 75, 135, 0.3) !important;
    }}
    
    /* Primary buttons custom styling */
    div.stButton > button[kind="primary"] {{
        background-color: #004B87 !important;
        color: #ffffff !important;
        border: 1px solid #004B87 !important;
    }}
    
    div.stButton > button[kind="primary"]:hover {{
        background-color: #003660 !important;
        border-color: #003660 !important;
        box-shadow: 0 6px 15px rgba(0, 54, 96, 0.4) !important;
    }}

    /* Ensure inner button elements inherit colors correctly */
    div.stButton > button * {{
        color: inherit !important;
    }}

    /* Custom progress bar accent color */
    .stProgress > div > div > div > div {{
        background-color: #FFCD00 !important;
    }}
    
    [data-testid="stProgress"] > div {{
        background-color: {card_bg} !important;
    }}

    /* Chat message bubble styling overrides */
    [data-testid="stChatMessage"] {{
        background-color: {chat_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px;
    }}

    /* Quiz feedback boxes */
    .quiz-feedback-success {{
        padding: 15px;
        background-color: {success_bg} !important;
        color: {text_on_light_success} !important;
        border-radius: 8px;
        border-left: 5px solid {success_border} !important;
        margin-top: 15px;
    }}

    .quiz-feedback-error {{
        padding: 15px;
        background-color: {error_bg} !important;
        color: {text_on_light_error} !important;
        border-radius: 8px;
        border-left: 5px solid {error_border} !important;
        margin-top: 15px;
    }}

    /* Hide footer and viewer badges, but keep stHeader and MainMenu visible */
    footer {{
        display: none !important;
    }}
    div[class^="viewerBadge"] {{
        display: none !important;
    }}
    div[data-testid="stConnectionStatus"] {{
        display: none !important;
    }}

    /* Vocabulary card responsive styles */
    .vocab-card {{
        display: flex;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        overflow: hidden;
        min-height: 180px;
        transition: all 0.3s ease;
    }}
    .vocab-card:hover {{
        box-shadow: 0 8px 25px rgba(0, 75, 135, 0.15);
        transform: translateY(-2px);
    }}
    .vocab-image {{
        width: 280px;
        min-width: 280px;
        background-size: cover;
        background-position: center;
        border-left: 1px solid rgba(128, 128, 128, 0.1);
    }}
    @media (max-width: 768px) {{
        .vocab-card {{
            flex-direction: column !important;
        }}
        .vocab-image {{
            width: 100% !important;
            min-width: 100% !important;
            height: 220px !important;
            border-left: none !important;
            border-top: 1px solid rgba(128, 128, 128, 0.15) !important;
        }}
    }}

    </style>
    """
