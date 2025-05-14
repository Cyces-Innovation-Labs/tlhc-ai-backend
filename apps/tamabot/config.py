from djchoices import ChoiceItem, DjangoChoices


class StatusChoices(DjangoChoices):
    """Choices for therad status."""

    approved = ChoiceItem("approved", "Approved")
    rejected = ChoiceItem("rejected", "Rejected")

class ChatbotTypeChoices(DjangoChoices):
    """Choices for Chatbot type choices."""

    support = ChoiceItem("support", "Support")
    emotional = ChoiceItem("emotional", "Emotional")