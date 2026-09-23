import pytest

from app.storage import (
    create_chat,
    create_document,
    create_message,
    delete_chat,
    delete_document,
    get_chat,
    get_document,
    get_messages_by_chat,
    init_db,
    list_chats,
    list_documents,
    update_chat_timestamp,
    update_document_status,
)


@pytest.fixture
def db(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def test_create_document(db):
    doc = create_document("doc_1", "file.pdf", sqlite_path=db)
    assert doc["id"] == "doc_1"
    assert doc["filename"] == "file.pdf"
    assert doc["status"] == "PROCESSING"


def test_get_document_returns_none_for_missing(db):
    assert get_document("missing", sqlite_path=db) is None


def test_list_documents_empty(db):
    assert list_documents(db) == []


def test_list_documents_ordered(db):
    create_document("d1", "a.txt", sqlite_path=db)
    create_document("d2", "b.txt", sqlite_path=db)
    docs = list_documents(db)
    assert len(docs) == 2
    assert docs[0]["id"] == "d2"


def test_update_document_status(db):
    create_document("d1", "f.txt", sqlite_path=db)
    update_document_status("d1", "READY", sqlite_path=db)
    doc = get_document("d1", sqlite_path=db)
    assert doc["status"] == "READY"


def test_delete_document(db):
    create_document("d1", "f.txt", sqlite_path=db)
    delete_document("d1", sqlite_path=db)
    assert get_document("d1", sqlite_path=db) is None


def test_create_chat(db):
    chat = create_chat("c1", "My Chat", sqlite_path=db)
    assert chat["id"] == "c1"
    assert chat["title"] == "My Chat"


def test_list_chats_ordered(db):
    create_chat("c1", "First", sqlite_path=db)
    create_chat("c2", "Second", sqlite_path=db)
    chats = list_chats(db)
    assert len(chats) == 2
    assert chats[0]["id"] == "c2"


def test_update_chat_timestamp(db):
    create_chat("c1", sqlite_path=db)
    update_chat_timestamp("c1", sqlite_path=db)
    chat = get_chat("c1", sqlite_path=db)
    assert chat is not None


def test_delete_chat_removes_messages(db):
    create_chat("c1", sqlite_path=db)
    create_message("m1", "c1", "user", "hello", sqlite_path=db)
    delete_chat("c1", sqlite_path=db)
    assert get_chat("c1", sqlite_path=db) is None
    assert get_messages_by_chat("c1", sqlite_path=db) == []


def test_create_message_stores_citations(db):
    create_chat("c1", sqlite_path=db)
    msg = create_message("m1", "c1", "assistant", "answer", [{"idx": 1}], sqlite_path=db)
    assert msg["citations"] == [{"idx": 1}]
    msgs = get_messages_by_chat("c1", sqlite_path=db)
    assert msgs[0]["citations"] == [{"idx": 1}]


def test_get_messages_ordered(db):
    create_chat("c1", sqlite_path=db)
    create_message("m1", "c1", "user", "q1", sqlite_path=db)
    create_message("m2", "c1", "assistant", "a1", sqlite_path=db)
    msgs = get_messages_by_chat("c1", sqlite_path=db)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_init_db_creates_parent_directory(tmp_path):
    from app.storage import init_db

    db_path = tmp_path / "nested" / "deep" / "test.db"
    assert not db_path.parent.exists()
    init_db(str(db_path))
    assert db_path.parent.exists()
    assert db_path.exists()


def test_init_db_does_not_fail_on_existing_directory(tmp_path):
    from app.storage import init_db

    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    init_db(str(db_path))
    assert db_path.exists()
