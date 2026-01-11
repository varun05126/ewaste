import base64
import io

from groq import Groq
from PIL import Image

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings

# ============================================================
# CONFIGURE GROQ (TEXT ONLY)
# ============================================================
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Predefined e-waste items
EWASTE_ITEMS = {
    "phone": "smartphone",
    "charger": "charger",
    "laptop": "laptop",
    "tablet": "tablet",
    "headphones": "headphones",
    "keyboard": "keyboard",
    "mouse": "mouse",
    "monitor": "monitor",
    "cable": "cable",
    "battery": "battery",
    "powerbank": "powerbank",
    "speaker": "speaker",
    "camera": "camera",
    "earbuds": "earbuds",
    "adapter": "adapter",
    "remote": "remote",
    "webcam": "webcam",
}

# ============================================================
# STATIC PAGE ROUTES
# ============================================================
def homepage(request): 
    return render(request, "index.html")

def services(request): 
    return render(request, "services.html")

def about(request): 
    return render(request, "about.html")

def team(request): 
    return render(request, "team.html")

def contact(request): 
    return render(request, "contact.html")

def login(request): 
    return render(request, "login.html")

def signup(request): 
    return render(request, "signup.html")

def pickup(request): 
    return render(request, "pickup.html")

def reqs(request): 
    return render(request, "reqs.html")

def detection(request): 
    return render(request, "detection.html")

def data_destruction(request): 
    return render(request, "data-destruction.html")

def refurbishment(request): 
    return render(request, "refurbishment.html")

# ============================================================
# CAMERA PAGE
# ============================================================
def ewaste_camera_page(request):
    return render(request, "ewaste-camera.html")

# ============================================================
# E-WASTE DETECTION - MANUAL SELECTION
# ============================================================
@csrf_exempt
def camera_ai_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # Get either auto-detected item or manual selection
    image_data = request.POST.get("image")
    manual_item = request.POST.get("item")  # Manual selection from user

    # ---- Validate image ----
    if not image_data or "," not in image_data:
        return JsonResponse(
            {"detected": "error", "caption": "invalid-image"}, 
            status=400
        )

    try:
        header, base64_data = image_data.split(",", 1)

        if not (
            header.startswith("data:image/jpeg")
            or header.startswith("data:image/png")
        ):
            return JsonResponse(
                {"detected": "error", "caption": "unsupported-format"},
                status=400,
            )

        image_bytes = base64.b64decode(base64_data, validate=True)

        if len(image_bytes) < 4000:
            return JsonResponse(
                {"detected": "error", "caption": "too-small-image"},
                status=400,
            )

        # Validate image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    except Exception:
        return JsonResponse(
            {"detected": "error", "caption": "bad-image-data"},
            status=400,
        )

    # Use manual selection if provided, otherwise use a placeholder
    if manual_item and manual_item in EWASTE_ITEMS:
        caption = manual_item.lower()
    else:
        # Default: ask user to select manually
        caption = "unknown"

    # ---- Check if electronic (e-waste) ----
    ewaste_keywords = list(EWASTE_ITEMS.keys()) + [
        "mobile", "smartphone", "wire", "usb", "airpods",
        "gadget", "device", "electronic", "tech",
    ]

    detected = "ewaste" if any(k in caption for k in ewaste_keywords) else "not-ewaste"

    return JsonResponse(
        {"detected": detected, "caption": caption}
    )

# ============================================================
# CHATBOT USING GROQ TEXT
# ============================================================
@csrf_exempt
def chatbot_response(request):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    user_message = request.POST.get("message", "")

    if not user_message:
        return JsonResponse({"response": "Please enter a message."})

    try:
        # Groq text call
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an e-waste guide assistant. Answer briefly and helpfully about "
                        "electronic waste recycling, proper disposal, environmental impact, and best practices. "
                        "Keep responses under 100 words."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0.4,
            max_tokens=256,
        )

        bot_reply = completion.choices[0].message.content

    except Exception as e:
        print("Groq Chat Error:", repr(e))
        bot_reply = "Sorry, technical issue occurred."

    return JsonResponse({"response": bot_reply})
