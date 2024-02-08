# this is network_delay.py in network folder #Accounts for different traffic types by adjusting the delay based on the specific QoS requirements of each traffic type.
#Incorporates a non-linear growth factor for the delay as the cell load increases, providing a more realistic simulation of network behavior under load.
#Adds random variability within ±10% of the calculated delay to simulate the unpredictable nature of real-world network conditions.
#Ensures that the delay does not exceed a specified maximum value, reflecting the practical limits of network performance degradation.
import math
import random

class NetworkDelay:
    def __init__(self, base_delay=10, max_delay=100):
        self.base_delay = base_delay
        self.max_delay = max_delay

    def calculate_delay(self, cell_load, traffic_type='data'):
        """
        Calculate network delay based on cell load and traffic type.
        Incorporates non-linear growth, random variability, and adjusts for traffic type.
        
        :param cell_load: The current load of the cell as a percentage.
        :param traffic_type: The type of traffic, affecting QoS.
        :return: The calculated network delay.
        """
        # Non-linear load factor calculation
        load_factor = math.exp(cell_load / 100) - 1
        
        # Adjust delay based on traffic type
        qos_factor = 1.0  # Default QoS factor
        if traffic_type == 'voice':
            qos_factor = 0.8  # Voice traffic might be more sensitive to delay
        elif traffic_type == 'video':
            qos_factor = 0.9  # Video traffic has slightly less sensitivity compared to voice
        elif traffic_type == 'game':
            qos_factor = 0.7  # Gaming traffic is very sensitive to delay
        elif traffic_type == 'iot':
            qos_factor = 1.1  # IoT traffic might be less sensitive to delay
        elif traffic_type == 'data':
            qos_factor = 1.0  # Default QoS factor for data traffic
        
        # Calculate preliminary delay
        delay = self.base_delay * (1 + load_factor) * qos_factor
        
        # Add random variability within ±10% of the current delay
        variability_factor = random.uniform(-0.1, 0.1)
        delay += delay * variability_factor
        
        # Ensure delay does not exceed max_delay
        delay = min(delay, self.max_delay)
        
        return delay

    # Placeholder for a method that adjusts base_delay based on UE throughput feedback
    # This method would need more context about how throughput data is collected and analyzed
    def adjust_for_throughput(self, throughput):
        """
        Adjust the base delay based on UE throughput feedback.
        
        :param throughput: Some metric or calculation representing UE throughput.
        """
        pass  # Implementation would depend on specific throughput metrics and goals

# Example usage
#network_delay = NetworkDelay()
#calculated_delay = network_delay.calculate_delay(cell_load=50, traffic_type='video')
#print(f"Calculated Network Delay: {calculated_delay} ms")