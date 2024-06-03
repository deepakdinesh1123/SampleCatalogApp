class ConfigViewMixin(object):
    def get_token(self):
        token = self.request.GET.get("token")
        return token

    def get_success_url(self):
        token = self.get_token()
        if token:
            return f"{self.success_url}?token={token}"
        return self.success_url
