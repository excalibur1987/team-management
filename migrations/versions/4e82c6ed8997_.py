"""empty message

Revision ID: 4e82c6ed8997
Revises: 53ceac12ff90
Create Date: 2021-05-17 13:37:08.286025

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4e82c6ed8997"
down_revision = "53ceac12ff90"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "roles",
        "id",
        existing_type=sa.INTEGER(),
        comment="Unique row identifier",
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "sessions",
        "id",
        existing_type=sa.INTEGER(),
        comment="Unique row identifier",
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "sessions",
        "user_id",
        existing_type=sa.INTEGER(),
        comment="user's table foreign key",
        existing_nullable=False,
    )
    op.alter_column(
        "sessions",
        "token",
        existing_type=sa.VARCHAR(),
        comment="session's token",
        existing_nullable=False,
    )
    op.alter_column(
        "sessions",
        "ip_address",
        existing_type=sa.VARCHAR(),
        comment="machine's ip address",
        existing_nullable=True,
    )
    op.alter_column(
        "sessions",
        "platform",
        existing_type=sa.VARCHAR(),
        comment="machine's os platform",
        existing_nullable=True,
    )
    op.alter_column(
        "sessions",
        "browser",
        existing_type=sa.VARCHAR(),
        comment="registered browser",
        existing_nullable=True,
    )
    op.alter_column(
        "sessions",
        "slug",
        existing_type=sa.VARCHAR(),
        comment="unique's slug identifier",
        existing_nullable=False,
    )
    op.alter_column(
        "sessions",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        comment="session's creation date",
        existing_nullable=False,
    )
    op.create_unique_constraint(op.f("uq_sessions_slug"), "sessions", ["slug"])
    op.alter_column(
        "user_roles",
        "id",
        existing_type=sa.INTEGER(),
        comment="Unique row identifier",
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "user_roles",
        "user_id",
        existing_type=sa.INTEGER(),
        comment="user's table foreign key",
        existing_nullable=False,
    )
    op.alter_column(
        "user_roles",
        "role_id",
        existing_type=sa.INTEGER(),
        comment="role's table foreign key",
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "id",
        existing_type=sa.INTEGER(),
        comment="Unique row identifier",
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(),
        comment="User's identifier",
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.BOOLEAN(),
        comment="Denotes active users",
        existing_nullable=False,
        existing_server_default=sa.text("(1)::boolean"),
    )
    op.alter_column(
        "users",
        "password",
        existing_type=sa.VARCHAR(),
        comment="Password hash",
        existing_nullable=False,
        existing_server_default=sa.text("''::character varying"),
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(),
        comment="User's personal unique email",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "photo",
        existing_type=sa.VARCHAR(),
        comment="User's avatar url",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "mobile",
        existing_type=sa.VARCHAR(),
        comment="Contact number",
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "first_name",
        existing_type=sa.VARCHAR(),
        comment="First Name",
        existing_nullable=False,
        existing_server_default=sa.text("''::character varying"),
    )
    op.alter_column(
        "users",
        "last_name",
        existing_type=sa.VARCHAR(),
        comment="Last Name",
        existing_nullable=False,
        existing_server_default=sa.text("''::character varying"),
    )
    op.create_unique_constraint(op.f("uq_users_email"), "users", ["email"])
    op.create_unique_constraint(op.f("uq_users_username"), "users", ["username"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
