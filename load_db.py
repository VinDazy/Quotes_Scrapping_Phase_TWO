import sqlite3
import json
import plotly.express as px
from streamlit_functions import *


class author:
    def __init__(self, author_id, author_name, author_link):
        self.author_id = author_id
        self.author_name = author_name
        self.author_link = author_link

    def __str__(self):
        return f"author_id : {self.author_id}, author_name: {self.author_name}, author_link : {self.author_link}"


class quote:
    def __init__(self, quote, quote_id, author_id):
        self.quote = quote
        self.quote_id = quote_id
        self.author_id = author_id

    def __str__(self) -> str:
        return f"quote_id : {self.quote_id}, author_id : {self.author_id}, quote : {self.quote}"


def getAuthorNamesFromTable():
    connection = sqlite3.connect("mydb.db")
    cur = connection.cursor()
    cur.execute("SELECT DISTINCT author_name FROM author")
    result = cur.fetchall()
    names = []
    for row in result:
        name = str(row[0])
        names.append(name)
    return names


def getAuthorQuotesFromTable(author_name):
    # Replace with your actual database filename
    connection = sqlite3.connect("mydb.db")
    cursor = connection.cursor()
    query = """
    SELECT q.quote
    FROM quote q
    JOIN author a ON q.author_id = a.author_id
    WHERE a.author_name = ?
    """
    cursor.execute(query, (author_name,))
    quotes = [row[0] for row in cursor.fetchall()]
    return quotes


def getAuthorBioLink(author_name):
    connection = sqlite3.connect('mydb.db')
    cursor = connection.cursor()
    query = """
    SELECT author_link
    FROM author
    where author_name=?
    """
    cursor.execute(query, (author_name,))
    result = cursor.fetchone()
    return result[0]


def getTagsFromTable():
    connection = sqlite3.connect("mydb.db")
    cursor = connection.cursor()
    tags = []
    query = """
    SELECT tag FROM tags
    """
    cursor.execute(query,)
    results = cursor.fetchall()
    for tag in results:
        tags.append(tag[0])
    return tags


def get_quotes_by_tags(tags, num_quotes):
    # Replace with your actual database filename
    connection = sqlite3.connect("mydb.db")
    cursor = connection.cursor()

    # Construct a query to retrieve quotes based on similar tags
    query = """
    SELECT DISTINCT q.quote
    FROM quote q
    JOIN tags_quotes tq ON q.quote_id = tq.quote_id
    JOIN tags t ON tq.tag_id = t.tag_id
    WHERE t.tag IN ({})
    LIMIT ?
    """.format(','.join(['?'] * len(tags)))

    cursor.execute(query, tags + [num_quotes])
    quotes = [row[0] for row in cursor.fetchall()]

    connection.close()

    return quotes, len(quotes)


def db_graph_tag_instance():
    # Replace with your actual database filename
    connection = sqlite3.connect("mydb.db")
    cursor = connection.cursor()

    # Construct a query to count tag instances
    query = """
    SELECT t.tag, COUNT(*) as instance_count
    FROM tags t
    JOIN tags_quotes tq ON t.tag_id = tq.tag_id
    GROUP BY t.tag
    ORDER BY instance_count DESC
    LIMIT 10
    """

    cursor.execute(query)
    tag_instances = cursor.fetchall()

    connection.close()

    tags = [tag for tag, _ in tag_instances]
    instances = [instance for _, instance in tag_instances]

    fig = px.bar(x=tags, y=instances, labels={'x': 'Tags', 'y': 'Instances'})
    fig.update_layout(
        title='Top 10 tags',
        height=500,
        width=650,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


def db_graph_author_quote():
    # Replace with your actual database filename
    connection = sqlite3.connect("mydb.db")
    cursor = connection.cursor()

    # Construct a query to get authors and their respective numbers of quotes
    query = """
    SELECT a.author_name, COUNT(*) as num_quotes
    FROM author a
    JOIN quote q ON a.author_id = q.author_id
    GROUP BY a.author_name
    ORDER BY num_quotes DESC
    LIMIT 10
    """

    cursor.execute(query)
    author_quotes = cursor.fetchall()

    connection.close()

    authors = [author for author, _ in author_quotes]
    num_quotes = [num_quotes for _, num_quotes in author_quotes]

    fig = px.bar(x=authors, y=num_quotes, labels={
                 'x': 'Authors', 'y': 'Number of Quotes'})
    fig.update_layout(
        title=f'Top {len(authors)} Authors',
        height=500,
        width=650,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def insert_author(author: author):
    con = sqlite3.connect("mydb.db")
    cursor = con.cursor()
    with con:
        cursor.execute("INSERT INTO author VALUES (?, ?, ?)",
                       (author.author_id, author.author_name, author.author_link))


def insert_quote(quote: quote):
    with con:
        cursor.execute("INSERT INTO quote VALUES (?, ?, ?)",
                       (quote.quote, quote.quote_id, quote.author_id))


def create_author_instances(data_dict):
    author_instances = []
    author_id_counter = 1

    for quote_id, quote_data in data_dict.items():
        author_name = quote_data['author']
        author_link = quote_data['author_bio']

        # Check if the author already exists in the list of author instances
        existing_author = next(
            (author for author in author_instances if author.author_name == author_name), None)

        if existing_author is None:
            # Create a new instance of the Author class for the distinct author
            new_author = author(author_id=author_id_counter,
                                author_name=author_name, author_link=author_link)
            author_instances.append(new_author)
            author_id_counter += 1

    return author_instances


def create_quote_instances(data_dict):
    quote_instances = []
    quote_id_counter = 1
    for quote_id, quote_data in data_dict.items():
        author_name = quote_data['author']

        # Fetch the author_id from the "author" table based on the author_name
        cursor.execute(
            "SELECT author_id FROM author WHERE author_name=?", (author_name,))
        result = cursor.fetchone()

        if result is None:
            # If the author is not found in the "author" table, you can handle it accordingly
            # For now, we'll simply skip this quote
            continue

        author_id = result[0]

        # Create a new instance of the Quote class and add it to the quote_instances list
        new_quote = quote(
            quote=quote_data['quote'], quote_id=quote_id_counter, author_id=author_id)
        quote_instances.append(new_quote)
        quote_id_counter += 1
    return quote_instances


def fill_tags_table():
    with con:
        with open("tags.txt", 'r') as f:
            tag_id = 1
            for word in f:
                word = word.strip()
                cursor.execute(
                    "INSERT INTO tags VALUES (?, ?)", (word, tag_id))
                tag_id += 1


def fill_tags_quotes_table(data_dict):
    with con:
        for quote_data in data_dict.values():
            quote_text = quote_data['quote']
            quote_id = get_quote_id(quote_text)

            if quote_id is not None:
                tags = quote_data['tags']
                for tag in tags:
                    tag_id = get_tag_id(tag)

                    if tag_id is not None:
                        cursor.execute(
                            "INSERT INTO tags_quotes VALUES (?, ?)", (tag_id, quote_id))


def fill_author_table(data_dict):
    for author_instance in create_author_instances(data_dict):
        insert_author(author_instance)


def fill_quote_table(data_dict):
    for quote_instance in create_quote_instances(data_dict):
        insert_quote(quote_instance)

def FILL_DATA_BASE(pages_number):
    import os 
    file_path = "mydb.db"
    if not os.path.exists(file_path):
         con = sqlite3.connect("mydb.db")
         cursor = con.cursor()

         cursor.execute(
         """
            CREATE TABLE author(
            author_id integer,
            author_name string,
            author_link text
            )
         """)
         cursor.execute(
         """
            CREATE TABLE quote(
            quote text,
            quote_id integer,
            author_id integer
            )
         """)


         cursor.execute(
         """
            CREATE TABLE tags(
            tag text,
            tag_id integer
            )
         """)
         cursor.execute(
         """
            CREATE TABLE tags_quotes(
            tag_id integer,
            quote_id integer
            )
         """)
         data_dict=st_scrape(pages_number)
         fill_author_table(data_dict=data_dict)
         fill_quote_table(data_dict=data_dict)
         fill_tags_table()
         fill_tags_quotes_table(data_dict=data_dict)

def get_tag_id(tag):
    cursor.execute("SELECT tag_id FROM tags WHERE tag=?", (tag,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return None



def get_quote_id(quote_text):
    cursor.execute("SELECT quote_id FROM quote WHERE quote=?", (quote_text,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    else:
        return None






