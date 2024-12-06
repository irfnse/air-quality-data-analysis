import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import folium_static

sns.set(style="dark")

def get_most_polution(df):
    lat = [39.982056, 40.2161, 40.2944, 39.9292472, 39.9385, 39.9123, 40.3243, 39.9350, 40.1269, 39.8822, 39.9702, 39.9086]
    lon = [116.411233, 116.2347, 116.2167, 116.4177314, 116.3511, 116.1699, 116.6318, 116.4556, 116.6564, 116.4104, 116.3105, 116.3443]
    most_polution = df[["station","PM2.5","PM10","SO2","NO2","CO","O3","RAIN"]].groupby('station').mean()
    most_polution.reset_index(inplace=True)
    most_polution['lat'] = lat
    most_polution['lon'] = lon
    most_polution['max_v'] = most_polution[['PM2.5', 'PM10', 'O3']].max(axis=1)
    most_polution['max_c'] = most_polution[['PM2.5', 'PM10', 'O3']].max().idxmax()

    return most_polution

def get_color_and_quality(aqi):
    if aqi <= 50:
        return 'green', 'Good'
    elif aqi <= 100:
        return 'yellow', 'Moderate'
    elif aqi <= 150:
        return 'orange', 'Unhealthy for Sensitive Groups'
    elif aqi <= 200:
        return 'red', 'Unhealthy'
    elif aqi <= 300:
        return 'purple', 'Very Unhealthy'
    else:
        return 'maroon', 'Hazardous'

def get_corr_rain(df):
    corr_pm25 = round(df['RAIN'].corr(df['PM2.5']),2)
    corr_pm10 = round(df['RAIN'].corr(df['PM10']),2)
    corr_so2 = round(df['RAIN'].corr(df['SO2']),2)
    corr_no2 = round(df['RAIN'].corr(df['NO2']),2)
    corr_co = round(df['RAIN'].corr(df['CO']),2)
    corr_03 = round(df['RAIN'].corr(df['O3']),2)

    corr_rain = {'parameter': ['PM2.5','PM10','SO2','NO2','CO','O3'],
                'correlation': [corr_pm25,corr_pm10,corr_so2,corr_no2,corr_co,corr_03]}
    corr_rain_df = pd.DataFrame(corr_rain)
    
    return corr_rain_df.transpose()

def get_air_pollution(df):
    air_pollution = df[['date',"PM2.5","PM10","SO2","NO2","CO","O3","RAIN"]]
    air_pollution['date'] = pd.to_datetime(air_pollution['date'])
    air_pollution = air_pollution.set_index('date').resample('ME').mean()

    return air_pollution

def show_maps(df, ovr='all'):
    if ovr == "all":
        maps = folium.Map(location = [39.929986, 116.422867],zoom_start = 10)

        station_most = df.sort_values(by='max_v', ascending=False).reset_index(drop=True)

        for index, row in station_most.iterrows():
            if index == 0:
                dv = 2
            else:
                dv = index + 1
            rad = row['max_v']/dv

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=rad,
                color=get_color_and_quality(row['max_v'])[0],
                fill=True,
                fill_color=get_color_and_quality(row['max_v'])[0],
                fill_opacity=0.9,
                tooltip=folium.Tooltip(f"{row['station']} Station<br>PM2.5: {round(row['PM2.5'],2)}<br>PM10: {round(row['PM10'],2)}<br>O3: {round(row['O3'],2)}<br>{get_color_and_quality(row['max_v'])[1]}", permanent=False)
            ).add_to(maps)
    else:
        for index, row in df.iterrows():
            maps = folium.Map(location = [row['lat'], row['lon']],zoom_start = 13)
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=15,
                color=get_color_and_quality(row['max_v'])[0],
                fill=True,
                fill_color=get_color_and_quality(row['max_v'])[0],
                fill_opacity=0.9,
                tooltip=folium.Tooltip(f"{row['station']} Station<br>PM2.5: {round(row['PM2.5'],2)}<br>PM10: {round(row['PM10'],2)}<br>O3: {round(row['O3'],2)}<br>{get_color_and_quality(row['max_v'])[1]}", permanent=False)
            ).add_to(maps)

    folium_static(maps)

all_station_df = pd.read_csv('https://raw.githubusercontent.com/irfnse/air-quality-data-analysis/refs/heads/master/dashboard/all_station.csv')
station_most = get_most_polution(all_station_df)
air_pollution = get_air_pollution(all_station_df)

st.title("Air Quality in China Station")
tab1, tab2 = st.tabs(["Overall Average", "Average by Station"])
with tab1:
    st.header("Average Air Quality from 2013 to 2017")
    show_maps(station_most)

    st.subheader("PM2.5, PM10, and Rain Trend")
    st.line_chart(air_pollution[["PM2.5","PM10","RAIN"]])

    st.subheader("Average PM2.5, PM10, and Rain in China Station")
    most = station_most[["PM2.5","PM10","RAIN"]]
    st.write("Average PM2.5 and PM10 in China Station")
    st.bar_chart(station_most[["PM2.5","PM10","station"]].set_index('station'))
    st.write("Average Rain in China Station")
    st.bar_chart(station_most[["RAIN","station"]].set_index('station'))
    st.header("Correlation")
    corr_df = all_station_df[["PM2.5","PM10","SO2","NO2","CO","O3","RAIN"]]
    fig = px.imshow(round(corr_df.corr(),2))
    st.plotly_chart(fig)

    st.subheader("Rain vs Air Pollutants")
    st.table(get_corr_rain(corr_df))

with tab2:
    station = st.selectbox("",["Aotizhongxin","Changping","Dingling","Dongsi","Guanyuan","Gucheng","Huairou","Nongzhanguan","Shunyi","Tiantan","Wanliu","Wanshouxigong"])
    st.subheader("Average Air Quality {} Station from 2013 to 2017".format(station))
    station_most = station_most[station_most['station'] == station]
    show_maps(station_most,station)


    with st.container():
        cols1, cols2, cols3 = st.columns([1,1,3])
        with cols3:
            st.markdown(""" <div style="font-size:16px;">&nbsp</div> <div style="font-size:30px;">{} </div> """.format(get_color_and_quality(station_most.loc[0,'max_v'])[1]), unsafe_allow_html=True)
        cols3.metric("Most Polutant", station_most.loc[0,'max_c'])
        cols1.metric("PM2.5", round(station_most.loc[0,'PM2.5']))
        cols1.metric("O3", round(station_most.loc[0,'O3']))
        cols2.metric("PM10", round(station_most.loc[0,'PM10']))
        cols2.metric("NO2", round(station_most.loc[0,'NO2']))



    st.subheader("Air Pollution Trend")
    station_air = get_air_pollution(all_station_df[all_station_df['station'] == station])
    st.line_chart(station_air[['PM2.5','PM10','SO2','NO2','O3']])