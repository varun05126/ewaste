import base64
import io
import json

from groq import Groq
from PIL import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings

# ============================================================
# CONFIGURE GROQ (used for both chatbot + vision detection)
# ============================================================
groq_client = Groq(api_key=settings.GROQ_API_KEY)


# ============================================================
# STATIC PAGE ROUTES
# ============================================================
def homepage(request):        return render(request, "index.html")
def services(request):        return render(request, "services.html")
def about(request):           return render(request, "about.html")
def team(request):            return render(request, "team.html")
def contact(request):         return render(request, "contact.html")
def login(request):           return render(request, "login.html")
def signup(request):          return render(request, "signup.html")
def pickup(request):          return render(request, "pickup.html")
def reqs(request):            return render(request, "reqs.html")
def detection(request):       return render(request, "detection.html")
def data_destruction(request):return render(request, "dd.html")
def refurbishment(request):   return render(request, "re.html")

# ============================================================
# CAMERA PAGE
# ============================================================
def ewaste_camera_page(request):
    return render(request, "ewaste-camera.html")

# ============================================================
# E-WASTE DETECTION — GROQ VISION AI (llama-4-scout)
# ============================================================
@csrf_exempt
def camera_ai_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        body = json.loads(request.body)
        image_data = body.get("image", "")
    except (json.JSONDecodeError, AttributeError):
        image_data = request.POST.get("image", "")

    # ---- Validate image ----
    if not image_data or "," not in image_data:
        return JsonResponse({"error": "No valid image provided"}, status=400)

    try:
        _, base64_data = image_data.split(",", 1)
        image_bytes = base64.b64decode(base64_data, validate=True)

        if len(image_bytes) < 4000:
            return JsonResponse({"error": "Image too small or blank"}, status=400)

        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    except Exception:
        return JsonResponse({"error": "Bad image data"}, status=400)

    # ---- Send to Groq Vision (llama-4-scout) ----
    raw = ""
    try:
        buf = io.BytesIO()
        pil_image.save(buf, format="JPEG", quality=85)
        b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

        prompt = (
            "You are an expert e-waste classifier. Analyze the image carefully.\n\n"
            "Reply with ONLY a raw JSON object — no markdown, no code fences, no extra text:\n"
            "{\"waste_type\":\"<item>\",\"category\":\"<E-Waste|Recyclable|Hazardous|Non-E-Waste>\","
            "\"hazardous\":<true|false>,\"confidence\":<0-100>,"
            "\"disposal_tip\":\"<one sentence>\",\"reward_points\":<5-50>,\"is_ewaste\":<true|false>}\n\n"
            "If no electronic item is visible: waste_type=Unknown, is_ewaste=false, category=Non-E-Waste."
        )

        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}},
                ],
            }],
            temperature=0.1,
            max_tokens=300,
        )

        raw = completion.choices[0].message.content.strip()

        # Extract JSON object from response
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        result = json.loads(raw)

        return JsonResponse({
            "success": True,
            "detected": "ewaste" if result.get("is_ewaste") else "not-ewaste",
            "caption": result.get("waste_type", "Unknown"),
            "result": result,
        })

    except json.JSONDecodeError as e:
        print(f"[EWASTE] JSON parse error: {e} | raw: {raw!r}")
        return JsonResponse({
            "success": False,
            "detected": "error",
            "error": f"AI returned unparseable response: {raw[:200]}",
        }, status=500)
    except Exception as e:
        print(f"[EWASTE] Groq vision error: {type(e).__name__}: {e}")
        return JsonResponse({
            "success": False,
            "detected": "error",
            "error": f"{type(e).__name__}: {str(e)}",
        }, status=500)


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
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=256,
        )
        bot_reply = completion.choices[0].message.content
    except Exception as e:
        print("Groq Chat Error:", repr(e))
        bot_reply = "Sorry, technical issue occurred."

    return JsonResponse({"response": bot_reply})


# ============================================================
# GOOGLE SITE VERIFICATION + SEO
# ============================================================
def google_verify(request):
    return HttpResponse(
        "google-site-verification: googleb5949ab1058f2676.html",
        content_type="text/html"
    )

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://ewaste-txgr.onrender.com.sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
