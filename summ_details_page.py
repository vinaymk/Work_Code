import streamlit as st

st.title("Rule Builder and Search")

# Initialize session state for storing the query, actions, and results
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'actions' not in st.session_state:
    st.session_state.actions = []
if 'results' not in st.session_state:
    st.session_state.results = None
if 'page' not in st.session_state:
    st.session_state.page = 'Summary'

# Text input for entering conditions
user_input = st.text_input("Enter condition:", key="condition")

# Function to update the query and actions
def update_query(action):
    st.session_state.query += action
    st.session_state.actions.append(action)

# Function to simulate search and return results
def search(query):
    # Dummy search results
    summary_results = ["Result 1 summary", "Result 2 summary", "Result 3 summary"]
    detailed_results = ["Result 1 detailed information", "Result 2 detailed information", "Result 3 detailed information"]
    return summary_results, detailed_results

# Buttons for adding to the query
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("Open Bracket"):
        update_query(" (")
with col2:
    if st.button("Close Bracket"):
        update_query(" )")
with col3:
    if st.button("AND"):
        update_query(" AND ")
with col4:
    if st.button("OR"):
        update_query(" OR ")
with col5:
    if st.button("NOT"):
        update_query(" NOT ")

# Buttons for adding condition and removing last condition
col6, col7 = st.columns(2)
with col6:
    if st.button("Add Condition"):
        update_query(f" {user_input} ")
with col7:
    if st.button("Remove Last Condition"):
        if st.session_state.actions:
            last_action = st.session_state.actions.pop()
            st.session_state.query = st.session_state.query[:-len(last_action)]

# Display the current query
st.write("Current Query:")
st.code(st.session_state.query)

# Button to reset the query
if st.button("Reset Query"):
    st.session_state.query = ""
    st.session_state.actions = []

# Search button to execute the query
if st.button("Search"):
    summary_results, detailed_results = search(st.session_state.query)
    st.session_state.results = {
        'summary': summary_results,
        'detailed': detailed_results
    }

# Display results if search has been performed
if st.session_state.results:
    # Page navigation
    page = st.radio("Select page", ["Summary", "Detailed"], key="page")

    if page == "Summary":
        st.write("Summary Results:")
        for result in st.session_state.results['summary']:
            st.write(result)
    elif page == "Detailed":
        st.write("Detailed Results:")
        for result in st.session_state.results['detailed']:
            st.write(result)
