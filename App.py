import nltk
nltk.download('stopwords')
import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
#from streamlit.web.cli import main
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
#import pafy
import plotly.express as px

# From here to 
import subprocess, sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import pafy

except Exception as error:
    print("Error: ", error)
    install("git+https://github.com/mps-youtube/pafy.git")
    import pafy
#here
#Just to resolve youtube-dl issue on cloud

def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def to_1D(series):
    return pd.Series([x.replace('[','').replace(']','') for _list in series for x in _list.split(", ")])

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

connection = pymysql.connect(**st.secrets["mysql"])
cursor = connection.cursor()

def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

st.set_page_config(
   page_title="Resume Doctor",
   page_icon='./Logo/SRA_Logo(1).ico',
)
def run():
    st.title("📝 Resume Doctor")
    st.sidebar.markdown("# Choose User Type")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options 👇🏻:", activities)
    # link = '[©Developed by vishal](http://github.com/vishulearener)'
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/SRA_Logo.png')
    img = img.resize((200,200))
    st.image(img)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS sradatab;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(400) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Normal User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload your Resume", type=["pdf"])
        if pdf_file is not None:
            #with st.spinner('Uploading your Resume....'):
                 #time.sleep(4)
                 #pass
            save_image_path = './Uploaded_Resumes/'+ pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info**")

                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                except:
                    pass    
                try:
                    st.text('Degree: ' + resume_data['degree'])
                    st.text('College_Name: ' + resume_data['college_name'])
                except:
                    pass
                try:
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >=3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                text='See our skills recommendation',
                    value=resume_data['skills'],key = '1')

                ##  recommendation
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                #
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'skills' in resume_text:
                    resume_score = resume_score+20

                if 'Objective' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                #if 'Declaration'  in resume_text:
                #    resume_score = resume_score + 20
                #    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',unsafe_allow_html=True)
                #else:
                #    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

                if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('**Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have added in your Resume. **")
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                              str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                              str(recommended_skills), str(rec_course))


                #Bonus videos 
                with st.expander("Bonus Videos"):
                ## Resume writing video
                    st.header("**Video for Resume Writing Tips💡**")
                    resume_vid = random.choice(resume_videos)
                    res_vid_title = fetch_yt_video(resume_vid)
                    st.subheader("✅ **"+res_vid_title+"**")
                    st.video(resume_vid)

                ## Interview Preparation Video
                    st.header("**Video for Interview 👨‍💼 Tips💡**")
                    interview_vid = random.choice(interview_videos)
                    int_vid_title = fetch_yt_video(interview_vid)
                    st.subheader("✅ **" + int_vid_title + "**")
                    st.video(interview_vid)

                connection.commit()
            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')
        genre = st.radio(
        "Choose the admin type",
        ('Guest admin', 'admin'),horizontal=True)
        if genre == 'admin':
            ad_user = st.text_input("Username")
            ad_password = st.text_input("Password", type='password')
        else:
            ad_user = 'curiousvishu'
            ad_password = 'thankyoudevsnest'
        if st.button('Login'):
            if ad_user == 'curiousvishu' and ad_password == 'thankyoudevsnest':
                st.success("Welcome Vishu")
                st.snow()
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's Data 🛢️**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)
                
                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field 🎓 according to the Skills**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field 🎓 according to the Skills')
                st.plotly_chart(fig)


                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's 💼 Experienced Level")
                st.plotly_chart(fig)

                labels = plot_data.resume_score.unique()
                values = plot_data.resume_score.value_counts()
                st.subheader("📈 **bar-Chart for User's👨‍💻 Experienced Level**")
                fig = px.bar(df,x="Resume Score", title="bar-Chart📈 for User's 🎯 Resume Score")
                st.plotly_chart(fig)

                st.subheader("📈 **bar-Chart for User's👨‍💻 Experienced Level**")
                d= to_1D(plot_data["Actual_skills"]).value_counts()
                d=pd.DataFrame({'skill':d.index, 'count':d.values})
                fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                st.plotly_chart(fig)

                tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs(["Web Development", "Android Development", "Data Science","IOS Development","UI-UX Development","dummy"])
                

                with tab1:
                    d = plot_data[plot_data.Predicted_Field == 'Web Development']
                    labels = d.User_level.unique()
                    values = d.User_level.value_counts()
                    st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                    fig = px.pie(d, values=values, names=labels, title="Pie-Chart for User's 💼 Experienced Level")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for for User's 🎯 Resume Score**")
                    fig = px.bar(d,x="resume_score", title="bar-Chart📈 for User's 🎯 Resume Score")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for User's 🛠️ Skills**")
                    d= to_1D(d["Actual_skills"]).value_counts()
                    d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                    st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                with tab2:
                    d = plot_data[plot_data.Predicted_Field == 'Android Development']
                    labels = d.User_level.unique()
                    values = d.User_level.value_counts()
                    st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                    fig = px.pie(d, values=values, names=labels, title="Pie-Chart for User's 💼 Experienced Level")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for for User's 🎯 Resume Score**")
                    fig = px.bar(d,x="resume_score", title="bar-Chart📈 for User's 🎯 Resume Score")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for User's 🛠️ Skills**")
                    d= to_1D(d["Actual_skills"]).value_counts()
                    d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                    st.plotly_chart(fig)



                with tab3:
                    d = plot_data[plot_data.Predicted_Field == 'Data Science']
                    labels = d.User_level.unique()
                    values = d.User_level.value_counts()
                    st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                    fig = px.pie(d, values=values, names=labels, title="Pie-Chart for User's 💼 Experienced Level")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for for User's 🎯 Resume Score**")
                    fig = px.bar(d,x="resume_score", title="bar-Chart📈 for User's 🎯 Resume Score")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for User's 🛠️ Skills**")
                    d= to_1D(d["Actual_skills"]).value_counts()
                    d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                    st.plotly_chart(fig)


                with tab4:
                    d = plot_data[plot_data.Predicted_Field == 'IOS Development']
                    labels = d.User_level.unique()
                    values = d.User_level.value_counts()
                    st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                    fig = px.pie(d, values=values, names=labels, title="Pie-Chart for User's 💼 Experienced Level")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for for User's 🎯 Resume Score**")
                    fig = px.bar(d,x="resume_score", title="bar-Chart📈 for User's 🎯 Resume Score")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for User's 🛠️ Skills**")
                    d= to_1D(d["Actual_skills"]).value_counts()
                    d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                    st.plotly_chart(fig)

                with tab5:
                    d = plot_data[plot_data.Predicted_Field == 'UI-UX Development']
                    labels = d.User_level.unique()
                    values = d.User_level.value_counts()
                    st.subheader("📈 **Pie-Chart for User's 💼 Experienced Level**")
                    fig = px.pie(d, values=values, names=labels, title="Pie-Chart for User's 💼 Experienced Level")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for for User's 🎯 Resume Score**")
                    fig = px.bar(d,x="resume_score", title="bar-Chart📈 for User's 🎯 Resume Score")
                    st.plotly_chart(fig)

                    st.subheader("📈 **bar-Chart for User's 🛠️ Skills**")
                    d= to_1D(d["Actual_skills"]).value_counts()
                    d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's 🛠️ Skills")
                    st.plotly_chart(fig)
                    


                with tab6:
                    labels = plot_data.resume_score.unique()
                    values = plot_data.resume_score.value_counts()
                    st.subheader("📈 ** bar-Chart for User's👨‍💻 Experienced Level**")
                    ##print(df['Predicted Field'])
                    ##print(plot_data[plot_data.Predicted_Field == 'Web Development'])
                    #d = plot_data[plot_data.Predicted_Field == 'Web Development']
                    ##print('iknowyou1')
                    #print(df[df['Predicted Field'=='Web Development']])
                    #fig= d.hist(bins=30)
                    #d = plot_data[plot_data.Predicted_Field == 'UI-UX Development'].groupby(by=["Recommended_skills"]).size().reset_index(name="counts")
                    ##print(plot_data.explode('Actual_skills'))
                    ###print(type(plot_data["Actual_skills"]))
                    ##print(df)
                    #d= pd.DataFrame(plot_data["Actual_skills"].transpose())
                    #d = pd.DataFrame().assign(Courses=df['Courses']
                    #def to_1D(series):
                    #    return pd.Series([x.replace('[','').replace(']','') for _list in series for x in _list.split(", ")])
                    #[x for _list in series for x in _list]
                    #fruit_dict = {}
                    #for i in plot_data["Actual_skills"]:
                    #    for j in i.split(", "):
                    #        #print(i,j)
                    #        if j not in fruit_dict:
                    #            fruit_dict[j] = 1
                    #        else:
                    #            fruit_dict[j] += 1
                    #print(fruit_dict)
                    ##d= to_1D(plot_data["Actual_skills"]).value_counts()
                    ##print(d)
                    ##print(d.explode('Actual_skills'))
                    #d=plot_data["Actual_skills"].explode().value_counts()
                    ##print(d)
                    ##d=pd.DataFrame({'skill':d.index, 'count':d.values})
                    ##print(d)
                    ##fig = px.bar(d,x="skill",y="count",title="bar-Chart📈 for User's👨‍💻 Experienced Level")
                    #fig= px.bar(data_frame=d, x="Recommended_skills", y="counts", barmode="group")
                    #fig = px.bar(plot_data[plot_data.Predicted_Field == 'UI-UX Development'],x="Recommended_skills", title="bar-Chart📈 for User's👨‍💻 Experienced Level")
                    st.plotly_chart(fig)



            else:
                st.error("Wrong ID & Password Provided")
run()
