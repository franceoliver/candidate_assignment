import pandas as pd
import requests
import json
import pprint
import os
## "https://developer.domain.com.au/docs/v2/apis/pkg_properties_locations/references/suburbperformance_get_bynamedsuburb"

def demographic_api(year, state, suburb, postcode):
    client_id = 'client_f36178501f2a595281e0b57f21eb0f7b'
    client_secret = 'secret_9bbe7ba2532607c4385060d22ba39c64'
    scopes = ['api_demographics_read']
    auth_url = 'https://auth.domain.com.au/v1/connect/token'

    #Optional Input
    year = year # Census Year of data to return
    url_additions = f'?types=AgeGroupOfPopulation%2C%20CountryOfBirth%2C%20NatureOfOccupancy%2C%20Occupation%2C%20GeographicalPopulation%2C%20DwellingStructure%2C%20EducationAttendance%2C%20HousingLoanRepayment%2C%20MaritalStatus%2C%20Religion%2C%20TransportToWork%2C%20FamilyComposition%2C%20HouseholdIncome%2C%20Rent%2C%20LabourForceStatus&year={year}'


    #Required input
    state = state
    suburb = suburb
    postcode = postcode
    url_endpoint = f'https://api.domain.com.au/sandbox/v2/demographics/{state}/{suburb}/{postcode}/'


    response = requests.post(auth_url, data = {'client_id' : client_id,
                                                 "client_secret" : client_secret,
                                                 "grant_type":"client_credentials",
                                                 "scope": scopes,
                                                 "Content-Type":"text/json"})

    json_res = response.json()
    access_token = json_res["access_token"]
    print(access_token)
    auth = {"Authorization":"Bearer " + access_token}
    url = url_endpoint + url_additions
    resl = requests.get(url, headers=auth)
    r = resl.json()
    pprint.pprint(r)

    r['demographics'][0]['items'][0]

    df = pd.DataFrame()
    for period in range(len(r['demographics'])):
        temp_df = pd.DataFrame(data={'state' : state,
                                    'suburb' : suburb,
                                    'postcode' : postcode,
                                    'type' : [r['demographics'][period]['type']],
                                    'total' : [r['demographics'][period]['total']],
                                    'year' : [r['demographics'][period]['year']]})
        for list_item in range(len(r['demographics'][period]['items'])):
            for key in r['demographics'][period]['items'][list_item]:
                temp_df[key] = [r['demographics'][period]['items'][list_item][key]]
            df = pd.concat([df, temp_df])
            ## Pulling the most populat label from each category to join to the data set on year
            df = df.sort_values(by=['type', 'value']).drop_duplicates(subset= ['state', 'suburb', 'postcode', 'type'],
                                                                      keep='last')

    final_df = pd.DataFrame()
    for type_data in df['type']:
        print(type_data)
        final_df[type_data] = [df['label'].loc[df['type']==type_data][0]]
    final_df['state'] = state
    final_df['suburb'] = suburb
    final_df['postcode'] = postcode
    final_df['census_year'] = year
    return final_df

if __name__ == "__main__":
    df = pd.DataFrame()
    years = [2011, 2016]
    for year in years:
        temp_df = demographic_api(year, state ='NSW', suburb = 'Newtown', postcode= 2042)
        df = pd.concat([temp_df, df])
    for year in years:
        temp_df = demographic_api(year, state='NSW', suburb='Maroubra', postcode=2035)
        df = pd.concat([temp_df, df])

    df.to_csv(os.getcwd()+'/DATA/Census_data.csv', index=False)

