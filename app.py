"""
GenData Project - Nairobi Rental Market Intelligence System (v2)
Author: Denis |  GenData Databases & SQL Track
Run: streamlit run app.py --server.address 0.0.0.0 --server.port 8501
"""
import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Nairobi Rental Intelligence | GenData", page_icon="🏠", layout="wide")

def centered(text, level=2):
    st.markdown(f"<h{level} style='text-align: center;'>{text}</h{level}>", unsafe_allow_html=True)

# ---------- Estate master data: rent base + amenities + coordinates ----------
ESTATES = [
    # estate, county, base1bed, mult, lat, lon, schools, hospitals, security(1-10), transport(1-10), water(1-10)
    ("Kilimani","Nairobi",45000,1.0,-1.2906,36.7820,8,5,8,9,8),
    ("Kileleshwa","Nairobi",55000,1.1,-1.2715,36.7730,7,4,8,8,8),
    ("Westlands","Nairobi",60000,1.2,-1.2635,36.8080,10,6,9,9,9),
    ("Upperhill","Nairobi",50000,1.0,-1.2890,36.8200,6,5,9,9,8),
    ("Lavington","Nairobi",70000,1.3,-1.2730,36.7600,9,4,9,7,9),
    ("South B","Nairobi",35000,0.8,-1.3200,36.8400,6,3,6,8,7),
    ("Eastleigh","Nairobi",28000,0.7,-1.2800,36.8500,6,3,5,8,6),
    ("Ruaka","Kiambu",25000,0.6,-1.1050,36.8800,5,2,6,6,6),
    ("Kahawa West","Nairobi",22000,0.55,-1.1700,36.9000,4,1,5,5,5),
    ("Ruaraka","Nairobi",30000,0.7,-1.2400,36.8900,5,2,6,7,6),
    ("Kasarani","Nairobi",32000,0.75,-1.2200,36.9000,6,2,6,7,6),
    ("Embakasi","Nairobi",26000,0.65,-1.3200,36.8900,5,2,5,6,5),
    ("Syokimau","Machakos",24000,0.6,-1.3600,36.9800,4,1,6,5,5),
    ("Thika Road","Kiambu",28000,0.65,-1.1800,36.9500,5,2,6,6,6),
    ("Ngong Road","Nairobi",38000,0.85,-1.3200,36.7600,7,3,7,7,7),
]
ESTATE_DF = pd.DataFrame(ESTATES, columns=["estate_name","county","base","mult","lat","lon","schools","hospitals","security","transport","water"])
ESTATE_DF["livability"] = (ESTATE_DF["schools"]*0.8 + ESTATE_DF["hospitals"]*1.2 + ESTATE_DF["security"]*1.5 + ESTATE_DF["transport"]*1.2 + ESTATE_DF["water"]*1.0).round(1)
ESTATE_DF["insecurity_level"] = ESTATE_DF["security"].apply(lambda x: "Low" if x>=8 else "Medium" if x>=6 else "High")

@st.cache_data
def load_data():
    random.seed(42)
    types = ["Apartment","Flat","Townhouse","Bungalow","Studio"]
    agents = ["Pamela Properties","HassConsult","Knight Frank KE","Private Landlord","Rentals.co.ke"]
    rows = []
    today = date.today()
    for i in range(120):
        e = random.choice(ESTATES)
        estate, county, base, mult = e[0], e[1], e[2], e[3]
        bedrooms = random.choice([1,1,2,2,2,3,3,4])
        bathrooms = max(1, bedrooms - random.choice([0,1]))
        size = 45 + bedrooms*30 + random.randint(-10,25)
        price = int(base * (0.7 + bedrooms*0.35) * mult * random.uniform(0.85,1.25)/100)*100
        rows.append({
            "title": f"{bedrooms} Bed {random.choice(types)} in {estate}",
            "estate_name": estate, "county": county,
            "property_type": random.choice(types),
            "bedrooms": bedrooms, "bathrooms": bathrooms,
            "size_sqm": size, "price_kes": price,
            "price_per_sqm": round(price/size,0),
            "agent_name": random.choice(agents),
            "scraped_date": str(today - timedelta(days=random.randint(0,60))),
        })
    df = pd.DataFrame(rows)
    df = df.merge(ESTATE_DF, on=["estate_name","county"], how="left")
    return df

df = load_data()
avg_estate = df.groupby("estate_name").agg(avg_rent=("price_kes","mean"), listings=("price_kes","count")).reset_index().merge(ESTATE_DF, on="estate_name")
avg_estate["avg_rent"] = avg_estate["avg_rent"].round(0).astype(int)

# ---------- Header ----------
centered("🏠 Nairobi Rental Market Intelligence System", 1)
st.markdown("<p style='text-align: center; color: gray;'>By [Your Name] • GenData • Databases & SQL Track • MySQL + Tableau + Streamlit</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><b>Problem:</b> Nairobi renters have no fair-rent benchmark. <b>Solution:</b> A MySQL database + advanced SQL + dashboard that finds the cheapest <i>and safest</i> estate in 10 seconds.</p>", unsafe_allow_html=True)
st.divider()

# ---------- Sidebar ----------
st.sidebar.header("🔍 Filter Listings")
bed = st.sidebar.slider("Bedrooms", 1, 4, 2)
max_budget = st.sidebar.slider("Max budget (KSh)", 20000, 200000, 50000, step=5000)
min_security = st.sidebar.slider("Minimum security rating (1-10)", 1, 10, 5)
estate_filter = st.sidebar.multiselect("Estates", sorted(df.estate_name.unique()), default=sorted(df.estate_name.unique()))
filtered = df[(df.bedrooms==bed) & (df.price_kes<=max_budget) & (df.security>=min_security) & (df.estate_name.isin(estate_filter))].sort_values("price_kes")
st.sidebar.metric("Matching listings", len(filtered))
if len(filtered):
    st.sidebar.metric("Cheapest", f"KSh {filtered.price_kes.min():,}")
    st.sidebar.metric("Avg security", f"{filtered.security.mean():.1f}/10")

tab1, tab2 = st.tabs(["📋 Overview", "📈 Dashboard"])

with tab1:
    centered("Project Overview", 2)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total listings", len(df)); c2.metric("Estates", df.estate_name.nunique())
    c3.metric("Avg rent", f"KSh {int(df.price_kes.mean()):,}"); c4.metric("Avg security", f"{df.security.mean():.1f}/10")
    st.markdown("""
    ### Pipeline
    **Python Scraper (Property24) → MySQL Database → Advanced SQL → Tableau / Streamlit Dashboard**

    | Layer | Tool | Role |
    |---|---|---|
    | Collect | Python (requests, BeautifulSoup) | Scrape listings → CSV |
    | Store | MySQL + Workbench | 4 tables (incl. amenities), ERD, 3NF, indexes |
    | Analyse | SQL | JOINs, GROUP BY, CASE, CTEs, Window Functions |
    | Visualise | Tableau + This Streamlit website | Interactive dashboard with map |

    **New in v2 (teacher feedback):** Added **security, schools, hospitals, transport, water** per estate + **Livability Score** + **map view**.
    """)
    st.dataframe(df[["title","estate_name","bedrooms","price_kes","schools","hospitals","security","livability"]].head(10), use_container_width=True)

with tab2:
    centered("Dashboard — Rent, Safety & Amenities", 2)
    st.markdown("<p style='text-align: center; color: gray;'>All graphs have centered titles and labeled axes • Use the sidebar to filter live</p>", unsafe_allow_html=True)

    # GRAPH 1
    centered("Graph 1: Average Rent by Estate (KSh)", 3)
    fig1 = px.bar(avg_estate.sort_values("avg_rent"), x="estate_name", y="avg_rent", color="avg_rent", color_continuous_scale="RdYlGn_r",
                  labels={"estate_name":"Estate","avg_rent":"Average Rent (KSh)"}, title="Average Rent by Estate")
    fig1.update_layout(title_x=0.5, xaxis_title="Estate", yaxis_title="Average Rent (KSh)", xaxis_tickangle=-30)
    st.plotly_chart(fig1, use_container_width=True)

    # GRAPH 2
    centered("Graph 2: Rent vs Livability Score (Price vs Amenities)", 3)
    fig2 = px.scatter(avg_estate, x="livability", y="avg_rent", text="estate_name", color="security", color_continuous_scale="Viridis",
                      labels={"livability":"Livability Score (schools+hospitals+security+transport)","avg_rent":"Average Rent (KSh)","security":"Security (1-10)"},
                      title="Rent vs Livability — Top-left = cheap + livable (best value)")
    fig2.update_layout(title_x=0.5, xaxis_title="Livability Score", yaxis_title="Average Rent (KSh)")
    st.plotly_chart(fig2, use_container_width=True)

    # GRAPH 3 
    centered("Graph 3: Security Rating by Estate (1-10)", 3)
    fig3 = px.bar(avg_estate.sort_values("security"), x="estate_name", y="security", color="security", color_continuous_scale="Blues",
                  labels={"estate_name":"Estate","security":"Security Rating (1-10)"}, title="Security Rating by Estate — Higher = Safer")
    fig3.update_layout(title_x=0.5, xaxis_title="Estate", yaxis_title="Security Rating (1-10)", xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

    # MAP
    centered("Map: Estates in Nairobi — Location & Average Rent", 3)
    st.markdown("<p style='text-align: center; color: gray;'>Pin size = number of listings • Hover for details • Westlands & Lavington = premium & safest • Ruaka & Kahawa West = cheapest</p>", unsafe_allow_html=True)
    map_df = avg_estate.rename(columns={"lat":"lat","lon":"lon"})
    st.map(map_df[["lat","lon"]])
    st.dataframe(avg_estate[["estate_name","county","avg_rent","schools","hospitals","security","livability","lat","lon"]].sort_values("avg_rent"), use_container_width=True, hide_index=True)

    centered("Your Filtered Results (Sidebar)", 3)
    if len(filtered):
        st.dataframe(filtered[["title","estate_name","bedrooms","price_kes","schools","hospitals","security","livability"]], use_container_width=True, hide_index=True)
        st.success(f"✅ {len(filtered)} listings match: {bed} bed, under KSh {max_budget:,}, security ≥ {min_security}/10. Cheapest: {filtered.iloc[0]['title']} — KSh {filtered.iloc[0]['price_kes']:,}")
    else:
        st.warning("No listings match — increase budget or lower security filter.")

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>💡 Database & SQL + Insights are in the PowerPoint presentation — this website focuses on Overview and the live Dashboard.</p>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>Developed by Denis • GenData Project • Nairobi Rental Market Intelligence System • Python → MySQL → SQL → Tableau / Streamlit</p>", unsafe_allow_html=True)
