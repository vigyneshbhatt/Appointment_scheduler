import requests

class ApiHandler:
    def __init__(self, api_token, base_url="http://scheduling-interview-2021-265534043.us-west-2.elb.amazonaws.com"):
        self.api_token = api_token
        self.base_url = base_url

    def start_test_system(self):
        response = requests.post(f"{self.base_url}/api/Scheduling/Start", params={"token": self.api_token})
        print("start_test_system response", response)
        return response.status_code == 200

    def stop_test_system(self):
        response = requests.post(f"{self.base_url}/api/Scheduling/Stop", params={"token": self.api_token})
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_next_appointment_request(self):
        response = requests.get(f"{self.base_url}/api/Scheduling/AppointmentRequest", params={"token": self.api_token})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return None  
        else:
            return None

    def get_current_schedule(self):
        response = requests.get(f"{self.base_url}/api/Scheduling/Schedule", params={"token": self.api_token})
        print("get_current_schedule response", response)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def schedule_appointment(self, appointment_info_request):
        response = requests.post(f"{self.base_url}/api/Scheduling/Schedule", params={"token": self.api_token}, json=appointment_info_request)
        return response.status_code == 200