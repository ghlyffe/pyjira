class Login(object):
    def __init__(self, session):
        self.__session = session
        self.__url = session.get_url('auth/latest/session')

        self.__cache = None

    def login(self, uname, passwd, force = False):
        if self.__cache and not force:
            return self.__cache

        resp = self.__session.post(self.__url,json={'username':uname,'password':passwd})

        if resp.status_code == 200:
            return self.current_user(force)
        elif resp.status_code == 401:
            raise Exception("Login failed: Invalid credentials")
        elif resp.status_code == 403:
            raise Exception("Login failed: CAPTCHA, throttling, or other temporary login failure")
        else:
            raise Exception("Login failed: Unexpected status response %d" % resp.status_code)

    def login_cli(self, uname, force=False):
        import getpass
        passwd = getpass.getpass()
        return self.login(uname, passwd, force)

    def current_user(self, force=False):
        if self.__cache and not force:
            return self.__cache

        cu = self.__session.get(self.__url)
        if(cu.status_code != 200):
            raise Exception("Error getting user after successful login, code %d" % cu.status_code)
        else:
            self.__cache = cu.json()
        return self.__cache

    def logout(self):
        resp = self.__session.delete(self.__url)
        if resp.status_code not in (204,401): #201=success, 401=not authenticated
            raise Exception("Error logging out user, code %d" % resp.status_code)

    def name(self):
        if not self.__cache:
            raise Exception("User not logged in")

        return self.__cache
