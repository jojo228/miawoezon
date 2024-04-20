from django.db import models
from main import models as main_models


class Conversation(main_models.TimeStampedModel):

    participants = models.ManyToManyField("authentication.Client", blank=True)

    def __str__(self):
        usernames = []
        for user in self.participants.all():
            usernames.append(user.user.username)
        return ", ".join(usernames)

    def count_messages(self):
        return self.messages.count()

    count_messages.short_description = "Number of Messages"

    def count_participants(self):
        return self.participants.count()

    count_participants.short_description = "Number of Participants"


class Message(main_models.TimeStampedModel):

    message = models.TextField()
    user = models.ForeignKey(
        "authentication.Client", related_name="messages", on_delete=models.CASCADE
    )
    conversation = models.ForeignKey(
        "Conversation", related_name="messages", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.message
