from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler

def create_session():
    firestore_handler = FirestoreHandler()
    session = firestore_handler.create_session()

    return session
