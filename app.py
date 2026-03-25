###Responsible for running the project as a whole
import streamlit as st
import json
import os
from datetime import datetime
from searcher import search_company, search_companies_by_geography
from analyzer import analyze_and_select_urls, extract_company_names
from extractor import extract_company_data

st.set_page_config(
    page_title="Account Intelligence Radar",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
    <style>
        /* Base font size — much bigger */
        html, body, [class*="css"] {
            font-size: 22px !important;
        }

        /* Page padding */
        .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        /* Tabs — each takes half the width */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0px;
            width: 100%;
        }
        .stTabs [data-baseweb="tab"] {
            width: 50%;
            text-align: center;
            font-size: 20px !important;
            font-weight: bold;
            padding: 18px 0px !important;
        }

        /* Input fields — much taller */
        input[type="text"] {
            height: 70px !important;
            font-size: 20px !important;
            padding: 16px 20px !important;
        }

        /* Labels above inputs */
        label {
            font-size: 20px !important;
            font-weight: bold !important;
            margin-bottom: 10px !important;
        }

        /* Text areas — much taller */
        textarea {
            font-size: 20px !important;
            line-height: 1.8 !important;
            min-height: 160px !important;
            padding: 16px 20px !important;
        }

        /* Button — green and big */
        .stButton > button {
            height: 65px !important;
            font-size: 22px !important;
            font-weight: bold !important;
            width: 100% !important;
            background-color: #2d9e5f !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            margin-top: 2rem !important;
        }
        .stButton > button:hover {
            background-color: #238a50 !important;
        }
        .stButton > button:disabled {
            background-color: #888 !important;
            cursor: not-allowed !important;
        }

        /* More space between elements */
        .stTextInput, .stTextArea {
            margin-bottom: 1.5rem !important;
        }

        /* Bigger text in results */
        .stMarkdown p {
            font-size: 18px !important;
            line-height: 1.8 !important;
        }

        /* Divider spacing */
        hr {
            margin: 2rem 0 !important;
        }
    </style>
""", unsafe_allow_html=True)


def save_report(company_name, data):
    os.makedirs("reports", exist_ok=True)
    safe_name = company_name.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"reports/{safe_name}_{timestamp}"

    json_path = f"{base_filename}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    md_path = f"{base_filename}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Account Intelligence Report: {company_name}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Company Identifiers\n")
        f.write(f"- **Name:** {data.get('company_name', 'N/A')}\n")
        f.write(f"- **Headquarters:** {data.get('headquarters', 'N/A')}\n\n")

        f.write("## Business Snapshot\n")
        f.write("### Business Units\n")
        for unit in data.get("business_units", []):
            f.write(f"- {unit}\n")

        f.write("\n### Products and Services\n")
        for product in data.get("products_and_services", []):
            f.write(f"- {product}\n")

        f.write("\n### Target Industries\n")
        for industry in data.get("target_industries", []):
            f.write(f"- {industry}\n")

        f.write("\n## Leadership\n")
        for exec in data.get("key_executives", []):
            f.write(f"- **{exec.get('name', '')}** — {exec.get('title', '')}\n")

        f.write("\n## Strategic Initiatives\n")
        for initiative in data.get("strategic_initiatives", []):
            f.write(f"- {initiative}\n")

        f.write("\n## Evidence Sources\n")
        for url in data.get("source_urls", []):
            f.write(f"- {url}\n")

    return json_path, md_path


def display_report(data):
    st.success(" Extraction completed successfully!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(" Company Identifiers")
        st.write(f"**Name:** {data.get('company_name', 'N/A')}")
        st.write(f"**Headquarters:** {data.get('headquarters', 'N/A')}")

        st.subheader(" Key Executives")
        executives = data.get("key_executives", [])
        if executives:
            for exec in executives:
                st.write(f"- **{exec.get('name', '')}** — {exec.get('title', '')}")
        else:
            st.write("No executives found")

    with col2:
        st.subheader(" Business Units")
        units = data.get("business_units", [])
        if units:
            for unit in units:
                st.write(f"- {unit}")
        else:
            st.write("No business units found")

        st.subheader(" Target Industries")
        industries = data.get("target_industries", [])
        if industries:
            for industry in industries:
                st.write(f"- {industry}")
        else:
            st.write("No industries found")

    st.subheader(" Products and Services")
    products = data.get("products_and_services", [])
    if products:
        for product in products:
            st.write(f"- {product}")
    else:
        st.write("No products found")

    st.subheader(" Strategic Initiatives")
    initiatives = data.get("strategic_initiatives", [])
    if initiatives:
        for initiative in initiatives:
            st.write(f"- {initiative}")
    else:
        st.write("No strategic initiatives found")

    st.subheader(" Evidence Sources")
    for url in data.get("source_urls", []):
        st.write(f"- {url}")

    st.subheader(" Raw JSON Data")
    st.json(data)


#  Main App

st.title("🎯 Account Intelligence Radar")
st.write("Turn a company name or geography into an actionable intelligence report.")
st.divider()

tab1, tab2 = st.tabs(["🏢 Company Mode", "🌍 Geography Mode"])

with tab1:

    company_name = st.text_input(
        "Company Name",
        placeholder="e.g. Saudi Aramco",
        key="company_name_input"
    )

    objective = st.text_area(
        "Objective",
        placeholder="e.g. Extract headquarters, business units, core products, target industries, key executives, and recent strategic initiatives.",
        height=180,
        key="company_objective"
    )

    if "last_company" not in st.session_state:
        st.session_state.last_company = ""
    if "last_objective" not in st.session_state:
        st.session_state.last_objective = ""
    if "is_running" not in st.session_state:
        st.session_state.is_running = False

    run_button = st.button(
        "🔍 Generate Report",
        type="primary",
        key="company_btn",
        disabled=st.session_state.is_running
    )

    if run_button:
        if not company_name.strip():
            st.error(" Please enter a company name")

        elif not objective.strip():
            st.error(" Please enter an objective")

        elif (company_name.strip() == st.session_state.last_company and
                objective.strip() == st.session_state.last_objective):
            st.warning(" You already searched for this company with the same objective. Please modify your search before running again.")

        else:
            st.session_state.is_running = True
            st.session_state.last_company = company_name.strip()
            st.session_state.last_objective = objective.strip()

            with st.spinner(" Step 1/3: Searching Google..."):
                search_results = search_company(company_name, objective)

            if not search_results:
                st.error(" No search results found. Please try a different company name.")
                st.session_state.is_running = False

            else:
                with st.spinner(" Step 2/3: AI is selecting best URLs..."):
                    selected_urls = analyze_and_select_urls(
                        search_results,
                        company_name,
                        objective
                    )

                if not selected_urls:
                    st.error(" Could not select URLs. Please try again.")
                    st.session_state.is_running = False

                else:
                    with st.spinner(" Step 3/3: Extracting company data..."):
                        report_data = extract_company_data(
                            selected_urls,
                            company_name,
                            objective
                        )

                    if not report_data:
                        st.error(" Could not extract data. Please try again.")
                        st.session_state.is_running = False

                    else:
                        display_report(report_data)
                        json_path, md_path = save_report(company_name, report_data)

                        st.divider()
                        st.subheader("⬇ Download Report")

                        col1, col2 = st.columns(2)
                        with col1:
                            with open(json_path, "r", encoding="utf-8") as f:
                                st.download_button(
                                    label=" Download JSON",
                                    data=f.read(),
                                    file_name=os.path.basename(json_path),
                                    mime="application/json",
                                    key="download_json_company"
                                )
                        with col2:
                            with open(md_path, "r", encoding="utf-8") as f:
                                st.download_button(
                                    label=" Download Markdown",
                                    data=f.read(),
                                    file_name=os.path.basename(md_path),
                                    mime="text/markdown",
                                    key="download_md_company"
                                )

                        st.session_state.is_running = False

with tab2:

    location = st.text_input(
        "Location",
        placeholder="e.g. Riyadh, Saudi Arabia",
        key="geo_location"
    )

    sectors = st.text_input(
        "Target Sectors",
        placeholder="e.g. manufacturing, energy, logistics",
        key="geo_sectors"
    )

    geo_objective = st.text_area(
        "Objective",
        placeholder="e.g. Extract headquarters, business units, core products, target industries, key executives, and recent strategic initiatives.",
        height=180,
        key="geo_objective"
    )

    if "last_location" not in st.session_state:
        st.session_state.last_location = ""
    if "last_sectors" not in st.session_state:
        st.session_state.last_sectors = ""
    if "is_running_geo" not in st.session_state:
        st.session_state.is_running_geo = False

    geo_button = st.button(
        "🔍  Find Companies",
        type="primary",
        key="geo_btn",
        disabled=st.session_state.is_running_geo
    )

    if geo_button:
        if not location.strip():
            st.error(" Please enter a location")

        elif not sectors.strip():
            st.error(" Please enter target sectors")

        elif not geo_objective.strip():
            st.error(" Please enter an objective")

        elif (location.strip() == st.session_state.last_location and
                sectors.strip() == st.session_state.last_sectors):
            st.warning(" You already searched for this location and sectors. Please modify your search before running again.")

        else:
            st.session_state.is_running_geo = True
            st.session_state.last_location = location.strip()
            st.session_state.last_sectors = sectors.strip()

            with st.spinner(" Step 1/3: Searching for companies..."):
                geo_results = search_companies_by_geography(
                    location,
                    sectors,
                    geo_objective
                )

            if not geo_results:
                st.error(" No companies found. Please try different location or sectors.")
                st.session_state.is_running_geo = False

            else:
                with st.spinner(" Step 2/3: AI is identifying companies..."):
                    company_names = extract_company_names(
                        geo_results,
                        location,
                        sectors
                    )

                if not company_names:
                    st.error(" Could not identify companies. Please try again.")
                    st.session_state.is_running_geo = False

                else:
                    st.success(f" Found {len(company_names)} companies!")
                    for i, name in enumerate(company_names):
                        st.write(f"**{i+1}. {name}**")

                    st.divider()
                    st.info(" To get a full report on any company, copy its name and use Company Mode.")
                    st.session_state.is_running_geo = False

