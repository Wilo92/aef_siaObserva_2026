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

    st.write(credentials)

    try:
        authenticator = stauth.Authenticate(
            credentials,
            "cgr_cookie_v1",
            "cgr_key_2026",
            30,
        )

        st.write("AUTH CREADO")

        resultado = authenticator.login()

        st.write("LOGIN EJECUTADO")
        st.write(resultado)

    except Exception as e:
        st.error(f"ERROR: {e}")
        return False

    return False