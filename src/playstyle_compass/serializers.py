from rest_framework import serializers
from .models import Game, Franchise, Character, Review, News, Deal


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """Base serializer that allows specifying fields dynamically."""

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        # Ensure all fields are read-only
        for field in self.fields.values():
            field.read_only = True


class GameSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class FranchiseSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Franchise
        fields = "__all__"


class CharacterSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Character
        fields = "__all__"


class GameReviewSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Review
        fields = [field.name for field in Review._meta.fields if field.name != "user"]


class NewsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = News
        fields = "__all__"


class DealsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Deal
        fields = "__all__"
