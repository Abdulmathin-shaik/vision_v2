from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Detection
from ultralytics import YOLO
import json
from PIL import Image
import os
from django.conf import settings
import plotly.express as px
import pandas as pd
from collections import Counter

# Load YOLO model
model = YOLO('yolov8n.pt')

def detect_page(request):
    return render(request, 'detection/detect.html')

@csrf_exempt
def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # Save the original image
        detection = Detection.objects.create(
            image=image_file,
            detected_objects='[]',
            confidence_scores='[]'
        )

        # Process image with YOLO
        results = model(str(detection.image.path))
        
        # Save the result image
        result_image_path = os.path.join(settings.MEDIA_ROOT, 'results', f'result_{detection.id}.jpg')
        results[0].save(result_image_path)
        detection.result_image = f'results/result_{detection.id}.jpg'

        # Extract and save detection results
        detected_objects = []
        confidence_scores = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detected_objects.append(result.names[int(box.cls[0])])
                confidence_scores.append(float(box.conf[0]))

        detection.set_detected_objects(detected_objects)
        detection.set_confidence_scores(confidence_scores)
        detection.save()

        return JsonResponse({
            'status': 'success',
            'detected_objects': detected_objects,
            'confidence_scores': confidence_scores,
            'result_image_url': detection.result_image.url
        })

    return JsonResponse({'status': 'error'})

def history_page(request):
    detections = Detection.objects.all()
    return render(request, 'detection/history.html', {'detections': detections})

def analytics_page(request):
    detections = Detection.objects.all()
    
    # Prepare data for charts
    all_objects = []
    for detection in detections:
        all_objects.extend(detection.get_detected_objects())
    
    # Object frequency chart
    object_counts = Counter(all_objects)
    df_objects = pd.DataFrame([
        {'Object': obj, 'Count': count} 
        for obj, count in object_counts.items()
    ])
    
    if not df_objects.empty:
        fig_objects = px.bar(df_objects, x='Object', y='Count', 
                           title='Detected Objects Frequency')
        chart_objects = fig_objects.to_html(full_html=False)
    else:
        chart_objects = "<p>No data available</p>"

    # Confidence distribution
    all_confidences = []
    all_conf_objects = []
    for detection in detections:
        objects = detection.get_detected_objects()
        scores = detection.get_confidence_scores()
        all_confidences.extend(scores)
        all_conf_objects.extend(objects)

    if all_confidences:
        df_conf = pd.DataFrame({
            'Object': all_conf_objects,
            'Confidence': all_confidences
        })
        fig_conf = px.box(df_conf, x='Object', y='Confidence',
                         title='Confidence Score Distribution by Object')
        chart_confidence = fig_conf.to_html(full_html=False)
    else:
        chart_confidence = "<p>No data available</p>"

    context = {
        'chart_objects': chart_objects,
        'chart_confidence': chart_confidence,
    }
    
    return render(request, 'detection/analytics.html', context) 