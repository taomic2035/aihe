import uuid


def test_create_memory_and_audit():
    from backend.app.models import Memory, MemoryAudit, Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        m = Memory(
            id=str(uuid.uuid4()),
            user_id="u1",
            type="episodic",
            content="我喜欢喝美式，住在上海",
            importance=0.8,
        )
        s.add(m)
        s.commit()
        s.refresh(m)
        assert m.id is not None

        # soft delete + audit
        m.deleted_at = "2026-08-22T00:00:00"
        audit = MemoryAudit(
            id=str(uuid.uuid4()),
            memory_id=m.id,
            action="delete",
            actor="user",
        )
        s.add(audit)
        s.commit()

        # query not deleted
        active = s.query(Memory).filter(Memory.deleted_at.is_(None)).all()
        assert len(active) == 0

        audits = s.query(MemoryAudit).filter(MemoryAudit.memory_id == m.id).all()
        assert len(audits) == 1
        assert audits[0].action == "delete"
