import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import json
import os

def save_user_history(filename, data_info):
    """Save user upload history to a JSON file"""
    history = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            history = json.load(f)
    history.append(data_info)
    with open(filename, 'w') as f:
        json.dump(history, f)

def main():
    st.set_page_config(
        page_title="Data Analysis Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS for sidebar
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-image: linear-gradient(#2e7bcf,#2e7bcf);
            color: white;
        }
        .sidebar-text {
            padding: 10px;
            border-radius: 5px;
            background-color: rgba(255,255,255,0.1);
            margin: 10px 0;
        }
        .simple-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f0f2f6;
            text-align: center;
            padding: 10px;
            border-top: 1px solid #e6e6e6;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar
    with st.sidebar:
        st.title("📊 Analysis Control Panel")
        st.markdown("---")
        
        # File Upload Section
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        # User Statistics
        st.markdown("---")
        st.subheader("📈 Session Statistics")
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        if 'last_analysis' not in st.session_state:
            st.session_state.last_analysis = None
            
        st.markdown(f"""
            <div class='sidebar-text'>
            🔍 Analyses performed: {st.session_state.analysis_count}<br>
            ⏱️ Last analysis: {st.session_state.last_analysis or 'None'}<br>
            </div>
        """, unsafe_allow_html=True)
        
        # Tips Section
        st.markdown("---")
        st.subheader("💡 Quick Tips")
        tips = [
            "Upload CSV files for instant analysis",
            "Use the correlation matrix to find relationships",
            "Export your processed data anytime",
            "Try different chart types for better insights"
        ]
        for tip in tips:
            st.markdown(f"• {tip}")
            
        # About Section
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
            <div class='sidebar-text'>
            This dashboard helps you analyze CSV data with:
            • Interactive visualizations
            • Statistical summaries
            • Data export capabilities
            • Real-time analysis
            </div>
        """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Load and cache data
        @st.cache_data
        def load_data():
            return pd.read_csv(uploaded_file)
        
        df = load_data()
        
        # Update session statistics
        st.session_state.analysis_count += 1
        st.session_state.last_analysis = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Save analysis history
        analysis_info = {
            "filename": uploaded_file.name,
            "timestamp": st.session_state.last_analysis,
            "rows": len(df),
            "columns": len(df.columns)
        }
        save_user_history("analysis_history.json", analysis_info)
        
        # Main content
        st.title("📊 Data Analysis Dashboard")
        
        # Data Overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Missing Values", df.isna().sum().sum())
        
        # Data Preview
        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        # Column Selection
        st.subheader("Select Columns for Analysis")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("X-axis", df.columns)
        with col2:
            y_axis = st.selectbox("Y-axis", numeric_cols)
        
        # Visualization
        st.subheader("Data Visualization")
        chart_type = st.radio(
            "Select Chart Type",
            ["Scatter Plot", "Line Chart", "Bar Chart", "Box Plot"],
            horizontal=True
        )
        
        if chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
        elif chart_type == "Line Chart":
            fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
        elif chart_type == "Bar Chart":
            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        else:
            fig = px.box(df, x=x_axis, y=y_axis, title=f"Distribution of {y_axis} by {x_axis}")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.subheader("Statistical Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Descriptive Statistics")
            st.dataframe(df[numeric_cols].describe())
        
        with col2:
            st.write("Correlation Matrix")
            corr = df[numeric_cols].corr()
            fig = px.imshow(corr, 
                          title="Correlation Heatmap",
                          color_continuous_scale="RdBu")
            st.plotly_chart(fig, use_container_width=True)
        
        # Data Export
        st.subheader("Export Processed Data")
        if st.button("Download Processed Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    else:
        st.title("Welcome to Data Analysis Dashboard! 📊")
        st.write("Please upload a CSV file to begin analysis.")
        
        # Example data
        st.subheader("Or try with example data")
        if st.button("Load Example Dataset"):
            example_data = pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=100),
                'Sales': np.random.normal(100, 20, 100),
                'Customers': np.random.randint(50, 200, 100),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
            })
            example_data.to_csv('example.csv', index=False)
            with open('example.csv', 'rb') as f:
                st.download_button(
                    label="Download Example Dataset",
                    data=f,
                    file_name="example.csv",
                    mime="text/csv"
                )

    # Footer
    st.markdown("""
        <div class="simple-footer">
            <span style="color: black;">Developed with ❤️ by Mehwish Fatima | Agentic AI Developer</span>
        </div>
        <div style='margin-bottom: 25px;'></div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
