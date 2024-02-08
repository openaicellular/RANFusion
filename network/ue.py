#This is UE class, ue.py in network directory
import random
import re
from datetime import datetime
from influxdb_client import Point
from logs.logger_config import ue_logger
import uuid

class UE:
    existing_ue_ids = set()  # Keep track of all existing UE IDs to avoid duplicates
    ue_instances = {}

    def __init__(self, config, **kwargs):
        self.config = config
        # Check if UE ID is provided and unique
        ue_id = kwargs.get('ue_id', '').strip()
        if ue_id and ue_id in UE.existing_ue_ids:
            # Handle the case where the provided ID is not unique
            raise ValueError(f"UE ID {ue_id} is already in use.")
        elif not ue_id:
            # Generate a unique UE ID if not provided
            ue_id_counter = max((int(id[2:]) for id in UE.existing_ue_ids if id.startswith('UE')), default=0) + 1
            ue_id = f"UE{ue_id_counter}"
            while ue_id in UE.existing_ue_ids:  # Ensure the generated UE ID is unique
                ue_id_counter += 1
                ue_id = f"UE{ue_id_counter}"
        
        # Set the UE ID and add it to the tracking structures
        self.ID = ue_id
        self.instance_id = str(uuid.uuid4())  # Generic unique identifier for the instance of the ue
        UE.existing_ue_ids.add(ue_id)
        UE.ue_instances[ue_id] = self  # Store the instance in the dictionary
        self.IMEI = kwargs.get('imei') or self.allocate_imei()         # International Mobile Equipment Identity
        self.throughput = 0 ## Initialize throughput attribute
        self.Location = kwargs.get('location')         # Geographic location of the UE
        self.ConnectedCellID = kwargs.get('connected_cell_id')        # ID of the cell to which the UE is connected
        self.ConnectedSector = kwargs.get('connected_sector')        # Sector of the cell to which the UE is connected
        self.gNodeB_ID = kwargs.get('gnodeb_id')        # ID of the gNodeB to which the UE is connected
        self.IsMobile = kwargs.get('is_mobile')        # Indicates if the UE is mobile or stationary
        self.ServiceType = kwargs.get('service_type', random.choice(["video", "game", "voice", "data", "IoT"]))        # Type of service the UE is using (e.g., video, game)
        self.SignalStrength = kwargs.get('initial_signal_strength')        # Initial signal strength of the UE
        self.RAT = kwargs.get('rat')        # Radio Access Technology used by the UE
        self.MaxBandwidth = kwargs.get('max_bandwidth')        # Maximum bandwidth available to the UE
        self.DuplexMode = kwargs.get('duplex_mode')        # Duplex mode used by the UE (e.g., FDD, TDD)
        self.TxPower = kwargs.get('tx_power')        # Transmission power of the UE
        self.Modulation = kwargs.get('modulation')        # Modulation technique used by the UE
        self.Coding = kwargs.get('coding')        # Coding scheme used by the UE
        self.MIMO = kwargs.get('mimo')        # Indicates if MIMO is used by the UE
        self.Processing = kwargs.get('processing')        # Processing capabilities of the UE
        self.BandwidthParts = kwargs.get('bandwidth_parts')        # Bandwidth parts allocated to the UE
        self.ChannelModel = kwargs.get('channel_model')        # Channel model used for the UE's connection
        self.Velocity = kwargs.get('velocity')        # Velocity of the UE if it is mobile
        self.Direction = kwargs.get('direction')        # Direction of the UE's movement if it is mobile
        self.TrafficModel = kwargs.get('traffic_model')        # Traffic model used for the UE's data transmission
        self.SchedulingRequests = kwargs.get('scheduling_requests')        # Number of scheduling requests made by the UE
        self.RLCMode = kwargs.get('rlc_mode')        # RLC mode used by the UE
        self.SNRThresholds = kwargs.get('snr_thresholds')        # SNR thresholds for the UE
        self.HOMargin = kwargs.get('ho_margin')        # Handover margin for the UE
        self.N310 = kwargs.get('n310')        # N310 parameter for the UE, related to handover
        self.N311 = kwargs.get('n311')        # N311 parameter for the UE, related to handover
        self.Model = kwargs.get('model')        # Model of the UE
        self.ScreenSize = kwargs.get('screensize', f"{random.uniform(5.0, 7.0):.1f} inches")        # Screen size of the UE
        self.BatteryLevel = kwargs.get('batterylevel', random.randint(10, 100))        # Battery level of the UE
        self.TrafficVolume = 0        # Traffic volume handled by the UE (initialized to 0)
        self.DataSize = kwargs.get('datasize')        # Data size transmitted/received by the UE
        ue_logger.info(f"UE initialized with ID {self.ID} at {datetime.now()}")

    @staticmethod
    def allocate_imei():
        # Generate and return a random IMEI during UE initialization
        while True:
            start = str(random.randint(10000000, 99999999))  # Generate an 8-digit TAC
            while len(start) < 14:
                start += str(random.randint(0, 9))
            imei = start + str(UE.calc_check_digit(start))
            break
        return imei

    @staticmethod
    def calc_check_digit(number):
        alphabet = '0123456789'
        n = len(alphabet)
        number = tuple(alphabet.index(i) for i in reversed(str(number)))
        return (sum(number[::2]) + sum(sum(divmod(i * 2, n)) for i in number[1::2])) % n

    @staticmethod
    def camel_to_snake(name):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @staticmethod
    def from_json(json_data):
        ues = []
        for item in json_data["ues"]:
            item = {UE.camel_to_snake(key): value for key, value in item.items()}
            ue = UE(**item)
            ues.append(ue)
        return ues
    
    @classmethod
    def get_ue_instance_by_id(cls, ue_id):
        """
        Retrieve a UE instance by its ID.
        
        :param ue_id: The ID of the UE to retrieve.
        :return: The UE instance with the given ID, or None if not found.
        """
        return cls.ue_instances.get(ue_id, None)
    
    def serialize_for_influxdb(self):
        point = Point("ue_metrics") \
            .tag("ue_id", str(self.ID)) \
            .tag("connected_cell_id", str(self.ConnectedCellID)) \
            .tag("connected_sector_id", str(self.ConnectedSector)) \
            .tag("entity_type", "ue") \
            .tag("gnb_id", str(self.gNodeB_ID)) \
            .tag("instance_id", str(self.instance_id)) \
            .field("imei", str(self.IMEI)) \
            .field("service_type", str(self.ServiceType)) \
            .field("signal_strength", float(self.SignalStrength)) \
            .field("rat", str(self.RAT)) \
            .field("max_bandwidth", int(self.MaxBandwidth)) \
            .field("duplex_mode", str(self.DuplexMode)) \
            .field("tx_power", int(self.TxPower)) \
            .field("modulation", ','.join(self.Modulation) if isinstance(self.Modulation, list) else str(self.Modulation)) \
            .field("coding", str(self.Coding)) \
            .field("mimo", str(self.MIMO)) \
            .field("processing", str(self.Processing)) \
            .field("bandwidth_parts", ','.join(map(str, self.BandwidthParts)) if isinstance(self.BandwidthParts, list) else str(self.BandwidthParts)) \
            .field("channel_model", str(self.ChannelModel)) \
            .field("velocity", float(self.Velocity)) \
            .field("direction", str(self.Direction)) \
            .field("traffic_model", str(self.TrafficModel)) \
            .field("scheduling_requests", int(self.SchedulingRequests)) \
            .field("rlc_mode", str(self.RLCMode)) \
            .field("snr_thresholds", ','.join(map(str, self.SNRThresholds))) \
            .field("ho_margin", str(self.HOMargin)) \
            .field("n310", str(self.N310)) \
            .field("n311", str(self.N311)) \
            .field("model", str(self.Model)) \
            .field("screen_size", str(self.ScreenSize)) \
            .field("battery_level", int(self.BatteryLevel)) \
            .time(datetime.utcnow())
        return point
    
    def update_parameters(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                ue_logger.info(f"Updated {key} for UE {self.ID} to {value}")
            else:
                ue_logger.warning(f"Attempted to update non-existent attribute {key} for UE {self.ID}")