from modeltranslation.translator import TranslationOptions, register
from .models import QuizQuestion, QuizUserResponse


@register(QuizQuestion)
class QuizQuestionTranslationOptions(TranslationOptions):
    fields = (
        "question_text",
        "option1",
        "option2",
        "option3",
        "option4",
    )


@register(QuizUserResponse)
class QuizQuestionTranslationOptions(TranslationOptions):
    fields = ("response_text",)
