from rest_framework import serializers
from .models import Game, Franchise, Character, Review, News

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = tuple(fields)

    def __init__(self, *args, **kwargs):
        # Get the fields parameter passed to the serializer
        fields = kwargs.pop('fields', None)
        
        # If specific fields are passed, limit the serializer to those fields
        if fields:
            # Only include the fields provided in the 'fields' list
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        super().__init__(*args, **kwargs)

class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Franchise
        fields = '__all__'
        read_only_fields = tuple(fields)

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = tuple(fields)

class GameReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [field.name for field in Review._meta.fields if field.name != 'user']
        read_only_fields = tuple(fields)

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = tuple(fields)