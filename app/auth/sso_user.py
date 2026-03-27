from fastapi import Request
from app.core.ip_addr import ip_addr
from app.core.logger import log
from app.config.app_config import top_post, top_view, middle_post, work_post, tester


SECURITY_KEYS = {
    "username",
    "fio",
    "full_name",
    "dep_name",
    "post",
    "roles",
    "top_level",
    "top_view",
    "rfbn_id",
}


class SSO_User:
    """
    FastAPI-совместимый объект пользователя.
    Не использует Flask session, не использует g.
    Все данные передаются извне.
    """

    def __init__(self):
        self.username = None
        self.src_user = None
        self.post = ""
        self.dep_name = ""
        self.roles = ""
        self.top_level = 0
        self.top_view = 0
        self.rfbn_id = ""
        self.fio = ""
        self.full_name = ""
        self.ip_addr = ""

    def check_tester(self):
        if "login_name" in tester and tester["login_name"] == self.username:
            self.rfbn_id = tester["rfbn_id"]
            self.top_level = tester["top_level"]
            self.top_view = tester["top_view"]

    def restore_user(self, request: Request):
        session=request.session

        self.username = session.get("username", None)
        if "username" not in session:
            log.info(f"RESTORE_USER. USERNAME not in SESSION: {session}")
            return None

        self.fio = session.get("fio", "")
        self.full_name = session.get("full_name", "")
        self.dep_name = session.get("dep_name", "")
        self.post = session.get("post", "")
        self.roles = session.get("roles", "")
        self.top_level = session.get("top_level", 0)
        self.top_view = session.get("top_view", 0)
        self.rfbn_id = session.get("rfbn_id", "")
        self.ip_addr = session.get("ip_addr", "")
        self.full_name = session.fio
        return self

    def authenticate_and_init(self, src_user: dict, request):
        """
        Аналог get_user_by_name, но без Flask.
        session — это request.session (dict-like).
        """

        ip = ip_addr(request)
        self.src_user = src_user

        if not src_user or "login_name" not in src_user:
            log.info(f"SSO FAIL. USERNAME: {src_user}, ip_addr: {ip}")
            return None

        log.debug(f"SSO_USER. src_user: {src_user}")

        self.username = src_user["login_name"]

        # Проверка обязательных полей
        required = ["fio", "dep_name", "post"]
        for field in required:
            if field not in src_user:
                log.info(f"SSO FAIL. USER {self.username}: missing {field}")
                return None

        # Основные поля
        self.rfbn_id = src_user.get("rfbn_id", "")
        self.dep_name = src_user.get("dep_name", "")
        self.post = src_user.get("post", "")
        self.fio = src_user.get("fio", "")
        self.full_name = self.fio
        self.ip_addr = ip

        # Определение ролей
        self._assign_roles()

        # Тестер
        self.check_tester()

        # Сохраним в контексте
        self.save_context(request)

        log.info(
            f"---> SSO SUCCESS\n"
            f"\tUSERNAME: {self.username}\n"
            f"\tIP_ADDR: {self.ip_addr}\n"
            f"\tFIO: {self.fio}\n"
            f"\tROLES: {self.roles}\n"
            f"\tPOST: {self.post}\n"
            f"\tTOP_VIEW: {self.top_view}\n"
            f"\tTOP_LEVEL: {self.top_level}\n"
            f"\tRFBN: {self.rfbn_id}\n"
            f"\tDEP_NAME: {self.dep_name}\n<---"
        )

        return self

    def save_context(self, request):
        session = request.session
        # удалить только security‑контекст
        for key in SECURITY_KEYS:
            session.pop(key, None)

        session["username"] = self.username
        session["fio"] = self.fio
        session["full_name"] = self.full_name
        session["dep_name"] = self.dep_name
        session["post"] = self.post
        session["roles"] = self.roles
        session["top_level"] = self.top_level
        session["top_view"] = self.top_view
        session["rfbn_id"] = self.rfbn_id
        session["ip_addr"] = self.ip_addr

    def _assign_roles(self):
        """Логика определения ролей — полностью перенесена из Flask."""
        # TOP
        list_top_dep = top_post.get(self.post, [])
        if self.dep_name in list_top_dep:
            self.roles = "TOP_VIEW"
            self.top_level = 2
            self.top_view = 1

        # VIEW
        if self.top_view == 0:
            list_top_view = top_view.get(self.post, [])
            if "*" in list_top_view or self.dep_name in list_top_view:
                self.roles = "TOP_VIEW"
                self.top_view = 1

        # HEAD
        if self.top_level == 0:
            list_middle_dep = middle_post.get(self.post, [])
            if "*" in list_middle_dep or self.dep_name in list_middle_dep:
                self.roles = "Head"
                self.top_level = 1

        # OPERATOR
        if self.top_level == 0:
            list_work_dep = work_post.get(self.post, [])
            if "*" in list_work_dep or self.dep_name in list_work_dep:
                self.roles = "Operator"
            else:
                log.info(f"SSO. Undefined ROLE for: {self.username}")
                return None

    def is_authenticated(self):
        log.info(f'Check is_authenticated {self.username}')
        return bool(self.roles)

    def have_role(self, role_name):
        return role_name == self.roles
