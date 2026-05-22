from ai_modules.summarizer import generate_summary
from ai_modules.keyword_extractor import extract_keywords
from ai_modules.translator import (
    translate_to_english,
    detect_language,
    translate_back,
    normalize_text
)
from gtts import gTTS
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)
from flask_mysqldb import MySQL
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from google import genai
import os
import requests

app = Flask(__name__)

# -------------------------------------------------
# GEMINI AI CONFIGURATION
# -------------------------------------------------

GEMINI_API_KEY = "cc4ae3b44b11dd9c85030dc71701d1ae"

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# -------------------------------------------------
# SECRET KEY
# -------------------------------------------------

app.secret_key = "secretkey"

# -------------------------------------------------
# MYSQL CONFIGURATION
# -------------------------------------------------

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'krishimitra-ai'

# -------------------------------------------------
# UPLOAD FOLDERS
# -------------------------------------------------

app.config['UPLOAD_FOLDER'] = 'static/uploads'

# -------------------------------------------------
# MYSQL INITIALIZATION
# -------------------------------------------------

mysql = MySQL(app)

# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------

@app.route('/')
def index():

    return render_template('index.html')

# -------------------------------------------------
# REGISTER PAGE
# -------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        password = generate_password_hash(
            request.form['password']
        )

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO users(name, email, password)
            VALUES(%s, %s, %s)
            """,
            (
                name,
                email,
                password
            )
        )

        mysql.connection.commit()

        cur.close()

        return redirect('/login')

    return render_template('register.html')

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            [email]
        )

        user = cur.fetchone()

        cur.close()

        if user and check_password_hash(
            user[3],
            password
        ):

            session['user_id'] = user[0]

            session['user_name'] = user[1]

            return redirect('/dashboard')

        else:

            return "Invalid Email or Password"

    return render_template('login.html')

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:

        return redirect('/login')

    search = request.args.get('search')

    cur = mysql.connection.cursor()

    if search:

        query = """
        SELECT * FROM posts
        WHERE
        crop_name LIKE %s
        OR issue_title LIKE %s
        OR description LIKE %s
        OR ai_summary LIKE %s
        OR keywords LIKE %s
        ORDER BY id DESC
        """

        search_term = "%" + search + "%"

        cur.execute(
            query,
            (
                search_term,
                search_term,
                search_term,
                search_term,
                search_term
            )
        )

    else:

        cur.execute(
            "SELECT * FROM posts ORDER BY id DESC"
        )

    posts = cur.fetchall()

    cur.close()

    return render_template(
        'dashboard.html',
        posts=posts
    )

# -------------------------------------------------
# ANALYTICS DASHBOARD
# -------------------------------------------------

@app.route('/analytics')
def analytics():

    if 'user_id' not in session:

        return redirect('/login')

    cur = mysql.connection.cursor()

    # -----------------------------------------
    # TOTAL POSTS
    # -----------------------------------------

    cur.execute(
        "SELECT COUNT(*) FROM posts"
    )

    total_posts = cur.fetchone()[0]

    # -----------------------------------------
    # TOTAL FARMERS
    # -----------------------------------------

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cur.fetchone()[0]

    # -----------------------------------------
    # MOST REPORTED CROPS
    # -----------------------------------------

    cur.execute(
        """
        SELECT crop_name, COUNT(*)
        FROM posts
        GROUP BY crop_name
        ORDER BY COUNT(*) DESC
        """
    )

    crop_data = cur.fetchall()

    # -----------------------------------------
    # MOST COMMON ISSUES
    # -----------------------------------------

    cur.execute(
        """
        SELECT issue_title, COUNT(*)
        FROM posts
        GROUP BY issue_title
        ORDER BY COUNT(*) DESC
        """
    )

    issue_data = cur.fetchall()

    # -----------------------------------------
    # TOP CROP
    # -----------------------------------------

    cur.execute(
        """
        SELECT crop_name, COUNT(*) as total
        FROM posts
        GROUP BY crop_name
        ORDER BY total DESC
        LIMIT 1
        """
    )

    top_crop_data = cur.fetchone()

    top_crop = top_crop_data[0]

    # -----------------------------------------
    # TOP ISSUE
    # -----------------------------------------

    cur.execute(
        """
        SELECT issue_title, COUNT(*) as total
        FROM posts
        GROUP BY issue_title
        ORDER BY total DESC
        LIMIT 1
        """
    )

    top_issue_data = cur.fetchone()

    top_issue = top_issue_data[0]

    # -----------------------------------------
    # DAILY POSTS TREND
    # -----------------------------------------

    cur.execute(
        """
        SELECT DATE(created_at), COUNT(*)
        FROM posts
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
        """
    )

    trend_data = cur.fetchall()

    cur.close()

    # -----------------------------------------
    # PREPARE CHART DATA
    # -----------------------------------------

    crop_labels = []

    crop_values = []

    for row in crop_data:

        crop_labels.append(row[0])

        crop_values.append(row[1])

    issue_labels = []

    issue_values = []

    for row in issue_data:

        issue_labels.append(row[0])

        issue_values.append(row[1])

    # -----------------------------------------
    # TREND CHART DATA
    # -----------------------------------------

    trend_labels = []

    trend_values = []

    for row in trend_data:

        trend_labels.append(
            str(row[0])
        )

        trend_values.append(
            row[1]
        )

    return render_template(

        'analytics.html',

        total_posts=total_posts,

        total_users=total_users,

        top_crop=top_crop,

        top_issue=top_issue,

        crop_labels=crop_labels,

        crop_values=crop_values,

        issue_labels=issue_labels,

        issue_values=issue_values,

        trend_labels=trend_labels,

        trend_values=trend_values
    )

# -------------------------------------------------
# CHATBOT PAGE
# -------------------------------------------------

@app.route('/chatbot')
def chatbot():

    if 'user_id' not in session:

        return redirect('/login')

    return render_template(
        'chatbot.html'
    )

# -------------------------------------------------
# REAL AI CHATBOT API
# -------------------------------------------------

@app.route(
    '/chatbot-api',
    methods=['POST']
)
def chatbot_api():

    data = request.get_json()

    user_message = data['message']

    prompt = f"""
    You are KrishiMitra AI,
    an intelligent agriculture assistant.

    Help farmers with:
    - crop diseases
    - pest attacks
    - irrigation
    - fertilizers
    - soil health
    - weather impact
    - prevention tips

    Support:
    - English
    - Kannada
    - Hindi

    Give simple farmer-friendly answers.

    Farmer Question:
    {user_message}
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        reply = response.text

    except:

        message = user_message.lower()

        # -----------------------------------------
        # FALLBACK RESPONSES
        # -----------------------------------------

        if (
            'soil' in message or
            'fertility' in message or
            'ಮಣ್ಣು' in message or
            'मिट्टी' in message
        ):

            reply = """
            Soil fertility can be improved using compost,
            organic manure,
            crop rotation,
            and balanced fertilizers.
            """

        elif (
            'pest' in message or
            'insect' in message or
            'ಕೀಟ' in message or
            'कीट' in message
        ):

            reply = """
            Pest attacks can be reduced using neem oil spray,
            organic pesticides,
            and proper field monitoring.
            """

        elif (
            'water' in message or
            'irrigation' in message or
            'ನೀರು' in message or
            'पानी' in message
        ):

            reply = """
            Proper irrigation is important.
            Avoid overwatering and maintain balanced moisture.
            """

        elif (
            'yellow' in message or
            'leaf' in message or
            'ಹಳದಿ' in message or
            'पीला' in message
        ):

            reply = """
            Yellow leaves may occur due to nutrient deficiency,
            water stress,
            or fungal infection.
            """

        else:

            reply = f"""
            KrishiMitra AI Assistant 🌱

            I understood your question:

            "{user_message}"

            Please provide more crop details,
            symptoms,
            or farming problems
            for better agricultural guidance.
            """

    return jsonify({

        'reply': reply
    })

# -------------------------------------------------
# CREATE POST
# -------------------------------------------------

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():

    if 'user_id' not in session:

        return redirect('/login')

    if request.method == 'POST':

        # -----------------------------------------
        # FORM DATA
        # -----------------------------------------

        crop_name = request.form['crop_name']

        issue_title = request.form['issue_title']

        description = request.form['description']

        translated_crop = normalize_text(crop_name)
        
        translated_issue = normalize_text(issue_title)


        # -----------------------------------------
        # DETECT LANGUAGE
        # -----------------------------------------

        language = detect_language(description)

        # -----------------------------------------
        # TRANSLATE TO ENGLISH
        # -----------------------------------------

        translated_text = translate_to_english(
            description
        )

        # -----------------------------------------
        # GENERATE AI SUMMARY
        # -----------------------------------------

        english_summary = generate_summary(
            translated_text
        )

        # -----------------------------------------
        # TRANSLATE BACK
        # -----------------------------------------

        ai_summary = translate_back(
            english_summary,
            language
        )

        # -----------------------------------------
        # EXTRACT KEYWORDS
        # -----------------------------------------

        keywords = extract_keywords(
            translated_text
        )

        # -----------------------------------------
        # IMAGE UPLOAD
        # -----------------------------------------

        image = request.files['image']

        filename = image.filename

        image_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        image.save(image_path)

        # -----------------------------------------
        # gTTS LANGUAGE MAP
        # -----------------------------------------

        language_map = {

            "en-IN": "en",

            "kn-IN": "kn",

            "te-IN": "te",

            "ta-IN": "ta",

            "hi-IN": "hi"
        }

        gtts_language = language_map.get(
            language,
            "en"
        )

        # -----------------------------------------
        # GENERATE AUDIO
        # -----------------------------------------

        tts = gTTS(
            text=ai_summary,
            lang=gtts_language
        )

        audio_file = filename + ".mp3"

        audio_path = os.path.join(
            "static/audio",
            audio_file
        )

        tts.save(audio_path)

        # -----------------------------------------
        # SAVE TO DATABASE
        # -----------------------------------------

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO posts(
                user_id,
                crop_name,
                issue_title,
                description,
                image,
                ai_summary,
                keywords,
                audio
            )
            
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['user_id'],
                translated_crop,
                translated_issue,
                description,
                filename,
                ai_summary,
                keywords,
                audio_file
            )
        )

        mysql.connection.commit()

        cur.close()

        return redirect('/dashboard')

    return render_template('create_post.html')

# -------------------------------------------------
# WEATHER ADVISORY
# -------------------------------------------------

@app.route(
    '/weather',
    methods=['GET', 'POST']
)
def weather():

    if 'user_id' not in session:

        return redirect('/login')

    weather_data = None

    advice = None

    if request.method == 'POST':

        city = request.form['city']

        api_key = "cc4ae3b44b11dd9c85030dc71701d1ae"

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response = requests.get(url)

        data = response.json()

        print(data)

        if data['cod'] == 200:

            temperature = data['main']['temp']

            humidity = data['main']['humidity']

            description = data['weather'][0]['description']

            wind_speed = data['wind']['speed']

            weather_data = {

                'city': city,

                'temperature': temperature,

                'humidity': humidity,

                'description': description,

                'wind_speed': wind_speed
            }

            # -----------------------------------------
            # AI FARMING ADVICE
            # -----------------------------------------

            if 'rain' in description.lower():

                advice = """
                Rain expected.
                Avoid pesticide spraying today.
                Ensure proper drainage.
                """

            elif temperature > 35:

                advice = """
                High temperature detected.
                Increase irrigation
                and avoid afternoon watering.
                """

            elif humidity > 80:

                advice = """
                High humidity may increase fungal diseases.
                Monitor crops carefully.
                """

            else:

                advice = """
                Weather conditions look suitable for farming activities.
                Continue regular monitoring.
                """

    return render_template(

        'weather.html',

        weather_data=weather_data,

        advice=advice
    )

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------

if __name__ == '__main__':

    app.run(debug=True)