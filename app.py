import streamlit as st

from terminalops.agent import MissingDependencyError, create_terminalops_agent


st.set_page_config(page_title="TerminalOps UI", page_icon=":desktop_computer:")
st.title("TerminalOps")


if "agent_error" not in st.session_state:
    st.session_state.agent_error = None

if "agent" not in st.session_state:
    try:
        st.session_state.agent, _ = create_terminalops_agent(
            confirm_callback=lambda command: True
        )
    except MissingDependencyError as exc:
        st.session_state.agent_error = str(exc)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.agent_error:
    st.error(st.session_state.agent_error)
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask TerminalOps about your Docker, git, or system tasks..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
