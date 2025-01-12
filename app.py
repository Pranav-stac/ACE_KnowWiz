import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
from datetime import datetime, timedelta
import numpy as np

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Set page config
st.set_page_config(
    page_title="AI Marketing Suite",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS with guaranteed visibility
st.markdown("""
    <style>
    /* Global dark theme */
    .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* All text elements */
    p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* All containers and cards */
    .stMarkdown, .element-container, .stTextInput, .stTextArea, .stSelectbox, 
    .stMultiSelect, .stSlider, .stCheckbox, .stFileUploader, .stTabs, 
    .streamlit-expanderHeader, [data-testid="stSidebar"], .stAlert, 
    .stMetricValue, .stProgress {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Feature cards */
    .feature-card {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1px solid #333333 !important;
        margin: 10px 0 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        background-color: #000000 !important;
        padding: 10px !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #ff4b4b !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* File uploader */
    .stFileUploader>div>div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px dashed #333333 !important;
    }
    
    /* Multiselect */
    .stMultiSelect>div>div>div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Tables */
    .dataframe {
        color: #ffffff !important;
    }
    
    .dataframe th {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .dataframe td {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Links */
    a {
        color: #ff4b4b !important;
    }
    
    a:hover {
        color: #ff6b6b !important;
    }
    
    /* Code blocks */
    code {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Plotly charts background */
    .js-plotly-plot {
        background-color: #000000 !important;
    }
    
    /* Success messages */
    .success-message {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #28a745 !important;
    }
    
    /* Error messages */
    .stAlert {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #dc3545 !important;
    }
    
    /* Checkbox */
    .stCheckbox>div>div>div>label {
        color: #ffffff !important;
    }
    
    /* Selectbox options */
    .stSelectbox>div>div>div>ul {
        background-color: #1a1a1a !important;
    }
    
    .stSelectbox>div>div>div>ul>li {
        color: #ffffff !important;
    }
    
    /* All other elements */
    * {
        color: #ffffff !important;
        border-color: #333333 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        background-color: #000000 !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background-color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎯 AI Marketing Suite")
page = st.sidebar.selectbox(
    "Choose a Feature",
    ["Home", "Content Generator", "Campaign Analyzer", "Visual Content Creator", "Audience Insights"]
)

# Home Page
if page == "Home":
    st.title("🚀 Welcome to AI Marketing Suite")
    st.markdown("""
    ### Transform Your Marketing Strategy with AI
    
    This powerful suite of tools helps you create, analyze, and optimize your marketing campaigns using cutting-edge AI technology.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>✍️ Content Generator</h4>
        <p>Create engaging marketing copy and social media posts with AI assistance.</p>
        <ul>
        <li>Social Media Posts</li>
        <li>Email Campaigns</li>
        <li>Blog Posts</li>
        <li>Product Descriptions</li>
        </ul>
        </div>
        
        <div class="feature-card">
        <h4>📊 Campaign Analyzer</h4>
        <p>Get detailed insights and optimization suggestions for your campaigns.</p>
        <ul>
        <li>Performance Metrics</li>
        <li>Trend Analysis</li>
        <li>ROI Calculation</li>
        <li>Audience Engagement</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>🎨 Visual Content Creator</h4>
        <p>Analyze and optimize your marketing visuals with AI insights.</p>
        <ul>
        <li>Image Analysis</li>
        <li>Design Recommendations</li>
        <li>Brand Consistency Check</li>
        <li>Visual Impact Score</li>
        </ul>
        </div>
        
        <div class="feature-card">
        <h4>👥 Audience Insights</h4>
        <p>Understand your target audience better with AI-powered analysis.</p>
        <ul>
        <li>Demographic Analysis</li>
        <li>Behavior Patterns</li>
        <li>Channel Preferences</li>
        <li>Content Recommendations</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# Content Generator
elif page == "Content Generator":
    st.title("✍️ AI Content Generator")
    
    with st.expander("📌 Content Generation Tips", expanded=False):
        st.markdown("""
        - Be specific about your target audience
        - Include key messages and brand voice
        - Consider the platform requirements
        - Focus on value proposition
        """)
    
    content_type = st.selectbox(
        "What type of content do you need?",
        ["Social Media Post", "Email Campaign", "Blog Post", "Product Description", "Ad Copy", "Website Copy"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_audience = st.text_input("Target Audience", placeholder="e.g., young professionals")
        tone = st.selectbox("Tone of Voice", ["Professional", "Casual", "Humorous", "Formal", "Inspirational", "Educational"])
        brand_voice = st.text_area("Brand Voice Guidelines", placeholder="Enter your brand's voice characteristics")
    
    with col2:
        industry = st.text_input("Industry", placeholder="e.g., Technology")
        key_points = st.text_area("Key Points to Include", placeholder="Enter key points separated by new lines")
        platform = st.selectbox("Platform", ["Any", "LinkedIn", "Instagram", "Facebook", "Twitter", "Email", "Website"])

    advanced_options = st.expander("Advanced Options", expanded=False)
    with advanced_options:
        word_limit = st.slider("Word Limit", 50, 1000, 200)
        include_cta = st.checkbox("Include Call-to-Action", value=True)
        seo_optimize = st.checkbox("Optimize for SEO", value=True)

    if st.button("Generate Content"):
        if not GOOGLE_API_KEY:
            st.error("Please set up your Google API key in the .env file")
        else:
            with st.spinner("Generating content..."):
                prompt = f"""
                Create a {content_type} for the {industry} industry.
                Target Audience: {target_audience}
                Tone: {tone}
                Platform: {platform}
                Brand Voice: {brand_voice}
                Key Points: {key_points}
                Word Limit: {word_limit} words
                {'Include a compelling call-to-action' if include_cta else ''}
                {'Optimize for SEO with relevant keywords' if seo_optimize else ''}
                Make it engaging and persuasive.
                """
                response = model.generate_content(prompt)
                st.success("Content Generated!")
                
                # Display generated content in a nice format
                st.markdown("### Generated Content")
                st.markdown('<div class="feature-card">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Provide additional options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Generate Alternative Version"):
                        with st.spinner("Generating alternative..."):
                            response = model.generate_content(prompt + "\nCreate a different version with the same requirements.")
                            st.markdown("### Alternative Version")
                            st.markdown(response.text)
                
                with col2:
                    if st.button("Get Improvement Suggestions"):
                        with st.spinner("Analyzing content..."):
                            analysis_prompt = f"Analyze this content and provide specific suggestions for improvement:\n\n{response.text}"
                            analysis = model.generate_content(analysis_prompt)
                            st.markdown("### Improvement Suggestions")
                            st.markdown(analysis.text)

# Campaign Analyzer
elif page == "Campaign Analyzer":
    st.title("📊 Campaign Analyzer")
    
    # Sample data template
    st.markdown("""
    ### 📥 Upload Campaign Data
    Upload your campaign data in CSV format. Need a template? [Download Sample Template](#)
    """)
    
    uploaded_file = st.file_uploader("Upload your campaign data (CSV)", type=['csv'])
    
    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            st.success("Data uploaded successfully!")
            
            # Time period selection
            col1, col2 = st.columns(2)
            with col1:
                date_range = st.date_input(
                    "Select Date Range",
                    value=(data['date'].min(), data['date'].max())
                )
            with col2:
                metrics = st.multiselect(
                    "Select Metrics to Display",
                    ['impressions', 'clicks', 'conversions', 'cost'],
                    default=['impressions', 'clicks']
                )
            
            # Overview metrics
            st.subheader("Campaign Overview")
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric(
                    "Total Impressions",
                    f"{data['impressions'].sum():,.0f}",
                    f"{data['impressions'].pct_change().mean():.1%}"
                )
            
            with metric_cols[1]:
                st.metric(
                    "Total Clicks",
                    f"{data['clicks'].sum():,.0f}",
                    f"{data['clicks'].pct_change().mean():.1%}"
                )
            
            with metric_cols[2]:
                ctr = (data['clicks'].sum() / data['impressions'].sum()) * 100
                st.metric("Average CTR", f"{ctr:.2f}%")
            
            with metric_cols[3]:
                if 'cost' in data.columns:
                    cpc = data['cost'].sum() / data['clicks'].sum()
                    st.metric("Average CPC", f"${cpc:.2f}")
            
            # Performance over time
            st.subheader("Performance Trends")
            fig = go.Figure()
            
            for metric in metrics:
                fig.add_trace(
                    go.Scatter(
                        x=data['date'],
                        y=data[metric],
                        name=metric.capitalize(),
                        mode='lines+markers'
                    )
                )
            
            fig.update_layout(
                title="Campaign Performance Over Time",
                xaxis_title="Date",
                yaxis_title="Value",
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance analysis
            if st.button("Generate Performance Analysis"):
                with st.spinner("Analyzing campaign performance..."):
                    analysis_prompt = f"""
                    Analyze this campaign data and provide insights:
                    - Total Impressions: {data['impressions'].sum():,.0f}
                    - Total Clicks: {data['clicks'].sum():,.0f}
                    - Average CTR: {ctr:.2f}%
                    
                    Provide:
                    1. Key performance insights
                    2. Trend analysis
                    3. Improvement recommendations
                    4. Actionable next steps
                    """
                    analysis = model.generate_content(analysis_prompt)
                    st.markdown("### 📈 Campaign Analysis")
                    st.markdown(analysis.text)
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.markdown("Please ensure your CSV file has the required columns: date, impressions, clicks")

# Visual Content Creator
elif page == "Visual Content Creator":
    st.title("🎨 Visual Content Creator")
    
    tab1, tab2 = st.tabs(["Image Analysis", "Design Guidelines"])
    
    with tab1:
        st.markdown("### Upload Marketing Visual")
        uploaded_image = st.file_uploader("Upload an image for analysis", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            analysis_type = st.multiselect(
                "Select Analysis Types",
                ["Brand Consistency", "Visual Appeal", "Message Clarity", "Target Audience Fit", "Composition"],
                default=["Brand Consistency", "Visual Appeal"]
            )
            
            if st.button("Analyze Image"):
                with st.spinner("Analyzing image..."):
                    prompt = f"""
                    Analyze this marketing image considering:
                    {', '.join(analysis_type)}
                    
                    Provide:
                    1. Strengths and weaknesses
                    2. Specific improvement suggestions
                    3. Target audience impact
                    4. Brand alignment score
                    5. Visual appeal rating
                    
                    Format the response in markdown with clear sections.
                    """
                    response = vision_model.generate_content([prompt, image])
                    
                    st.markdown("### 🎯 Image Analysis Results")
                    st.markdown(response.text)
    
    with tab2:
        st.markdown("### Brand Design Guidelines")
        col1, col2 = st.columns(2)
        
        with col1:
            brand_colors = st.text_input("Brand Colors (hex codes)", placeholder="#FF4B4B, #000000")
            brand_fonts = st.text_input("Brand Fonts", placeholder="Primary: Arial, Secondary: Georgia")
        
        with col2:
            image_types = st.multiselect(
                "Common Image Types",
                ["Product Photos", "Team Photos", "Lifestyle Images", "Infographics"],
                default=["Product Photos"]
            )
            target_platforms = st.multiselect(
                "Target Platforms",
                ["Instagram", "Facebook", "LinkedIn", "Website", "Email"],
                default=["Instagram"]
            )
        
        if st.button("Generate Design Guidelines"):
            with st.spinner("Generating guidelines..."):
                prompt = f"""
                Create comprehensive design guidelines for:
                Colors: {brand_colors}
                Fonts: {brand_fonts}
                Image Types: {', '.join(image_types)}
                Platforms: {', '.join(target_platforms)}
                
                Include:
                1. Platform-specific recommendations
                2. Image size specifications
                3. Visual style guide
                4. Best practices
                """
                guidelines = model.generate_content(prompt)
                st.markdown("### 📋 Design Guidelines")
                st.markdown(guidelines.text)

# Audience Insights
elif page == "Audience Insights":
    st.title("👥 Audience Insights")
    
    tab1, tab2 = st.tabs(["Audience Analysis", "Competitor Analysis"])
    
    with tab1:
        st.markdown("""
        ### Define Your Target Audience
        Provide detailed information about your target audience for comprehensive insights.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            audience_description = st.text_area(
                "Audience Description",
                placeholder="e.g., Urban professionals aged 25-35 interested in fitness and wellness"
            )
            industry_focus = st.text_input("Industry Focus", placeholder="e.g., Health & Wellness")
        
        with col2:
            geographic_focus = st.text_input("Geographic Focus", placeholder="e.g., North America")
            pain_points = st.text_area("Known Pain Points", placeholder="List main challenges or needs")
        
        advanced = st.expander("Advanced Options", expanded=False)
        with advanced:
            interests = st.multiselect(
                "Key Interests",
                ["Technology", "Health", "Fashion", "Travel", "Food", "Sports", "Education"],
                default=["Technology"]
            )
            platforms = st.multiselect(
                "Preferred Platforms",
                ["Instagram", "LinkedIn", "Facebook", "Twitter", "TikTok"],
                default=["Instagram"]
            )
        
        if st.button("Generate Audience Insights"):
            if not GOOGLE_API_KEY:
                st.error("Please set up your Google API key in the .env file")
            else:
                with st.spinner("Analyzing audience..."):
                    prompt = f"""
                    Analyze this target audience:
                    Description: {audience_description}
                    Industry: {industry_focus}
                    Geography: {geographic_focus}
                    Pain Points: {pain_points}
                    Interests: {', '.join(interests)}
                    Platforms: {', '.join(platforms)}
                    
                    Provide detailed insights including:
                    1. Demographic Profile
                    2. Psychographic Analysis
                    3. Content Preferences
                    4. Channel Strategy
                    5. Pain Points & Solutions
                    6. Buying Behaviors
                    7. Engagement Opportunities
                    8. Content Recommendations
                    
                    Format the response in markdown with clear sections.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("### 📊 Audience Insights Report")
                    st.markdown(response.text)
    
    with tab2:
        st.markdown("### Competitor Analysis")
        competitors = st.text_area(
            "List Main Competitors",
            placeholder="Enter competitor names and their key strengths"
        )
        
        if st.button("Analyze Competitors"):
            with st.spinner("Analyzing competitors..."):
                prompt = f"""
                Analyze these competitors in relation to the target audience:
                {competitors}
                
                Provide:
                1. Competitive Positioning
                2. Strength/Weakness Analysis
                3. Market Opportunities
                4. Differentiation Strategy
                
                Format as a strategic analysis report.
                """
                analysis = model.generate_content(prompt)
                st.markdown("### 🎯 Competitive Analysis Report")
                st.markdown(analysis.text)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This AI Marketing Suite helps marketers create, analyze, and optimize "
    "their marketing campaigns using advanced AI technology."
) 