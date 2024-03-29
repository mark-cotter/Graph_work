import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import io
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

def fetch_data_from_github(file_path):
    try:
        # Fetch the raw content of the CSV file from GitHub
        response = requests.get(file_path)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Error fetching data from GitHub: {e}")
        return None

def create_subscription_growth_chart(df_sub):
    fig_sub = go.Figure()

    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Netflix Sub Change Q2Q'],
                                 mode='lines+markers', name='Netflix',
                                 line=dict(color='red')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Disney + Sub Change Q2Q'],
                                 mode='lines+markers', name='Disney+',
                                 line=dict(color='blue')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Hulu Sub Change Q2Q'],
                                 mode='lines+markers', name='Hulu',
                                 line=dict(color='green')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Peacock Subs Change Q2Q'],
                                 mode='lines+markers', name='Peacock',
                                 line=dict(color='black')))

    fig_sub.update_layout(title_text='Subscription Growth Over Time',
                          xaxis_title='Quarter',
                          yaxis_title='Sub Increase in millions',
                          legend=dict(title='Services'))

    return fig_sub

def create_netflix_subscription_breakdown_chart(df_netflix_data):
    fig_netflix = go.Figure()

    fig_netflix.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'],
                                     mode='lines+markers', name='Netflix', line=dict(color='red')))

    fig_netflix.add_shape(
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

    fig_netflix.add_annotation(
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
    fig_netflix.add_trace(go.Scatter(x=price_hike_quarters,
                                     y=df_netflix_data.loc[df_netflix_data['Price Hike for at least 1 plan'] == True, 'Sub Increase Q2Q M'],
                                     mode='markers', name='Price Hike for at least 1 plan',
                                     marker=dict(symbol='x', size=13, color='black')))

    fig_netflix.add_trace(go.Scatter(x=['23Q1'], y=[df_netflix_data.loc[df_netflix_data['Quarter'] == '23Q1', 'Sub Increase Q2Q M'].iloc[0]],
                                     mode='markers', name='Password Sharing Crackdown',
                                     marker=dict(symbol='circle', size=10, color='blue')))

    fig_netflix.update_layout(title_text='Detailed Netflix Subscription Timeline',xaxis_title='Quarter', yaxis_title='Sub Increase in millions', height=370)

    return fig_netflix

def create_netflix_subscription_growth_chart(df_netflix_data, df_sub):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], 
                             y=df_netflix_data['Sub Increase Q2Q M'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red')))

    fig.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Disney + Sub Change Q2Q'],
                             mode='lines+markers', name='Disney+',
                             line=dict(color='blue')))

    fig.update_layout(
        title_text='Netflix Sub Growth Over Time',
        xaxis_title='Quarter',
        yaxis_title='Sub Increase in millions',
        height=370
    )

    return fig

def plot_netflix_stock_growth(df_data):
    needed_quarters = ["18Q2", "18Q3", "18Q4", "19Q1", "19Q2", "19Q3", "19Q4", "20Q1", "20Q2"]
    df_data = df_data[df_data["Quarter"].isin(needed_quarters)]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_data['Quarter'],
        y=df_data['Netflix Stock Change Q2Q %'],
        mode='lines+markers',
        name='Netflix',
        line=dict(color='red')
    ))

    fig.add_trace(go.Scatter(
        x=df_data['Quarter'],
        y=df_data['NASDAQ Change Q2Q %'],
        mode='lines+markers',
        name='NASDAQ',
        line=dict(color='blue')
    ))

    # Add marker for x = "20Q1"
    fig.add_trace(go.Scatter(
        x=["20Q1"],
        y=[df_data.loc[df_data['Quarter'] == "20Q1", 'Netflix Stock Change Q2Q %'].iloc[0]],  # Get the corresponding y value
        mode='markers',
        name='Covid-19 Beginning',
        marker=dict(color='green', size=15, symbol="cross")
    ))

    fig.update_layout(
        title_text='Netflix Stock Growth Over Quarters',
        xaxis_title='Quarter',
        yaxis_title='Stock Increase Percentage',
        yaxis=dict(tickformat=".1%"),
        height=370
    )

    st.plotly_chart(fig)


def create_genre_breakdown_charts(df_genre):
    # Create the plot for total hours viewed by genre
    genre_sum = df_genre.groupby("Genre")["Hours Viewed"].sum().reset_index()
    genre_sum_sorted = genre_sum.sort_values(by="Hours Viewed", ascending=False)
    fig_genre_total_hours = go.Figure(
        data=[go.Bar(
            x=genre_sum_sorted["Genre"],
            y=genre_sum_sorted["Hours Viewed"],
            name="Total Hours Viewed"
        )]
    )
    fig_genre_total_hours.update_layout(
        title="Total Hours Viewed by Genre",
        xaxis_title="Genre",
        yaxis_title="Total Hours Viewed",
        yaxis=dict(range=[0, genre_sum_sorted["Hours Viewed"].max() + 1000000])
    )

    # Subset the DataFrame for Genre equals Children
    df_children = df_genre[df_genre['Genre'] == 'Children']
    cocomelon_hours = df_children[df_children['Title'].str.contains('CoComelon', case=False)]['Hours Viewed'].sum()
    paw_patrol_hours = df_children[df_children['Title'].str.contains('PAW Patrol', case=False)]['Hours Viewed'].sum()
    other_hours = df_children[~df_children['Title'].str.contains('CoComelon|PAW Patrol', case=False)]['Hours Viewed'].sum()

    fig_genre_comparison = go.Figure()
    fig_genre_comparison.add_trace(go.Bar(
        x=['CoComelon & PAW Patrol', 'All Other Childrens Shows'],
        y=[cocomelon_hours + paw_patrol_hours, other_hours],
        marker_color=['blue', 'green']
    ))
    fig_genre_comparison.update_layout(
        title='CoComelon & PAW Patrol Compared to All Other Childrens TV Shows',
        xaxis_title='Category',
        yaxis_title='Combined Viewing Hours'
    )

    return fig_genre_total_hours, fig_genre_comparison

def create_region_breakdown_chart(df_region):
    fig = go.Figure()

    values = df_region[df_region['Quarter'] == df_region['Quarter'].iloc[0]][['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub']].iloc[0].tolist()
    pie_chart = go.Pie(labels=['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub'], values=values, name=df_region['Quarter'].iloc[0])
    fig.add_trace(pie_chart)

    buttons = [dict(label='Play',
                     method='animate',
                     args=[None, dict(frame=dict(duration=400, redraw=True), fromcurrent=True)]),
               dict(label='Pause',
                    method='animate',
                    args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate')])]

    fig.update_layout(title='Subscription Distribution Over Quarters in Millions', 
                      updatemenus=[dict(type='buttons', showactive=False, buttons=buttons)],
                      annotations=[dict(text=df_region['Quarter'].iloc[0], showarrow=False, x=0.9, y=0.3, font=dict(size=20))],
                      height=380,
                      legend=dict(traceorder='normal', title=dict(font=dict(size=16)), font=dict(size=18)))  # Set the legend font size

    frames = [go.Frame(data=[go.Pie(labels=['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub'],
                                    values=df_region[df_region['Quarter'] == quarter][['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub']].iloc[0].tolist(),
                                    name=quarter)],
                       name=quarter,
                       layout=dict(annotations=[dict(text=quarter, showarrow=False, x=0.8, y=0.5, font=dict(size=20))]))
              for quarter in df_region['Quarter']]

    fig.frames = frames

    return fig


def create_mean_duration_graph(df_movies):
    df_movies["duration"] = df_movies["duration"].str.replace(' min', '')
    df_movies["duration"] = df_movies["duration"].astype(int)

    df_movies['date_added'] = pd.to_datetime(df_movies['date_added'])
    df_movies = df_movies[df_movies['date_added'].dt.year >= 2015]
    mean_duration = df_movies.groupby(df_movies['date_added'].dt.to_period('M'))['duration'].mean().reset_index()
    mean_duration['date_added'] = mean_duration['date_added'].astype(str)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=mean_duration['date_added'], y=mean_duration['duration'], mode='lines+markers', name='Mean Duration',
                             line=dict(color='blue', width=2)))

    fig.update_layout(title='Mean Duration of Netflix Movies by Month Added (Since 2015)',
                      xaxis_title='Month Added',
                      yaxis_title='Mean Duration (minutes)')

    return fig


def create_users_breakdown_histogram(df_users):
    fig = go.Figure(data=[go.Histogram(x=df_users["Age"])])

    # Update layout
    fig.update_layout(
        title="Users Age Breakdown",
        xaxis_title="Age",
        yaxis_title="Frequency"
    )

    return fig

def create_gender_distribution_pie_chart(df_users):
    gender_counts = df_users['Gender'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=gender_counts.index, values=gender_counts)])

    # Update layout
    fig.update_layout(
        title="Gender Distribution",
        height=500,
        width=700
    )

    return fig

def create_subscription_pie_chart(df):
    import plotly.graph_objects as go
    
    subscription_counts = df['Subscription Type'].value_counts()
    
    fig = go.Figure(data=[go.Pie(labels=subscription_counts.index, values=subscription_counts, textinfo='label+percent')])

    custom_text = []
    for label in subscription_counts.index:
        if label == 'Basic':
            custom_text.append('$7 a month')
        elif label == 'Standard':
            custom_text.append('$10 a month')
        elif label == 'Premium':
            custom_text.append('$15 a month')
        else:
            custom_text.append('')

    fig.update_traces(text=custom_text, textposition='inside', textinfo='text+percent')

    fig.update_layout(
        title="Subscription Type Distribution",
        height=500,
        width=700
    )

    return fig

def create_subscription_revenue_bar_chart(df):
    import plotly.graph_objects as go
    
    grouped_df = df.groupby('Subscription Type')['Monthly Revenue'].sum().reset_index()

    fig = go.Figure(data=[go.Bar(
        x=grouped_df['Subscription Type'],
        y=grouped_df['Monthly Revenue'],
        marker_color='skyblue'
    )])

    # Update layout
    fig.update_layout(
        title="Monthly Revenue by Subscription Type",
        xaxis_title="Subscription Type",
        yaxis_title="Monthly Revenue",
        height=500,
        width=700
    )

    return fig


def plot_Q4_sub_growth(df_netflix_data):
    q4_mask = df_netflix_data['Just Quarter Value'] == 'Q4'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'],
                             mode='lines+markers', name='Netflix', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_netflix_data[q4_mask]['Quarter'], y=df_netflix_data[q4_mask]['Sub Increase Q2Q M'],
                             mode='markers', name='Q4', marker=dict(color='blue', size=10, symbol='cross')))
    
    # Update layout
    fig.update_layout(title='Netflix Q4 Subscription Increase', xaxis_title='Quarter', yaxis_title='Subscription Increase')
    
    # Display the plot
    st.plotly_chart(fig)

def plot_lockdown_effect(df_netflix_data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'], mode='lines+markers', name='Netflix',
                             line=dict(color='red')))

    fig.add_annotation(
        go.layout.Annotation(
            x='20Q1',
            y=15,
            xref="x",
            yref="y",
            text="Beginning of COVID-19 Pandemic",
            showarrow=True,
            arrowhead=2,
            ax=-100,
            ay=-40
        )
    )

    # Add markers for each level of lockdown separately
    fig.add_trace(go.Scatter(x=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'No Lockdown']['Quarter'],
                             y=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'No Lockdown']['Sub Increase Q2Q M'],
                             mode='markers', marker=dict(color='green', size=10), name='No Lockdown'))

    fig.add_trace(go.Scatter(x=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'Weak Lockdown']['Quarter'],
                             y=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'Weak Lockdown']['Sub Increase Q2Q M'],
                             mode='markers', marker=dict(color='yellow', size=10), name='Weak Lockdown'))

    fig.add_trace(go.Scatter(x=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'Strong Lockdown']['Quarter'],
                             y=df_netflix_data[df_netflix_data['Level of Lockdown'] == 'Strong Lockdown']['Sub Increase Q2Q M'],
                             mode='markers', marker=dict(color='red', size=10), name='Strong Lockdown'))

    fig.update_layout(title_text='Effect of Lockdown on Netflix Sub Growth',
                      xaxis_title='Quarter',
                      yaxis_title='Sub Increase in millions',
                      height=370)

    return fig

def plot_netflix_sub_growth_v_price_hikes(df_netflix_data):
    # Create a Plotly figure
    fig = go.Figure()

    # Add trace for Netflix subscription growth
    fig.add_trace(go.Scatter(
        x=df_netflix_data['Quarter'],
        y=df_netflix_data['Sub Increase Q2Q M'],
        mode='lines+markers',
        name='Netflix',
        line=dict(color='red')
    ))

    # Add markers for price hike quarters
    price_hike_quarters = df_netflix_data[df_netflix_data['Price Hike for at least 1 plan'] == True]['Quarter']
    fig.add_trace(go.Scatter(
        x=price_hike_quarters,
        y=df_netflix_data.loc[df_netflix_data['Price Hike for at least 1 plan'] == True, 'Sub Increase Q2Q M'],
        mode='markers',
        name='Price Hike for at least 1 plan',
        marker=dict(symbol='x', size=13, color='black')
    ))

    # Update layout
    fig.update_layout(
        title_text='Netflix Price Hikes Effect',
        xaxis_title='Quarter',
        yaxis_title='Sub Increase in millions',
        height=370
    )

    # Render the figure in Streamlit
    st.plotly_chart(fig)


def plot_password_sharing_crackdown_effect(df_netflix_data):
    
    # Create the plot
    fig = go.Figure()
    
    # Add the main trace (Netflix subscription growth)
    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], 
                             y=df_netflix_data['Sub Increase Q2Q M'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red'),
                             showlegend=True))
    
    # Add a vertical rectangle to highlight the period of password sharing crackdown
    fig.add_vrect(x0='23Q1', x1=df_netflix_data['Quarter'].max(),
                  fillcolor="rgba(0,0,255,0.2)", layer="below", line_width=0)
    
    # Add an annotation to mark the password sharing crackdown
    fig.add_annotation(
        go.layout.Annotation(
            x='23Q1',
            y=10,  # Adjust the y-position as needed
            xref="x",
            yref="y",
            text="Password Sharing Crackdown",
            showarrow=True,
            arrowhead=2,
            ax=-70,
            ay=-30
        )
    )

    # Update layout
    fig.update_layout(title_text='Effect of Password Sharing Crackdown on Sub Growth',
                      xaxis_title='Quarter',
                      yaxis_title='Sub Increase in millions',
                      height=370,
                      showlegend=True)

    # Display the plot in Streamlit
    st.plotly_chart(fig)


def plot_netflix_subscription_growth(df_netflix_data):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], 
                             y=df_netflix_data['Sub Increase Q2Q M'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red')))
    
    fig.update_layout(title_text='Netflix Quarterly Subscription Growth',
                      xaxis_title='Quarter',
                      yaxis_title='Sub Increase in millions',
                      height=370,
                      showlegend=True)
    
    st.plotly_chart(fig)

def Q4_analysis(df_netflix_data):
    st.write("### Q4")
    st.markdown("""
        The first thing noticed was that Q4 seems to have a consistenly higher number of new subscribers compared to the other
        quarters.
        """)
    plot_Q4_sub_growth(df_netflix_data)
    st.markdown("""
        It had to be investigated if these differences in subscription growth were statistcally significant so an ANOVA (Analysis
        of Variance) Test in R was done to see if the mean values of Q4 compared to other quarters were signifcantly different.
        """)
    st.image("https://github.com/mark-cotter/Graph_work/raw/8d24e9ac6a05e1539b528a6c414e3845b2a49b47/R%20Screenshot%20Q4%20Test.png")
    st.markdown("""
        The above output from the test in R has a highlighted p value of 0.02. This is lower than the 5% level of significance which 
        means the null hypothesis that there is no difference in the mean value between Q4 and the other quarters should be rejected.

        The fact that Q4 leads to higher subscription rates follows conventional wisdom that people watch more tv and movies during these
        months. This is likely due to factors such as worse weather forcing people to stay inside and more holidays from work meaning
        people have access to more leisure time.
        """)
    st.write("")
    st.write("")
    
def Covid_19_Analysis(df_netflix_data):
    st.write("### Effect of Covid 19 Lockdown")
    st.markdown("""
        Another aspect that stood out is the peak of the graph at 20Q1. This could likely be explained by the Covid 19 Pandemic
        lockdown which forced everyone into their homes in 2020.
        """)
    st.plotly_chart(plot_lockdown_effect(df_netflix_data))
    st.markdown("""
        The above chart shows the level of lockdown that was active in each quarter broken down by how strict the lockdown level was
        on average on a worldwide basis . It will now be statistically investigated if the strength of these lockdown has an effect
        on the number of new subscribers for Netflix.
        """)
    st.image("Covid 19 Lockdown FYP.png")
    st.markdown("""
        Another ANOVA test was used to compare the means of the 3 groups and then Tukeys HSD (Honest Significant Difference) was used
        to quantify the differences between groups and see if they were statistically significant.

        As you can see from the p values Strong lockdown is signifcantly different from the other 2 as its p-value is less than
        the 5% significance level. This makes sense as a stronglockdown would force people inside where streaming is one of the
        only activities one can do. It is also interesting that the largest difference is between Strong and Weak lockdown instead
        of Strong and no Lockdown. This could be because weak lockdowns occurred directly after Strong lockdowns meaning people 
        had had their fill of streaming from being stuck inside and were more inclined to do activites outdoors.
        """)
    st.write("")
    st.write("")

def Price_Hikes_Analysis(df_netflix_data):
    st.write("### Price Hikes")
    st.markdown("""
        One trend that motivated this project was to analyse the effect Netflix's price increases had on its number
        of subscribers as these increases are very controversial on social media when they're done and speculation was that these 
        would lead to less people using the service. The graph below shows the quarters where Netflix increased
        the prices on at least 1 plan. 
        """)
    plot_netflix_sub_growth_v_price_hikes(df_netflix_data)
    st.markdown("""
        Statistical tests will be performed to see if these price hikes had a statistically significant effect on the 
        number of subscribers gained in that quarter.
        """)
    st.image("Netflix Price Hikes Screenshot.png")
    st.markdown("""
        The above R output from an ANOVA test with a p value of 0.77 which is well above the 5% significance level shows that
        these quarters with a price hike did not signicantly affect Netflix's subscription numbers. This goes against the common
        sentiment when these price hikes are introduced that people say they won't use Netflix but the subscription numbers show
        otherwise.

        This points to how Netflix is becoming more of a necessity in households and therefore demand for it is becoming more 
        inelastic as even though the prices increase people will continue to buy the service as they could not imagine not having
        access to their favourite TV shows and movies.
        """)
    st.write("")
    st.write("")

def Password_Sharing_Crackdown_Analysis(df_netflix_data):
    st.write("### Effect of Password Sharing Crackdown")
    st.markdown("""
        Netflix's controversial decison to crack down on people sharing passwords was a big inspiration for this project. There was
        big interest in how Netflix's subscription numbers performed as the public consensus was that people would refuse to buy
        new accounts when they lost access to the old one. We will see what the trend is after introducing these changes and is this
        trend statistically significant
        """)
    plot_password_sharing_crackdown_effect(df_netflix_data)
    st.markdown("""
        As you can see from the above graph this change seems to have the opposite effect from what was expected. The trend after 
        introducing the crackdown is positive indicating that the public bought more Netflix subscription after the crackdown was
        introduces
        """)
    st.image("Password Sharing Test.png")
    st.markdown("""
        A chow test was performed which tests if the values after a certain break point (in this case when the crack down began) 
        are significantly different compared tobefore it. As you can see although it is close the above p value is below the 5% 
        level of significance causing the null hypothesis that there is no difference between the subscription figures before
        and after the password sharing crackdown was introduced.

        This shows that although the public sentiment was against the decision the benefit of getting some people to buy their
        own account instead of sharing it with someone has offset the bad publicity from the decision.
        """)
    st.write("")
    st.write("")

def data_heatmap(df_data):
    correlation_matrix = df_data.corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='viridis', fmt=".2f")
    plt.title('Correlation Matrix Heatmap')
    st.pyplot(fig)

def plot_streaming_services_Q2Q_growth(df_data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Netflix Sub Change Q2Q'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Disney Sub Change Q2Q'], 
                             mode='lines+markers', 
                             name='Disney+',
                             line=dict(color='blue')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Hulu Sub Change Q2Q'], 
                             mode='lines+markers', 
                             name='Hulu',
                             line=dict(color='green')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Peacock Sub Change Q2Q'], 
                             mode='lines+markers', 
                             name='Peacock',
                             line=dict(color='black')))

    fig.update_layout(title_text='Quarterly Subscription Growth of Streaming Services',
                      xaxis_title='Quarter',
                      yaxis_title='Sub Increase in millions',
                      height=370,
                      showlegend=True)
 
    st.plotly_chart(fig)

def plot_total_subscriber_growth(df_data):
    fig = go.Figure()
    

    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Netflix Subscribers'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Disney+ Subscribers'], 
                             mode='lines+markers', 
                             name='Disney+',
                             line=dict(color='blue')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Hulu Subscribers'], 
                             mode='lines+markers', 
                             name='Hulu',
                             line=dict(color='green')))
    
    fig.add_trace(go.Scatter(x=df_data['Quarter'], 
                             y=df_data['Peacock Subscribers'], 
                             mode='lines+markers', 
                             name='Peacock',
                             line=dict(color='black')))
    
    fig.update_layout(title_text='Total Subscriber Growth for Streaming Services',
                      xaxis_title='Quarter',
                      yaxis_title='Subscribers in millions',
                      height=370,
                      showlegend=True)

    st.plotly_chart(fig)


import streamlit as st
import pandas as pd
from scipy.stats import spearmanr

def analyze_competition():
    st.write("### Competition Analysis")
    st.markdown("""
    Competition in the streaming marketplace has been rising in recent years with service like Disney+, Hulu and Peacock now 
    trying to compete with Netflix. We will investigate has this increased level of competition affected Netflix's subscriptions.
    """)
    df_data = pd.read_csv("Sub_Change_Summary.csv")
    columns_of_interest = ["Disney Sub Change Q2Q", "Netflix Sub Change Q2Q", "Hulu Sub Change Q2Q", "Peacock Sub Change Q2Q"]
    subset = df_data[columns_of_interest]
    data_heatmap(subset)
    st.markdown("""
    Our usual metric of quarter to quarter subscription increase does not give any promising results for how Netflix is 
    affected as all correlation coefficients for Netflix in the above correlation heat map above are close to 0 showing 
    they're not strongly correlated. We will expand to other variables such as total subscribers compared to quarterly 
    subscriber increase to see if there is any correlation.
    """)
    columns_to_keep = df_data.columns[df_data.columns != 'Quarter']
    subset = df_data[columns_to_keep]
    data_heatmap(subset)
    st.markdown("""
    The expanded correlation heat map above shows relationships between total quarterly subscribers as well as quarterly increase
    in subscribers for each service. The first interesting observation is that the total quarterly subscribers seems strongly
    positively correlated for each service as each coefficient is above 0.8.

    This indicates that an increase in one services subscribers tends to occur alongside an increase in subscribers for the other
    services and vice versa for decreases. This goes against how competition usually works where more people buying one service means
    less people use the other service. The Spearman Rank statistical test will now be performed to determine if it can be 
    confidently said that this correlation is significant and not random. Unfortunately this test can't be performed for 
    Peacock as it only has data from 21Q3 so due to more limited sample size the results would be unreliable.
    """)
    cc_ND, p_ND = spearmanr(df_data['Netflix Subscribers'], df_data['Disney+ Subscribers'])
    cc_NH, p_NH = spearmanr(df_data['Netflix Subscribers'], df_data['Hulu Subscribers'])
    cc_HD, p_HD = spearmanr(df_data['Hulu Subscribers'], df_data['Disney+ Subscribers'])
    st.write("**Total Subscribers Correlation Testing**")
    st.write("Netflix-Disney+ Test Statistic", cc_ND)
    st.write("p-value:", round(p_ND, 6))
    st.write("Netflix-Hulu Test Statistic:", cc_NH)
    st.write("p-value:", round(p_NH, 13))
    st.write("Hulu-Disney+ Test Statistic:", cc_HD)
    st.write("p-value:", round(p_HD, 6))
    st.write("")
    st.markdown("""
    The above Spearman Rank tests all gave p values less than a 5% significance level. This means that there is enough evidence
    to conclude that there is a significant non random association between the 2 variables. Although of course correlation does
    not equal causation it can be concluded that these variables tend to positively trend in the same direction in terms of
    total subscriber numbers.

    However another observation from the original heatmap is the reasonably strong negative correlation between Netflix
    Subscribers and Disney and Hulu sub change Q2Q of -0.74 and -0.75 respectively.
    """)
    columns_of_interest = ["Disney Sub Change Q2Q", "Hulu Sub Change Q2Q", "Netflix Subscribers"]
    subset = df_data[columns_of_interest]
    data_heatmap(subset)
    st.write("")
    st.markdown("""
    These negative correlations suggest that although the total subscriber numbers of these services are positively associated
    if Netflix is rapidly growing that can have a negative association with Netflix's competitors new quarterly subscribers figures. 
    The Spearman tests will show if there is a significant non random association between these variables.
    """)
    st.write("")
    cc_ND, p_ND = spearmanr(df_data['Netflix Subscribers'], df_data['Disney Sub Change Q2Q'])
    cc_NH, p_NH = spearmanr(df_data['Netflix Subscribers'], df_data["Hulu Sub Change Q2Q"])
    st.write("**Netflix Subscribers Vs Competitors Q2Q Increases Correlation Testing**")
    st.write("Netflix-Disney+ Q2Q Change Test Statistic", cc_ND)
    st.write("p-value:", round(p_ND, 6))
    st.write("Netflix-Hulu Q2Q Change Test Statistic:", cc_NH)
    st.write("p-value:", round(p_NH, 5))
    st.write("")
    st.markdown("""
    As both p values are below the 5% significance level we can conclude that there is a significant non random association 
    between Netflix Susbcribers and the other 2 variables. This is interesting as you'd assume Netflix subscribers being positively 
    correlated to other services total subscriber numbers and negatively association with the quarterly increase of other 
    services subscribers would be a contradiction. 
    """)
    plot_streaming_services_Q2Q_growth(df_data)
    plot_total_subscriber_growth(df_data)
    st.markdown("""
    The above graph shows that since 2020 each services total subscribers has been increasing and even with the slight downturn
    in new subscribers for Disney+ and Hulu the number of total subscribers has barely decreased compared to how many subscribers
    they already had. Since the trends has been usually positive throughout the years it makes sense that there is strong 
    positive correlation for total quarterly subscribers between each streaming service. This shows that since 2020 the 
    size of streaming market has grown massively which has positively benefitted all services involved.

    The quarter to quarter subscription increase numbers are clearly more variable as shown in the graph above. The recent 
    downturn in new subscribers in 2023 for Disney+ and Hulu obviously has a bigger effect on this metric and has caused it to 
    drop significantly. This has coincided with an increase in new subscribers for Netflix in 2023. Netflix's increase compared
    to Disney+ and Hulus decrease has understandably caused a negative correlation. This could possibly point to the market
    becoming more saturated in 2023 and new customers now only want to purchase one new streaming service which is usually 
    Netflix showing that Netflix is coming out on top in the streamer wars.

    It also must be acknowledged that correlation does not equal causation and these relationships could have other unseen factors
    which could be the cause of these trends. It will be interesting however to see if this trend continues and Disney+ and Hulu
    continue to struggle to gain new subscribers while Netflix thrives.
    """)

    
def main():

    st.sidebar.title("Navigation")
    # Create tabs in the sidebar
    tabs = ["Netflix Subscription Breakdown", "Genre Breakdown", "Region Breakdown", "Content Breakdown", "Users Breakdown", "Placeholder", "Competition Breakdown"]
    selected_tab = st.sidebar.radio("Select Analysis", tabs)

    if selected_tab == "Netflix Subscription Breakdown":
        # Placeholder for GitHub URL for subscription change over quarters data
        github_url = "https://github.com/mark-cotter/Graph_work/raw/d679935c202d14da6b62ef8eb2e9f0483f111f49/sub_change_Q2Q.csv"
        
        # Fetch data from GitHub for subscription change over quarters
        df_sub = fetch_data_from_github(github_url)
        if df_sub is not None:
            st.plotly_chart(create_subscription_growth_chart(df_sub))
            # Fetch data from GitHub for Netflix subscription breakdown
            df_netflix_data = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/69fd5b807a41c08b4e0a2559f8186a1050d17037/just_netflix_data.csv")
            if df_netflix_data is not None:
                st.plotly_chart(create_netflix_subscription_breakdown_chart(df_netflix_data))
                st.write("## Analysis")
                st.write("Analysis about how the most related variable to netflix seems to be Disney+.")
                st.plotly_chart(create_netflix_subscription_growth_chart(df_netflix_data, df_sub))

                # Plot Netflix stock growth
                plot_netflix_stock_growth(df_netflix_data)
                
            else:
                st.warning("Please provide the GitHub URL for Netflix subscription breakdown data.")
        else:
            st.warning("Please provide the GitHub URL for subscription change over quarters data.")

    elif selected_tab == "Placeholder":
        # Fetch data from GitHub for Netflix subscription breakdown
        df_netflix_data = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/69fd5b807a41c08b4e0a2559f8186a1050d17037/just_netflix_data.csv")
        if df_netflix_data is not None:
            plot_netflix_subscription_growth(df_netflix_data)
            st.markdown("""
            The above graph shows Netflix's subscription growth over time. Several analysis were performed about observations that
            could be gleaned from this graph. In the selection bar below select that topics that you would like to learn more about
            """)

            # Allow user to select which analyses to perform
            selected_analyses = st.multiselect("Select analyses to perform:", ["Q4 Analysis", "COVID-19 Analysis", "Price Hikes Analysis", "Password Sharing Crackdown Analysis"])
            st.write("")
            st.write("")
            # Call selected analyses based on user's selection
            if "Q4 Analysis" in selected_analyses:
                Q4_analysis(df_netflix_data)
            if "COVID-19 Analysis" in selected_analyses:
                Covid_19_Analysis(df_netflix_data)
            if "Price Hikes Analysis" in selected_analyses:
                Price_Hikes_Analysis(df_netflix_data)
            if "Password Sharing Crackdown Analysis" in selected_analyses:
                Password_Sharing_Crackdown_Analysis(df_netflix_data)

           
    elif selected_tab == "Competition Breakdown":
            analyze_competition()

    elif selected_tab == "Genre Breakdown":
        # Load genre breakdown data
        df_genre = pd.read_csv("Netflix_Genre_Breakdown.csv")
        # Remove commas from "Hours Viewed" and convert to integer
        df_genre["Hours Viewed"] = df_genre["Hours Viewed"].str.replace(",", "").astype(int)

        fig_genre_total_hours, fig_genre_comparison = create_genre_breakdown_charts(df_genre)
        st.plotly_chart(fig_genre_total_hours)
        st.plotly_chart(fig_genre_comparison)

    elif selected_tab == "Region Breakdown":
        # Fetch data from GitHub
        df_region = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/d2608fd649be8cd2367a4a5a8c694651766c14e3/netflix_region_breakdown.csv")
        if df_region is not None:
            st.plotly_chart(create_region_breakdown_chart(df_region))

    elif selected_tab == "Content Breakdown":
        # Load Netflix movie details data
        df_netflix_movies_data = pd.read_csv("Netflix_movie_details.csv")
        # Create mean duration graph
        mean_duration_fig = create_mean_duration_graph(df_netflix_movies_data)
        # Display the graph
        st.plotly_chart(mean_duration_fig)
    
    elif selected_tab == "Users Breakdown":
        # Load user data and create histogram
        df_users = pd.read_csv("Netflix Userbase.csv")
        fig_users_histogram = create_users_breakdown_histogram(df_users)
        st.plotly_chart(fig_users_histogram)

        # Add pie chart for gender distribution
        fig_gender_distribution = create_gender_distribution_pie_chart(df_users)
        st.plotly_chart(fig_gender_distribution)
        
        # Add pie chart for subscription type distribution
        fig_subscription_distribution = create_subscription_pie_chart(df_users)
        st.plotly_chart(fig_subscription_distribution)
        
        # Add bar chart for subscription revenue
        fig_subscription_revenue = create_subscription_revenue_bar_chart(df_users)
        st.plotly_chart(fig_subscription_revenue)

if __name__ == "__main__":
    main()
