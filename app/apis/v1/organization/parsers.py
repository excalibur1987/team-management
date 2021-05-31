from flask_restx.reqparse import RequestParser

organization_parser = RequestParser()

organization_parser.add_argument(
    "orgName",
    dest="organization_name",
    type=str,
    required=True,
    location="form",
).add_argument("description", type=str, required=True, location="form",).add_argument(
    "orgAddressL1",
    dest="organization_addr_line1",
    type=str,
    required=True,
    location="form",
).add_argument(
    "orgAddressL2",
    dest="organization_addr_line2",
    type=str,
    required=False,
    default="",
    location="form",
).add_argument(
    "orgCountry",
    dest="organization_country",
    type=str,
    required=True,
    location="form",
).add_argument(
    "orgCity",
    dest="organization_city",
    type=str,
    required=True,
    location="form",
).add_argument(
    "myInfo", dest="my_info", type=bool, location="form"
).add_argument(
    "orgEmail",
    dest="organization_email",
    type=str,
    required=False,
    location="form",
).add_argument(
    "orgPhone",
    dest="organization_phone",
    type=str,
    required=False,
    location="form",
)


department_parser = RequestParser()
department_parser.add_argument("depID", dest="dep_id", type=int, location="form")
department_parser.add_argument("depName", dest="dep_name", type=str, location="form")
