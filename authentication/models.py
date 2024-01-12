from staff_account.models import AccountCommonInfo


class Client(AccountCommonInfo):
    def __str__(self):
        return self.user.get_full_name()
