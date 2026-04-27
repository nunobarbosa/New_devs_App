from typing import Any, Dict, List


async def get_properties_for_tenant(
    tenant_id: str,
    page: int = 1,
    page_size: int = 1000,
) -> Dict[str, Any]:
    """
    Fetch properties directly from the database using the same SQLAlchemy
    DatabasePool approach as reservations.py.
    """
    try:
        from app.core.database_pool import DatabasePool
        from sqlalchemy import text

        db_pool = DatabasePool()
        await db_pool.initialize()

        if not db_pool.session_factory:
            raise Exception("Database pool not available")

        safe_page = max(page, 1)
        safe_page_size = min(max(page_size, 1), 1000)
        offset = (safe_page - 1) * safe_page_size

        async with db_pool.get_session() as session:
            count_query = text("""
                SELECT COUNT(*) AS total
                FROM properties
                WHERE tenant_id = :tenant_id
            """)
            data_query = text("""
                SELECT id, tenant_id, name, timezone, created_at
                FROM properties
                WHERE tenant_id = :tenant_id
                ORDER BY name ASC
                LIMIT :limit OFFSET :offset
            """)

            count_result = await session.execute(count_query, {"tenant_id": tenant_id})
            total = count_result.scalar() or 0

            data_result = await session.execute(data_query, {
                "tenant_id": tenant_id,
                "limit": safe_page_size,
                "offset": offset,
            })

            properties: List[Dict[str, Any]] = [
                {
                    "id": row.id,
                    "tenant_id": row.tenant_id,
                    "name": row.name,
                    "timezone": row.timezone,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in data_result.fetchall()
            ]

            return {
                "data": properties,
                "total": total,
                "page": safe_page,
                "page_size": safe_page_size,
            }

    except Exception as e:
        print(f"Database error fetching properties for tenant {tenant_id}: {e}")
        raise
