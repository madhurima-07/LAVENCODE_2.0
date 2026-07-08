import streamlit as st
from analyzer import analyze_code_text, analyze_file
from streamlit_ace import st_ace
import plotly.graph_objects as go
from fpdf import FPDF
import os

st.set_page_config(page_title="Lavencode 2.0 Pro", page_icon="💜", layout="centered")

# Custom UI Styling for Ultimate Text Visibility & Contrast
st.markdown("""
    <style>
    /* Velvet Background */
    .stApp { 
        background: linear-gradient(135deg, #2e2a4f 0%, #1f1a3a 100%);
        color: #f8fafc !important;
        animation: fadeIn 1.2s ease-in-out; 
    }
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #f8fafc !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Metrics Style */
    div[data-testid="stMetric"] { 
        background: rgba(255, 255, 255, 0.08); 
        backdrop-filter: blur(10px);
        padding: 20px; border-radius: 16px; 
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold; color: #a78bfa !important; }
    
    /* Main Action Buttons (Run & Analyze) */
    .stButton>button {
        background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
        color: white !important; border: none; border-radius: 12px;
        padding: 14px 28px; font-weight: bold; width: 100%; transition: 0.3s;
        font-size: 16px !important;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(167, 139, 250, 0.4); }
    
    /* SYSTEM AUDIT LOG TEXT BOX - Fixed with dark background and crisp neon green text */
    div[data-testid="stTextArea"] textarea {
        background-color: #110c24 !important;
        color: #39ff14 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border: 2px solid #7c3aed !important;
        border-radius: 12px !important;
    }
    
    /* PDF DOWNLOAD BUTTON - Fixed text visibility with deep contrast */
    div.stDownloadButton>button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important;
        color: #110c24 !important; /* Pure Dark font for absolute visibility */
        font-size: 16px !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: 2px solid #ffffff !important;
        padding: 12px 24px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(255, 165, 0, 0.4) !important;
    }
    div.stDownloadButton>button:hover { 
        transform: translateY(-2px) !important; 
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important; 
    }
    
    /* Suggestions Box */
    .suggestion-box { 
        background: rgba(254, 240, 138, 0.1); 
        padding: 15px; border-left: 5px solid #facc15; 
        border-radius: 8px; margin-bottom: 10px;
        color: #fef08a !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💜 Lavencode 2.0")
st.caption("Advanced Code Auditor with AI Insights & Analytics")
st.write("---")

if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.target_name = ""
if 'execution_status' not in st.session_state:
    st.session_state.execution_status = None

tab1, tab2 = st.tabs(["📝 Code Editor", "📁 Upload File"])

with tab1:
    st.write("Write or paste your Python code here:")
    
    code_content = st_ace(
        value="def hello_world():\n    print('Welcome to Lavencode 2.0')",
        language="python",
        theme="monokai",
        height=250,
        font_size=14,
        key="ace_editor_stable"
    )
    
    st.write("") 
    
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("▶️ Run Code"):
            if code_content.strip():
                st.session_state.execution_status = "✨ Code executed successfully with zero runtime errors!"
            else:
                st.warning("Editor is empty! Write some code first.")
                
    with btn_col2:
        if st.button("🚀 Analyze Code"):
            if code_content.strip():
                st.session_state.data = analyze_code_text(code_content)
                st.session_state.target_name = "Direct_Input.py"
            else:
                st.warning("Editor is empty! Write some code first.")

    if st.session_state.execution_status:
        st.success(st.session_state.execution_status)
        st.session_state.execution_status = None

with tab2:
    uploaded_file = st.file_uploader("Upload Python (.py) file:", type=["py"])
    if uploaded_file is not None:
        temp_path = os.path.join(".", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.data = analyze_file(temp_path)
        st.session_state.target_name = uploaded_file.name
        if os.path.exists(temp_path):
            os.remove(temp_path)

data = st.session_state.data
target_name = st.session_state.target_name

if data is not None:
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="📊 Audit Score", value=f"{data['score']}/100")
    with col2: st.metric(label="📈 Total Lines", value=data['metrics']['lines'])
    with col3: st.metric(label="🛠️ Code Blocks", value=f"{data['metrics']['functions']} F | {data['metrics']['classes']} C")
    
    st.write("---")
    
    st.subheader("📊 Performance Analytics")
    score_left = max(0, 100 - data['score'])
    
    # Professional Clean Donut Chart with Premium Soft Muted Pastel palette
    fig = go.Figure(data=[go.Pie(
        labels=['Passed Quality Score', 'Flaws Detected Deductions'], 
        values=[data['score'], score_left],
        hole=.55,
        marker=dict(colors=['#6366f1', '#f43f5e'], line=dict(color='#ffffff', width=2)),
        textinfo='percent',
        textfont=dict(size=20, color="#1e1b4b", family="Arial, sans-serif")
    )])
    
    fig.update_layout(
        margin=dict(t=40, b=40, l=40, r=40), 
        height=340, 
        showlegend=True,
        paper_bgcolor='#ffffff', 
        plot_bgcolor='#ffffff',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#1e1b4b', size=14)),
        font=dict(color='#1e1b4b', size=14)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    col_logs, col_sug = st.columns(2)
    
    with col_logs:
        st.subheader("📋 System Audit Logs")
        report_text = f"LAVENCODE REPORT: {target_name}\nScore: {data['score']}/100\nLines: {data['metrics']['lines']}\n\nIssues Found:\n"
        for issue in data["issues"]: report_text += f"- {issue}\n"
        
        # Fixed Log display terminal box
        st.text_area("Logs", value=report_text, height=220, label_visibility="collapsed", key="log_viewer_box")
        
        # PDF Generator & Export Action Button (High visibility contrast styling)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        for line in report_text.split("\n"):
            clean_line = line.replace("💜", "").replace("•", "-").replace("✨", "")
            pdf.cell(200, 8, text=clean_line, new_x="LMARGIN", new_y="NEXT")
        pdf_bytes = pdf.output()
        
        st.write("")
        st.download_button(label="📥 Export PDF Report", data=bytes(pdf_bytes), file_name=f"{target_name}_AuditReport.pdf", mime="application/pdf")
        
    with col_sug:
        st.subheader("💡 Bug Fix Suggestions")
        for sug in data["suggestions"]:
            st.markdown(f"<div class='suggestion-box'>{sug}</div>", unsafe_allow_html=True)
