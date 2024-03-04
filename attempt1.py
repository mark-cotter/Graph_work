import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import io

# Define the URL of the CSV file in the GitHub repository
github_raw_url = "https://github.com/mark-cotter/Graph_work/raw/30874f3e1a3e36c2aa44f4bd5101818dbd7b1724/just_netflix_data_csv_error_tester.csv"

def fetch_data_from_github():
    try:
        # Fetch the raw content of the CSV file from GitHub
        response = requests.get(github_raw_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Error fetching data from GitHub: {e}")
        return None

def main():
    # Set the theme to light mode
    st.set_page_config(page_title="Netflix Analysis", page_icon=":tv:", layout="wide", initial_sidebar_state="expanded", theme="light")

    st.title("Netflix Analysis")

    # Create tabs
    tabs = ["Netflix Subscription Breakdown", "Genre Breakdown"]
    selected_tab = st.radio("Select Analysis", tabs)

    if selected_tab == "Netflix Subscription Breakdown":
        # Fetch data from GitHub
        df_netflix_data = fetch_data_from_github()
        if df_netflix_data is not None:
            # Plotting
            fig = go.Figure()

            fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'],
                                     mode='lines+markers', name='Netflix', line=dict(color='red')))

            fig.add_shape(
                go.layout.Shape(
                    type="rect",
                    x0='19Q4',
                    y0=0,
                    x1='20Q2',
                    y1=16,
                    fillcolor="rgba(0, 0, 255, 0.15)",
                    line=dict(color="rgba(255, 0, 0, 0.5)"),
                )
            )

            fig.add_annotation(
                go.layout.Annotation(
                    x='19Q4',
                    y=15,
                    xref="x",
                    yref="y",
                    text="COVID-19 Pandemic",
                    showarrow=True,
                    arrowhead=2,
                    ax=-100,
                    ay=-40
                )
            )

            price_hike_quarters = df_netflix_data[df_netflix_data['Price Hike for at least 1 plan'] == True]['Quarter']
            fig.add_trace(go.Scatter(x=price_hike_quarters,
                                     y=df_netflix_data.loc[df_netflix_data['Price Hike for at least 1 plan'] == True, 'Sub Increase Q2Q M'],
                                     mode='markers', name='Price Hike for at least 1 plan',
                                     marker=dict(symbol='x', size=13, color='black')))

            fig.add_trace(go.Scatter(x=['23Q1'], y=[df_netflix_data.loc[df_netflix_data['Quarter'] == '23Q1', 'Sub Increase Q2Q M'].iloc[0]],
                                     mode='markers', name='Password Sharing Crackdown',
                                     marker=dict(symbol='circle', size=10, color='blue')))

            fig.update_layout(xaxis_title='Quarter', yaxis_title='Sub Increase in millions', height=370)

            st.plotly_chart(fig)

    elif selected_tab == "Genre Breakdown":
        # Placeholder for genre breakdown
        st.write("Fill in genre breakdown here")

if __name__ == "__main__":
    main()