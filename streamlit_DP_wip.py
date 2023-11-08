import pandas as pd

import nzpy

import streamlit as st

# Enter your own netezza login credentials
dbConnectUser = 'jrodenberg'
dbConnectPswd = 'Triangle123!'
db = 'EDW_LANDING'

def getDepartments():
    # Initialize/open connection
    conn = nzpy.connect(user=dbConnectUser, password = dbConnectPswd, host='edwprd.basspro.net',port=5480,database=db,securityLevel=1,logLevel=0)
    
    # Get all departments with active or new SKUs
    departmentsQuery = f'''
    SELECT DISTINCT DEPARTMENT_MEMBER_NUMBER || '-' || DEPARTMENT_NAME AS DEPT
         , DEPARTMENT_MEMBER_NUMBER
    FROM EDW_SPOKE.NZ.DIM_PRODUCT_BPS PD
    WHERE SKU_DISPOSITION_CODE IN ('A','N')
      AND DEPARTMENT_MEMBER_NUMBER < 850
    GROUP BY 1,2
    HAVING DEPT IS NOT NULL
    ORDER BY 2
    '''
    df = pd.read_sql(departmentsQuery, conn)

    conn.close()
    return df['DEPT'].to_list()

def getSubDepartments(departmentNums):
    # Initialize/open connection
    conn = nzpy.connect(user=dbConnectUser, password = dbConnectPswd, host='edwprd.basspro.net',port=5480,database=db,securityLevel=1,logLevel=0)
    
    # Get all sub departments with active or new SKUs in selected hierarchy
    query = f'''
    SELECT DISTINCT SUB_DEPARTMENT_MEMBER_NUMBER || '-' || SUB_DEPARTMENT_NAME AS SUB_DEPTS
         , SUB_DEPARTMENT_MEMBER_NUMBER
    FROM EDW_SPOKE.NZ.DIM_PRODUCT_BPS
    WHERE DEPARTMENT_MEMBER_NUMBER IN ( '''
    for index in range(0, len(departmentNums)-1):
        query += f''' '{departmentNums[index]}','''
    query += f''' '{departmentNums[-1]}' '''
    query += f''' )
    AND SUB_DEPARTMENT_NAME IS NOT NULL
    AND SUB_DEPARTMENT_MEMBER_NUMBER IS NOT NULL
    AND DEPARTMENT_MEMBER_NUMBER < 850
    AND SKU_DISPOSITION_CODE IN ('A','N')
    GROUP BY 1,2
    ORDER BY 2;
    '''

    # Print code if checkbox is selected
    if st.session_state.CSwitch:
        st.divider()
        st.code(query)
    
    df = pd.read_sql(query, conn)

    conn.close()
    return df['SUB_DEPTS'].to_list()

def getClasses(departmentNums, subDepartmentNums):
    # Initialize/open connection
    conn = nzpy.connect(user=dbConnectUser, password = dbConnectPswd, host='edwprd.basspro.net',port=5480,database= db,securityLevel=1,logLevel=0)
    
    # Get all classes with active or new SKUs in selected hierarchy
    query = f'''
    SELECT DISTINCT CLASS_MEMBER_NUMBER || '-' || CLASS_NAME AS CLASSES
         , CLASS_MEMBER_NUMBER
    FROM EDW_SPOKE.NZ.DIM_PRODUCT_BPS
    WHERE DEPARTMENT_MEMBER_NUMBER IN ( '''
    for index in range(0, len(departmentNums)-1):
        query += f''' '{departmentNums[index]}','''
    query += f''' '{departmentNums[-1]}' '''
    query += f''' )
    AND SUB_DEPARTMENT_MEMBER_NUMBER IN ( '''
    for index in range(0, len(subDepartmentNums)-1):
        query += f''' '{subDepartmentNums[index]}','''
    query += f''' '{subDepartmentNums[-1]}' '''
    query += f''' )
    AND CLASS_NAME IS NOT NULL
    AND CLASS_MEMBER_NUMBER IS NOT NULL
    AND DEPARTMENT_MEMBER_NUMBER < 850
    AND SKU_DISPOSITION_CODE IN ('A','N')
    GROUP BY 1,2
    ORDER BY 2;
    '''

    # Print code if checkbox is selected
    if st.session_state.CSwitch:
        st.divider()
        st.code(query)
    
    df = pd.read_sql(query, conn)

    conn.close()
    return df['CLASSES'].to_list()

def getSubClasses(departmentNums, subDepartmentNums, classNums):
    # Initialize/open connection
    conn = nzpy.connect(user=dbConnectUser, password = dbConnectPswd, host='edwprd.basspro.net',port=5480,database=db,securityLevel=1,logLevel=0)
    
    # Get all sub classes with active or new SKUs in selected hierarchy
    query = f'''
    SELECT DISTINCT SUB_CLASS_DISPLAY_NUMBER || ' - ' || SUB_CLASS_NAME AS SUB_CLASSES
         , SUB_CLASS_MEMBER_NUMBER
    FROM EDW_SPOKE.NZ.DIM_PRODUCT_BPS
    WHERE DEPARTMENT_MEMBER_NUMBER IN ( '''
    for index in range(0, len(departmentNums)-1):
        query += f''' '{departmentNums[index]}','''
    query += f''' '{departmentNums[-1]}' '''
    query += f''' )
    AND SUB_DEPARTMENT_MEMBER_NUMBER IN ( '''
    for index in range(0, len(subDepartmentNums)-1):
        query += f''' '{subDepartmentNums[index]}','''
    query += f''' '{subDepartmentNums[-1]}' '''
    query += f''' )
    AND CLASS_MEMBER_NUMBER IN ( '''
    for index in range(0, len(classNums)-1):
        query += f''' '{classNums[index]}','''
    query += f''' '{classNums[-1]}' '''
    query += f''' )
    AND SUB_CLASS_NAME IS NOT NULL
    AND SUB_CLASS_MEMBER_NUMBER IS NOT NULL
    AND DEPARTMENT_MEMBER_NUMBER < 850
    AND SKU_DISPOSITION_CODE IN ('A','N')
    GROUP BY 1,2
    ORDER BY 2;
    '''

    # Print code if checkbox is selected
    if st.session_state.CSwitch:
        st.divider()
        st.code(query)
    
    df = pd.read_sql(query, conn)

    conn.close()
    return df['SUB_CLASSES'].to_list()
# Takes in date as a string and uses it in query
def getWeek(date):
    # Initialize/open connection
    conn = nzpy.connect(user='jrodenberg', password = 'Triangle123!', 
                        host='edwprd.basspro.net',port=5480,database='EDW_LANDING',securityLevel=1,logLevel=0)
    cursor = conn.cursor()
    

    dateQuery = f'''
        SELECT WEEK_NUMBER_IN_FISCAL_YEAR 
        FROM EDW_SPOKE.NZ.DIM_DATE 
        WHERE DATE_VALUE = '{date}'
    '''

    cursor.execute(dateQuery)
    weekNum = cursor.fetchone()
    conn.close()
    return weekNum

def GetMerchant(): 
    # Initialize/open connection
    conn = nzpy.connect(user='jrodenberg', password = 'Triangle123!', 
                        host='edwprd.basspro.net',port=5480,database='EDW_LANDING',securityLevel=1,logLevel=0)
    cursor = conn.cursor()
    

    query = '''
        SELECT DISTINCT MCHNUM as MERCHANT
        FROM NZ.PRODUCT_BPS_INVMST
        WHERE MCHNUM NOT LIKE 'Z%' 
        AND MCHNUM NOT  LIKE 'A%'
        AND MCHNUM NOT LIKE 'M%' 
        AND MCHNUM NOT LIKE 'T%'
        AND MCHNUM NOT LIKE 'D%'
        AND MCHNUM NOT LIKE 'W%'
        AND MCHNUM IS NOT NULL 
        AND MCHNUM != ''
    '''

    df = pd.read_sql(query, conn)
    conn.close()
    return df['MERCHANT'].tolist()

def GetStoreNum():
    # Initialize/open connection
    conn = nzpy.connect(user='jrodenberg', password = 'Triangle123!', 
                        host='edwprd.basspro.net',port=5480,database='EDW_LANDING',securityLevel=1,logLevel=0)
    cursor = conn.cursor()
    

    query = '''SELECT DISTINCT strnbr as STRNBR
    FROM NZ.INV_BPS_MRSLRM1P
    WHERE STRNBR BETWEEN 0 AND 100
    OR STRNBR BETWEEN 301 AND 500   
    order by 1
    '''

    df = pd.read_sql(query, conn)
    conn.close()
    return df['STRNBR'].tolist() 



#======================-------------APP BUILDING-------------======================#
#-[ ]---------Set title, initial variable values, etc.                                                     -[Displayed Element(s)]-
st.set_page_config( layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title('Demand Planning Forecast Variance')
if 'CSwitch' not in st.session_state:
    st.session_state.CSwitch = False

st.session_state.CSwitch = st.checkbox('Show Prepared Queries', value=True)    
st.divider()
    #getting dept and dropdown 
storesMenu = GetStoreNum()

stores = st.multiselect('Stores:',storesMenu) 

if len(stores) == 0: 
    stores = storesMenu

deptsMenu = getDepartments()

chosenDepts = st.multiselect('Departments:', deptsMenu)

if len(chosenDepts) == 0: 
        chosenDepts = deptsMenu

deptsList = [x.split('-')[0] for x in chosenDepts]

if len(deptsList) > 0:
        subDeptsMenu = getSubDepartments(deptsList)
        chosenSubDepts = st.multiselect('Sub-Departments:', subDeptsMenu)
        if len(chosenSubDepts) == 0: 
            chosenSubDepts = subDeptsMenu
        subDeptsList = [x.split('-')[0] for x in chosenSubDepts]


        if len(subDeptsList) > 0:
            classesMenu = getClasses(deptsList,subDeptsList)
            chosenClasses = st.multiselect('Classes:', classesMenu)
            if len(chosenClasses) == 0: 
                chosenClasses = classesMenu
            classList = [x.split('-')[0] for x in chosenClasses]

from datetime import date, timedelta

##dateinput = st.date_input("Pick Your Date Range:",min_value= date.today() - timedelta(days=180), max_value= date.today())

##date_range = getWeek(dateinput)

##Initialize FCST Error Query 

def main_query():

# Use a list comprehension to add single quotes to each value
    #subClassesFilter = [f"'{sub_class}'" for sub_class in chosenSubClasses]
# Join the filtered values using commas
    ##subClassesFilterStr = ', '.join(subClassesFilter)

    query = f'''WITH PAST_FCST AS 
              (
              SELECT
            DEPARTMENT_MEMBER_NUMBER DEPT_NUM,
              DEPARTMENT_NAME AS DEPT,
              P.SUB_DEPARTMENT_MEMBER_NUMBER AS SUB_NUM,
                     P.SUB_DEPARTMENT_NAME AS SUB_DEPT,
       P.CLASS_MEMBER_NUMBER AS CLASS_NUM,
       P.CLASS_NAME AS CLASS_NAME,
       P.SUB_CLASS_NAME AS SUB_CLASS_NAME,
       P.SUB_CLASS_MEMBER_NUMBER AS SUB_CLASS_NUM,
                     SKUNBR,
                     STRNBR,
              PERCENTILE_CONT(.5) WITHIN GROUP (ORDER BY CASE WHEN SKUSDT >= {date.today() - timedelta(days=180)} THEN TYFUNT END) AS PAST_FCST
              FROM
                     EDW_HUB_STAGE.NZ.ARCHIVE_DOMO_MRSLRH1P M1
                     JOIN EDW_SPOKE..DIM_PRODUCT_BPS P ON 
                     P.SKU_DISPLAY_NUMBER = M1.SKUNBR 
              WHERE TYFUNT > 0
                     AND SKUSDT >= {date.today() - timedelta(days=180)}
                     AND P.SUB_CLASS_MEMBER_NUMBER != 998
                     AND P.SUB_DEPARTMENT_MEMBER_NUMBER != 918
                     AND category_name IS NOT NULL 
                     GROUP BY DEPARTMENT_MEMBER_NUMBER,
                    DEPARTMENT_NAME ,
                     P.SUB_DEPARTMENT_MEMBER_NUMBER,
                     P.SUB_DEPARTMENT_NAME,
                    P.CLASS_MEMBER_NUMBER,
                    P.CLASS_NAME,
                    SKUNBR,
                    STRNBR,
                    P.SUB_CLASS_NAME,
                    P.SUB_CLASS_MEMBER_NUMBER
                     HAVING PAST_FCST IS NOT NULL
),

       CURRENT_FCST AS (
              SELECT
              DISTINCT DEPARTMENT_MEMBER_NUMBER AS DEPT_NUM,
              DEPARTMENT_NAME AS DEPT,
                     P.SUB_DEPARTMENT_MEMBER_NUMBER AS SUB_NUM,
                     P.SUB_DEPARTMENT_NAME AS SUB_DEPT,
       P.CLASS_MEMBER_NUMBER AS CLASS_NUM,
       P.CLASS_NAME AS CLASS_NAME,
       MAX(P.STYLE_DISPLAY_NUMBER) AS STYLE,
                     SKUNBR ,
                     MAX(P.SKU_NAME) AS SKU_NAME,
                     STRNBR ,
                     MAX(CASE WHEN SKUSDT > {date.today() - timedelta(days=180)} THEN TYFUNT END) AS CURRENT_FCST,
                     MAX(MRPP.PRICE) AS PRICE 
              FROM
                     NZ.INV_BPS_MRSLRM1P M2
                     JOIN EDW_SPOKE..DIM_PRODUCT_BPS P ON 
                     P.SKU_DISPLAY_NUMBER = M2.SKUNBR 
                     JOIN NZ.PO_BPS_MRPPCW1P AS MRPP 
                     ON M2.SKUNBR = MRPP.INUMBR
              WHERE
                     TYFUNT > 0
                     AND MRPP.PRICECOD = 'USD'
                     AND M2.SKUSDT > {date.today() - timedelta(days=180)}
                     AND P.SUB_CLASS_MEMBER_NUMBER != 998
                     AND P.SUB_DEPARTMENT_MEMBER_NUMBER != 918
                     AND category_name IS NOT null

                     GROUP BY DEPARTMENT_MEMBER_NUMBER,
                    DEPARTMENT_NAME,
                     P.SUB_DEPARTMENT_MEMBER_NUMBER,
                     P.SUB_DEPARTMENT_NAME,
                    P.CLASS_MEMBER_NUMBER,
                    P.CLASS_NAME,
                    SKUNBR,
                    STRNBR),
                     
                     
              REPORT AS    (SELECT
              P.DEPT,
              P.DEPT_NUM,
       P.SUB_NUM,
       P.SUB_DEPT,
       P.CLASS_NUM,
       P.CLASS_NAME,
              P.SUB_CLASS_NUM,
              P.SUB_CLASS_NAME,
       F.STYLE,
       P.SKUNBR,
       F.SKU_NAME,
       P.STRNBR,
       F.PRICE AS PRICE,
       ROUND(P.PAST_FCST,0) AS PAST,
       ROUND(F.CURRENT_FCST,0) AS CURRENT_FCST,
       ROUND(F.CURRENT_FCST - P.PAST_FCST,0) AS FCST_CHANGE,
       ROUND(F.PRICE * FCST_CHANGE,2) AS FCST$_VAR
FROM
       PAST_FCST P
JOIN CURRENT_FCST F ON
       P.SKUNBR = F.SKUNBR 
       AND P.STRNBR = F.STRNBR
WHERE FCST_CHANGE != 0 
AND ABS(FCST_CHANGE) > 50
--AND P.CLASS_NUM = 
ORDER BY ABS(F.CURRENT_FCST - P.PAST_FCST) DESC) 

SELECT MST.MCH AS MERCHANT,
R.DEPT_NUM||'-'||R.DEPT AS DEPT,
R.SUB_NUM||'-'||R.SUB_DEPT AS SUB_DEPT,
       R.CLASS_NUM||'-'||R.CLASS_NAME AS CLASS,
              R.SUB_CLASS_NUM||'-'||R.SUB_CLASS_NAME AS SUB_CLASS,
              R.STYLE,
       R.SKUNBR,
       R.SKU_NAME,
       R.STRNBR,
       R.PRICE,
       R.PAST,
       R.CURRENT_FCST,
       R.FCST_CHANGE,
       R.FCST$_VAR
FROM REPORT R 
LEFT JOIN(SELECT MST1.MCHNUM AS MCH, MST1.INUMBR FROM NZ.PRODUCT_BPS_INVMST MST1) MST ON R.SKUNBR = MST.INUMBR
WHERE R.DEPT_NUM IN('''
    for index in range(0, len(deptsList)-1):
        query += f''' '{deptsList[index]}','''
    query += f''' '{deptsList[-1]}' '''
    query += f''') 
AND R.SUB_NUM IN ( '''
    for index in range(0, len(subDeptsList)-1):
        query += f''' '{subDeptsList[index]}','''
    query += f''' '{subDeptsList[-1]}' '''
    query += f''')
    AND R.CLASS_NUM IN('''
    for index in range(0, len(classList)-1):
        query += f''' '{classList[index]}','''
    query += f''' '{classList[-1]}' '''
    query += f''')
    AND R.STRNBR IN('''
    for index in range(0, len(stores)-1):
        query += f''' '{stores[index]}','''
    query += f''' '{stores[-1]}' '''
    query += f''')'''
        
    st.code(query)

    conn = nzpy.connect(user='jrodenberg', password = 'Triangle123!', host='edwprd.basspro.net',
                        port=5480,database='EDW_LANDING',securityLevel=1,logLevel=0)

    df = pd.read_sql(query,conn)

    conn.close 

    return df
df = main_query()

st.dataframe(df.head(5))

import streamlit as st

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='fcst_change.csv',
    mime='text/csv',
)

