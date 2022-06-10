from base import client, USER, db
from app import Mensch


def test_menschen_auth(client):
    resp = client.get("/menschen", follow_redirects=False)
    assert resp.status_code == 401
    resp = client.get("/mensch/add", follow_redirects=False)
    assert resp.status_code == 401
    resp = client.get("/mensch/123/edit", follow_redirects=False)
    assert resp.status_code == 401


def test_menschen_list(client):
    resp = client.get("/mensch/add", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200


def test_menschen_add_valid(client):
    resp = client.get("/mensch/add", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200

    name = "test_user1"
    bezugsgruppe = "Zitrone"
    phone = "0157523423"

    data = {'name': name,
            'telephone': phone,
            'bezugsgruppe': bezugsgruppe}
    resp = client.post("/mensch/add", data=data, follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 302

    resp = client.get("/menschen", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200
    assert name in resp.text
    assert phone in resp.text
    assert bezugsgruppe in resp.text

    mensch = Mensch.query.filter_by(name=name)
    mensch.delete()
    db.session.commit()


def test_menschen_add_invalid_already_exists(client):
    name = "test_user1"
    bezugsgruppe = "Zitrone"
    phone = "0157523423"

    data = {'name': name,
            'telephone': phone,
            'bezugsgruppe': bezugsgruppe}
    resp = client.post("/mensch/add", data=data, follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 302

    resp = client.post("/mensch/add", data=data, follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200
    assert "Es existiert bereits ein Mensch mit Namen" in resp.text

    mensch = Mensch.query.filter_by(name=name)
    mensch.delete()
    db.session.commit()


def test_menschen_add_invalid_error_message_missing_field(client):
    # bezugsgruppe is missing
    data = {'name': "test_user123",
            'telephone': "34342"}

    resp = client.post("/mensch/add", data=data, follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200
    assert "Bezugsgruppe</label>: This field is required" in resp.text


def test_menschen_add_invalid_phone(client):
    for phone in ["0123 314", "not a number", "1234"]:
        data = {'name': "test_user123",
                'bezugsgruppe': 'hasen',
                'telephone': phone}

        resp = client.post("/mensch/add", data=data, follow_redirects=False, auth=(USER, USER))
        assert resp.status_code == 200
        assert "Die Telefonnummer muss entweder" in resp.text


def test_menschen_delete(client):
    # I need this to get access to db ...
    resp = client.get("/menschen", follow_redirects=False, auth=(USER, USER))
    mensch = Mensch(name="test_user1111", bezugsgruppe="Fisch", telephone="01487538")
    db.session.add(mensch)
    db.session.commit()
    resp = client.get(f"/mensch/{mensch.id}/delete", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200
    db.session.delete(mensch)
    db.session.commit()


def test_menschen_edit(client):
    # I need this to get access to db ...
    resp = client.get("/menschen", follow_redirects=False, auth=(USER, USER))
    mensch = Mensch(name="test_user2222", bezugsgruppe="Fisch", telephone="01487538")
    db.session.add(mensch)
    db.session.commit()
    resp = client.get(f"/mensch/{mensch.id}/edit", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 200

    name = "test_user11011"
    data = {'name': name,
            'bezugsgruppe': 'Hasen',
            'telephone': "0234324"}
    resp = client.post(f"/mensch/{mensch.id}/edit", data=data, follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 302
    assert Mensch.query.get(mensch.id).name == name

    db.session.delete(mensch)
    db.session.commit()


def test_menschen_edit_not_found(client):
    resp = client.get("/mensch/12333333/edit", follow_redirects=False, auth=(USER, USER))
    assert resp.status_code == 404
