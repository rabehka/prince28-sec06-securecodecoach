"""add GIN index to document metadata

Revision ID: c23c65eaec90
Revises: 37f196e109b0
"""

from alembic import op

# Revision identifiers
revision = "c23c65eaec90"  # pragma: allowlist secret
down_revision = "37f196e109b0"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_documents_metadata_gin",
        "documents",
        ["metadata"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_metadata_gin",
        table_name="documents",
    )
