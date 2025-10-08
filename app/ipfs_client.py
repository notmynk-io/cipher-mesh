import ipfshttpclient

class IPFSClient:
    def __init__(self, addr="/dns/localhost/tcp/5001/http"):
        # Connect to local IPFS node
        self.client = ipfshttpclient.connect(addr)

    def add_bytes(self, data: bytes) -> str:
        """
        Add byte data to IPFS and return CID.
        """
        cid = self.client.add_bytes(data)
        return cid

    def get_bytes(self, cid: str) -> bytes:
        """
        Retrieve data from IPFS by CID.
        """
        data = self.client.cat(cid)
        return data
