import os
import json
import uuid
from huggingface_hub import InferenceClient
from google import genai
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from models import db, User, SavedOutfit

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY"
)

# DATABASE CONFIGURATION

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in .env"
    )

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# GEMINI CLIENT

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in .env"
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# HUGGING FACE Setup

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is not configured in .env")

hf_client = InferenceClient(token=HF_TOKEN)

# FOLDERS

UPLOAD_FOLDER = "uploads"
GENERATED_FOLDER = "static/generated"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    GENERATED_FOLDER,
    exist_ok=True
)

# AI SYSTEM PROMPT

SYSTEM_PROMPT = """
You are a professional, friendly, and helpful AI fashion stylist.

Your goal is to make the user feel confident and stylish.

You must carefully follow the user's selected fashion preferences.

IMPORTANT:
- Never assume the user is a woman.
- Never assume the user is a man.
- Always follow the selected gender category: Men, Women, or Unisex.
- The generated outfit must match the selected gender category.
- Follow the selected occasion, style, season, colors, and budget.
- If an image is provided, analyze the clothing, colors, style, and context shown in the image.
- If the user uploads clothing, use the visible clothing as part of your recommendation when appropriate.
- Recommendations should be realistic, wearable, and visually coherent.
- The image_query must clearly describe the intended gender/category so the image generator does not produce the wrong type of outfit.

CRITICAL:
Your response must contain a valid JSON object.

The JSON must follow this structure exactly:

{
  "outfit_name": "Name of the look",
  "top": "Detailed description of the top",
  "bottom": "Detailed description of the bottom",
  "shoes": "Footwear recommendation",
  "accessories": "Matching accessories",
  "style_tip": "A friendly, encouraging styling tip",
  "image_query": "A highly descriptive prompt for an AI image generator. Clearly describe the selected gender/category, clothing pieces, colors, occasion, style, season, accessories, and overall fashion photography."
}

Do not add markdown around the JSON.
"""

# LOGIN USER LOADER

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(
        User,
        int(user_id)
    )

# HOME

@app.route("/")
def home():
    return render_template(
        "index.html"
    )

# REGISTER

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = (
            request.form.get("username")
            or request.form.get("name")
        )

        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return "All fields are required", 400

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already exists", 400

        hashed_pw = generate_password_hash(
            password
        )

        new_user = User(
            username=username,
            email=email,
            password=hashed_pw
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )

# LOGIN

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):
            login_user(user)

            return redirect(
                url_for("chat")
            )

        return "Invalid credentials", 401

    return render_template(
        "login.html"
    )

# LOGOUT

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )

# CHAT PAGE

@app.route("/chat")
@login_required
def chat():

    return render_template(
        "chat.html"
    )

# AI STYLING

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    user_text = request.form.get("text") or ""
    image_file = request.files.get("image")

    # Fashion preferences
    
    gender = request.form.get("gender", "Unisex")
    occasion = request.form.get("occasion", "Casual")
    style = request.form.get("style", "Casual")
    season = request.form.get("season", "Any Season")
    colors = request.form.get("colors", "Any")
    budget = request.form.get("budget", "Medium")

    try:
        contents_list = []

        # Upload image to Gemini if provided
        
        if image_file and image_file.filename != "":
            safe_filename = (
                f"{uuid.uuid4().hex}_{image_file.filename}"
            )

            path = os.path.join(
                UPLOAD_FOLDER,
                safe_filename
            )

            image_file.save(path)

            uploaded_file = client.files.upload(
                file=path
            )

            contents_list.append(uploaded_file)

        # Build personalized request        

        preferences = f"""
        Selected Fashion Preferences:

        Gender/Category: {gender}
        Occasion: {occasion}
        Style: {style}
        Season: {season}
        Preferred Colors: {colors}
        Budget Level: {budget}

        User Request:
        {user_text}
        """

        contents_list.append(
            f"{SYSTEM_PROMPT}\n{preferences}"
        )
      
        # GEMINI: Fashion analysis
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_list
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response"
            )

        text_resp = response.text

        # Extract JSON        

        start_idx = text_resp.find("{")
        end_idx = text_resp.rfind("}")

        if start_idx != -1 and end_idx != -1:
            raw_json = text_resp[
                start_idx:end_idx + 1
            ]
        else:
            raw_json = (
                text_resp
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        data = json.loads(raw_json)
        
        # Make sure image prompt respects preferences        

        image_query = data.get(
            "image_query",
            "High-end fashion photography of a stylish outfit"
        )

        enhanced_prompt = (
            f"{image_query}, "
            "full-body fashion photograph, "
            "head-to-toe view of the model, "
            "face clearly visible and fully inside the frame, "
            "entire head and hair visible, "
            "no face cropping, "
            "no head cropping, "
            "no body cropping, "
            "model standing naturally, "
            "complete outfit visible from head to shoes, "
            "realistic human anatomy, "
            "professional fashion editorial photography, "
            "high-end fashion photography, "
            "natural facial features, "
            "sharp focus on the model, "
            "detailed clothing textures, "
            "balanced composition, "
            "premium lighting"
        )
        
        # HUGGING FACE: Generate outfit image        

        image_found = False

        image_filename = (
            f"outfit_{uuid.uuid4().hex}.png"
        )

        image_path = os.path.join(
            GENERATED_FOLDER,
            image_filename
        )

        try:
            generated_image = hf_client.text_to_image(
                prompt=enhanced_prompt,
                model="black-forest-labs/FLUX.1-schnell"
            )

            generated_image.save(image_path)

            image_found = True

            print(
                f"Image generated successfully: "
                f"{image_path}"
            )

        except Exception as img_err:
            print(
                "Hugging Face Image Generation Failed:",
                img_err
            )
        
        # Generated image URL        

        if image_found:
            data["generated_image_url"] = (
                f"/static/generated/"
                f"{image_filename}"
            )
        else:
            data["generated_image_url"] = (
                "https://images.unsplash.com/"
                "photo-1490481658327-477593838029"
                "?q=80&w=1000&auto=format&fit=crop"
            )
        
        # Return additional preference information        

        data["preferences"] = {
            "gender": gender,
            "occasion": occasion,
            "style": style,
            "season": season,
            "colors": colors,
            "budget": budget
        }

        return jsonify(data)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

        error_msg = str(e)

        if "RESOURCE_EXHAUSTED" in error_msg:
            error_msg = (
                "The AI service is temporarily busy. "
                "Please try again in a little while."
            )

        return jsonify({
            "outfit_name": "Stylist is taking a breather",
            "top": "",
            "bottom": "",
            "shoes": "",
            "accessories": "",
            "style_tip": f"Error: {error_msg}",
            "generated_image_url": (
                "https://images.unsplash.com/"
                "photo-1490481658327-477593838029"
                "?q=80&w=1000&auto=format&fit=crop"
            )
        })
    
# SAVE OUTFIT

@app.route(
    "/save_outfit",
    methods=["POST"]
)
@login_required
def save_outfit():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No outfit data received"
        }), 400

    try:

        outfit = SavedOutfit(

            user_id=current_user.id,

            outfit_name=data.get(
                "outfit_name",
                "Untitled"
            ),

            top=data.get(
                "top",
                ""
            ),

            bottom=data.get(
                "bottom",
                ""
            ),

            shoes=data.get(
                "shoes",
                ""
            ),

            accessories=data.get(
                "accessories",
                ""
            ),

            style_tip=data.get(
                "style_tip",
                ""
            ),

            # Save the generated fashion visual
            generated_image_url=data.get(
                "generated_image_url",
                ""
            )
        )

        db.session.add(outfit)

        db.session.commit()

        return jsonify({
            "message": "Outfit Saved"
        }), 200

    except Exception as e:

        db.session.rollback()

        print(
            f"SAVE ERROR: {e}"
        )

        return jsonify({
            "error": str(e)
        }), 500

#DELETE OUTFIT
@app.route("/delete_outfit/<int:outfit_id>", methods=["POST"])
@login_required
def delete_outfit(outfit_id):
    outfit = SavedOutfit.query.filter_by(
        id=outfit_id,
        user_id=current_user.id
    ).first()

    if not outfit:
        return jsonify({
            "error": "Outfit not found."
        }), 404

    try:
        # Remove locally generated image if it exists
        image_url = outfit.generated_image_url or ""

        if image_url.startswith("/static/generated/"):
            image_path = os.path.join(
                GENERATED_FOLDER,
                os.path.basename(image_url)
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete outfit from database
        db.session.delete(outfit)
        db.session.commit()

        return jsonify({
            "message": "Outfit deleted successfully."
        }), 200

    except Exception as e:
        db.session.rollback()

        print(f"DELETE ERROR: {e}")

        return jsonify({
            "error": "Unable to delete outfit."
        }), 500
    
# SAVED OUTFITS

@app.route("/saved")
@login_required
def saved():

    outfits = (
        SavedOutfit.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            SavedOutfit.id.desc()
        )
        .all()
    )

    return render_template(
        "saved.html",
        outfits=outfits
    )

# DATABASE INITIALIZATION

def initialize_database():

    with app.app_context():

        db.create_all()

        
        # Add generated_image_url to existing databases
        # db.create_all() does NOT modify an existing table.
        # Therefore, if SavedOutfit already existed, we add
        # the new column safely here.

        inspector = inspect(
            db.engine
        )

        columns = [
            column["name"]
            for column in inspector.get_columns(
                "saved_outfit"
            )
        ]

        if "generated_image_url" not in columns:

            print(
                "Adding generated_image_url "
                "column to saved_outfit..."
            )

            db.session.execute(
                text(
                    """
                    ALTER TABLE saved_outfit
                    ADD COLUMN generated_image_url VARCHAR(500)
                    """
                )
            )

            db.session.commit()

            print(
                "generated_image_url column added."
            )


# Initialize database
initialize_database()

# RUN APPLICATION

if __name__ == "__main__":

    app.run(
        debug=True
    )