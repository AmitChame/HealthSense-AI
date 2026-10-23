from django.apps import AppConfig
import sys


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    rule_engine = None
    active_model = None
    food_grader = None
    normalizer = None
    allergen_detector = None
    concern_detector = None
    shap_explainer = None
    reason_generator = None

    def ready(self):
        # Prevent double-initialization in auto-reload mode
        if 'runserver' in sys.argv or 'test' in sys.argv:
            try:
                from src.rules.rule_engine import HealthSenseRuleEngine
                from src.features.food_grader import HealthSenseFoodGrader
                from src.ingredient_engine.normalizer import IngredientNormalizer
                from src.ingredient_engine.allergen_detector import AllergenDetector
                from src.ingredient_engine.concern_detector import ConcernDetector
                from src.explainability.reason_generator import HealthSenseReasonGenerator
                from src.explainability.shap_explainer import HealthSenseShapExplainer
                from src.models.model_factory import ModelFactory

                ApiConfig.rule_engine = HealthSenseRuleEngine()
                ApiConfig.food_grader = HealthSenseFoodGrader()
                ApiConfig.normalizer = IngredientNormalizer()
                ApiConfig.allergen_detector = AllergenDetector()
                ApiConfig.concern_detector = ConcernDetector()
                ApiConfig.reason_generator = HealthSenseReasonGenerator()

                # Load active model from configuration
                try:
                    ApiConfig.active_model = ModelFactory.load_active_model()
                    ApiConfig.shap_explainer = HealthSenseShapExplainer(ApiConfig.active_model)
                except Exception as e:
                    print(f"[ApiConfig] Model loading notice: {e}")
                    ApiConfig.active_model = ModelFactory.create_model()

            except Exception as e:
                print(f"[ApiConfig] Error during ready initialization: {e}")
