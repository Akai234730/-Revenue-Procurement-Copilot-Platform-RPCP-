"""add auth tables

Revision ID: 0002_auth_tables
Revises: 0001_initial
Create Date: 2026-04-20 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = '0002_auth_tables'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'permissions',
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)

    op.create_table(
        'roles',
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_roles_code'), 'roles', ['code'], unique=True)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    op.create_table(
        'users',
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('display_name', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('dept_id', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('title', sa.String(length=128), nullable=False, server_default=''),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.String(length=64), nullable=False),
        sa.Column('permission_id', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id']),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('role_id', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
    )


def downgrade() -> None:
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_code'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')
