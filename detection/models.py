from django.db import models
import json

class Detection(models.Model):
    image = models.ImageField(upload_to='detections/')
    result_image = models.ImageField(upload_to='results/', null=True, blank=True)
    detected_objects = models.TextField()  # Store JSON of detected objects
    confidence_scores = models.TextField()  # Store JSON of confidence scores
    timestamp = models.DateTimeField(auto_now_add=True)

    def set_detected_objects(self, objects_list):
        self.detected_objects = json.dumps(objects_list)

    def get_detected_objects(self):
        return json.loads(self.detected_objects)

    def set_confidence_scores(self, scores_list):
        self.confidence_scores = json.dumps(scores_list)

    def get_confidence_scores(self):
        return json.loads(self.confidence_scores)

    class Meta:
        ordering = ['-timestamp'] 