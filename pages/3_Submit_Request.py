import os
import streamlit as st
from openai import OpenAI
from utils.db import requests_col
from dotenv import load_dotenv

load_dotenv()

client_ai = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

st.set_page_config(page_title="Household Service Request",
                   layout="centered", page_icon="🛠️")
st.title("🛠️ Household Service Request")

with st.form("request_form"):
    name = st.text_input("Your Name")
    category = st.selectbox("Service Category", [
        "Plumbing", "Electrical", "Carpentry", "Appliance Repair", "Painting", "Other"])
    description = st.text_area("Describe the issue")
    urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
    location = st.text_input("Location")
    photo = st.file_uploader("Upload a photo of the problem", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("Submit Request")

if submitted:
    request_data = {
        "name": name,
        "category": category,
        "description": description,
        "urgency": urgency,
        "location": location,
    }
    requests_col.insert_one(request_data)
    st.success("✅ Request submitted successfully!")

    prompt = f"""
    Client Name: {name}
    Service Type: {category}
    Urgency: {urgency}
    Location: {location}

    Issue Description:
    {description}

    Generate a professional service report in a structured format (title, summary, scope of work, estimated costs, next steps, notes).
    Avoid markdown formatting.
    """

    if st.button("Generate Service Report"):
        with st.spinner("Generating report using DeepSeek..."):
            response = client_ai.chat.completions.create(
                model="deepseek-ai/deepseek-r1",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                top_p=0.7,
                max_tokens=4096,
                stream=True
            )

            report_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    report_text += chunk.choices[0].delta.content
                    st.write(chunk.choices[0].delta.content)

        st.download_button("📄 Download Report", report_text,
                           file_name="service_report.txt")
        st.success("✅ Report generated successfully!")
        st.balloons()