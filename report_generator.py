from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import datetime
import os

def generate_pdf_report(output_path, forecast_out, tips_out, year_plots):

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, height - 50, "Eco Electricity Usage Report")

    # Date
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, "Generated on: " + str(datetime.date.today()))

    # Forecast Summary
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 110, "📈 Forecast Summary")

    c.setFont("Helvetica", 12)
    c.drawString(60, height - 140, f"Predicted Usage: {forecast_out['predicted_usage_kWh']} kWh")
    c.drawString(60, height - 160, f"Predicted Bill: ₹{forecast_out['predicted_bill_inr']}")
    c.drawString(60, height - 180, f"MAE: {forecast_out['mae_units']}")
    c.drawString(60, height - 200, f"R2 Score: {forecast_out['r2_score']}")
    

    # Smart Tips Section
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 240, "💡 Smart Tips")

    y = height - 265
    c.setFont("Helvetica", 11)

    for tip in tips_out["tips"]:
        c.drawString(60, y, f"- {tip}")
        y -= 20

    # New page for graphs
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📊 Electricity Usage Graphs")

    y_img = height - 120

    for plot in year_plots:
        if os.path.exists(plot):
            img = ImageReader(plot)
            c.drawImage(img, 50, y_img - 200, width=500, height=200, preserveAspectRatio=True)
            y_img -= 240

            if y_img < 150:
                c.showPage()
                y_img = height - 100

    c.save()
