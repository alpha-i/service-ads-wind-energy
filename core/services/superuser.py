from core import services
from core.models.customer import Company, User, UserPermissions

ALPHAI_DOMAIN = 'alpha-i.co'


def create_admin(username, password):

    alphai_company = services.company.get_for_domain(ALPHAI_DOMAIN)

    if not alphai_company:
        alphai_company = services.company.insert(
            Company(name='alphai', domain=ALPHAI_DOMAIN)
        )

    email = f"{username}@{ALPHAI_DOMAIN}"

    user = services.user.get_by_email(email)
    if not user:
        user = User(
            email=email,
            confirmed=True,
            company_id=alphai_company.id,
            permissions=UserPermissions.ADMIN
        )

        user.hash_password(password)
        user = services.user.insert(user)
    else:
        print(f"User with email {email} already exists")
    return user
