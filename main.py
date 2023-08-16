import streamlit as st
from streamlit_functions import *
from load_db import *
import time 


st.set_page_config(page_title="Quotes Scrapping ",layout="wide", page_icon="💾")
hide_menu_style="""
<style>

footer {visibility: hidden;}
</style> 
"""
st.markdown(hide_menu_style,unsafe_allow_html=True)
st.header("Quotes Scrapping Phase-Two")
pages_form=st.form(key="input")

with pages_form :
    pages_number=pages_form.slider("Number of pages to scrape",value=1,max_value=10,min_value=1)
    scrape=pages_form.form_submit_button("Scrape")
    @st.cache_data
    def scrape_data(pages_number):
        FILL_DATA_BASE(pages_number)
        with st.spinner('Gathering resources...'):
                    time.sleep(2)
    scrape_data(pages_number)
    if scrape:
        data_dict=scrape_data(pages_number)
author_form=st.form(key="author")
author_name=author_form.selectbox("Author name",options=getAuthorNamesFromTable())
display=author_form.form_submit_button("Display author information")
with author_form:
    quotes,image,link=author_form.columns(3)
    if display:
        with quotes:
            quotes.subheader(f"{author_name} Quotes")
            for quote in getAuthorQuotesFromTable(author_name=author_name):
                quotes.write(quote)
        with image:
            image.subheader(f'{author_name} Image')
            edited_author_name=author_name.replace(" ",'_')
            st_scrape_image(author_name,image)
        with link:
            link.subheader(f"{author_name} Link")
            link.write(getAuthorBioLink(author_name=author_name))
quotes_form=st.form(key="quote")

input_form,output_column=quotes_form.columns(2)
display_quotes=quotes_form.form_submit_button("Display Quotes")
with input_form:
    tags = input_form.multiselect("Select the tag(s)", options=getTagsFromTable())
    number = input_form.number_input("Number of quotes to display", min_value=1, max_value=100)

if display_quotes:
    with output_column:
        quotes, num = get_quotes_by_tags(tags=tags, num_quotes=number)
        if num==0:
            output_column.error("Sorry, we could not find any quotes containing similar tags. Please try different tags")
        elif num<number:
            output_column.warning(f"Sorry we could only find {num} matching quotes")
        for quote in quotes:
            output_column.write(quote)

graph_form=st.form(key="graph")
tags_instances,author_quotes=graph_form.columns(2)
display_graph=graph_form.form_submit_button("Display Graphs")
if display_graph:
    with tags_instances:
        fig=db_graph_tag_instance()
        tags_instances.plotly_chart(fig)
    with author_quotes:
        figg=db_graph_author_quote()
        author_quotes.plotly_chart(figg)


    







