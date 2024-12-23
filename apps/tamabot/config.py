from djchoices import ChoiceItem, DjangoChoices


class StatusChoices(DjangoChoices):
    """Choices for therad status."""

    approved = ChoiceItem("approved", "Approved")
    rejected = ChoiceItem("rejected", "Rejected")