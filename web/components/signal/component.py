class Signal:

    def __init__(
        self,
        slot,
        name="Empty",
        value=None,
        status="N/A",
        color="gray",
    ):
        self.slot = slot
        self.name = name
        self.value = value
        self.status = status
        self.color = color
