import os 
import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import plotly.figure_factory as ff
warnings.filterwarnings('ignore')
st.set_page_config("Super Store",page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Dashboard")
st.markdown('<style>div.block-container{padding: 3rem;}</style>',unsafe_allow_html=True)
f1 = st.file_uploader(" :file_folder: Upload your file", type=["csv", "xlsx","xls"], key="file_uploader1")

if f1 is not None:
    # filename = f1.name
    st.info(f"File uploaded: {f1.name}")
    if f1.name.endswith('.csv'):
        df = pd.read_csv(f1)
    else:
        df = pd.read_excel(f1)
    
    # st.dataframe(df)
    st.subheader("Data Overview")
    st.dataframe(df.head())
    # st.dataframe(df.dtypes)
        
    col1, col2 = st.columns((2))

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    # st.dataframe(pd.to_datetime(df["Order Date"], errors='coerce'))


    start_date = df["Order Date"].min()
    end_date = df["Order Date"].max()

    with col1:
        start = pd.to_datetime(st.date_input("Start Date", start_date))
    with col2:
        end = pd.to_datetime(st.date_input("End Date", end_date))


    df = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)].copy()

    st.sidebar.header("CHOOSE FILTER :mag:")

    unique_regions= df["Region"].unique()
    unique_states = df["State"].unique()
    unique_cities = df["City"].unique()
    # st.sidebar.subheader("Pick the region")
    st.sidebar.markdown("""<h3 style = 'text-align: left; padding:10px ;position:absolute;top:10px;left:0px'>Pick the region</h3>  <div style="margin-top: 25px;"></div> """, unsafe_allow_html=True)
    region = st.sidebar.multiselect("",unique_regions,key="regions")

    if region is not None and len(region) > 0:   # region
        df2 = df[df["Region"].isin(region)]

    else:
        df2 = df.copy()

    st.sidebar.markdown("""<h3 style = 'text-align: left; padding:10px ;position:absolute;top:10px;left:0px'>Pick the state</h3>  <div style="margin-top: 25px;"></div> """, unsafe_allow_html=True)
    state = st.sidebar.multiselect("",unique_states,key="states")

    if state is not None and len(state) > 0:   # state
        df3 = df2[df2["State"].isin(state)]
    else:
        df3 = df2.copy()



    # Filter Data based on region and state and city

    st.sidebar.markdown("""<h3 style = 'text-align: left; padding:10px ;position:absolute;top:10px;left:0px'>Pick the city</h3>  <div style="margin-top: 25px;"></div> """, unsafe_allow_html=True)
    city = st.sidebar.multiselect("",unique_cities,key="cities")


    #Filerting part 
    filtered_data = df.copy()
    # It is possible that user may not select any region, state or city
    # Multiselect returns [] when nothing is selected, so check with `not ...`
    if not region and not state and not city:
        # st.success("Here I am nothing here")
        filtered_data = df.copy()

    elif region and not state and not city:   # Only region selected
        filtered_data = df2.copy()

    elif not region and state and not city:  # Only state selected
        filtered_data = df3.copy()

    elif not region and not state and city:  # Only city selected
        filtered_data = df[df["City"].isin(city)]

    elif region and state and not city:  # Region + state

        filtered_data = df3.copy()

    elif region and not state and city:  # Region + city
        filtered_data = df2[df2["City"].isin(city)]

    else:  # Either State + City or Region + State + City
        filtered_data = df3[df3["City"].isin(city)]    


    category_df = filtered_data.groupby(by=["Category"],as_index=False)["Sales"].sum()
    # st.dataframe(category_df)
    # st.dataframe(filtered_data)
    # st.dataframe(df2)
    # st.dataframe(df3)


    with col1:
        st.subheader("Category wise Sales")
        fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 200)

    with col2:
        st.subheader("Region wise Sales")
        fig = px.pie(filtered_data, values = "Sales", names = "Region", hole = 0.5)
        fig.update_traces(text = filtered_data["Region"], textposition = "outside")
        st.plotly_chart(fig,use_container_width=True)
    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Category_ViewData"):
            # st.write(category_df.style.background_gradient(cmap="Blues"))
            st.write(category_df)
            csv = category_df.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                                help = 'Click here to download the data as a CSV file')

    with cl2:
        with st.expander("Region_ViewData"):
            region = filtered_data.groupby(by = "Region", as_index = False)["Sales"].sum()
            # st.write(region.style.background_gradient(cmap="Oranges"))
            st.write(region)
            csv = region.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                            help = 'Yo vro Click here to download the data as a CSV file')    

    # time seroies analysos

    st.subheader("Time Series Analysis")
    filtered_data["year-month"] = filtered_data["Order Date"].dt.strftime("%Y : %b")
    # st.dataframe(filtered_data)
    filterdf = filtered_data.groupby(filtered_data["year-month"], as_index=False)["Sales"].sum()
    filterdf["Sales"] = filterdf["Sales"].round(2)
    # st.dataframe(filterdf)
    pxline = px.line(filterdf, x="year-month", y="Sales", markers=True, template="seaborn")

    st.plotly_chart(pxline, use_container_width=True)

    st.subheader("Tree Map")
    fig3 = px.treemap(filtered_data, path=["Region","Category","Sub-Category"], values="Sales",
                    color="Sales", hover_data=["Sales","Profit"], template="seaborn")
    fig3.update_layout(width=800, height=600)
    st.plotly_chart(fig3, use_container_width=True)

    chart1,chart2 = st.columns((2))

    with chart1:
        st.subheader("Segment by Sales")
        figsegment = px.pie(filtered_data,values="Sales",names="Segment",hole=0.3,template="plotly_dark")
        figsegment.update_traces(text=filtered_data["Segment"], textposition="outside")
        st.plotly_chart(figsegment, use_container_width=True)
        
    with chart2:
        st.subheader("Cateogary wise Sales")
        figcategory = px.pie(filtered_data,values="Sales",names="Category",hole=0.3,template="plotly_dark")
        figcategory.update_traces(text=filtered_data["Category"], textposition="outside")
        st.plotly_chart(figcategory, use_container_width=True)


    st.subheader(":point_right: Month wise Sub-Category Sales Summary")

    with st.expander("Summary_Table"):
        df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
        fig = ff.create_table(df_sample, colorscale = "Cividis")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("Month wise sub-Category Table")
        filtered_data["month"] = filtered_data["Order Date"].dt.month_name()
        sub_category_Year = pd.pivot_table(data = filtered_data, values = "Sales", index = ["Sub-Category"],columns = "month")
        st.dataframe(sub_category_Year)


    data1 = px.scatter(filtered_data, x = "Sales", y = "Profit", size = "Quantity")
    data1.update_layout(
        title=dict(
            text="Relationship between Sales and Profits using Scatter Plot.",
            font=dict(size=20)
        ),
        xaxis=dict(
            title=dict(
                text="Sales",
                font=dict(size=19)
            )
        ),
        yaxis=dict(
            title=dict(
                text="Profit",
                font=dict(size=19)
            )
        )
    )

    st.plotly_chart(data1,use_container_width=True)


    with st.expander("View Data"):
        st.write(filtered_data.iloc[:500,1:20:2])

    # Download orginal DataSet
    csv = df.to_csv(index = False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv",help= 'Click here to download the data as a CSV file')
