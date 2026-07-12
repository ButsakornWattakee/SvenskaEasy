# -*- coding: utf-8 -*-

def get_custom_css(theme="Dark"):
    if theme == "Light":
        bg_color = "#f4f6fa"           # Soft pastel grey-blue background
        text_color = "#1e293b"         # Deep slate for high contrast readability
        muted_text = "#475569"         # Muted slate grey
        card_bg = "#ffffff"            # Pure white cards
        sidebar_bg = "#e9ecef"         # Muted sidebar background
        form_bg = "#ffffff"
        border_color = "rgba(0, 0, 0, 0.08)"
        input_bg = "#ffffff"
        tab_bg = "#e9ecef"
        chat_bg = "#e9ecef"
        success_bg = "rgba(16, 185, 129, 0.1)"  # Soft emerald green bg
        error_bg = "rgba(239, 68, 68, 0.1)"     # Soft rose red bg
        success_border = "#10b981"
        error_border = "#ef4444"
        text_on_light_success = "#065f46"
        text_on_light_error = "#991b1b"
        hover_bg = "#dbeafe"           # Very soft pastel blue
        hover_text = "#004B87"          # Dark Swedish Blue
    else:
        # Default Dark Theme
        bg_color = "#0f172a"           # Deep slate dark background
        text_color = "#f1f5f9"         # Bright soft grey
        muted_text = "#94a3b8"         # Muted lavender-grey
        card_bg = "#1e293b"            # Slate blue-grey cards
        sidebar_bg = "#0b0f19"         # Darker slate sidebar
        form_bg = "#1e293b"
        border_color = "rgba(255, 255, 255, 0.08)"
        input_bg = "#1e293b"
        tab_bg = "#0b0f19"
        chat_bg = "#1e293b"
        success_bg = "rgba(52, 211, 153, 0.15)"
        error_bg = "rgba(248, 113, 113, 0.15)"
        success_border = "#34d399"
        error_border = "#f87171"
        text_on_light_success = "#34d399"
        text_on_light_error = "#f87171"
        hover_bg = "#334155"           # Muted slate blue
        hover_text = "#facc15"          # Warm pastel Swedish Yellow

    return f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@200;300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Background and Colors */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"], .main, .stApp {{
        background-color: {bg_color} !important;
        background-image: none !important;
        background: {bg_color} !important;
        color: {text_color} !important;
        font-family: 'Kanit', 'Outfit', sans-serif;
    }}

    /* Block Container background */
    [data-testid="stBlockContainer"], .block-container {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    /* General text overrides */
    p, li, a, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{
        color: {muted_text} !important;
    }}


    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', 'Kanit', sans-serif;
        color: {text_color} !important;
    }}

    /* Force Sidebar Background and Text */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebarNav"] {{
        background-color: {sidebar_bg} !important;
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color} !important;
    }}

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
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
        background-color: {card_bg} !important;
        background: {card_bg} !important;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid {border_color} !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .dashboard-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
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
    }}

    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {{
        border-color: #FFCD00 !important;
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
        color: {muted_text} !important;
        background-color: transparent !important;
    }}
    [data-baseweb="tab"][aria-selected="true"] {{
        color: #004B87 !important;
        font-weight: bold !important;
        border-bottom-color: #004B87 !important;
    }}

    /* Radio button containers */
    [data-testid="stRadio"] label, [data-testid="stRadio"] div, [data-testid="stRadio"] p {{
        color: {text_color} !important;
    }}

    /* Custom Streamlit button adjustments */
    div.stButton > button {{
        border-radius: 8px;
        font-weight: 500;
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        transition: all 0.2s ease;
    }}

    div.stButton > button:hover {{
        background-color: {hover_bg} !important;
        color: {hover_text} !important;
        border-color: {hover_bg} !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0, 75, 135, 0.15);
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

    </style>
    """
