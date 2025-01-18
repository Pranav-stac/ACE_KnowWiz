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
import base64
from image_scraper import ChromaImageScraper
import time
from PIL import ImageDraw, ImageFont, ImageColor
from time import sleep

# Set page config
st.set_page_config(
    page_title="AI Marketing Suite",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    /* Main content styling */
    .main {
        padding: 2rem;
        background-color: #ffffff;
    }
    
    /* Card styling */
    .stCard {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1 {
        color: #2E4057;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: #2E4057;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #FF6B6B;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #FF5252;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    /* Hide code blocks */
    .element-container:has(>.stMarkdown) pre {
        display: none !important;
    }
    
    /* Improve card hover effects */
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Improve typography */
    .card-title {
        color: #2E4057;
        margin-bottom: 10px;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .card-text {
        color: #666;
        line-height: 1.5;
    }
    
    .learn-more {
        margin-top: 15px;
        color: #FF6B6B;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

if 'generated_image_path' not in st.session_state:
    st.session_state.generated_image_path = None
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = ""

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        self.requests = [req for req in self.requests 
                        if now - req < timedelta(minutes=1)]
        
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0]).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(now)

# Initialize rate limiter
rate_limiter = RateLimiter(requests_per_minute=50)

def safe_generate_content(prompt, model=None):
    if model is None:
        model = genai.GenerativeModel('gemini-pro')
    try:
        rate_limiter.wait_if_needed()
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "Error: No response generated"
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    st.error("Please set up your Google API key in the .env file")
    st.stop()

try:
    # Basic configuration without additional settings
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Initialize models
    model = genai.GenerativeModel('gemini-pro')
    vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    # Quick test
    response = model.generate_content("test")
    if not response:
        raise Exception("No response from API")
        
except Exception as e:
    st.error(f"API Error: {str(e)}")
    st.stop()

# Page selection
page = st.sidebar.selectbox(
    "",
    ["Home", "Content Generator", "Logo Generator", "Post Image Generator", 
     "Visual Content Creator", "Audience Insights", "AR/VR Advertisements", "Campaign Management Hub"],
    format_func=lambda x: {
        "Home": "🏠 Home",
        "Content Generator": "✍️ Content Generator",
        "Logo Generator": "🎨 Logo Generator",
        "Post Image Generator": "📸 Post Image Generator",
        "Visual Content Creator": "🖼️ Visual Content Creator",
        "Audience Insights": "👥 Audience Insights",
        "AR/VR Advertisements": "🎮 AR/VR Ads",
        "Campaign Management Hub": "🎯 Campaign Management Hub"
    }[x]
)

# Page routing
if page == "Home":
    st.title("🏠 Welcome to AI Marketing Suite")
    
    # Add custom CSS to hide code and improve styling
    st.markdown("""
        <style>
        /* Hide code blocks */
        .element-container:has(>.stMarkdown) pre {
            display: none !important;
        }
        
        /* Improve card hover effects */
        .feature-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        /* Improve typography */
        .card-title {
            color: #2E4057;
            margin-bottom: 10px;
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .card-text {
            color: #666;
            line-height: 1.5;
        }
        
        .learn-more {
            margin-top: 15px;
            color: #FF6B6B;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Updated Get Started section with AR/VR Ads card
    st.markdown("""
    <div style="padding: 20px 0;">
        <h2 style="color: #2E4057; margin-bottom: 30px;">🚀 Get Started</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <!-- Content Generator Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">✍️</div>
                <div class="card-title">Content Generator</div>
                <p class="card-text">Create engaging content for your marketing campaigns with AI-powered assistance.</p>
                <div class="learn-more">Learn more →</div>
            </div>
            
            <!-- Logo Generator Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">🎨</div>
                <div class="card-title">Logo Generator</div>
                <p class="card-text">Design unique and professional logos for your brand identity.</p>
                <div class="learn-more">Learn more →</div>
            </div>
            
            <!-- Post Image Generator Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">📸</div>
                <div class="card-title">Post Image Generator</div>
                <p class="card-text">Create eye-catching social media images that drive engagement.</p>
                <div class="learn-more">Learn more →</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
            <!-- Visual Content Creator Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">🖼️</div>
                <div class="card-title">Visual Content Creator</div>
                <p class="card-text">Design and customize visual content for your marketing campaigns.</p>
                <div class="learn-more">Learn more →</div>
            </div>
            
            <!-- Audience Insights Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">👥</div>
                <div class="card-title">Audience Insights</div>
                <p class="card-text">Analyze your target audience and competitors for better targeting.</p>
                <div class="learn-more">Learn more →</div>
            </div>
            
            <!-- AR/VR Ads Card -->
            <div class="feature-card">
                <div style="font-size: 2em; margin-bottom: 15px;">🎮</div>
                <div class="card-title">AR/VR Advertisements</div>
                <p class="card-text">Create immersive AR/VR experiences for your marketing campaigns.</p>
                <div class="learn-more">Learn more →</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Updated Quick Tips section
    st.markdown("""
    <div style="background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 40px;">
        <h2 style="color: #2E4057; margin-bottom: 20px;">🎯 Quick Tips</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <div style="font-size: 1.5em; margin-bottom: 10px;">💡</div>
                <p style="color: #666; line-height: 1.6;">Use clear, specific prompts for best results</p>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <div style="font-size: 1.5em; margin-bottom: 10px;">🎨</div>
                <p style="color: #666; line-height: 1.6;">Experiment with different styles and formats</p>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <div style="font-size: 1.5em; margin-bottom: 10px;">💾</div>
                <p style="color: #666; line-height: 1.6;">Save your favorite generations for future reference</p>
            </div>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <div style="font-size: 1.5em; margin-bottom: 10px;">📊</div>
                <p style="color: #666; line-height: 1.6;">Analyze your audience before creating content</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "Content Generator":
    st.title("✍️ Content Generator")
    
    with st.expander("📌 Content Writing Tips", expanded=False):
        st.markdown("""
        - Keep your target audience in mind
        - Maintain consistent brand voice
        - Use engaging hooks
        - Include clear calls-to-action
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Social Media Post", "Blog Post", "Email Newsletter", "Product Description", "Ad Copy"]
        )
        target_audience = st.text_input("Target Audience", placeholder="e.g., Young professionals, parents, etc.")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Retail", "Education", "Entertainment", "Other"]
        )
    
    with col2:
        tone = st.selectbox(
            "Tone of Voice",
            ["Professional", "Casual", "Friendly", "Formal", "Humorous", "Inspirational"]
        )
        key_points = st.text_area("Key Points to Include", placeholder="Enter main points to cover")
        content_length = st.select_slider(
            "Content Length",
            options=["Very Short", "Short", "Medium", "Long", "Very Long"]
        )

    if st.button("Generate Content"):
        if not target_audience or not key_points:
            st.error("Please fill in all required fields")
        else:
            with st.spinner("Generating content..."):
                prompt = f"""
                Create a {content_type} for {target_audience} in the {industry} industry.
                Tone: {tone}
                Length: {content_length}
                Key Points: {key_points}
                
                Format the content appropriately for the chosen type.
                Include:
                1. Attention-grabbing opening
                2. Key messages
                3. Call to action
                4. Relevant hashtags (if social media)
                """
                
                generated_content = safe_generate_content(prompt)
                if generated_content:
                    st.markdown("### 📝 Generated Content")
                    st.markdown(generated_content)
                    
                    # Add copy button
                    st.markdown("""
                    <style>
                    .stButton>button {
                        width: 100%;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("📋 Copy to Clipboard"):
                        st.write("Content copied to clipboard!")
                        st.session_state['clipboard'] = generated_content

elif page == "Logo Generator":
    st.title("🎨 Logo Generator")
    
    with st.expander("📌 Logo Design Tips", expanded=False):
        st.markdown("""
        - Keep it simple and memorable
        - Ensure scalability
        - Consider color psychology
        - Maintain brand consistency
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Company Name")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Retail", "Education", "Other"]
        )
        style = st.selectbox(
            "Logo Style",
            ["Modern", "Classic", "Minimalist", "Bold", "Playful", "Luxurious"]
        )
    
    with col2:
        style = st.selectbox(
            "Logo Style",
            ["Modern", "Classic", "Minimalist", "Bold", "Playful", "Luxurious"]
        )
    
    if st.button("Generate Logo"):
        if not company_name:
            st.error("Please enter a company name")
        else:
            with st.spinner("Generating logo..."):
                try:
                    # Initialize the scraper
                    scraper = ChromaImageScraper()
                    
                    # Only use company name in the prompt
                    prompt = f"{company_name} logo"
                    
                    # Generate and get the image
                    logo_path = scraper.get_generated_image(prompt)
                    
                    if logo_path:
                        # Display the generated logo
                        st.image(logo_path, caption="Generated Logo")
                        st.success("Logo generated successfully!")
                        
                        # Add download button
                        with open(logo_path, "rb") as file:
                            btn = st.download_button(
                                label="Download Logo",
                                data=file,
                                file_name=f"{company_name}_logo.png",
                                mime="image/png"
                            )
                    else:
                        st.error("Failed to generate logo")
                    
                    # Close the scraper
                    scraper.close()
                    
                except Exception as e:
                    st.error(f"Error generating logo: {str(e)}")
                    try:
                        scraper.close()
                    except:
                        pass

elif page == "Post Image Generator":
    st.title("📸 Post Image Generator")
    
    # Create two columns for image and caption
    image_col, caption_col = st.columns([1, 1])
    
    with image_col:
        st.markdown("### Generate Marketing Image")
        platform = st.selectbox(
            "Platform",
            ["Instagram", "Facebook", "LinkedIn", "Twitter"],
            index=0
        )
        mood = st.selectbox(
            "Image Mood",
            ["Professional", "Casual", "Energetic", "Luxurious", "Minimalist"],
            index=0
        )
        style_preference = st.selectbox(
            "Style",
            ["Modern", "Vintage", "Corporate", "Artistic", "Natural"],
            index=0
        )
        color_theme = st.text_input("Color Theme", placeholder="e.g., blue and white, warm tones")
        
        image_description = st.text_area(
            "Image Description",
            placeholder="Describe the image you want to generate..."
        )
        
        if st.button("Generate Image"):
            try:
                with st.spinner("Generating image..."):
                    scraper = ChromaImageScraper()
                    prompt = f"""Create a {mood} {style_preference} image for {platform} 
                               with {color_theme} colors. {image_description}"""
                    
                    image_path = scraper.get_generated_image(prompt)
                    if image_path:
                        st.session_state.generated_image_path = image_path
                        st.success("Image generated successfully!")
                        
                scraper.close()
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
        
        # Always show the image if it exists in session state
        if 'generated_image_path' in st.session_state and st.session_state.generated_image_path and os.path.exists(st.session_state.generated_image_path):
            st.image(st.session_state.generated_image_path, caption="Generated Image")
            with open(st.session_state.generated_image_path, "rb") as file:
                st.download_button(
                    label="Download Original Image",
                    data=file,
                    file_name="generated_image.png",
                    mime="image/png",
                    key="download_original"
                )
    
    with caption_col:
        st.markdown("### Caption Options")
        caption_tab1, caption_tab2 = st.tabs(["AI Generated Caption", "Manual Caption"])
        
        with caption_tab1:
            if st.button("Generate Caption"):
                with st.spinner("Generating caption..."):
                    caption_prompt = f"""
                    Create an engaging social media caption for a {platform} post.
                    Image description: {image_description}
                    Mood: {mood}
                    Style: {style_preference}
                    
                    Keep it concise and engaging. Include relevant hashtags.
                    """
                    generated_caption = safe_generate_content(caption_prompt)
                    if generated_caption:
                        st.session_state.generated_caption = generated_caption
            
            # Always show the generated caption if it exists
            if 'generated_caption' in st.session_state and st.session_state.generated_caption:
                st.text_area("Generated Caption (editable)", 
                           value=st.session_state.generated_caption, 
                           key="gen_caption_1",
                           height=200)
        
        with caption_tab2:
            manual_caption = st.text_area(
                "Enter Custom Caption",
                placeholder="Enter your own caption for the post",
                height=200
            )
    
    # Caption Overlay Options (below both columns)
    if 'generated_image_path' in st.session_state and st.session_state.generated_image_path and os.path.exists(st.session_state.generated_image_path):
        st.markdown("---")
        st.markdown("### Caption Overlay Options")
        add_caption = st.checkbox("Add Caption to Image")
        
        if add_caption:
            overlay_col1, overlay_col2, overlay_col3 = st.columns(3)
            
            with overlay_col1:
                caption_position = st.selectbox(
                    "Caption Position",
                    ["Top", "Bottom", "Center", "Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"]
                )
                bg_color = st.color_picker("Background Color", "#000000")
            
            with overlay_col2:
                text_color = st.color_picker("Text Color", "#FFFFFF")
                caption_size = st.slider("Caption Size", 10, 100, 30)
            
            with overlay_col3:
                text_opacity = st.slider("Text Opacity", 0.0, 1.0, 1.0)
                bg_opacity = st.slider("Background Opacity", 0.0, 1.0, 0.7)
            
            # Get caption text from either AI or manual input
            caption_text = st.session_state.get('generated_caption', '') if st.session_state.get('generated_caption', '') else manual_caption
            
            if caption_text and st.button("Apply Caption", key="apply_caption"):
                try:
                    # Open the image
                    img = Image.open(st.session_state.generated_image_path)
                    
                    # Create a copy for modification
                    modified_image = img.copy()
                    draw = ImageDraw.Draw(modified_image, 'RGBA')
                    
                    # Load font
                    try:
                        font = ImageFont.truetype("arial.ttf", caption_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # Calculate text size
                    bbox = draw.textbbox((0, 0), caption_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Position mapping with adjusted padding for bottom position
                    bottom_padding = 40  # Increased padding for bottom position
                    position_map = {
                        "Top": ((img.width - text_width) // 2, 20),
                        "Bottom": ((img.width - text_width) // 2, img.height - text_height - bottom_padding),
                        "Center": ((img.width - text_width) // 2, (img.height - text_height) // 2),
                        "Top-Left": (20, 20),
                        "Top-Right": (img.width - text_width - 20, 20),
                        "Bottom-Left": (20, img.height - text_height - bottom_padding),
                        "Bottom-Right": (img.width - text_width - 20, img.height - text_height - bottom_padding)
                    }
                    
                    x, y = position_map.get(caption_position, (20, 20))
                    
                    # Draw background rectangle with extra padding
                    bg_rgba = (*ImageColor.getrgb(bg_color), int(255 * bg_opacity))
                    padding = 20
                    draw.rectangle(
                        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                        fill=bg_rgba
                    )
                    
                    # Draw text twice to create bold effect
                    text_rgba = (*ImageColor.getrgb(text_color), int(255 * text_opacity))
                    # First pass
                    draw.text((x-1, y), caption_text, font=font, fill=text_rgba)
                    draw.text((x+1, y), caption_text, font=font, fill=text_rgba)
                    draw.text((x, y-1), caption_text, font=font, fill=text_rgba)
                    draw.text((x, y+1), caption_text, font=font, fill=text_rgba)
                    # Second pass (main text)
                    draw.text((x, y), caption_text, font=font, fill=text_rgba)
                    
                    # Display modified image
                    st.image(modified_image, caption="Image with Caption")
                    
                    # Save and provide download button
                    output_path = st.session_state.generated_image_path.replace('.png', '_with_caption.png')
                    modified_image.save(output_path, "PNG")
                    
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="Download Image with Caption",
                            data=file,
                            file_name="generated_image_with_caption.png",
                            mime="image/png",
                            key="download_captioned"
                        )
                except Exception as e:
                    st.error(f"Error adding caption: {str(e)}")

elif page == "Visual Content Creator":
    st.title("🖼️ Visual Content Creator")
    
    # Image upload
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
        
        # Caption options
        st.markdown("### Caption Options")
        add_caption = st.checkbox("Add Caption to Image")
        
        if add_caption:
            caption_col1, caption_col2 = st.columns(2)
            
            with caption_col1:
                caption_text = st.text_input("Caption Text")
                caption_position = st.selectbox(
                    "Position",
                    ["Top", "Bottom", "Center"]
                )
                
            with caption_col2:
                font_size = st.slider("Font Size", 10, 100, 30)
                text_color = st.color_picker("Text Color", "#FFFFFF")
                bg_opacity = st.slider("Background Opacity", 0.0, 1.0, 0.5)
            
            if st.button("Apply Caption"):
                try:
                    # Apply caption to image
                    img_with_caption = add_caption_to_image(
                        image, caption_text, caption_position, 
                        font_size, text_color, bg_opacity
                    )
                    st.image(img_with_caption, caption="Image with Caption")
                    
                    # Add download button
                    if st.button("Download Image"):
                        # Add download functionality
                        pass
                except Exception as e:
                    st.error(f"Error adding caption: {str(e)}")

elif page == "Audience Insights":
    st.title("👥 Audience Insights")
    
    tab1, tab2 = st.tabs(["Audience Analysis", "Competitor Analysis"])
    
    with tab1:
        st.markdown("### Target Audience Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            demographics = st.text_area(
                "Demographics",
                placeholder="Age range, gender, location, income level, etc."
            )
            interests = st.text_area(
                "Interests & Hobbies",
                placeholder="What does your audience like?"
            )
        
        with col2:
            pain_points = st.text_area(
                "Pain Points",
                placeholder="What problems do they face?"
            )
            goals = st.text_area(
                "Goals & Aspirations",
                placeholder="What do they want to achieve?"
            )
        
        if st.button("Analyze Audience"):
            if not demographics or not interests:
                st.error("Please fill in the required fields")
            else:
                with st.spinner("Analyzing audience..."):
                    prompt = f"""
                    Analyze this target audience:
                    Demographics: {demographics}
                    Interests: {interests}
                    Pain Points: {pain_points}
                    Goals: {goals}
                    
                    Provide:
                    1. Audience Profile
                    2. Key Motivations
                    3. Communication Preferences
                    4. Content Recommendations
                    5. Marketing Channels
                    6. Engagement Strategies
                    7. Purchase Behavior
                    8. Brand Preferences
                    
                    Format the response in markdown with clear sections.
                    """
                    analysis = safe_generate_content(prompt)
                    if analysis:
                        st.markdown("### 📊 Audience Analysis Report")
                        st.markdown(analysis)
    
    with tab2:
        st.markdown("### Competitor Analysis")
        competitors = st.text_area(
            "List Main Competitors",
            placeholder="Enter competitor names and their key strengths"
        )
        
        if st.button("Analyze Competitors"):
            if not competitors:
                st.error("Please enter competitor information")
            else:
                with st.spinner("Analyzing competitors..."):
                    prompt = f"""
                    Analyze these competitors:
                    {competitors}
                    
                    Provide:
                    1. Competitive Positioning
                    2. Strength/Weakness Analysis
                    3. Market Opportunities
                    4. Differentiation Strategy
                    
                    Format as a strategic analysis report.
                    """
                    analysis = safe_generate_content(prompt)
                    if analysis:
                        st.markdown("### 🎯 Competitive Analysis Report")
                        st.markdown(analysis)

elif page == "AR/VR Advertisements":
    st.title("🎮 AR/VR Advertisements")
    
    st.markdown("""
    <div class="stCard">
        <h2>Create Immersive AR/VR Ads</h2>
        <p>Generate interactive AR/VR advertisements with QR code integration.</p>
        <ul>
            <li>Create engaging AR experiences</li>
            <li>Generate QR codes for easy access</li>
            <li>Track viewer engagement</li>
            <li>Customize AR content</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Add redirect button with custom styling
    st.markdown("""
        <style>
        .redirect-button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .redirect-button:hover {
            background-color: #45a049;
        }
        </style>
        <a href="https://15.206.147.226:8443/" target="_blank" class="redirect-button">
            Launch AR/VR Creator
        </a>
    """, unsafe_allow_html=True)
    
    # Add information about the AR/VR platform
    st.markdown("""
    <div class="stCard">
        <h3>How It Works</h3>
        <ol>
            <li>Click the button above to launch the AR/VR creator</li>
            <li>Design your immersive advertisement</li>
            <li>Generate a QR code for your AR experience</li>
            <li>Share with your audience</li>
        </ol>
        <p><strong>Note:</strong> The AR/VR creator will open in a new tab.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "Campaign Management Hub":
    st.title("🎯 Campaign Management Hub")
    
    # Create tabs for different sections
    tabs = st.tabs(["📊 Performance Analytics", "#️⃣ Hashtag Analytics"])
    
    # Tab 1: Performance Analytics
    with tabs[0]:
        st.markdown("""
        <div class="stCard">
            <h2>Campaign Performance Analytics</h2>
            <p>Upload your campaign data and get comprehensive insights with advanced visualizations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload section with multiple format support
        uploaded_file = st.file_uploader(
            "Upload Campaign Data", 
            type=['csv', 'xlsx', 'json'],
            help="Support for CSV, Excel, and JSON formats"
        )
        
        # Sample data download section
        with st.expander("📥 Download Sample Data"):
            col1, col2, col3 = st.columns(3)
            
            # Generate sample data
            sample_dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            sample_data = pd.DataFrame({
                'date': sample_dates,
                'platform': np.random.choice(['Instagram', 'Facebook', 'LinkedIn', 'Twitter'], 30),
                'impressions': np.random.normal(5000, 1000, 30).astype(int),
                'engagement': np.random.normal(500, 100, 30).astype(int),
                'clicks': np.random.normal(200, 50, 30).astype(int),
                'conversions': np.random.normal(20, 5, 30).astype(int),
                'cost': np.random.normal(100, 20, 30).round(2)
            })
            
            # Create download buttons for different formats
            with col1:
                csv = sample_data.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV Template",
                    csv,
                    "campaign_data_template.csv",
                    "text/csv",
                    key='download-csv'
                )
            
            with col2:
                excel_buffer = io.BytesIO()
                sample_data.to_excel(excel_buffer, index=False)
                st.download_button(
                    "📥 Download Excel Template",
                    excel_buffer.getvalue(),
                    "campaign_data_template.xlsx",
                    key='download-excel'
                )
            
            with col3:
                json_str = sample_data.to_json(orient='records', date_format='iso')
                st.download_button(
                    "📥 Download JSON Template",
                    json_str,
                    "campaign_data_template.json",
                    key='download-json'
                )
        
        if uploaded_file:
            try:
                # Load data based on file type
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:  # JSON
                    df = pd.read_json(uploaded_file)
                
                # Convert date column to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                # Enhanced Dashboard Layout
                st.markdown("### 📈 Campaign Performance Dashboard")
                
                # Expanded KPI metrics row
                metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
                with metrics_col1:
                    st.metric("Total Impressions", f"{df['impressions'].sum():,.0f}")
                with metrics_col2:
                    st.metric("Avg. Engagement Rate", f"{(df['engagement'].sum() / df['impressions'].sum() * 100):.2f}%")
                with metrics_col3:
                    st.metric("Total Conversions", f"{df['conversions'].sum():,.0f}")
                with metrics_col4:
                    st.metric("Total Revenue", f"${(df['conversions'].sum() * 50):,.2f}")
                with metrics_col5:
                    roi = ((df['conversions'].sum() * 50) - df['cost'].sum()) / df['cost'].sum() * 100
                    st.metric("ROI", f"{roi:.1f}%")
                
                # Time Series Analysis with Enhanced Features
                st.markdown("#### 📈 Performance Trends")
                col1, col2 = st.columns([1, 2])
                with col1:
                    metric_options = ['impressions', 'engagement', 'clicks', 'conversions', 'cost']
                    selected_metrics = st.multiselect("Select Metrics", metric_options, 
                                                    default=['impressions', 'engagement'])
                    trend_type = st.radio("Trend View", ["Daily", "Weekly", "Monthly"])
                
                with col2:
                    # Resample data based on selected trend type
                    if trend_type == "Weekly":
                        df_trend = df.set_index('date').resample('W').sum().reset_index()
                    elif trend_type == "Monthly":
                        df_trend = df.set_index('date').resample('M').sum().reset_index()
                    else:
                        df_trend = df
                    
                    fig = go.Figure()
                    for metric in selected_metrics:
                        fig.add_trace(go.Scatter(
                            x=df_trend['date'],
                            y=df_trend[metric],
                            name=metric.capitalize(),
                            mode='lines+markers',
                            line=dict(width=3),
                            marker=dict(size=8)
                        ))
                    fig.update_layout(
                        title="Metric Trends Over Time",
                        xaxis_title="Date",
                        yaxis_title="Value",
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Platform Performance Analysis
                st.markdown("#### 🎯 Platform Performance Analysis")
                platform_col1, platform_col2 = st.columns(2)
                
                with platform_col1:
                    # Radar Chart for Platform Performance
                    platform_metrics = df.groupby('platform').agg({
                        'impressions': 'sum',
                        'engagement': 'sum',
                        'clicks': 'sum',
                        'conversions': 'sum',
                        'cost': 'sum'
                    }).reset_index()
                    
                    # Normalize metrics for radar chart
                    metrics_to_normalize = ['impressions', 'engagement', 'clicks', 'conversions']
                    for metric in metrics_to_normalize:
                        platform_metrics[f'{metric}_normalized'] = (platform_metrics[metric] - platform_metrics[metric].min()) / \
                                                                 (platform_metrics[metric].max() - platform_metrics[metric].min())
                    
                    fig_radar = go.Figure()
                    for platform in platform_metrics['platform']:
                        platform_data = platform_metrics[platform_metrics['platform'] == platform]
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[platform_data[f'{metric}_normalized'].iloc[0] for metric in metrics_to_normalize],
                            theta=metrics_to_normalize,
                            name=platform,
                            fill='toself'
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True,
                        title="Platform Performance Comparison"
                    )
                    st.plotly_chart(fig_radar)
                
                with platform_col2:
                    # Sunburst Chart for Campaign Distribution
                    fig_sunburst = px.sunburst(
                        df,
                        path=['platform', 'campaign_type'],
                        values='impressions',
                        title="Campaign Distribution by Platform and Type"
                    )
                    st.plotly_chart(fig_sunburst)
                
                # Conversion Funnel
                st.markdown("#### 🔄 Conversion Funnel Analysis")
                funnel_data = [
                    dict(name="Impressions", value=df['impressions'].sum()),
                    dict(name="Engagement", value=df['engagement'].sum()),
                    dict(name="Clicks", value=df['clicks'].sum()),
                    dict(name="Conversions", value=df['conversions'].sum())
                ]
                
                fig_funnel = go.Figure(go.Funnel(
                    y=[stage['name'] for stage in funnel_data],
                    x=[stage['value'] for stage in funnel_data],
                    textinfo="value+percent initial"
                ))
                
                fig_funnel.update_layout(title="Marketing Funnel Overview")
                st.plotly_chart(fig_funnel, use_container_width=True)
                
                # Cost Analysis
                st.markdown("#### 💰 Cost Analysis")
                cost_col1, cost_col2, cost_col3 = st.columns(3)
                
                with cost_col1:
                    # Cost per Platform Treemap
                    fig_cost_tree = px.treemap(
                        df,
                        path=['platform', 'campaign_type'],
                        values='cost',
                        title="Cost Distribution"
                    )
                    st.plotly_chart(fig_cost_tree)
                
                with cost_col2:
                    # CPC Trends
                    df['cpc'] = df['cost'] / df['clicks']
                    fig_cpc = px.line(
                        df.groupby('date')['cpc'].mean().reset_index(),
                        x='date',
                        y='cpc',
                        title="Cost per Click Trends"
                    )
                    st.plotly_chart(fig_cpc)
                
                with cost_col3:
                    # ROAS by Platform
                    platform_roas = df.groupby('platform').apply(
                        lambda x: (x['conversions'].sum() * 50) / x['cost'].sum()
                    ).reset_index()
                    platform_roas.columns = ['platform', 'roas']
                    
                    fig_roas = px.bar(
                        platform_roas,
                        x='platform',
                        y='roas',
                        title="Return on Ad Spend by Platform",
                        text=platform_roas['roas'].round(2)
                    )
                    fig_roas.update_traces(texttemplate='%{text}x', textposition='outside')
                    st.plotly_chart(fig_roas)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # Tab 2: Hashtag Analytics
    with tabs[1]:
        st.markdown("""
        <div class="stCard">
            <h2>Hashtag Analytics</h2>
            <p>Generate and analyze hashtags for your content.</p>
        </div>
        """, unsafe_allow_html=True)
        
        hashtag_col1, hashtag_col2 = st.columns(2)
        
        with hashtag_col1:
            topic = st.text_input("Topic/Industry")
            platform_hashtags = st.selectbox(
                "Platform for Hashtags",
                ["Instagram", "Twitter", "LinkedIn"]
            )
        
        with hashtag_col2:
            hashtag_count = st.slider("Number of Hashtags", 5, 30, 15)
            include_trending = st.checkbox("Include Trending Hashtags", True)
        
        if st.button("Generate Hashtags"):
            with st.spinner("Analyzing and generating hashtags..."):
                prompt = f"""
                Generate {hashtag_count} relevant hashtags for {topic} on {platform_hashtags}.
                Consider:
                - Industry-specific tags
                - Engagement-focused tags
                - {'Trending hashtags' if include_trending else 'Evergreen hashtags'}
                - Brand-building tags
                
                Format the response as:
                1. Popular Hashtags (with estimated post counts)
                2. Niche Hashtags
                3. Industry Hashtags
                4. Engagement Hashtags
                """
                hashtags = safe_generate_content(prompt)
                if hashtags:
                    st.markdown(hashtags)

# Add helper function for adding captions to images
def add_caption_to_image(image, caption_text, position, font_size, text_color, bg_opacity):
    # Create a copy of the image
    img_with_caption = image.copy()
    draw = ImageDraw.Draw(img_with_caption, 'RGBA')
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text size and position
    text_width, text_height = draw.textsize(caption_text, font=font)
    image_width, image_height = image.size
    
    # Calculate position based on selection
    if position == "Top":
        x = (image_width - text_width) // 2
        y = 10
    elif position == "Bottom":
        x = (image_width - text_width) // 2
        y = image_height - text_height - 10
    else:  # Center
        x = (image_width - text_width) // 2
        y = (image_height - text_height) // 2
    
    # Draw background rectangle
    bg_color = (0, 0, 0, int(255 * bg_opacity))
    padding = 10
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill=bg_color
    )
    
    # Draw text
    draw.text((x, y), caption_text, font=font, fill=text_color)
    
    return img_with_caption

# Add footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This AI Marketing Suite helps marketers create, analyze, and optimize "
    "their marketing campaigns using advanced AI technology."
) 