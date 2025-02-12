import os 
import json 
from dotenv import load_dotenv 

## lets load the env variables 

load_dotenv(dotenv_path='./.env')

def create_service_account_json(output_file="service_account.json"):
    "Loads service account credentials from env vaiables"

    try: 
        credentials = {
        "type": os.environ["TYPE"],
        "project_id": os.environ["PROJECT_ID"],
        "private_key_id": os.environ["PRIVATE_KEY_ID"],
        "private_key": os.environ["PRIVATE_KEY"].replace("\\n", "\n"),  # Handle newlines in the key
        "client_email": os.environ["CLIENT_EMAIL"],
        "client_id": os.environ["CLIENT_ID"],
        "auth_uri": os.environ["AUTH_URL"],
        "token_uri": os.environ["TOKEN_URL"],
        "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER"],
        "client_x509_cert_url": os.environ["CLIENT_CERT"],
        "universe_domain": os.environ["UNIVERSE_DOMAIN"]
        }
        for key, value in credentials.items():
            if not value:
                raise ValueError("Missing required env variables: {e} from e")

        with open(output_file, "w") as json_file:
            json.dump(credentials, json_file, indent=4)
        
        print("Service account JSON file generated as : {output_file}")
    
    except Exception as e:
        raise Exception(f"Missing environment vaiable {e}")

    except Exception as e:
        raise Exception(f"Failed to create service_account.json")

    # except KeyError as e:
    #     raise ValueError(f)
    # return credentials  