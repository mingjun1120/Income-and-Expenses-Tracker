# Import base streamlit dependency
import streamlit as st
from streamlit.web import cli as stcli
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu

# Import system
import sys

# Import plotly for visualization
import plotly.graph_objects as go

# Import database.py
import database as db

import calendar
from datetime import datetime


def main():
    # --- SETTINGS ---
    incomes = ["Salary", "Blog", "Other Income"]
    expenses = ["Rent", "Utilities", "Groceries", "Car", "Other Expenses", "Saving"]
    currency = "MYR"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"  # https://www.webfx.com/tools/emoji-cheat-sheet/

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")
    st.title(body=f"{page_title} {page_icon}")

    # --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    # # --- HIDE STREAMLIT STYLE ---
    # hide_st_style = """
    #             <style>
    #             #MainMenu {visibility: hidden;}
    #             footer {visibility: hidden;}
    #             header {visibility: hidden;}
    #             </style>
    #             """
    # st.markdown(body=hide_st_style, unsafe_allow_html=True)

    # --- NAVIGATION MENU ---
    selected = option_menu(menu_title=None,
                           options=["Data Entry", "Data Visualization"],
                           icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
                           orientation="horizontal"
                           )

    # --- INPUT & SAVE PERIODS ---
    if selected == "Data Entry":
        st.header(body=f"Data Entry in {currency}")
        with st.form(key="entry_form", clear_on_submit=True):
            col1, col2 = st.columns(spec=2)
            col1.selectbox(label="Select Month:", options=months, key="month")
            col2.selectbox(label="Select Year:", options=years, key="year")

            "---"  # Divider

            with st.expander(label="Income"):
                for income in incomes:
                    st.number_input(label=f"{income}:", min_value=0, step=10, format="%i", key=income)
            with st.expander(label="Expenses"):
                for expense in expenses:
                    st.number_input(label=f"{expense}:", min_value=0, step=10, format="%i", key=expense)
            with st.expander(label="Comment"):
                comment = st.text_area(label="", placeholder="Enter a comment here...")

            "---"  # Divider

            submitted = st.form_submit_button(label="Save Data")
            if submitted:
                period = f"{st.session_state['year']}_{st.session_state['month']}"
                incomes = {income: st.session_state[income] for income in incomes}
                expenses = {expense: st.session_state[expense] for expense in expenses}
                # Insert data into database
                db.insert_period(period=period, incomes=incomes, expenses=expenses, comment=comment)
                st.success("Data saved!")

    if selected == "Data Visualization":
        # --- PLOT PERIODS ---
        st.header(body="Data Visualization")
        with st.form("saved_periods"):
            period = st.selectbox(label="Select Period:", options=db.get_all_periods())
            submitted = st.form_submit_button(label="Plot Period")
            if submitted:
                period_data = db.get_period(period=period)
                comment = period_data.get("comment")
                expenses = period_data.get("expenses")
                incomes = period_data.get("incomes")

                # Create metrics
                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense
                col1, col2, col3 = st.columns(spec=3)
                col1.metric(label="Total Income", value=f"{total_income} {currency}")
                col2.metric(label="Total Expense", value=f"{total_expense} {currency}")
                col3.metric(label="Remaining Budget", value=f"{remaining_budget} {currency}")
                st.text(body=f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30)  # , color="#E694FF"
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data=data)
                fig.update_layout(title={"text": "Use of Incomes in Every Expense", "x": 0.5, "font": {"family": "Arial", "size": 24}},
                                  margin=dict(l=5, r=5, t=45, b=10),
                                  font=dict(family="Arial", size=18)
                                  )
                st.plotly_chart(figure_or_data=fig, use_container_width=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if st.runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
