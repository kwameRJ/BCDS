import streamlit as st
from db import *
import ast
from aps_fxns import *
import pandas as pd

st.title("Breast Cancer Detection System")
headerSection = st.empty()
mainSection = st.empty()
logSection = st.empty()
session = st.session_state


# Page: Add User
def add_user_page():
    with mainSection.container():
        st.header("Add User")
        # Form to add a new user
        col1, col2 = st.columns([3,2])
        with col1:
            name = st.text_input("Name", key='name')
            password = st.text_input("Password", type="password", key='password')
        with col2:
            id = st.text_input("ID/Username", key='username')
            role = st.selectbox("Role", ["Administrator", "Staff"], key='role')

        if role and role == "Staff":
            job_title = st.selectbox("School", [i.title() for i in medical_staff], key='job_title')
            
    if check_session(attributes_dict[role.lower()]):
        if st.button("Add User"):
            user_info = {}
            for i in attributes_dict[role.lower()]:
                if i!='id' and i!="created_at":
                    user_info[i] = session[i]
        # Validation checks and logic to add user to the system
            try:
                create_entity(eval(role), **user_info)
                clear_session(attributes_dict[role.lower()])
                st.success("User added successfully!")
            except IntegrityError:
                st.warning('A user with the same ID already exists')
            
        # Add user to database or perform other actions


def check_session(keys):
    for key in keys:
        if key != 'id' and key !="created_at":
            if not session[key]:
                return False
    else:
        return True

def clear_session(keys):
    for key in keys:
        if key in session:
            del session[key]
# Page: Edit User
def edit_user_page():
    st.header("Edit User")
    # Form to edit an existing user
    user_id = st.selectbox("Select User", ["User 1", "User 2", "User 3"])  # Example user selection
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["Lecturer", "Administrator", "Student"])
    permissions = st.multiselect("Permissions", ["View Courses", "Edit Courses", "View Users", "Edit Users"])
    if st.button("Update User"):
        # Validation checks and logic to update user information
        # Update user in database or perform other actions
        st.success("User information updated successfully!")

# Page: Remove User
def remove_user_page():
    st.header("Remove User")
    # Confirmation page to remove a user
    user_id = st.selectbox("Select User", ["User 1", "User 2", "User 3"])  # Example user selection
    user_info = read_user(user_id)  # Function to fetch user information from database
    if user_info:
        st.warning("You are about to remove the following user:")
        st.write(f"Username: {user_info['username']}")
        st.write(f"Email: {user_info['email']}")
        if st.button("Confirm Removal"):
            # Logic to remove user from the system
            # Remove user from database or perform other actions
            st.success("User removed successfully!")

# Page: View Users
def view_users_page(user_type):
    user_class = entity_dict[user_type]
    user_df_keys = df_dict[user_type]
    user_attribute_keys = attributes_dict[user_type]
    with headerSection.container():
        st.header(f"Manage {user_type.title()}s")
    # Table or list view of all users in the system
    users = get_all_entity(user_class)
    with mainSection.container():
        search_item = st.text_input("Search Bar",key='search_bar',placeholder="Search")
        if search_item:
            data = []
            for i in users:
                for key,val in i.items():
                    if key in user_df_keys and search_item.lower() in str(val).lower():
                        data.append(i)
                        break
        else:
            data = users
        
        # Function to fetch all users from database
        if data:
            df = pd.DataFrame(data)
            if "job_title" in df.columns:
                df["job_title"] = (
                    df["job_title"].astype("category").cat.set_categories(medical_staff)
                    )
            if "gender" in df.columns:
                df["gender"] = (
                    df["gender"].astype("category").cat.set_categories(['Male', 'Female'])
                    )
            df.drop(['id', 'created_at'],axis=1,inplace=True)
            edited_df = st.experimental_data_editor(df,key=f"{user_type}_editor",num_rows='dynamic')
           
            edited_data = session[f"{user_type}_editor"]["edited_cells"]
            added_data =  session[f"{user_type}_editor"]["added_rows"]
            deleted_rows =  session[f"{user_type}_editor"]["deleted_rows"]
            with logSection.container():
                edit_data(edited_data, users, user_class,user_df_keys)
            if st.button('Save Updates'):
                edit_data(edited_data, users, user_class,user_df_keys, update=True)
                add_data(added_data, user_type, user_class,user_df_keys)
                #action for edited cells
                for row in deleted_rows:
                    delete_entity(user_class,users[row]['id'])
                
                if deleted_rows:
                    st.success("Users Deleted Successfully")

                del edited_data,added_data, deleted_rows

        else:
            st.warning(f"No {user_type}s found in the system.")

def edit_data(edited_data, users, user_class,user_df_keys, update=False):
    
    for key,val in edited_data.items():
        data_row, data_col = key.split(':')
        user = users[int(data_row)]
        entity = user_class.get(user_class.id== user['id'])
        col = user_df_keys[int(data_col)-1]
        if update:
            if col in ['name','first_name', 'last_name', 'address']:
                val=val.title()
            elif col in ['email']:
                val = val.lower()
            user[col] = val
            try:
                update_entity(entity,**user)
            except IntegrityError:
                st.warning(f'Please ensure all fields are filled for {user["name"]} | {user["username"]}')
            logSection.empty()
        else:
           f"- Changed {col} from {user[col]} to {val}"


def add_data(added_data, user_type, user_class,user_df_keys):
    for row_num,row in enumerate(added_data):
        user = {"role": user_type}
        for key,val in row.items():
            col = user_df_keys[int(key)-1]
            if col in ['name','first_name', 'last_name', 'address']:
                val=val.title()
            elif col in ['email']:
                val = val.lower()
            user[col] = val
        
        if len(user)>1:
            for i in user_df_keys:
                if i not in user:
                    st.warning(f'Please type in a {i} for new user {row_num}')
                    break
                elif not user[i]:
                    st.warning(f'Please type in a {i} for new user {row_num}')
                    break
            else:
                try:
                    create_entity(user_class, **user)
                    st.success(f"{user['name']} added successfully!")
                except IntegrityError:
                    st.warning('A user with the same ID already exists')
        else:
            pass
def view_admin_page():
    view_users_page('administrator')

def view_staff_page():
    view_users_page('staff')

def view_patient_page():
    view_users_page('patient')

def add_patient_page():
    with mainSection.container():
        st.header("Register New Patient")
        # Form to add a new user
        col1, col2 = st.columns([3,2])
        with col1:
            first_name = st.text_input("First Name", key='first_name')
            gender = st.selectbox("Gender",['Male', 'Female'] ,key='gender')
        with col2:
            last_name = st.text_input("Last Name", key='last_name')
            dob = st.date_input('Date of Birth',key='dob')
        st.subheader('Contact Information')
        st.markdown('---')
        col1, col2 = st.columns([3,2])
        with col1:
            phone = st.text_input('Phone Number', key='phone')
        with col2:
            email = st.text_input("email", key='email')
        address = st.text_area('Address', key='address')



        
            
    if check_session(attributes_dict['patient']):
        if st.button("Add Patient"):
            user_info = {}
            for i in attributes_dict['patient']:
                if i!='id' and i!="created_at":
                    user_info[i] = session[i]
                    if i in ['first_name','last_name','gender']:
                        user_info[i] = user_info[i].title()
                    
                
        # Validation checks and logic to add user to the system
            try:
                create_entity(Patient, **user_info)
                clear_session(attributes_dict['patient'])
                st.success("Patient added successfully!")
            except IntegrityError:
                st.warning('A patient with the same ID already exists')

def view_patient_info_page():
    
    patient = session.get('selected_patient',None)
    if patient:
        diagnostic_results = DiagnosticResult.select().where(DiagnosticResult.patient == patient)

        # Display patient information
        st.header(f"Patient {patient.id}")
        st.write(f"**Name:** {patient.first_name} {patient.last_name}")
        st.write(f"**Date of birth:** {patient.dob}")
        st.write(f"**Gender:** {patient.gender}")
        st.write(f"**Email:** {patient.email}")
        st.write(f"**Phone:** {patient.phone}")
        st.write(f"**Address:** {patient.address}")

        # Display diagnostic results
        if diagnostic_results:
            st.header("Diagnostic Results")
            for result in diagnostic_results:
                with st.expander(result.result_name):
                    
                    for i in ast.literal_eval(result.result_value):
                            percent = float(i[1])
                            text = f"{i[0]} {round(percent*100,2)}%"
                            st.progress(percent, text = text)
                    st.write(f"**Date:** {result.created_at}")
                    st.write("---")
        else:
            st.warning("No diagnostic results found for this patient.")

def test_main():
    patient = session.get('selected_patient',None)
    results = session.get('prediction_results', [])
    class_name = ['Benign with Density=1', 'Malignant with Density=1', 'Benign with Density=2',
                      'Malignant with Density=2', 'Benign with Density=3', 'Malignant with Density=3',
                      'Benign with Density=4', 'Malignant with Density=4']
    # Upload image
    uploaded_file = st.file_uploader("Upload mammology image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file)
    
        # Display results
        if st.button("Predict"):
            # Load and preprocess image
            with st.spinner("Processing Image..."):
                image = Image.open(uploaded_file)
                image = np.array(image)
                image = preprocess(image)
                image = image / 255.0
                im = image.reshape(-1, 224, 224, 3)

            # Make prediction
            with st.spinner("Generating Prediction"):
                pred = model.predict(im)[0]
            
            st.snow()
            results = list(zip(class_name, pred))
            results.sort(key=lambda x:x[1], reverse=True)
            
            session['prediction_results'] = results
            st.subheader("Results")
            st.divider()
            level = f"Prediction: {round(float(results[0][1])*100,2)}%"
            cancer = f"Cancer Type: {results[0][0]}"
            
            st.info(cancer)
            st.warning(level)
            with st.expander("See Detailed Results"):
                for i in results:
                    percent = float(i[1])
                    text = f"{i[0]} {round(percent*100,2)}%"
                    st.progress(percent, text = text)

        if patient and results:
            if st.button("Save Results"):
                result_name = f"{patient.last_name}_{patient.first_name}_{datetime.now()}"
                result_value = results
                st.write(patient.first_name)
                DiagnosticResult.create(patient=patient, result_name=result_name, result_value=result_value)
                st.success("Results Saved")
                del session['prediction_results']


def patient_history_page():
    patient = session.get("selected_patient", None)
    if patient:
        results = DiagnosticResult.select().where(DiagnosticResult.patient == patient)

    # Display diagnostic results in Streamlit expanders
        if len(results) == 0:
            st.write("No diagnostic results found for this patient.")
        else:
            for result in results:
                with st.expander(result.result_name):
                    st.write(f"Created at: {result.created_at}")
                    for i in ast.literal_eval(result.result_value):
                        percent = float(i[1])
                        text = f"{i[0]} {round(percent*100,2)}%"
                        st.progress(percent, text = text)
                    if st.button("Delete"):
                        result.delete_instance()
                        st.write("Deleted the following diagnostic result:")
                        st.write(f"Result name: {result.result_name}")
                        st.write(f"Created at: {result.created_at}")
                
            
def generate_report(patient):
    # Get patient data from the database
    diagnostic_results = DiagnosticResult.select().where(DiagnosticResult.patient == patient)

    # Generate report
    report = f"Patient Name: {patient.first_name} {patient.last_name}\n"
    for result in diagnostic_results:
        report += f"Result Name: {result.result_name}\n"
        report +=f"Created at: {result.created_at}\n"
        report_values = eval(result.result_value)
        for value in report_values:
            report += f"- {value[0]}: {value[1]}\n"
        report += "\n"

    # Display report
    st.text(report)
    return report

def generate_report_page():
# Generate reports for selected patients
    patients = get_all_entity(Patient)
    if patients:
        selected_patients = st.multiselect('Select patients to generate reports for', range(len(patients)), format_func=lambda x: f"{patients[x]['last_name']}, {patients[x]['first_name']}")
        
        if selected_patients:
            all_reports=''
            for patient in selected_patients:
                all_reports += generate_report(read_patient(patients[patient]['id'])) + "\n\n"


            # Add a button to download all reports as a single text file
            st.download_button('Download Reports', all_reports)
                
            
    

admin_menu_options = {
    "Dashboard": [],
    "User Management": ["Add User", "Manage Administrators","Manage Staff"],
    "Patient Management": ["Register Patient", "Manage Patients"],
    "Patient Reporting": ["Generate Patient Reports", "Visualize and Analyze Patient Data", "Data Backups"],
    "Logout": []
} 

staff_menu_options = {
    "Dashboard": [],
    "Patient Management": ["Register Patient", "Manage Patients"],
    "View Patient Data": ["Patient Information", "Run Tests","Medical History"],
    "Patient Reporting": ["Generate Patient Reports", "Visualize and Analyze Patient Data", "Data Backups"],
    "Update Profile Information":[],
    "Logout": []
}

menu_options = {
    'administrator': admin_menu_options,
    'staff': staff_menu_options,
}
submenu_pages = {
    "Add User": add_user_page,
    "Manage Administrators": view_admin_page,
    "Manage Staff": view_staff_page,
    "Manage Patients": view_patient_page,
    "Register Patient": add_patient_page,
    "Patient Information": view_patient_info_page,
    "Run Tests": test_main,
    "Medical History": patient_history_page,
    "Generate Patient Reports": generate_report_page
}

# Main Menu
def main_menu():
    menu = menu_options['staff']
    options = [i for i in menu.keys()]
    selected_option = st.sidebar.selectbox("Main Menu", options)
    return selected_option

def submenus(options):
    if options:
        selected_option = st.sidebar.radio("Submenu", options)
        return selected_option
    
# Main menu selection
menu = menu_options['staff']
selected_option = main_menu()

if selected_option == "View Patient Data":

    patients = get_all_entity(Patient)
    if patients:
        index = st.sidebar.selectbox("Select Patient", range(len(patients)), format_func=lambda x: f"{patients[x]['last_name']}, {patients[x]['first_name']}")
        session['selected_patient'] = read_patient(patients[index]['id'])
    else:
        st.warning("No patients have been registered. Please visit the patient management section to add a new patient.")


selected_submenu = submenus(menu[selected_option])
if selected_submenu:
    submenu_pages[selected_submenu]()

