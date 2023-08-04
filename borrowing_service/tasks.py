from datetime import date, timedelta

from .send_message_to_telegram import send_to_telegram
from celery import shared_task
from .models import Borrowing


@shared_task
def check_overdue_borrowings():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
             expected_return_date__lte=tomorrow,
             actual_return_date__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                     f"Overdue borrowing: Book {borrowing.book.title} " 
                     f"borrowed by {borrowing.user.email}"
            )
            send_to_telegram(message)
    else:
        message = "No borrowings overdue today!"
        send_to_telegram(message)
