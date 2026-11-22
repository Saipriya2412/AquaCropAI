
import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)

from werkzeug.utils import secure_filename

from database.db import get_db_connection, create_table
from models.weather_service import get_weather
from models.water_prediction import analyze_water
from models.disease_prediction import predict_disease
from models.paddy_prediction import predict_paddy_disease

app = Flask(__name__)

app.secret_key = "aquacrop-ai-secret-key"

# Create database tables
create_table()

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Farmer registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        farmer_name = request.form.get("farmer_name", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        farm_area = request.form.get("farm_area", "").strip()
        crop = request.form.get("crop", "")
        soil_type = request.form.get("soil_type", "")
        crop_stage = request.form.get("crop_stage", "")
        irrigation_source = request.form.get("irrigation_source", "")
        irrigation_method = request.form.get("irrigation_method", "")

        if not farmer_name or not location or not farm_area:
            flash("Please fill in all required fields.")
            return redirect(url_for("register"))

        try:
            farm_area = float(farm_area)

            if farm_area <= 0:
                raise ValueError

        except ValueError:
            flash("Enter a valid farm area.")
            return redirect(url_for("register"))

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO farmers (
                farmer_name,
                phone,
                location,
                farm_area,
                crop,
                soil_type,
                crop_stage,
                irrigation_source,
                irrigation_method
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            farmer_name,
            phone,
            location,
            farm_area,
            crop,
            soil_type,
            crop_stage,
            irrigation_source,
            irrigation_method
        ))

        connection.commit()
        connection.close()

        flash("Farmer registered successfully!")

        return redirect(url_for("dashboard"))

    return render_template("register.html")

# Farmer dashboard
@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    farmers = connection.execute(
        "SELECT * FROM farmers ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        farmers=farmers
    )

# Water risk analysis
@app.route("/water", methods=["GET", "POST"])
def water():

    connection = get_db_connection()

    farmers = connection.execute(
        "SELECT * FROM farmers"
    ).fetchall()

    connection.close()

    result = None

    if request.method == "POST":

        farmer_id = request.form.get("farmer_id")
        soil_moisture = request.form.get("soil_moisture")
        rainfall = request.form.get("rainfall")

        farmer = next(
            (f for f in farmers if str(f["id"]) == farmer_id),
            None
        )

        if farmer is None:
            flash("Please select a valid farm.")
            return redirect(url_for("water"))

        try:
            moisture = float(soil_moisture)
            rain = float(rainfall)

            if not 0 <= moisture <= 100 or rain < 0:
                raise ValueError

            # Get live weather forecast
            try:
                weather_data = get_weather(farmer["location"])

                forecast_rainfall = weather_data[
                    "today_rainfall_forecast"
                ]

            except Exception:
                forecast_rainfall = 0

                flash(
                    "Live weather unavailable. "
                    "Analysis uses no forecast rainfall."
                )

            # Analyze water conditions
            result = analyze_water(
                farmer["crop"],
                moisture,
                rain,
                forecast_rainfall,
                farmer["crop_stage"]
            )

        except (ValueError, TypeError):
            flash("Enter valid moisture and rainfall values.")

    return render_template(
        "water.html",
        farmers=farmers,
        result=result
    )

# Live Weather Intelligence
@app.route("/weather", methods=["GET", "POST"])
def weather():

    connection = get_db_connection()

    farmers = connection.execute(
        "SELECT * FROM farmers"
    ).fetchall()

    connection.close()

    weather_data = None

    if request.method == "POST":

        farmer_id = request.form.get("farmer_id")

        farmer = next(
            (f for f in farmers if str(f["id"]) == farmer_id),
            None
        )

        if farmer is None:
            flash("Please select a valid farm.")

        else:
            try:
                weather_data = get_weather(farmer["location"])

            except (ValueError, KeyError):
                flash(
                    "Weather information could not be found "
                    "for this location."
                )

            except Exception:
                flash(
                    "Unable to connect to the weather service. "
                    "Please try again."
                )

    return render_template(
        "weather.html",
        farmers=farmers,
        weather_data=weather_data
    )

# Groundwater Intelligence
@app.route("/groundwater", methods=["GET", "POST"])
def groundwater():

    connection = get_db_connection()

    farmers = connection.execute(
        "SELECT * FROM farmers"
    ).fetchall()

    if request.method == "POST":

        farmer_id = request.form.get("farmer_id")
        water_level = request.form.get("water_level")
        recorded_on = request.form.get("recorded_on")
        notes = request.form.get("notes", "").strip()

        farmer = next(
            (f for f in farmers if str(f["id"]) == farmer_id),
            None
        )

        try:
            level = float(water_level)

            if level < 0 or farmer is None or not recorded_on:
                raise ValueError

            connection.execute("""
                INSERT INTO groundwater_records
                (farmer_id, water_level, recorded_on, notes)
                VALUES (?, ?, ?, ?)
            """, (
                farmer_id,
                level,
                recorded_on,
                notes
            ))

            connection.commit()

            flash("Groundwater record saved successfully!")

        except (ValueError, TypeError):
            flash("Please enter valid groundwater details.")

        connection.close()

        return redirect(url_for("groundwater"))

    # Get all groundwater records
    records = connection.execute("""
        SELECT groundwater_records.*, farmers.farmer_name
        FROM groundwater_records
        JOIN farmers
        ON groundwater_records.farmer_id = farmers.id
        ORDER BY recorded_on ASC, groundwater_records.id ASC
    """).fetchall()

    # Get the most recently recorded farmer
    latest_record = connection.execute("""
        SELECT farmer_id
        FROM groundwater_records
        ORDER BY recorded_on DESC, id DESC
        LIMIT 1
    """).fetchone()

    groundwater_status = "Not enough data"

    status_message = (
        "Add at least two readings to check the groundwater trend."
    )

    # Compare the latest two readings
    if latest_record:

        latest_two = connection.execute("""
            SELECT water_level
            FROM groundwater_records
            WHERE farmer_id = ?
            ORDER BY recorded_on DESC, id DESC
            LIMIT 2
        """, (latest_record["farmer_id"],)).fetchall()

        if len(latest_two) == 2:

            latest_level = latest_two[0]["water_level"]
            previous_level = latest_two[1]["water_level"]

            if latest_level < previous_level:

                groundwater_status = "Improving"

                status_message = (
                    "Groundwater depth has decreased. "
                    "The water table is closer to the surface."
                )

            elif latest_level > previous_level:

                groundwater_status = "Declining"

                status_message = (
                    "Groundwater depth has increased. "
                    "The water table is deeper."
                )

            else:

                groundwater_status = "Stable"

                status_message = (
                    "Groundwater depth has not changed."
                )

    connection.close()

    return render_template(
        "groundwater.html",
        farmers=farmers,
        records=records,
        groundwater_status=groundwater_status,
        status_message=status_message
    )

# AI Crop Disease Detection
@app.route("/disease", methods=["GET", "POST"])
def disease():

    result = None
    selected_crop = "Paddy"

    # Clear old flash messages when opening the page
    if request.method == "GET":
        get_flashed_messages()

    if request.method == "POST":

        selected_crop = request.form.get("crop", "Paddy")

        # Support both old and new HTML input names
        file = request.files.get("image")

        if file is None:
            file = request.files.get("leaf_image")

        if selected_crop not in ["Paddy", "Maize"]:

            flash(
                "AI disease detection is currently available "
                "for Paddy and Maize.",
                "warning"
            )

        elif file is None or file.filename == "":

            flash("Please select a leaf image.", "warning")

        else:

            allowed_extensions = (
                ".jpg", ".jpeg", ".png", ".webp"
            )

            if not file.filename.lower().endswith(allowed_extensions):

                flash(
                    "Please upload a JPG, JPEG, PNG or WEBP image.",
                    "warning"
                )

            else:

                try:

                    upload_folder = os.path.join(
                        app.root_path,
                        "static",
                        "uploads"
                    )

                    os.makedirs(upload_folder, exist_ok=True)

                    filename = secure_filename(file.filename)

                    if not filename:
                        raise ValueError("Invalid image filename")

                    filename = str(uuid.uuid4()) + "_" + filename

                    image_path = os.path.join(
                        upload_folder,
                        filename
                    )

                    file.save(image_path)

                    # Paddy disease prediction
                    if selected_crop == "Paddy":

                        result = predict_paddy_disease(image_path)

                    # Maize disease prediction
                    elif selected_crop == "Maize":

                        result = predict_disease(image_path)

                except Exception:

                    app.logger.exception(
                        "Crop disease prediction failed"
                    )

                    flash(
                        "Prediction failed. Please try another image.",
                        "danger"
                    )

    return render_template(
        "disease.html",
        result=result,
        selected_crop=selected_crop
    )

# Run application
if __name__ == "__main__":
    app.run(debug=True)