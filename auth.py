import os
import streamlit as st
import streamlit_authenticator as stauth


def autenticar():

    credentials = {
        "usernames": {
            os.getenv("APP_USER_1"): {
                "name": os.getenv("APP_NAME_1"),
                "password": os.getenv("APP_PASSWORD_HASH_1"),
            },
            os.getenv("APP_USER_2"): {
                "name": os.getenv("APP_NAME_2"),
                "password": os.getenv("APP_PASSWORD_HASH_2"),
            },
            os.getenv("APP_USER_3"): {
                "name": os.getenv("APP_NAME_3"),
                "password": os.getenv("APP_PASSWORD_HASH_3"),
            },
            os.getenv("APP_USER_4"): {
                "name": os.getenv("APP_NAME_4"),
                "password": os.getenv("APP_PASSWORD_HASH_4"),
            },
        }
    }
   

    authenticator = stauth.Authenticate(
        credentials,
        "cgr_cookie_v1",
        "cgr_key_2026",
        30,
    )

    authenticator.login()

    if st.session_state.get("authentication_status"):
        authenticator.logout("Cerrar sesión", "sidebar")
        return True

    if st.session_state.get("authentication_status") is False:
        st.error("Usuario o contraseña incorrectos")
        return False

    return False
