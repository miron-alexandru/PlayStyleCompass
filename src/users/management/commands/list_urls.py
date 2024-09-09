from django.core.management.base import BaseCommand
from django.urls import get_resolver


class Command(BaseCommand):
    help = "List all URL patterns"

    def handle(self, *args, **kwargs):
        urls = get_resolver().url_patterns
        self.stdout.write(self.style.SUCCESS("Listing all URL patterns:"))
        self.list_urls(urls, "")

    def list_urls(self, urls, prefix):
        for pattern in urls:
            if hasattr(pattern, "url_patterns"):
                self.list_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                self.stdout.write(f"{prefix}{pattern.pattern}")
