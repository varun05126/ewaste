import base64
import google.generativeai as genai
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.conf import settings

# ============================================================
# CONFIGURE GEMINI (GLOBAL)
# ============================================================
genai.configure(api_key=settings.GEMINI_API_KEY)


# ============================================================
# STATIC PAGE ROUTES
# ============================================================
def homepage(request): return render(request, "index.html")
def services(request): return render(request, "services.html")
def about(request): return render(request, "about.html")
def team(request): return render(request, "team.html")
def contact(request): return render(request, "contact.html")
def login(request): return render(request, "login.html")
def signup(request): return render(request, "signup.html")
def pickup(request): return render(request, "pickup.html")
def reqs(request): return render(request, "reqs.html")
def detection(request): return render(request, "detection.html")
def data_destruction(request): return render(request, "data-destruction.html")
def refurbishment(request): return render(request, "refurbishment.html")


# ============================================================
# CAMERA PAGE
# ============================================================
def ewaste_camera_page(request):
    return render(request, "ewaste-camera.html")


# ============================================================
# STRICT E-WASTE DETECTION USING GEMINI 2.0 FLASH
# ============================================================
@csrf_exempt
def camera_ai_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    image_data = request.POST.get("image")

    # ---- Validate Base64 ----
    if not image_data or "," not in image_data:
        return JsonResponse({"detected": "error", "caption": "invalid-image"}, status=400)

    try:
        header, base64_data = image_data.split(",", 1)

        # must be jpeg or png
        if not (
            header.startswith("data:image/jpeg") or
            header.startswith("data:image/png")
        ):
            return JsonResponse({
                "detected": "error",
                "caption": "unsupported-format"
            }, status=400)

        image_bytes = base64.b64decode(base64_data, validate=True)

        if len(image_bytes) < 4000:  # too small = corrupted
            return JsonResponse({
                "detected": "error",
                "caption": "too-small-image"
            }, status=400)

    except Exception:
        return JsonResponse({
            "detected": "error",
            "caption": "bad-image-data"
        }, status=400)

    # ---- Strict detection prompt ----
    strict_prompt = """
    You are an object identification system.

    RULES:
    - Return ONLY a single object name.
    - No sentences, punctuation or explanation.
    - Electronics list: phone, charger, adapter, cable, battery, laptop, camera,
      mouse, keyboard, earbuds, airpods, webcam, powerbank, speaker, remote.
    - If unsure: still guess one object.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content([
            strict_prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])

        caption = response.text.strip().lower()
        caption = caption.split()[0]  # only one word

    except Exception as e:
        print("Gemini Detection Error:", e)
        return JsonResponse({
            "detected": "error",
            "caption": "ai-error"
        })

    # ---- Check if electronic ----
    ewaste_keywords = [
        "phone", "mobile", "smartphone",
        "charger", "adapter", "cable", "wire", "usb",
        "battery", "powerbank",
        "earbuds", "airpods",
        "laptop", "mouse", "keyboard",
        "speaker", "camera", "webcam",
        "remote", "gadget", "device"
    ]

    detected = "ewaste" if any(k in caption for k in ewaste_keywords) else "not-ewaste"

    return JsonResponse({
        "detected": detected,
        "caption": caption
    })


# ============================================================
# CHATBOT USING GEMINI 2.0 FLASH
# ============================================================
@csrf_exempt
def chatbot_response(request):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    user_message = request.POST.get("message", "")

    if not user_message:
        return JsonResponse({"response": "Please enter a message."})

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        reply = model.generate_content(
            f"You are an e-waste guide. Answer briefly.\nUser: {user_message}"
        )

        bot_reply = reply.text.strip()

    except Exception as e:
        print("Gemini Chatbot Error:", e)
        bot_reply = "Sorry, technical issue occurred."

    return JsonResponse({"response": bot_reply})