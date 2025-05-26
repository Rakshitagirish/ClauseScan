import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px

# Load user data
@st.cache_data
def load_user_data():
    try:
        df = pd.read_csv("users.csv", header=None, names=["username", "hashed_password"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "hashed_password"])

# Page config
st.set_page_config("User Management Dashboard", layout="wide")

# Title & Intro
st.markdown("""
    <style>
        .gradient-text {
            font-size: 48px;
            font-weight: bold;
            background: linear-gradient(90deg, #1995AD, #A1C6EA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>

    <h1 class='gradient-text'>👥 User Management Dashboard</h1>
    <p style='color:#555;'>Manage user accounts, detect weak security, and review account activity.</p>
""", unsafe_allow_html=True)


df = load_user_data()

# Sidebar search
st.sidebar.header("🔍 Search")
search_term = st.sidebar.text_input("Search username:")
filtered_df = df[df["username"].str.contains(search_term, case=False, na=False)] if search_term else df

# Summary stats
st.subheader("📊 Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👤 Total Users", df.shape[0])
with col2:
    st.metric("🔑 Unique Passwords", df["hashed_password"].nunique())
with col3:
    reused_count = df["hashed_password"].duplicated(keep=False).sum()
    st.metric("⚠️ Passwords Reused", reused_count)

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Users", "⚠️ Reused Passwords", "📈 Reuse Frequency"])

# Tab 1: User Table (safe)
with tab1:
    st.subheader("📋 User List")
    st.dataframe(filtered_df[["username"]], use_container_width=True)

# Tab 2: Reused Passwords (without showing hashes)
with tab2:
    st.subheader("⚠️ Users with Reused Passwords")
    reused_df = df[df.duplicated(subset="hashed_password", keep=False)]
    if reused_df.empty:
        st.success("✅ All users have unique passwords!")
    else:
        st.warning("Some users are sharing the same password (hash hidden).")
        grouped = reused_df.groupby("hashed_password")["username"].apply(list).reset_index()
        grouped["User Count"] = grouped["username"].apply(len)
        grouped["Users"] = grouped["username"].apply(lambda x: ", ".join(x))
        st.dataframe(grouped[["Users", "User Count"]], use_container_width=True)

# Tab 3: Chart
with tab3:
    st.subheader("🔢 Password Reuse Frequency (Anonymized)")
    if reused_df.empty:
        st.info("No reused passwords to display.")
    else:
        reuse_counts = reused_df["hashed_password"].value_counts().reset_index()
        reuse_counts.columns = ["Anonymized Password", "User Count"]
        reuse_counts["Anonymized Password"] = reuse_counts["Anonymized Password"].apply(lambda x: "hash_" + str(hash(x))[-6:])
        fig = px.bar(
            reuse_counts,
            x="Anonymized Password",
            y="User Count",
            title="Password Reuse (Anonymized)",
            color="User Count",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

# Optional: Download current view
st.sidebar.markdown("### 📥 Download Filtered Users")
st.sidebar.download_button(
    "Download CSV",
    filtered_df[["username"]].to_csv(index=False).encode(),
    file_name="filtered_users.csv",
    mime="text/csv"
)
