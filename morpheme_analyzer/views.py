import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from morpheme_analyzer.services import parse_text, analyze_text

# Create your views here.


def index(request) -> HttpResponse:
    return render(request, "index.html")


def analyze(request) -> JsonResponse:
    if request.method == "POST":
        body = json.loads(request.body)
        parsed_text = parse_text(body["textToAnalyze"])
        analyzed_text = analyze_text(parsed_text)
        return JsonResponse({"analyzed_text": analyzed_text})
        # return render(request, "result.html", {
        #     "analyzed_text": analyzed_text
        # })
    return JsonResponse({"error": "Something went wrong!"})
