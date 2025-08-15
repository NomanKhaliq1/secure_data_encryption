# app.py — Clear Options UI (Generate/Paste/Upload Key + Text/File Encrypt/Decrypt)
import streamlit as st
from cryptography.fernet import Fernet, InvalidToken

st.set_page_config(page_title="Encrypt/Decrypt", page_icon="🔒", layout="centered")
st.title("🔒 Encrypt / Decrypt")

# ----------------------------
# Session
# ----------------------------
if "key" not in st.session_state:
    st.session_state.key = None

# ----------------------------
# Helpers
# ----------------------------
def show_key():
    if st.session_state.key:
        st.code(st.session_state.key.decode(), language="plaintext")
        st.download_button("💾 Download key.txt", st.session_state.key, "key.txt", "text/plain")

def need_key():
    if not st.session_state.key:
        st.error("⚠️ Please set a key in Step 1 first.")
        return True
    return False

# ----------------------------
# STEP 1 — Key Method
# ----------------------------
st.header("Step 1: Choose Key Method")

key_method = st.radio(
    "Select how you want to set the key",
    ["Generate", "Paste", "Upload"],
    horizontal=True,
    key="key_method",
)

colA, colB = st.columns(2)

if key_method == "Generate":
    if colA.button("🔑 Generate Random Key", use_container_width=True, key="btn_gen"):
        st.session_state.key = Fernet.generate_key()
        st.success("✅ New key generated.")
    if colB.button("🗑️ Clear Key", use_container_width=True, key="btn_clear"):
        st.session_state.key = None
        st.info("Key cleared from session.")
    show_key()

elif key_method == "Paste":
    pasted = st.text_input("Paste Fernet Key (Base64)", placeholder="e.g. V0VfY2xlYXJfdGhpcy1pcy1hLWtleQ==", key="paste_box")
    btn_cols = st.columns(2)
    if btn_cols[0].button("Use Pasted Key", use_container_width=True, key="btn_use_paste"):
        if pasted.strip():
            try:
                _ = Fernet(pasted.strip().encode())
                st.session_state.key = pasted.strip().encode()
                st.success("✅ Key loaded from pasted text.")
            except Exception:
                st.error("❌ Invalid key. It must be a Fernet Base64 key.")
        else:
            st.warning("Paste a key first.")
    if btn_cols[1].button("🗑️ Clear Key", use_container_width=True, key="btn_clear2"):
        st.session_state.key = None
        st.info("Key cleared from session.")
    show_key()

else:  # Upload
    uploaded_key = st.file_uploader("Upload key.txt", type=["txt"], key="key_file")
    btn_cols = st.columns(2)
    if btn_cols[0].button("Use Uploaded Key", use_container_width=True, key="btn_use_upload"):
        if uploaded_key:
            data = uploaded_key.read().strip()
            try:
                _ = Fernet(data)
                st.session_state.key = data
                st.success("✅ Key loaded from file.")
            except Exception:
                st.error("❌ Invalid key file. Should be a Fernet Base64 key.")
        else:
            st.warning("Choose a key file first.")
    if btn_cols[1].button("🗑️ Clear Key", use_container_width=True, key="btn_clear3"):
        st.session_state.key = None
        st.info("Key cleared from session.")
    show_key()

st.divider()

# ----------------------------
# STEP 2 — Action Type & Mode
# ----------------------------
st.header("Step 2: What do you want to work on?")

action_type = st.radio("Pick data type", ["Text", "File"], horizontal=True, key="action_type")
mode = st.radio("Pick mode", ["Encrypt", "Decrypt"], horizontal=True, key="mode")

# ----------------------------
# TEXT WORKFLOW
# ----------------------------
if action_type == "Text":
    help_txt = "Type plain text to encrypt" if mode == "Encrypt" else "Paste encrypted token to decrypt"
    text_input = st.text_area("Text", height=160, placeholder=help_txt, key="text_box")

    btn_label = "Encrypt Text" if mode == "Encrypt" else "Decrypt Text"
    if st.button(btn_label, use_container_width=True, key="btn_text"):
        if need_key():
            pass
        elif not text_input.strip():
            st.warning("Please enter text first.")
        else:
            f = Fernet(st.session_state.key)
            try:
                if mode == "Encrypt":
                    token = f.encrypt(text_input.encode("utf-8"))
                    st.success("✅ Encrypted.")
                    st.code(token.decode("utf-8"), language="plaintext")
                    st.download_button("💾 Download encrypted.txt", token, "encrypted.txt", "text/plain")
                else:
                    token_str = text_input.strip()
                    plain = f.decrypt(token_str.encode("utf-8"))
                    st.success("✅ Decrypted.")
                    st.code(plain.decode("utf-8"), language="plaintext")
                    st.download_button("💾 Download decrypted.txt", plain, "decrypted.txt", "text/plain")
            except InvalidToken:
                st.error("❌ Invalid token or wrong key.")
            except Exception as e:
                st.error(f"Failed: {e}")

# ----------------------------
# FILE WORKFLOW
# ----------------------------
else:
    file_help = "Upload any file to encrypt" if mode == "Encrypt" else "Upload the .enc file to decrypt"
    up = st.file_uploader(file_help, type=None, key="file_box")

    btn_label = "Encrypt File" if mode == "Encrypt" else "Decrypt File"
    if st.button(btn_label, use_container_width=True, key="btn_file"):
        if need_key():
            pass
        elif not up:
            st.warning("Please upload a file first.")
        else:
            f = Fernet(st.session_state.key)
            data = up.read()
            try:
                if mode == "Encrypt":
                    out = f.encrypt(data)
                    out_name = up.name + ".enc"
                    st.success("✅ File encrypted.")
                else:
                    out = f.decrypt(data)
                    out_name = up.name[:-4] if up.name.endswith(".enc") else "decrypted.bin"
                    st.success("✅ File decrypted.")
                st.download_button("💾 Download", out, file_name=out_name, mime="application/octet-stream")
            except InvalidToken:
                st.error("❌ Invalid encrypted file or wrong key.")
            except Exception as e:
                st.error(f"Failed: {e}")

st.markdown("---")
st.caption("Keep your key safe. Without it, decryption is impossible.")
