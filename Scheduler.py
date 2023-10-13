from datetime import datetime, timedelta
import collections

class Scheduler:
    def __init__(self, api_handler):
        self.api_handler = api_handler
        self.doctorAppointments = collections.defaultdict(set)
        self.personAppointments = collections.defaultdict(set)

    def schedule(self):
        if self.api_handler.start_test_system():
            self.get_current_schedule()
            while True:
                next_request = self.api_handler.get_next_appointment_request()
                if next_request:
                    personId = next_request["personId"]
                    requestId = next_request["requestId"]
                    preferred_doctors = next_request["preferredDocs"]
                    preferred_times = next_request["preferredDays"]
                    if next_request["isNew"]:
                        self.schedule_new_patient_appointment(self, personId, requestId, preferred_doctors, preferred_times)
                    else:
                        self.schedule_existing_patient_appointment(self, personId, requestId, preferred_doctors, preferred_times)
                else:
                    print(self.api_handler.stop_test_system())
                    break 

        else:
            print("invalid token received")


    def get_current_schedule(self):
        current_schedule = self.api_handler.get_current_schedule()
        for schedule in current_schedule:
            self.doctorAppointments[schedule["doctorId"]].add(schedule["appointmentTime"])
            self.personAppointments[schedule["personId"]].add(schedule["appointmentTime"])

    def schedule_new_patient_appointment(self, personId, requestId, preferred_doctors, preferred_times):
        # New patients can only be scheduled for 3 pm or 4 pm
        for time in preferred_times:
            date_part = time.split('T')[0]
            new_preferred_times = [datetime.fromisoformat(f"{date_part}T{hour_value}:00.000Z") for hour_value in ["15:00", "16:00"]]
            for preferred_time in new_preferred_times:
                if self.is_valid_appointment_time(preferred_time, personId, True):
                    for doctorId in preferred_doctors:
                        if preferred_time not in self.doctorAppointments[doctorId]:
                            self.doctorAppointments[doctorId].add(preferred_time)
                            self.personAppointments[personId].add(preferred_time)
                            
                            self.api_handler.schedule_appointment({
                                                                    "doctorId": doctorId,
                                                                    "personId": personId,
                                                                    "appointmentTime": preferred_time,
                                                                    "isNewPatientAppointment": "true",
                                                                    "requestId": requestId
                                                                })
                            return True
        return False

    def schedule_existing_patient_appointment(self, personId, requestId, preferred_doctors, preferred_times):
        for time in preferred_times:
            date_part = time.split('T')[0]
            hour_part = datetime.fromisoformat(time[:-1]).hour
            hour_values = [hour_part.strftime("%H"), (hour_part+timedelta(hours=1)).strftime("%H")]
            new_preferred_times = [datetime.fromisoformat(f"{date_part}T{hour_value}:00:00.000Z") for hour_value in hour_values]
            for preferred_time in new_preferred_times:
                if self.is_valid_appointment_time(preferred_time, personId, False):
                    for doctorId in preferred_doctors:
                        if preferred_time not in self.doctorAppointments[doctorId]:
                            self.doctorAppointments[doctorId].add(preferred_time)
                            self.personAppointments[personId].add(preferred_time)
                            
                            self.api_handler.schedule_appointment({
                                                                    "doctorId": doctorId,
                                                                    "personId": personId,
                                                                    "appointmentTime": preferred_time,
                                                                    "isNewPatientAppointment": "false",
                                                                    "requestId": requestId
                                                                })
                            return True
        return False

    def is_valid_appointment_time(self, appointment_time, personId, isNewPatient):
        datetime_part = datetime.fromisoformat(appointment_time[:-1])

        if not isNewPatient:
            for appointment_time in self.personAppointments[personId]:
                blocked_date = datetime.fromisoformat(appointment_time[:-1])
                start_blocked = blocked_date - timedelta(days=6)
                end_blocked = blocked_date + timedelta(days=6)
                if start_blocked <= datetime_part <= end_blocked:
                    return False

        if 11 <= datetime_part.month <= 12 and datetime_part.year == 2021:
            if 0 <= datetime_part.weekday() <= 4:
                return 8 <= datetime_part.hour <= 16
        return False
