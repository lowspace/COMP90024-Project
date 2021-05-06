#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitterlance.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

    t =     {
  "_id": "_design/test",
  "views": {
    "new-view": {
      "map": "function (doc) {\n  sport = ['wrestling', 'weights', 'skiing', 'water polo', 'volleyball', 'tennis', 'team handball', 'table tennis', 'swimming', 'surfing', 'sprinting', 'skating', 'soccer', 'skateboarding', 'shooting', 'rugby', 'rowing', 'rodeo', 'racquetball', 'squash', 'pole vault', 'running', 'martial arts', 'jumps', 'lacrosse', 'ice hockey', 'jump', 'gymnastics', 'golf', 'football', 'fishing', 'field hockey', 'fencing', 'equestrian', 'diving', 'running', 'cycling', 'curling', 'cheerleading', 'canoe', 'kayak', 'bull', 'bareback', 'bronc riding', 'boxing', 'bowling', 'bobsledding', 'luge', 'billiards', 'basketball', 'baseball', 'softball', 'badminton', 'racing', 'archery']\n  for (var i=0; i<55;i++){\n  if (doc.val.text.toLowerCase().includes(sport[i]))\n   {emit(doc._id, 1); break}}\n}",
      "reduce": "_count"
    }
  },
  "language": "javascript",
  "options": {
    "partitioned": true
  }
}
    print("\n\n\n?>??\n\n\n")
    couch.put('tweetdb/_design/test', body=t)