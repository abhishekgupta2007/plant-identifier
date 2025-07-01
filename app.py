import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="Plant Identifier by Abhishek 🌿",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: green;'>🌱 Identify Any Plant Instantly</h1>", unsafe_allow_html=True)

# Plant.id API key
API_KEY = st.secrets["api"]["plant_id_key"]

# Google Lens Style Options
st.markdown("### How would you like to scan the leaf?")
option = st.radio("", ["📁 Choose from Gallery","📷 Use Camera"], horizontal=True)

image = None

if option == "📁 Choose from Gallery":
    uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)

elif option == "📷 Use Camera":
    image_data = st.camera_input("Take a photo")
    if image_data:
        image = Image.open(image_data)


# Show preview and identify
if image:
    st.image(image, caption="Scanned Image", width=300)

    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    with st.spinner("Identifying plant... please wait ⏳"):
        response = requests.post(
            "https://api.plant.id/v2/identify",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": st.secrets["api"]["plant_id_key"],
                "images": [img_str],
                "modifiers": ["crops_fast", "similar_images"],
                "plant_language": "en",
                "plant_details": ["common_names", "url", "name_authority", "wiki_description"]
            },
        )

    result = response.json()

    if "suggestions" in result:
        top = result["suggestions"][0]
        name = top["plant_name"]
        confidence = top["probability"] * 100
        description = top["plant_details"]["wiki_description"].get("value", "No description available.")

        common_names = top["plant_details"].get("common_names", [])

        # Try to find Indian-sounding common names
        indian_names = [n for n in common_names if any(lang in n.lower() for lang in ["hindi", "bengali", "tamil", "marathi", "telugu", "indian"])]

        st.success(f"**Scientific Name:** 🌱 **{name}** ({confidence:.2f}% confidence)")

        if indian_names:
            st.markdown(f"**Common Indian name(s):** {', '.join(indian_names)}")
        elif common_names:
            st.markdown(f"**Common name(s):** {', '.join(common_names)}")

        st.write(description)

    else:
        st.error("❌ Couldn't identify the plant.")
