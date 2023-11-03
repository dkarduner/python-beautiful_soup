# B"H 
# script to get nytimes best sellers book for 2021-2022 (104 weeks)

import requests, json, codecs
from bs4 import BeautifulSoup
from datetime import date, timedelta

#creating dates for requests
weeks = []
_date = date(2021, 1, 3)
weeks.append(_date)
while True:
    _date += timedelta(days=7)
    if _date.year == 2023:
        break
    else:
        weeks.append(_date)

best_seller_node = []
for week_number, _date in enumerate(weeks):
    week_data = {}
    week_data["week"] = week_number + 1
    week_data["data"] = []

    _year = str(_date.year)
    _month = str(_date.month).zfill(2)
    _day = str(_date.day).zfill(2)
    _endpoint = f"https://www.nytimes.com/books/best-sellers/{_year}/{_month}/{_day}/"
    
    #requesting data from nytimes
    r = requests.get(_endpoint)
    soup = BeautifulSoup(r.text, "html.parser")
    script_tags = soup.find_all('script')
    
    for st in script_tags:
        st = st.text
        if st.find('BestSellerBookListsConnection') > 0:
            
            # parsing data - deleting/transforming non-readable characters
            st = st.replace("window.__preloadedData = ","")
            st = st.replace(";","")
            st = st.replace("'","")
            st = "".join(c for c in st if ord(c)<128)    
            st = st.encode().decode('unicode-escape')
            st = st.encode().decode('utf-8')
            st = st.replace('undefined', '""')      
            st = st.replace('false', '""')
            st = st.replace('true', '""')
            st = st.replace('null', '""')
            st = st.replace('""""', '""')
            
            #saving data to file
            with open('data.json','w') as file:
                file.write(st)
            
            try:
                # loading saved data as .json from file
                with open('data.json') as f:
                    books_data_dict = json.load(f)      

                    for edge in books_data_dict['initialData']['data']['bestsellers']['overview']['bookLists']['edges']:
                        _data_node = {}
                        _data_node["category"] = edge['node']['displayName']
                        _data_node["book"] = []

                        for i, inner_edges in enumerate(edge['node']['books']['edges']):
                            _node_book = {}
                            _node_book['title'] = inner_edges['node']['title']
                            _node_book['imageUrl']= inner_edges['node']['imageUrl']
                            _node_book['position'] = i+1
                            _node_book['description'] = inner_edges['node']['description']
                            _data_node["book"].append(_node_book)

                    week_data["data"].append(_data_node)
                    print(f"Data from week: {week_number + 1} - {_date} extracted ok", "\n")
                    break
                    
            except:
                print(f"** Cannot parse data from week: {week_number + 1} - {_date}", "\n")
    
    # append each week data to best sellers list
    best_seller_node.append(week_data)

# generating output file
_output_dict = {}
_output_dict["best_seller"] = best_seller_node
with open("best_sellers_2022-2023.json", "w") as out_file:
    json.dump(_output_dict, out_file, indent = 4)
    
print("Output file generated: best_sellers_2021-2022.json")
