import streamlit as st
import pandas as pd
import pickle
import requests
import pycountry
import json
import altair as alt
from streamlit_option_menu import option_menu
import time

url = 'http://localhost:11434/api/chat'
headers = {'Content-Type': 'application/json'}

model = pickle.load(open('model/model_rf.pkl', 'rb'))

def classify_air_quality(value, unit):
    if unit == 'ppm':
        if value < 50:
            return 'Healthy'
        elif value < 100:
            return 'Normal'
        else:
            return 'Unhealthy'
    else:
        return 'Tidak Diketahui'

def create_prompt(hasil_prediksi, country):
    if hasil_prediksi == 'Healthy':
        prompt = f"""Berikan kegiatan yang cocok dilakukan saat kualitas udara {hasil_prediksi} di {country}.
        
        Hasil Prediksi Udara adalah {hasil_prediksi}.
        
        Buat menjadi singkat dan komunikatif, dalam bahasa indonesia dan maksimum 300 karakter. dengan frasa pertama selalu dimulai dengan
        'Hasil klasifikasi udara di {country} menunjukkan kualitas {hasil_prediksi}'
        """
    elif hasil_prediksi == 'Normal':
        prompt = f"""Berikan kegiatan yang cocok dilakukan saat kualitas udara {hasil_prediksi} di {country}. jelaskan juga saran kesehatan pada saat beraktivitas di kondisi udara yang {hasil_prediksi}. Ingatkan agar selalu tetap menjaga kesehatan
        
        Hasil Prediksi Udara adalah {hasil_prediksi}.
        
        Buat menjadi singkat dan komunikatif, dalam bahasa indonesia dan maksimum 300 karakter. dengan frasa pertama selalu dimulai dengan
        'Hasil klasifikasi udara di {country} menunjukkan kualitas {hasil_prediksi}'
        """
    else:
        prompt = f"""Berikan penjelasan mengenai dampak dan penyakit yang mungkin terjadi pada kesehatan manusia jika terpapar polusi udara dengan kualitas {hasil_prediksi}.
        
        Hasil Prediksi Udara adalah {hasil_prediksi}.
        
        Buat menjadi singkat dan komunikatif, dalam bahasa indonesia dan maksimum 300 karakter. dengan frasa pertama selalu dimulai dengan
        'Hasil klasifikasi udara di {country} menunjukkan kualitas {hasil_prediksi}'
        """
    
    sent_json = {"model": "llama3",
                 "messages": [{"role": "user", "content": prompt}],
                 "stream": True
                }
    return sent_json

def prediction_air_quality(temp, humidity, ppm):
    prediction = model.predict([[temp, humidity, ppm]])
    return prediction[0]

def stream_response(response):
    response_text = ""
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            try:
                json_response = json.loads(decoded_line)
                if "message" in json_response:
                    response_text += json_response["message"]["content"]
                    yield json_response["message"]["content"]
            except json.JSONDecodeError:
                pass
    yield response_text

def animate_typing(placeholder, text, delay=0.05):
        for i in range(len(text) + 1):
                placeholder.markdown(text[:i])
                time.sleep(delay)

def main():
    try:
        df = pd.read_csv('dataset/world_air_quality_fix.csv')
        df['Klasifikasi Kualitas Udara'] = df.apply(lambda row: classify_air_quality(row['Value'], row['Unit']), axis=1)
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return
    
    # Sidebar menu
    with st.sidebar:
        selected = option_menu(
            "Menu",
            ["Home", "Air Quality Monitor", "Test Sensor", "Profile"],
            icons=["house","bar-chart", "thermometer", "person-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # Home page
    if selected == "Home":
        st.title("Dashboard Kualitas Udara Dunia")
        st.header("Informasi Kualitas Udara")
        st.write("""
        Kualitas udara adalah ukuran seberapa bersih atau tercemarnya udara di suatu lokasi. 
        Polusi udara dapat berdampak negatif pada kesehatan manusia, hewan, dan tumbuhan.
        
        Berikut adalah klasifikasi kualitas udara berdasarkan jenis polutan yang digunakan pada aplikasi ini:
        
        - **Healthy:** Udara bersih dan tidak berdampak negatif terhadap kesehatan.
        - **Normal:** Udara yang kualitasnya cukup baik, tetapi mungkin sedikit berdampak pada kesehatan kelompok sensitif.
        - **Unhealthy:** Udara tercemar dan dapat menyebabkan dampak kesehatan pada sebagian besar populasi.
        
        Unit pengukuran polutan udara:
        - **ppm (parts per million):** Digunakan untuk mengukur konsentrasi gas polutan.
        """)

    # Air Quality Monitor page
    elif selected == "Air Quality Monitor":
        st.title("World Air Quality Monitor")
        
        sorted_countries = df['Country Label'].sort_values().unique()
        country = st.selectbox('Pilih Negara', sorted_countries)
        country_data = df[df['Country Label'] == country]
        
        st.dataframe(country_data[['City', 'Location', 'Pollutant', 'Value', 'Unit', 'Klasifikasi Kualitas Udara']])
        air_quality_summary = country_data['Klasifikasi Kualitas Udara'].value_counts()
        st.write('Ringkasan Kualitas Udara:')
        st.bar_chart(air_quality_summary)
        
        city = st.selectbox('Pilih Kota', country_data['City'].unique())
        city_data = country_data[country_data['City'] == city]
        
        st.write(f'Detail Kualitas Udara di {city}:')
        st.dataframe(city_data[['Pollutant', 'Value', 'Unit', 'Klasifikasi Kualitas Udara']])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Country Label:O', sort=None),
            y='count():Q',
            color='Klasifikasi Kualitas Udara:N',
            tooltip=['Country Label:N', 'count():Q', 'Klasifikasi Kualitas Udara:N']
        ).properties(
            title='Jumlah Data Kualitas Udara Berdasarkan Negara'
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

    # Test Sensor page
    elif selected == "Test Sensor":
        st.title("Test Sensor")
        st.header("Hasil Pembacaan Sensor")

        response = requests.get('http://IP4_ADDRESS:5000/get-data')
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
        else:
            st.error("Gagal mengambil data dari server")
            return

        selected_data = df.iloc[-1]
        st.write("Data :")
        st.write(selected_data)

        countries = [country.name for country in pycountry.countries]
        country = st.selectbox('Pilih Negara', countries)

        if st.button("Predict"):
            temp = selected_data['temp']
            humidity = selected_data['humidity']
            ppm = selected_data['ppm']
            result = prediction_air_quality(temp, humidity, ppm)
            
            if result == 'healthy':
                st.success(f"Kualitas Udara: {result}")
            elif result == 'normal':
                st.warning(f"Kualitas Udara: {result}")
            else:
                st.error(f"Kualitas Udara: {result}")
            
            with st.spinner("Mohon Tunggu Saran Kesehatan"):
                response = requests.post(url, json=create_prompt(result, country), headers=headers, stream=True)

                if response.status_code == 200:
                    placeholder = st.empty()
                    final_response = ""
                    for content in stream_response(response):
                        animate_typing(placeholder, content)
                        final_response += content

                else:
                    st.write("Server sedang dalam gangguan")

    # Profile page
    elif selected == "Profile":
        st.title("Profile Pengembang Aplikasi")
        st.header("Pengembang 1 👩🏻‍💻")
        st.write("""
        Nama: Adinda Rizki Sya'bana Diva
        
        Peran: Data Scientist
                
        Deskripsi: Bertanggung jawab dalam analisis data dan pembuatan model prediksi kualitas udara.
        """)

        st.header("Pengembang 2 👩🏻‍💻")
        st.write("""
        Nama: Salwa Nafisa
                
        Peran: Frontend Developer
                
        Deskripsi: Bertanggung jawab dalam desain antarmuka pengguna dan pengembangan fitur interaktif.
        """)

        st.header("Pengembang 3 👨🏻‍💻")
        st.write("""
        Nama: Rahman Ilyas Al Kahfi
                
        Peran: Backend Developer dan IOT Engineer
                
        Deskripsi: Bertanggung jawab dalam pengelolaan database, server, dan integrasi data ke dalam aplikasi. Selain itu Membuat Rangkaian IoT.
        """)


if __name__ == '__main__':
    main()
