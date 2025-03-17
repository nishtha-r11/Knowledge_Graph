import pandas as pd

def user_message(pds):

    user_message = (
        f"""
        You are an expert in knowledge graph construction.
        You will be given the Property descriptions which is the description of the properties of wikidata.
        Treat each description as independent.
        Extract the PID (property id) field that can be used for the QIDs of any influential people, person, place, or entity 
        that frequently appears in media, social media, TV programs, movies, sports programs, news programs, or other public spaces etc
        from each program description.
        For each of these add a new column as Relevant with information as "yes" or "no".
        Special Instructions:
            Extract the most relevant PID for each description. If the description does not fulfill the criteria then add "no" to the corresponding
            Relevant column.
            
        You can refer the below example for your reference:
        ------------------------------------------------------------------------------------------------------------------
        PID | Label | Description
        ------------------------------------------------------------------------------------------------------------------
        P6 | head of government | head of the executive power of this town, city, municipality, state, country, or other governmental body
        ------------------------------------------------------------------------------------------------------------------
        P10 | video | relevant video. For images, use the property P18. For film trailers, qualify with "object has role" (P3831)="trailer" (Q622550)
        ------------------------------------------------------------------------------------------------------------------
        P16 | transport network | network the infrastructure is a part of
        ------------------------------------------------------------------------------------------------------------------

        
        Provide output in the format below:
        ------------------------------------------------------------------------------------------------------------------
        PID | Label | Description | Relevant
        ------------------------------------------------------------------------------------------------------------------
        P6 | head of government | head of the executive power of this town, city, municipality, state, country, or other governmental body | yes
        ------------------------------------------------------------------------------------------------------------------
        P10 | video | relevant video. For images, use the property P18. For film trailers, qualify with "object has role" (P3831)="trailer" (Q622550) | yes
        ------------------------------------------------------------------------------------------------------------------
        P16 | transport network | network the infrastructure is a part of | no
        ------------------------------------------------------------------------------------------------------------------


        NOTE: Each description should be in a new row.
        Do not include any explanation for the results.
        <<<>>> 
        <<<
        show description: {pds}
        >>>
        """
    )

    return user_message



def complete(myquestion,session):

    prompt =myquestion
    model_name = 'llama3.1-405b'
    # model_name = 'mixtral-8x7b' 
    # model_name = 'llama3.1-405b'
    # model_name = 'claude-3-5-sonnet'
    cmd = """
            select snowflake.cortex.complete(?, ?) as response
            
          """
    
    df_response = session.sql(cmd, params=[model_name, prompt]).collect()
    return df_response


def process_response(data):
    data_str = data[0]['RESPONSE']
    # Split the data into lines
    lines = data_str.split('\n')
    
    # Initialize lists to store the data
    PID = []
    Label = []
    Description = []
    Relevant = []
    # Iterate through each line
    for line in lines:
        # Skip empty lines and separator lines
        if not line.strip() or '---' in line:
            continue
        
        # Split the line by '|' to separate columns
        parts = line.split('|')
        
        # Ensure there are exactly four parts
        if len(parts) != 4:
            continue
        
        # Strip whitespace from each part
        program_title = parts[0].strip()
        Label = parts[1].strip()
        Description = parts[2].strip()
        Relevant = parts[3].strip()
        
        # Append the data to respective lists
        PID.append(PID)
        Label.append(Label)
        Description.append(Description)
        Relevant.append(Relevant)
    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'PID': PID,
        'Label': Label,
        'Description': Description,
        'Relevant': Relevant
    })
    df = df.iloc[1:]
    return df

    
def main(session: snowpark.Session):
    # genres_to_filter = ["news", "sports", "home improvement", "weather", "documentary", "reality", "crime",
    #                     "mystery", "football", "entertainment", "outdoors", "basketball", "comedy", "adventure",
    #                     "hunting", "drama", "game show", "children", "action", "soccer", 
    #                     "animated", "history", "shopping", "baseball", "sitcom", 
    #                     "hockey", "gardening", "talk", "consumer", "science"] 

    df_main = pd.read_csv("C:/Users/nishtha.r/Downloads/GitHub/Knowledge_Graph/wikidata_properties_labels_sorted.csv")
    selected_pids = []

    # for index, row in df_main.iterrows():
    #     description = row['Description']
    #     pid = row['Pids']
        
    #     full_prompt = prompt.format(description=description, pid=pid)
        
    #     data = complete(user_message(formatted_list),session)
    #     df = process_response(data)
    #     response = llm.response(full_prompt)
        
    #     if 'yes' in response.lower():
    #         selected_pids.append(pid)

    # result_df = pd.DataFrame({'PID': selected_pids})
    # result_df.to_csv('selected_pids.csv', index=False)

    total_rows = df_main.shape[0]
    batch_size = 10
    n_loop = math.ceil(total_rows/batch_size)
    temp_df =pd.DataFrame()
    for i in range(0,5):
        start_idx = i * batch_size
        end_idx = min((i+1) * batch_size,total_rows)
        description = df_main['Description'].iloc[start_idx:end_idx].values
        # tile_id_list = df_main['Label'].iloc[i*10:(i+1)*10].values
        # formatted_list = "\n".join([f"{i+1}.{desc}" for i, desc in enumerate(tile_id_list)])
        data = complete(user_message(formatted_list),session)
        df = process_response(data)
        program_titles_from_df = df['Program_Title_Id']
        # if set(program_titles_from_df) != set(programs_tile_id_list):
        #     print("Not matching")
        #     random.shuffle(programs_list)
        #     formatted_list = "\n".join([f"{i+1}.{desc}" for i, desc in enumerate(programs_list)])
        #     data = complete(user_message(formatted_list),session)
        #     df = process_response(data)            
        
        temp_df = pd.concat([temp_df,df])
        
    temp_df.reset_index(drop=True,inplace=True)
    # temp_sp = session.create_dataframe(temp_df)
    
    # temp_df[['PROGRAM_TITLE','PROGRAM_ID']] = temp_df['Program_Title_Id'].str.split('_',expand=True)
    # programs = programs_dataframe.merge(temp_df,on=['PROGRAM_ID','PROGRAM_TITLE'],how="inner")
    # programs= programs[['SHOW_ID','SHOW_TITLE','PROGRAM_ID','TITLE_DESCRIPTION','PROGRAM_TITLE','NER', 'NER_Description']]
    # programs.reset_index(drop=True,inplace=True)

    return programs