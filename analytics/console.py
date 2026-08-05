from pprint import pprint

from .models import Event


def console_handler(event: Event):

    print("\n========== EVENT ==========")
    pprint(event)
    print("===========================\n")
