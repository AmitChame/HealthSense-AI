"""
Django REST Framework Serializers for HealthSense AI.
Matches both Android client JSON models and extended AI response schemas.
"""

from rest_framework import serializers
from typing import List, Dict, Any


class NutrimentsSerializer(serializers.Serializer):
    calories = serializers.FloatField(required=False, allow_null=True)
    sugars = serializers.FloatField(required=False, allow_null=True)
    sodium = serializers.FloatField(required=False, allow_null=True)
    fats = serializers.FloatField(required=False, allow_null=True)
    saturatedFat = serializers.FloatField(required=False, allow_null=True)
    proteins = serializers.FloatField(required=False, allow_null=True)
    carbohydrates = serializers.FloatField(required=False, allow_null=True)
    fiber = serializers.FloatField(required=False, allow_null=True)


class FoodProductSerializer(serializers.Serializer):
    barcode = serializers.CharField(required=True)
    productName = serializers.CharField(required=True)
    brand = serializers.CharField(required=False, allow_blank=True, default="")
    imageUrl = serializers.CharField(required=False, allow_blank=True, default="")
    servingSize = serializers.CharField(required=False, allow_blank=True, default="")
    ingredients = serializers.CharField(required=False, allow_blank=True, default="")
    allergens = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    nutriments = NutrimentsSerializer(required=False, default=dict)
    novaGroup = serializers.CharField(required=False, allow_null=True, default=None)
    nutriScore = serializers.CharField(required=False, allow_null=True, default=None)


class FamilyMemberSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_null=True, default=None)
    name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=False, default=30)
    gender = serializers.CharField(required=False, allow_blank=True, default="Other")
    healthConditions = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    allergies = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    dietaryPreferences = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")


class HealthFactorSerializer(serializers.Serializer):
    name = serializers.CharField()
    impact = serializers.CharField() # LOW, MODERATE, HIGH
    description = serializers.CharField()
    isAllergen = serializers.BooleanField(default=False)
    detectedValue = serializers.CharField(required=False, allow_null=True)
    thresholdValue = serializers.CharField(required=False, allow_null=True)


class FamilyRecommendationSerializer(serializers.Serializer):
    familyMemberId = serializers.CharField(required=False, allow_null=True)
    familyMemberName = serializers.CharField()
    familyMemberAge = serializers.IntegerField(required=False, default=0)
    healthSummary = serializers.CharField(required=False, default="")
    category = serializers.CharField() # RECOMMENDED, CAUTION, AVOID
    riskLevel = serializers.CharField() # LOW, MODERATE, HIGH
    riskScore = serializers.FloatField()
    summaryReason = serializers.CharField()
    healthFactors = HealthFactorSerializer(many=True, default=list)
    warnings = serializers.ListField(child=serializers.CharField(), default=list)
    # Extended AI fields
    foodGrade = serializers.CharField(required=False)
    ingredientConcerns = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    modelName = serializers.CharField(required=False)
    confidence = serializers.FloatField(required=False, default=0.95)
    assessmentConfidence = serializers.CharField(required=False, default="HIGH")
    frequencyRecommendation = serializers.CharField(required=False, default="OCCASIONAL")


class RecommendationRequestSerializer(serializers.Serializer):
    foodProduct = FoodProductSerializer(required=True)
    familyMembers = FamilyMemberSerializer(many=True, required=True)
    # Use CharField for timestamp to handle large Java milliseconds safely without overflow
    timestamp = serializers.CharField(required=False, default="0")


class RecommendationResponseSerializer(serializers.Serializer):
    barcode = serializers.CharField()
    productName = serializers.CharField()
    recommendations = FamilyRecommendationSerializer(many=True)
    overallVerdict = serializers.CharField()
    analyzedAt = serializers.IntegerField()
    disclaimer = serializers.CharField()
    # High-level AI summary
    foodGrade = serializers.CharField(required=False)
    foodQualityScore = serializers.FloatField(required=False)
    activeModel = serializers.CharField(required=False)
    source = serializers.CharField(required=False, default="REMOTE_BACKEND")
    assessmentConfidence = serializers.CharField(required=False, default="HIGH")
    frequencyRecommendation = serializers.CharField(required=False, default="OCCASIONAL")
