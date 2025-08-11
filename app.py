import os
import pandas as pd
import streamlit as st

# ----------- CONFIG ------------
BASE_PATH = r"D:\Downloads\galvanostatic_discharge_test\main_folder"  # Change this to your main folder path
CHEMISTRIES = ["LFP", "NMC", "NCA"]

# ----------- APP UI ------------
st.set_page_config(page_title="TEMPEST", page_icon="🔋", layout="centered")

st.markdown(
    """
    <h1 style="text-align:center; color:#2E86C1;">TEMPEST🔋</h1>
    <p style="text-align:center; font-size:18px;">
        Compare selected battery chemistries and find the one that stays coolest for your ambient temperature.
    </p>
    """,
    unsafe_allow_html=True
)

ambient_temp = st.number_input("🌡 Enter Ambient Temperature (°C):", min_value=-10.0, max_value=60.0, step=0.5)
selected_chems = st.multiselect("🔍 Select Battery Chemistries to Analyze:", CHEMISTRIES, default=CHEMISTRIES)
run_analysis = st.button("🚀 Run Analysis")

# ----------- HELPER FUNCTION ------------
def get_temp_folder(ambient):
    """Return the folder name based on ambient temperature."""
    if ambient < 20:
        return "5deg"
    elif 20 <= ambient <= 30:
        return "25deg"
    else:
        return "35deg"

def calculate_avg_time_above(folder_path, chemistry, ambient):
    """Calculate avg time above ambient temp per file for a given chemistry."""
    chem_folder = os.path.join(folder_path, chemistry)
    file_times = []

    for file_name in os.listdir(chem_folder):
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(chem_folder, file_name)
            try:
                df = pd.read_excel(file_path)

                mask = df["Surface_Temp(degC)"] > ambient
                time_values = (df["Test_Time(s)"] - df["Step_Time(s)"])[mask]
                total_time_for_file = time_values.sum()

                file_times.append(total_time_for_file)

            except Exception as e:
                st.error(f"Error reading {file_name}: {e}")

    if file_times:
        return sum(file_times) / len(file_times)  
    else:
        return None

# ----------- MAIN LOGIC ------------
if run_analysis:
    chosen_folder = get_temp_folder(ambient_temp)
    folder_path = os.path.join(BASE_PATH, chosen_folder)

    results = []
    for chem in selected_chems:
        avg_time = calculate_avg_time_above(folder_path, chem, ambient_temp)
        results.append({"Chemistry": chem, "Avg Time Above Ambient (s)": avg_time})

    results_df = pd.DataFrame(results)
    # st.dataframe(results_df.style.format({"Avg Time Above Ambient (s)": "{:.2f}"}))

    optimal_row = results_df.loc[results_df["Avg Time Above Ambient (s)"].idxmin()]
    optimal = optimal_row["Chemistry"]

    st.markdown(
        f"""
        <div style="background-color:#FFD700; padding:15px; border-radius:10px; 
                    text-align:center; font-size:22px; font-weight:bold; color:#000;">
            ✅ Optimal Battery: {optimal}
        </div>
        """,
        unsafe_allow_html=True
    )
