import streamlit as st
import pandas as pd
import joblib
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

# Load model
model = joblib.load("fraud_detection_pipeline.pkl")

st.title("Fraud Detection Prediction App")
st.markdown("Please enter the transaction details and use the predict button")
st.divider()

# Input fields
transaction_type = st.selectbox("Transaction Type", ["PAYMENT", "TRANSFER", "CASH_OUT", "DEPOSIT"])
amount = st.number_input("Amount", min_value=0.0, value=1000.0)
oldbalanceOrg = st.number_input("Old Balance (Sender)", min_value=0.0, value=10000.0)
newbalanceOrig = st.number_input("New Balance (Sender)", min_value=0.0, value=9000.0)
oldbalanceDest = st.number_input("Old Balance (Receiver)", min_value=0.0, value=0.0)
newbalanceDest = st.number_input("New Balance (Receiver)", min_value=0.0, value=0.0)

# PDF generation function
def generate_pdf(data, prediction):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=20)
    section_header = ParagraphStyle("SectionHeader", parent=styles["Heading2"], alignment=TA_LEFT, spaceAfter=10)

    story = []

    # Title
    story.append(Paragraph("Fraud Detection Report", title_style))
    story.append(Spacer(1, 12))

    # Transaction details
    story.append(Paragraph("Transaction Details:", section_header))

    # Capitalized table format
    data_table = [
        ["Type", str(data["type"]).capitalize()],
        ["Amount", f"{data['amount']}"],
        ["Old Balance (Sender)", f"{data['oldbalanceOrg']}"],
        ["New Balance (Sender)", f"{data['newbalanceOrig']}"],
        ["Old Balance (Receiver)", f"{data['oldbalanceDest']}"],
        ["New Balance (Receiver)", f"{data['newbalanceDest']}"],
    ]

    table = Table(data_table, hAlign="LEFT", colWidths=[200, 200])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(table)
    story.append(Spacer(1, 20))

    # Prediction result
    story.append(Paragraph("Prediction Result:", section_header))
    if prediction == 1:
        pred_text = "⚠️ Fraudulent Transaction Detected"
        pred_color = colors.red
    else:
        pred_text = "✅ Legitimate Transaction"
        pred_color = colors.green

    result_table = Table(
        [[pred_text]],
        hAlign="LEFT",
        colWidths=[300],
        style=[
            ("TEXTCOLOR", (0, 0), (-1, -1), pred_color),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ],
    )

    story.append(result_table)

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# Prediction button
if st.button("Predict"):
    input_data = pd.DataFrame([{
        "type": transaction_type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest
    }])

    prediction = model.predict(input_data)[0]

    st.subheader(f"Prediction : '{int(prediction)}'")

    if prediction == 1:
        st.error("This transaction can be fraud")
    else:
        st.success("This transaction looks like it is not a fraud")

    # Generate PDF report
    pdf_buffer = generate_pdf(input_data.iloc[0].to_dict(), prediction)

    # Download button
    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="fraud_detection_report.pdf",
        mime="application/pdf"
    )
