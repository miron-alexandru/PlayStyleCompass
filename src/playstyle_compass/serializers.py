from rest_framework import serializers
from .models import Game, Franchise, Character, Review, News

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = tuple(fields)

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