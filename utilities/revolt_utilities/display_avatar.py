import revolt


original_class = revolt.User


class NewUser(original_class):
    @property
    def display_avatar_url(self):
        return self.avatar.url if self.avatar else f"https://app.revolt.chat/api/users/{self.id}/default_avatar"


def patch():
    revolt.User.display_avatar_url = NewUser.display_avatar_url


def unpatch(client):
    revolt.User = original_class

    for user in client.users:
        try:
            del user.display_avatar_url
        except AttributeError:
            pass
