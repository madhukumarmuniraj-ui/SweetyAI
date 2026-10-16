# SweetyAI Extended Tools - Setup & Usage Guide

## 📦 Installation

### Quick Install (All Components)
```bash
pip install -r requirements_extended.txt
```

### Selective Installation

#### Computer Control Only
```bash
pip install pyautogui pygetwindow keyboard pyperclip
```

#### Browser Automation Only
```bash
pip install selenium playwright
playwright install  # Install browser drivers
```

#### Document Processing Only
```bash
pip install python-docx openpyxl python-pptx PyMuPDF pytesseract
```

#### Image Processing Only
```bash
pip install Pillow opencv-python
```

#### Media Processing Only
```bash
pip install moviepy pydub
```

#### Email & Calendar Only
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

#### Databases Only
```bash
pip install psycopg2-binary mysql-connector-python pymongo redis neo4j
```

#### API Ecosystem Only
```bash
pip install requests requests-oauthlib fastapi uvicorn
```

---

## 🚀 Usage Examples

### 1. Computer Control

```python
from app.tools import computer_control

# Mouse control
computer_control.move_mouse(500, 300)
computer_control.click_mouse(500, 300)
computer_control.double_click()
computer_control.scroll_mouse(5, 'down')

# Keyboard control
computer_control.type_text("Hello, World!")
computer_control.press_key('enter')
computer_control.press_hotkey('ctrl', 'c')

# Window management
windows = computer_control.list_windows()
computer_control.activate_window("Chrome")
computer_control.maximize_window("Chrome")
computer_control.resize_window("Chrome", 1024, 768)

# Screenshot
computer_control.screenshot_region(0, 0, 1920, 1080, "screenshot.png")

# Clipboard history
computer_control.save_to_clipboard_history("Important text")
history = computer_control.get_clipboard_history()
```

### 2. Browser Automation

```python
from app.tools import browser_automation

# Initialize browser
driver = browser_automation.create_webdriver(headless=False)

# Navigate and interact
browser_automation.navigate_to_url(driver, "https://example.com")
browser_automation.click_element(driver, "button#submit")
browser_automation.fill_form_field(driver, "input#email", "user@example.com")

# Extract data
text = browser_automation.extract_text(driver, "div.content")
links = browser_automation.extract_links(driver)

# Screenshot
browser_automation.take_screenshot(driver, "page.png")

# Scraping
data = browser_automation.scrape_table(driver, "table.data")

# Cleanup
browser_automation.close_browser(driver)
```

### 3. Document Processing

```python
from app.tools import document_processing

# DOCX
content = document_processing.read_docx("document.docx")
document_processing.write_docx("output.docx", "Hello, World!", styles={'font_size': 14})

# Excel
data = document_processing.read_excel("data.xlsx", sheet_name="Sheet1")
document_processing.write_excel("output.xlsx", data, sheet_name="Results")

# PowerPoint
document_processing.create_presentation("slides.pptx", [
    {"title": "Slide 1", "content": "Introduction"},
    {"title": "Slide 2", "content": "Details"}
])

# OCR
text = document_processing.ocr_image("scanned_document.png")

# PDF
pdf_text = document_processing.extract_pdf_text("document.pdf")
document_processing.merge_pdfs(["doc1.pdf", "doc2.pdf"], "merged.pdf")
```

### 4. Image Processing

```python
from app.tools import image_processing

# Basic operations
image_processing.resize_image("photo.jpg", "resized.jpg", width=800, height=600)
image_processing.crop_image("photo.jpg", "cropped.jpg", 100, 100, 400, 400)
image_processing.rotate_image("photo.jpg", "rotated.jpg", 90)

# Filters
image_processing.apply_filter("photo.jpg", "blurred.jpg", "blur")
image_processing.apply_filter("photo.jpg", "sharpened.jpg", "sharpen")

# Analysis
faces = image_processing.detect_faces("group_photo.jpg")
text = image_processing.extract_text_from_image("screenshot.png")
edges = image_processing.edge_detection("photo.jpg", "edges.jpg")

# Color manipulation
image_processing.adjust_brightness("photo.jpg", "brighter.jpg", factor=1.5)
image_processing.adjust_contrast("photo.jpg", "contrast.jpg", factor=1.3)
image_processing.convert_to_grayscale("photo.jpg", "gray.jpg")
```

### 5. Media Processing

```python
from app.tools import media_processing

# Audio
media_processing.convert_audio("audio.mp3", "audio.wav", "wav")
media_processing.trim_audio("audio.mp3", "trimmed.mp3", start=5, end=30)
media_processing.change_speed("audio.mp3", "faster.mp3", speed=1.5)

# Video
media_processing.extract_audio_from_video("video.mp4", "audio.mp3")
media_processing.trim_video("video.mp4", "trimmed.mp4", start=10, end=60)
media_processing.resize_video("video.mp4", "resized.mp4", width=1280, height=720)
media_processing.add_subtitles_to_video("video.mp4", "subtitled.mp4", "subtitles.srt")

# Analysis
duration = media_processing.get_video_duration("video.mp4")
info = media_processing.get_video_info("video.mp4")
```

### 6. Email & Calendar

```python
from app.tools.email_calendar import EmailClient, IMAPClient, GoogleCalendarClient
from datetime import datetime, timedelta

# Send email
email_client = EmailClient(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password"
)

email_client.send_email(
    to_addresses=["recipient@example.com"],
    subject="Test Email",
    body="Hello from SweetyAI!",
    attachments=["report.pdf"]
)

# Read emails
imap_client = IMAPClient(
    imap_server="imap.gmail.com",
    username="your_email@gmail.com",
    password="your_app_password"
)

emails = imap_client.fetch_emails(limit=10, unread_only=True)

# Google Calendar
calendar = GoogleCalendarClient(
    credentials_path="credentials.json",
    token_path="token.json"
)

calendar.authenticate()

# Create event
start_time = datetime.now() + timedelta(days=1)
end_time = start_time + timedelta(hours=1)

calendar.create_event(
    summary="Team Meeting",
    start_time=start_time,
    end_time=end_time,
    description="Quarterly review",
    attendees=["team@example.com"]
)

# Find free slots
free_slots = calendar.find_free_slots(duration_minutes=60, days_ahead=7)
```

### 7. Database Connectors

```python
from app.tools.database_connectors import (
    SQLiteClient, PostgreSQLClient, MongoDBClient, RedisClient, Neo4jClient
)

# SQLite
sqlite = SQLiteClient("database.db")
sqlite.connect()
results = sqlite.execute("SELECT * FROM users WHERE age > ?", (18,))

# PostgreSQL
postgres = PostgreSQLClient(
    host="localhost",
    database="mydb",
    user="postgres",
    password="password"
)
postgres.connect()
data = postgres.execute("SELECT * FROM users LIMIT 10")

# MongoDB
mongo = MongoDBClient("mongodb://localhost:27017", "mydb")
mongo.connect()
docs = mongo.find("users", {"age": {"$gt": 18}})
mongo.insert("users", {"name": "Alice", "age": 30})

# Redis (Caching)
redis = RedisClient(host="localhost", port=6379)
redis.connect()
redis.set("key", "value", expire=3600)
value = redis.get("key")

# Neo4j (Graph Database)
neo4j = Neo4jClient("bolt://localhost:7687", "neo4j", "password")
neo4j.connect()
neo4j.create_node("Person", {"name": "Alice", "age": 30})
neo4j.create_relationship(
    "Person", "name", "Alice",
    "Person", "name", "Bob",
    "KNOWS"
)
```

### 8. API Ecosystem

```python
from app.tools.api_ecosystem import (
    RESTAPIClient, OAuth2Client, RateLimiter, 
    WebhookListener, APIKeyManager
)

# REST API with rate limiting
api = RESTAPIClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

response = api.get("/users")
response = api.post("/users", data={"name": "Alice", "email": "alice@example.com"})

# OAuth2 Authentication
oauth = OAuth2Client(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_url="https://provider.com/oauth/authorize",
    token_url="https://provider.com/oauth/token"
)

auth_url = oauth.get_authorization_url()
# User visits auth_url, gets redirected back with code
token = oauth.fetch_token(authorization_response)

# Rate Limiting
limiter = RateLimiter(max_requests=100, time_window=60)
if limiter.is_allowed():
    # Make API call
    pass
else:
    wait_time = limiter.get_wait_time()
    print(f"Rate limited. Wait {wait_time}s")

# Webhook Listener
webhook = WebhookListener(secret_key="webhook-secret")

def handle_event(payload):
    print(f"Event received: {payload}")

webhook.register_handler("user.created", handle_event)
webhook.handle_webhook("user.created", {"user_id": 123})

# API Key Management
key_manager = APIKeyManager("api_keys.json")
key_manager.add_key("openai", "sk-...")
key_manager.add_key("anthropic", "sk-ant-...")
api_key = key_manager.get_key("openai")
```

---

## 🔧 Configuration

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to project root
6. First run will open browser for authentication

### Tesseract OCR Setup (Windows)

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

### FFmpeg Setup (for Media Processing)

1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`

---

## 🛡️ Security Notes

### API Keys
- Never commit API keys to version control
- Use `.env` files or secure key managers
- Rotate keys regularly

### Database Passwords
- Use environment variables
- Enable SSL/TLS connections
- Use read-only credentials when possible

### OAuth Tokens
- Store tokens securely
- Implement token refresh logic
- Use HTTPS for redirect URIs

---

## 🧪 Testing

```python
# Test computer control
from app.tools import computer_control
screen_size = computer_control.get_screen_size()
print(f"Screen: {screen_size}")

# Test browser automation
from app.tools import browser_automation
driver = browser_automation.create_webdriver(headless=True)
print("Browser automation ready")
browser_automation.close_browser(driver)

# Test document processing
from app.tools import document_processing
test_text = document_processing.ocr_image("test_image.png")
print(f"OCR result: {test_text}")
```

---

## 📊 System Status Check

Run this to verify all components:

```python
from app.tools import (
    computer_control, browser_automation, document_processing,
    image_processing, media_processing
)

print("Computer Control:", "✓" if computer_control.PYAUTOGUI_AVAILABLE else "✗")
print("Browser Automation:", "✓" if browser_automation.SELENIUM_AVAILABLE else "✗")
print("Document Processing:", "✓" if document_processing.DOCX_AVAILABLE else "✗")
print("Image Processing:", "✓" if image_processing.PIL_AVAILABLE else "✗")
print("Media Processing:", "✓" if media_processing.MOVIEPY_AVAILABLE else "✗")
```

---

## 🚨 Troubleshooting

### PyAutoGUI Failsafe
If mouse moves to top-left corner, PyAutoGUI will abort (safety feature).
Disable: `pyautogui.FAILSAFE = False`

### Selenium WebDriver Issues
```bash
pip install webdriver-manager  # Auto-downloads drivers
```

### Tesseract Not Found
Set path manually:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### FFmpeg Not Found
Install via package manager:
```bash
# Windows (Chocolatey)
choco install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

---

## 📚 Additional Resources

- [PyAutoGUI Docs](https://pyautogui.readthedocs.io/)
- [Selenium Docs](https://selenium-python.readthedocs.io/)
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)
- [MoviePy Docs](https://zulko.github.io/moviepy/)
- [Google Calendar API](https://developers.google.com/calendar)

---

**Status**: All components implemented ✅  
**System Completion**: ~85%  
**Last Updated**: 2026-10-03
