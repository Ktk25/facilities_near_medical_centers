import streamlit as st

from google_maps_cient import GoogleMapsClient, GOOGLE_API_KEY

def main():

    st.title("Facility Features App")

    facility = st.text_input('Type the name of Facility', 'Forest General Hospital Mississippi')

    radius   = st.selectbox('Select the Radius in Miles',
                            (1, 2, 3, 4, 5, 10, 15, 20, 30, 50, 100, 200))

    radius_meters = radius * 1609.34

    client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address_or_postal_code=facility)

    places = ['Places to Stay', 'Hospitals', 'Restaurants', 'Car Parkings', 'Malls',
              'Markets', 'Parks', 'Daycare', 'Beach']

    tabs   = st.tabs(places)

    for i, place in enumerate(places):
        with tabs[i]:
            place_df = client.search(place, radius=radius_meters)
            st.dataframe(place_df, use_container_width=True)
            lat_lng_df = place_df[['LAT', 'LON']]
            st.map(lat_lng_df)

if __name__ == '__main__':
    main()