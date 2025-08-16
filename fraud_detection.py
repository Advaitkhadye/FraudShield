import streamlit as st
import pandas as pd
import joblib
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

# -------------------- LOAD MODEL --------------------
model = joblib.load("fraud_detection_pipeline.pkl")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #141414, #1e1e2f);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        /* Main Title Glow */
        .header-title {
            font-size: 48px;
            font-weight: 900;
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 8px rgba(0, 198, 255, 0.7),
                         0 0 15px rgba(0, 114, 255, 0.5),
                         0 0 25px rgba(0, 114, 255, 0.6);
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from {
                text-shadow: 0 0 5px rgba(0, 198, 255, 0.6),
                             0 0 12px rgba(0, 114, 255, 0.4),
                             0 0 18px rgba(0, 114, 255, 0.6);
            }
            to {
                text-shadow: 0 0 15px rgba(0, 198, 255, 1),
                             0 0 25px rgba(0, 114, 255, 0.8),
                             0 0 35px rgba(0, 114, 255, 1);
            }
        }
        /* Subtitle soft glow */
        .header-subtitle {
            font-size: 18px;
            color: #bbb;
            margin-top: 5px;
            text-shadow: 0 0 4px rgba(255, 255, 255, 0.2);
        }
        .result-box {
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 20px;  /* 👈 Added space below the box */
        }
        .success-box { background-color: #e8f5e9; color: #2e7d32; }
        .error-box { background-color: #ffebee; color: #c62828; }
    </style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
        <h1 class="header-title">FraudShield</h1>
        <p class="header-subtitle">AI-Powered Fraud Detection System</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.title(" About")
st.sidebar.info("FraudShield helps predict if a transaction is fraudulent.\n\n**Created by Advait Khadye**")

# -------------------- COMMON PDF GENERATOR --------------------
def generate_pdf(df, title="Fraud Detection Report"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=20)
    th = ParagraphStyle("TableHeader", parent=styles["Normal"], fontName="Helvetica-Bold",
                        fontSize=10, leading=12, alignment=1)
    tc = ParagraphStyle("TableCell", parent=styles["Normal"], fontSize=10, leading=12, alignment=1)

    story = [Paragraph(title, title_style), Spacer(1, 12)]

    # Column renaming for nice headers
    col_map = {
        "type": "Type",
        "amount": "Amount",
        "oldbalanceOrg": "Old Balance (Sender)",
        "newbalanceOrig": "New Balance (Sender)",
        "oldbalanceDest": "Old Balance (Receiver)",
        "newbalanceDest": "New Balance (Receiver)",
        "Prediction": "Prediction Result",
        "prediction": "Prediction Result",
    }

    headers = [col_map.get(col, col) for col in df.columns]
    header_row = [Paragraph(h, th) for h in headers]

    table_data = [header_row]
    for _, row in df.iterrows():
        row_cells = []
        for col in df.columns:
            if col.lower() == "prediction":
                if row[col] in ["Fraud", 1]:
                    row_cells.append(Paragraph('<font color="red">■ Fraudulent</font>', tc))
                else:
                    row_cells.append(Paragraph('<font color="green">■ Legitimate</font>', tc))
            else:
                row_cells.append(Paragraph(str(row[col]), tc))
        table_data.append(row_cells)

    table = Table(table_data, hAlign="CENTER", colWidths=["*"] * len(headers), repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------- TEMPLATE CSV --------------------
def get_template_csv():
    template = pd.DataFrame([{
        "type": "PAYMENT",
        "amount": 1000,
        "oldbalanceOrg": 5000,
        "newbalanceOrig": 4000,
        "oldbalanceDest": 1000,
        "newbalanceDest": 2000
    }])
    return template.to_csv(index=False).encode("utf-8")

# -------------------- HEADER MAPPING --------------------
def map_headers(df):
    mapping = {
        "transaction_type": "type",
        "type": "type",
        "amt": "amount",
        "amount": "amount",
        "old_balance_sender": "oldbalanceOrg",
        "oldbalanceorg": "oldbalanceOrg",
        "new_balance_sender": "newbalanceOrig",
        "newbalanceorig": "newbalanceOrig",
        "old_balance_receiver": "oldbalanceDest",
        "oldbalancedest": "oldbalanceDest",
        "new_balance_receiver": "newbalanceDest",
        "newbalancedest": "newbalanceDest",
    }
    df = df.rename(columns=lambda x: x.strip().lower())
    df = df.rename(columns={col: mapping.get(col, col) for col in df.columns})
    return df

# -------------------- UI --------------------
st.subheader("🔎 Check Transactions")

tab1, tab2 = st.tabs(["➕ Single Transaction", "📂 Upload CSV"])

# --- SINGLE TRANSACTION ---
with tab1:
    transaction_type = st.selectbox("Transaction Type", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEPOSIT"])
    amount = st.number_input("Amount", min_value=0.0, value=1000.0)
    oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=5000.0)
    newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=4000.0)
    oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=1000.0)
    newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=2000.0)

    if st.button(" Predict Single"):
        input_data = pd.DataFrame([{
            "type": transaction_type, "amount": amount,
            "oldbalanceOrg": oldbalanceOrg, "newbalanceOrig": newbalanceOrig,
            "oldbalanceDest": oldbalanceDest, "newbalanceDest": newbalanceDest
        }])
        try:
            prediction = model.predict(input_data)[0]
            input_data["Prediction"] = "Fraud" if prediction == 1 else "Legit"

            box_class = "error-box" if prediction == 1 else "success-box"
            message = " Fraudulent Transaction" if prediction == 1 else "Legitimate Transaction"
            st.markdown(f"<div class='result-box {box_class}'>{message}</div>", unsafe_allow_html=True)

            st.download_button(
                "📄 Download PDF Report",
                data=generate_pdf(input_data, "Fraud Detection Report"),
                file_name="fraud_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# --- BULK (CSV) ---
with tab2:
    st.markdown("📥 Upload your CSV file or download the template to get started.")
    st.download_button("📑 Download CSV Template", data=get_template_csv(), file_name="template.csv", mime="text/csv")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df = map_headers(df)

            required_cols = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"⚠️ Missing columns in CSV: {missing_cols}")
            else:
                predictions = model.predict(df)
                df["Prediction"] = ["Fraud" if p == 1 else "Legit" for p in predictions]
                st.success("✅ Predictions generated successfully!")
                st.dataframe(df.head(20))

                st.download_button(
                    "📄 Download PDF Report",
                    data=generate_pdf(df, "Fraud Detection Report"),
                    file_name="fraud_predictions.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"⚠️ Error while processing file: {e}")
