# import streamlit as st

# st.title("Rule Builder")

# # Initialize session state for storing the query and actions
# if 'query' not in st.session_state:
#     st.session_state.query = ""
# if 'actions' not in st.session_state:
#     st.session_state.actions = []

# # Text input for entering conditions
# user_input = st.text_input("Enter condition:", key="condition")

# # Function to update the query and actions
# def update_query(action):
#     st.session_state.query += action
#     st.session_state.actions.append(action)

# # Buttons for adding to the query
# col1, col2, col3, col4, col5, col6 = st.columns(6)
# with col1:
#     if st.button("Open Bracket"):
#         update_query(" (")
# with col2:
#     if st.button("Close Bracket"):
#         update_query(" )")
# with col3:
#     if st.button("AND"):
#         update_query(" AND ")
# with col4:
#     if st.button("OR"):
#         update_query(" OR ")
# with col5:
#     if st.button("NOT"):
#         update_query(" NOT ")
# with col6:
#     if st.button("Add Condition"):
#         update_query(f" {user_input} ")

# # Button to remove the last condition
# if st.button("Remove Last Condition"):
#     if st.session_state.actions:
#         last_action = st.session_state.actions.pop()
#         st.session_state.query = st.session_state.query[:-len(last_action)]

# # Display the current query
# st.write("Current Query:")
# st.code(st.session_state.query)

# # Button to reset the query
# if st.button("Reset Query"):
#     st.session_state.query = ""
#     st.session_state.actions = []

import streamlit as st

st.title("Formulate Query")

# Initialize session state for storing the query and actions
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'actions' not in st.session_state:
    st.session_state.actions = []

# Text input for entering conditions
user_input = st.text_input("Enter search term:", key="condition")

# Function to update the query and actions
def update_query(action):
    st.session_state.query += action
    st.session_state.actions.append(action)

# Heading for the first two buttons
st.markdown("##### Operators : ")


# Buttons for adding to the query
col1, col2, _,col3,col4, col5 , = st.columns(6)
with col1:
    if st.button(" ( "):
        update_query(" (")
with col2:
    if st.button(" ) "):
        update_query(" )")
with col3:
    if st.button("   AND   "):
        update_query(" AND ")
with col4:
    if st.button("   OR   "):
        update_query(" OR ")
with col5:
    if st.button("   NOT"):
        update_query(" NOT ")


# Heading for the first two buttons
st.markdown("##### Perform operations : ")

# Buttons for adding condition and removing last condition
col6, _,col7,col8 = st.columns(4)
with col6:
    if st.button("Add text"):
        update_query(f" {user_input} ")
with col7:
    if st.button("Undo Last"):
        if st.session_state.actions:
            last_action = st.session_state.actions.pop()
            st.session_state.query = st.session_state.query[:-len(last_action)]

# Display the current query
st.write("Current Query:")
st.code(st.session_state.query)

# Button to reset the query
with col8:
    if st.button("Reset Query"):
        st.session_state.query = ""
        st.session_state.actions = []
