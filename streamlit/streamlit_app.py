import streamlit as st
import requests
import os

st.set_page_config(page_title="Bank Churn Predictor", layout="wide")

st.title("Bank Churn Prediction System")
st.write("Advanced analytics for customer churn prediction and data drift monitoring.")

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Tabs pour naviguer entre sections
tab1, tab2 = st.tabs(["Churn Prediction", "Drift Detection"])

# ========================
# TAB 1: PREDICTION
# ========================
with tab1:
    st.header("Customer Churn Prediction")
    st.write("Enter customer details below to predict churn risk.")

    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
            credit_score = st.number_input("Credit Score", min_value=0, max_value=1000, value=650, step=1)
            balance = st.number_input("Balance ($)", min_value=0.0, value=1000.0, step=100.0)
        
        with col2:
            tenure = st.number_input("Tenure (years)", min_value=0, max_value=50, value=5, step=1)
            products = st.number_input("Products", min_value=0, max_value=10, value=2, step=1)
            is_active = st.selectbox("Account Status", [1, 0], format_func=lambda x: "Active" if x == 1 else "Inactive")

        submitted = st.form_submit_button("Analyze Churn Risk", use_container_width=True)

    if submitted:
        payload = {
            "age": int(age),
            "credit_score": int(credit_score),
            "balance": float(balance),
            "tenure": int(tenure),
            "products": int(products),
            "is_active": int(is_active),
        }

        with st.spinner("Processing prediction..."):
            try:
                r = requests.post(f"{API_URL}/predict", json=payload, timeout=60)

                if r.status_code >= 400:
                    st.error(f"API Error (HTTP {r.status_code})")
                    try:
                        st.json(r.json())
                    except:
                        st.text(r.text)
                    st.stop()

                data = r.json()
                
                # Display result with styling
                col1, col2, col3 = st.columns(3)
                with col1:
                    status = "High Risk" if data["churn"] == 1 else "Low Risk"
                    st.metric("Churn Status", status)
                with col2:
                    prob = data["churn_probability"]
                    st.metric("Probability", f"{prob:.1%}")
                with col3:
                    if prob < 0.33:
                        risk = "Low"
                    elif prob < 0.66:
                        risk = "Medium"
                    else:
                        risk = "High"
                    st.metric("Risk Level", risk)
                
                st.success("Prediction completed successfully")
                with st.expander("View Full Response"):
                    st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: {str(e)[:100]}")
                st.info(f"Ensure the API is running at {API_URL}")


# ========================
# TAB 2: DRIFT DETECTION
# ========================
with tab2:
    st.header("Data Drift Detection")
    st.write("Monitor changes in data distribution over time.")
    
    st.info(
        "Data drift occurs when the statistical properties of features change, "
        "potentially reducing model accuracy. This analysis compares current data "
        "against a baseline reference."
    )

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Analysis Settings")
        simulate_drift = st.checkbox(
            "Use Simulated Drift",
            value=False,
            help="Apply synthetic changes to data for testing (age +8, balance +50%)"
        )
        
        if st.button("Run Drift Analysis", use_container_width=True, type="primary"):
            with st.spinner("Analyzing data distribution..."):
                try:
                    # Appeler l'endpoint /drift de l'API
                    params = {"simulate": simulate_drift}
                    r = requests.get(f"{API_URL}/drift", params=params, timeout=120)
                    
                    if r.status_code >= 400:
                        st.error(f"API Error (HTTP {r.status_code})")
                        try:
                            st.json(r.json())
                        except:
                            st.text(r.text)
                        st.stop()
                    
                    result = r.json()
                    
                    st.success("Analysis completed")
                    
                    # Display results
                    col1_res, col2_res = st.columns(2)
                    with col1_res:
                        if result.get("dataset_drift") is not None:
                            drift_detected = result["dataset_drift"]
                            status = "Drift Detected" if drift_detected else "No Drift"
                            st.metric("Drift Status", status)
                        else:
                            st.warning("Status unavailable")
                    
                    with col2_res:
                        mode = "Simulated" if simulate_drift else "Real Data"
                        st.metric("Analysis Mode", mode)
                    
                    # Links to reports
                    st.subheader("Generated Reports")
                    col_html, col_json = st.columns(2)
                    with col_html:
                        st.write("**HTML Report**")
                        st.caption(result.get('html_report', 'N/A'))
                    with col_json:
                        st.write("**JSON Report**")
                        st.caption(result.get('json_report', 'N/A'))
                    
                    # Show full response
                    with st.expander("View Full Response"):
                        st.json(result)
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {str(e)[:100]}")
                    st.info(f"Ensure the API is running at {API_URL}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader("How It Works")
        st.write(
            """
            **Process:**
            1. Reference Data: 60% of historical records
            2. Current Data: 40% of historical records
            3. Analysis: Evidently compares feature distributions
            4. Result: Boolean indicating drift detection
            
            **Example Simulated Changes:**
            - Age: +8 years
            - Credit score: -50 points
            - Balance: +50%
            - Activity: Higher inactivity rate
            """
        )
        
        st.divider()
        st.subheader("Resources")
        st.markdown(
            """
            - [Evidently Documentation](https://docs.evidentlyai.com/)
            - [Understanding Dataset Shift](https://en.wikipedia.org/wiki/Dataset_shift)
            - Reports saved to `/reports/drift_report.html`
            """
        )

# ========================
# FOOTER
# ========================
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption(f"API Endpoint: {API_URL}")
with col2:
    st.caption("Built with FastAPI, Streamlit, and MLflow")
