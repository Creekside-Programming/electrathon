packet_format: str = "<8sff"
"""format for use in struct.pack"""

sync_header: str = "chs-elec"
"""Added to top of packet to make absolutely sure that the data we are parsing is ours"""

network_id: int = 5