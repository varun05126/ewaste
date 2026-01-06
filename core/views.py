import base64
from groq import Groq

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.conf import settings

# ============================================================
# CONFIGURE GROQ (GLOBAL)
# ============================================================
client = Groq(api_key=settings.GROQ_API_KEY)

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
# STRICT E-WASTE DETECTION USING GROQ VISION
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
            header.startswith("data:image/jpeg")
            or header.startswith("data:image/png")
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
        # Groq vision call
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": strict_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}",
                            },
                        },
                    ],
                }
            ],
            temperature=0.2,
        )

        # Groq returns a list of content parts; first part is text
        caption = chat_completion.choices[0].message.content[0].text.strip().lower()
        caption = caption.split()[0]  # only one word

    except Exception as e:
        print("Groq Detection Error:", e)
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
# CHATBOT USING GROQ
# ============================================================
@csrf_exempt
def chatbot_response(request):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    user_message = request.POST.get("message", "")

    if not user_message:
        return JsonResponse({"response": "Please enter a message."})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an e-waste guide. Answer briefly.",
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
        print("Groq Chatbot Error:", e)
        bot_reply = "Sorry, technical issue occurred."

    return JsonResponse({"response": bot_reply})
