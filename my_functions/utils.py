from linkedin_api import Linkedin

# var to init

message_data = "I'm a graduate from an MSc in Statistics from Université PSL in Paris, " \
    + "after a year of experience as a Data Scientist, I am looking for" \
    + "a new opportunity in this sector."   

message_quant = "I'm a graduate from an MSc in Statistics and Quantitative Finance from Université " \
    + "PSL in Paris, after a year of experience as a Data Scientist, I am now looking to" \
    + "work as a Quant." 

end_of_message = "Feel free to contact me if you see a possible fit !"

regions_known = {'USA' : '103644278', 'France' : '105015875', 'UK' : '101165590', 'Holand' : '102890719'}

# funct to get connnect to linkedin acc

def open_file(filepath:str)-> str:
    '''Opens and reads a file'''
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
    
def get_credential(path):
    raw_data = open_file(path)
    data = raw_data.split(",")
    return [data[0][2:-1], data[1][1:-2]]


    
    
def is_profile_data_or_finance(profile, data_keywords = ['tech','data','engineer', 'analyst', 'analytics'] , quant_finance_keywords = ['quantitative', 'finance', 'fintech', 'financial', 'hft', 'hedge', 'asset']):
    
    count_data = 0
    count_quant = 0
    
    # Some recruiters don't have a summary, in this case we take the title
    try:
        summary = profile['summary'].lower()

    except KeyError:
        summary = profile['headline'].lower()
        
    summary = summary.split(" ")
    
    for word in summary:
        
        if(word in data_keywords):
            count_data += 1
            
        if(word in quant_finance_keywords):
            count_quant += 1
            
    if(count_quant > count_data):
        return 'finance'
    
    if(count_data > 0):
        return 'data'
    
    return 'NA'


def is_profile_fetched_french(profile, france_keywords = ['france', 'paris', 'île-de-france']):
    
    try:
        location = profile['location'].lower()
        
    except KeyError:
        return False
    
    for keyword in france_keywords:
        if(keyword in location):
            return True
    
    return False


def get_first_name_fetched_profile(profile):
    
    try:
        first_name = profile['name'].split(" ")[0]
    
    except:
        return False
    return first_name



def add_easy_personnalized_connection(current_recruiter, api, message_quant,
                                 message_data, end_of_message):

    message = ""

    first_name = get_first_name_fetched_profile(current_recruiter)
    is_french = is_profile_fetched_french(current_recruiter)
    current_profile = api.get_profile(current_recruiter['public_id'])
    sector = is_profile_data_or_finance(current_profile)


    if(sector == 'finance'):
        message = "Hello " + first_name + "\n" + message_quant + "\n" + end_of_message

    elif(sector == 'data'):
        message = "Hello " + first_name + "\n" + message_data + "\n" + end_of_message

    else:  
        return "na_recruiter"

    connection = api.add_connection(current_recruiter['public_id'], message)
    
    return [sector, connection]







def get_gpt_message(generic_message, profile, first_name):
        
    discussion = [
        {"role": "system", "content": "You adapt a generic message to a personnalized message saying that I am looking for a new opportunity to headhunters."},
        {"role": "user", "content": f"Here is the generic message : <<{generic_message}>>"},
        {"role": "assistant", "content": "What is the summary from the headhunter?"},
        {"role": "user", "content": f"Here is the summary from his profile : <<{profile['summary']}>> and his first name : <<{first_name}>>"},
        {"role": "assistant", "content": "What is the expected output ?"},        
        {"role": "user", "content": "Provide it in JSON format with the key : message. No more than 60 words."},
        {"role": "assistant", "content": "What is the expected content?"}, 
    ]


    message_prompt = "Greet the headhunter by the first name given, say that from my experience and "\
    + "qualification he may have opportunities that would fit my profile. "\
    + "Return just the JSON with the key message, nothing else"
    answer, discussion = gpt3_chat(message=message_prompt, messages=discussion)
    
    print(answer)
    answer = extract_only_dict_from_gpt_output(answer)
    print(answer)
    answer = json_to_dict(answer)
    
    return answer["message"]



def add_gpt_personnalized_connection(current_recruiter, api, message_quant,
                                 message_data, end_of_message):

    
    #first_name = get_first_name_fetched_profile(current_recruiter)   sometimes gives false idk why
    print(current_recruiter['name'])
    first_name = current_recruiter['name'].split(" ")[0]
    is_french = is_profile_fetched_french(current_recruiter)
    current_profile = api.get_profile(current_recruiter['public_id'])
    sector = is_profile_data_or_finance(current_profile)


    if(sector == 'finance'):
        generic_message = message_quant

    else:
        generic_message = message_data

    #else:  
    #    return "na_recruiter"
    
    personnalized_message = get_gpt_message(generic_message, current_profile, first_name)
    final_message = personnalized_message
    #final_message = "Hello " + first_name + "\n" + personnalized_message
    
    if(len(final_message) >299):
        final_message = final_message[0:300] 
    
    
    print(final_message)

    connection = api.add_connection(current_recruiter['public_id'], final_message)
    
    return [sector, connection, final_message]








def create_message_for_recruiter_from_profile(recruiter_profile_id, api):
    
    recruiter = api.get_profile(recruiter_profile_id)
    first_name = recruiter['firstName']
    
    if(first_name):
        
        message = "Hello "+ first_name + ", \n" + "I am a graduate from an Msc in Statistics with an experience " \
                  + "as a Data Scientist and I came across your profile. I am currently looking for a new position." \
                  + " Would you be available for an exchange to see if you might have an opportunity that could " \
                  + "fit with me ?"

    else:
        
        message = "Hello, I am a graduate from an Msc in Statistics with an experience" \
                  + "as a Data Scientist and I came across your job post for a " + job_title \
                  + " role. I am very interested in this opportunity and would love to learn more about the position."

    
    return message







def extract_only_dict_from_gpt_output(gpt_answer):
    in_json = False
    
    for current_char in gpt_answer:
        if(in_json):
            json = json + current_char
            if(current_char == '}'):
                return json
        else:
            if(current_char == '{'):
                json = '{'
                in_json = True
    return False
                
                
                
                
                
                
def send_follow_up_message(api, base_message, follow_up_message, limit = 100):
    
    conversations = api.get_conversations()
    
    for counter_message in range(min(limit, len(conversations['elements']))):
        
        last_message = conversations['elements'][counter_message]['events'][0]['eventContent']['com.linkedin.voyager.messaging.event.MessageEvent']['attributedBody']['text']
                
        if(base_message in last_message):
            
            conv_id = conversations['elements'][counter_message]['dashEntityUrn'].split(':')[-1]   
            api.send_message(follow_up_message, conv_id)
            
    return True



def gpt3_chat(message: str, messages:list[dict])-> tuple[str, list]:
    '''Returns GPT's response to the input message and appends it to the messages list'''
    messages.append({"role": "user", "content": message})
    # ChatGPT is powered by gpt-3.5-turbo, OpenAI’s most advanced language model.
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": response})
    return str(response), messages

def get_completion(prompt, model="gpt-3.5-turbo"): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]






def connect_firefox_to_my_linkedin(credentials):
    
    browser = webdriver.Firefox()

    # your secret credentials:
    email = credentials[0]
    password = credentials[1]
    # Go to linkedin and login
    browser.get('https://www.linkedin.com/login')
    time.sleep(3)
    browser.find_element(by =By.ID, value ='username').send_keys(email)
    browser.find_element(by =By.ID, value ='password').send_keys(password)
    browser.find_element(by =By.ID, value ='password').send_keys(Keys.RETURN)
    
    time.sleep(3)
    
    return browser


def get_recruiter_id_from_job(browser, job_id):
    
    browser.get(f"https://www.linkedin.com/jobs/view/{job_id}")

    time.sleep(2)
    
    sele_search = browser.find_elements(by=By.CLASS_NAME, value="mh4.pt4.pb3")
    
    if(len(sele_search) == 0):
        return False
    
    recruiter_public_id = sele_search[0].find_element(by=By.CSS_SELECTOR,value ='a').get_attribute('href').split('/')[-1]
    
    return recruiter_public_id







def add_new_row(sheet, row_to_insert):
    
    current_number_rows = len(sheet.get_all_values())
    sheet.insert_row(row_to_insert, current_number_rows + 1)

    return True

def delete_last_row(sheet):
    
    current_number_rows = len(sheet.get_all_values())
    sheet.delete_rows(current_number_rows)
    
    return True


def create_sheet(sheet_name, mail):
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("gs_credentials.json", scope)
    client = gspread.authorize(credentials)

    sheet = client.create(sheet_name)
    sheet.share(mail, perm_type='user', role='writer')
    
    return sheet


def connect_to_sheet(sheet_name):
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("gs_credentials.json", scope)
    client = gspread.authorize(credentials)
    
    sheet = client.open(sheet_name).sheet1
    
    return sheet









import json

def json_to_dict(json_string):
    """Converts a JSON-formatted string to a Python dictionary."""
    return json.loads(json_string)

def gpt_extract_job_function_from_title(job_title):

    prompt = f"""
    Your task is to extract the job title from a job post title. \
    We just want to keep the job function, no more than 3 words.
    Provide it in JSON format with the key: job_title 

    Job post title: ```{job_title}```
    """

    response = get_completion(prompt)
    response = json_to_dict(response)
    
    return response


def add_easy_connection_from_recruiter_job_post(recruiter_id, api):
    
    message = ""
    
    current_recruiter = api.get_profile(recruiter_id)

    first_name = get_first_name_fetched_profile(current_recruiter)
    print(first_name)
    
    is_french = is_profile_fetched_french(current_recruiter)
    print(is_french)
    
    sector = is_profile_data_or_finance(current_recruiter)
    print(sector)

    if(is_french):
        print("french")
        
    else:
        
        if(sector == 'finance'):
            message = "Hello " + first_name + "\n" + message_quant + "\n" + end_of_message

        else:
            message = "Hello " + first_name + "\n" + message_data + "\n" + end_of_message


    connection = api.add_connection(current_recruiter['public_id'], message)
    
    return [sector, connection]


def create_message_for_recruiter_from_job(recruiter_profile_id, job_title, api):
    
    recruiter = api.get_profile(recruiter_profile_id)
    first_name = recruiter['firstName']
    
    if(first_name):
        
        message = "Hello "+ first_name + ", \n" + "I am a graduate from an Msc in Statistics with an experience" \
                  + "as a Data Scientist and I came across your job post for a " + job_title \
                  + " role. I am very interested in this opportunity and would love to learn more about the position."

    else:
        
        message = "Hello, I am a graduate from an Msc in Statistics with an experience" \
                  + "as a Data Scientist and I came across your job post for a " + job_title \
                  + " role. I am very interested in this opportunity and would love to learn more about the position."

    
    return message
