import streamlit as st
import pandas as pd
import re


def vtt_time_to_seconds(vtt_time):
    time_parts = re.split(r'[:,.]', vtt_time)
    if len(time_parts) == 4:
        h, m, s, ms = map(float, time_parts)
        return h * 3600 + m * 60 + s + ms / 1000
    elif len(time_parts) == 3:
        m, s, ms = map(float, time_parts)
        return m * 60 + s + ms / 1000
    else:
        raise ValueError(f"Unexpected time format: {vtt_time}")


def parse_vtt(vtt_content):
    lines = vtt_content.split('\n')
    data = []
    i = 0

    while i < len(lines):
        if '-->' in lines[i]:
            time_line = lines[i]
            text_line = lines[i + 1] if (i + 1) < len(lines) else ""

            try:
                start_time, end_time = time_line.split(' --> ')
                start_seconds = vtt_time_to_seconds(start_time)
                end_seconds = vtt_time_to_seconds(end_time)

                if ': ' in text_line:
                    speaker, text = text_line.split(': ', 1)
                else:
                    speaker, text = 'Unknown', text_line

                data.append([start_seconds, end_seconds, speaker, text])
                i += 2
            except ValueError as e:
                st.error(f"Error processing line {i}: {e}")
                i += 1
        else:
            i += 1

    return pd.DataFrame(data, columns=['start', 'end', 'speaker', 'text'])


st.title('VTT to CSV Converter')

uploaded_file = st.file_uploader('Upload a VTT file', type='vtt')

if uploaded_file is not None:
    vtt_content = uploaded_file.getvalue().decode('utf-8')
    df = parse_vtt(vtt_content)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Download CSV',
        data=csv,
        file_name='output.csv',
        mime='text/csv'
    )

    st.write('Preview of the CSV file:')
    st.dataframe(df)
