import os
import random
import numpy as np
from helpers import predict_failure

normal_mean = {
    "Air temperature [K]": 299.97,
    "Process temperature [K]": 309.99,
    "Rotational speed [rpm]": 1540.26,
    "Torque [Nm]": 39.9,
    "Tool wear [min]": 106.69
}
fail_mean = {
    "Air temperature [K]": 300.88,
    "Process temperature [K]": 310.29,
    "Rotational speed [rpm]": 1496.48,
    "Torque [Nm]": 50.16,
    "Tool wear [min]": 143.78
}
normal_std = {
    "Air temperature [K]": 1.99,
    "Process temperature [K]": 1.48,
    "Rotational speed [rpm]": 167.39, ### might ruin everything
    "Torque [Nm]": 9.47,
    "Tool wear [min]": 62.94
}
fail_std = {
    "Air temperature [K]": 2.07,
    "Process temperature [K]": 1.36,
    "Rotational speed [rpm]": 384.94,
    "Torque [Nm]": 16.37,
    "Tool wear [min]": 72.75
}




class Machine:
    def __init__(self, machine_id,model):
        self.machine_id = machine_id
        self.uid = 0
        self.product_id = ""
        self.type = ""
        self.air_temperature = 0
        self.process_temperature = 0
        self.rotational_speed = 0
        self.torque = 0
        self.tool_wear = 0
        self.predicted_failure = False
        self.model = model

        self.csv_file_path = "machine_data.csv"
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'w') as f:
                f.write("UID,Machine ID,Product ID,Type,Air temperature [K],"
                         "Process temperature [K],Rotational speed [rpm],"
                         "Torque [Nm],Tool wear [min],Machine Failure\n")

    def generate_machine_data(self):
        
        self.product_id = self.generate_product_id()
        self.type = self.product_id[0]
        self.air_temperature = round(self.random_walk(normal_mean["Air temperature [K]"], normal_std["Air temperature [K]"]), 1)
        self.process_temperature = round(self.air_temperature + 10 + self.random_walk(0, normal_std["Process temperature [K]"]), 1)
        self.rotational_speed = round(self.calculate_rotational_speed(normal_mean["Rotational speed [rpm]"], normal_std["Rotational speed [rpm]"]), 1)
        self.torque = round(self.calculate_torque(normal_mean["Torque [Nm]"], normal_std["Torque [Nm]"]), 1)
        self.tool_wear += round(self.calculate_tool_wear(), 1)
        self.predicted_failure = self.predict_machine_failure()
        self.uid += 1

    def log_data_to_csv(self):
        csv_line = f"{self.uid},{self.machine_id},{self.product_id}," \
                   f"{self.type},{self.air_temperature}," \
                   f"{self.process_temperature},{self.rotational_speed}," \
                   f"{self.torque},{self.tool_wear}," \
                   f"{self.predicted_failure}\n"

        with open(self.csv_file_path, 'a') as f:
            f.write(csv_line)

    def generate_product_id(self):
        types = ["L", "M", "H"]
        weights = [0.5, 0.3, 0.2]
        selected_type = random.choices(types, weights=weights, k=1)[0]
        serial_number = np.random.randint(10000)
        return f"{selected_type}{serial_number}"

    def random_walk(self, mean, std_dev):
        return np.random.normal(mean, std_dev)

    def calculate_rotational_speed(self, mean, std):
        return np.random.normal(mean, std)

    def calculate_torque(self, mean, std):
        return max(0, mean + np.random.normal(0, std))

    def calculate_tool_wear(self):
        if self.product_id[0] == "H":
            return 5
        elif self.product_id[0] == "M":
            return 3
        else:
            return 2

    def predict_machine_failure(self):
        
        return predict_failure(self.model,self)

    def get_machine_status(self):
        return {
            "uid": self.uid,
            "machineId": self.machine_id,
            "productID": self.product_id,
            "type":self.type,
            "airTemperature": self.air_temperature,
            "processTemperature": self.process_temperature,
            "rotationalSpeed": self.rotational_speed,
            "torque": self.torque,
            "toolWear": self.tool_wear,
            "predictedFailure": self.predicted_failure
        }