## Human Readable names
FLAVOR_NAMES = ["Ubuntu", "Kubuntu", "Xubuntu", "Edubuntu"]
VERSION_NAMES = ["8.04.1", "8.04.2", "8.10"]
ARCHITECTURE_NAMES = ["i386", "AMD64"]
EDITION_NAMES = ["Desktop", "Server", "Alternate"]

## Codes for disc type
UBUNTU = 0
KUBUNTU = 1
XUBUNTU = 2
EDUBUNTU = 3

V_8_04_1 = 0
V_8_04_2 = 1
V_8_10 = 2

I386 = 0
AMD64 = 1

DESKTOP = 0
SERVER = 1
ALTERNATE = 2

HASHES = {(UBUNTU, V_8_10, ALTERNATE, AMD64) : "ea6d44667ea3fd435954d6e1f0e89122", 
          (UBUNTU, V_8_10, ALTERNATE, I386) : "f9e0494e91abb2de4929ef6e957f7753",
          (UBUNTU, V_8_10, DESKTOP, AMD64) : "f9cdb7e9ad85263dde17f8fc81a6305b",
          (UBUNTU, V_8_10, DESKTOP, I386) : "24ea1163ea6c9f5dae77de8c49ee7c03",
          (UBUNTU, V_8_10, SERVER, AMD64) : "e3028a105a083339be8e5af5afbe7444",
          (UBUNTU, V_8_10, SERVER, I386) : "a2ec9975a91e1228c8292ed9799dc302",
          (KUBUNTU, V_8_10, ALTERNATE, AMD64) : "4dc5bad5ee18648cd9dfbb87d86880b5",
          (KUBUNTU, V_8_10, ALTERNATE, I386) : "04a2c5c8f394175e6d6579e626995c7a",
          (KUBUNTU, V_8_10, DESKTOP, AMD64) : "824de6bea59d41637a41f17c00d33f7d",
          (KUBUNTU, V_8_10, DESKTOP, I386) : "82c02dc7386dfb6858a9ec09a5059e1e",
          (XUBUNTU, V_8_10, ALTERNATE, AMD64) : "3539726b4aa58801427578bb66da5fd1",
          (XUBUNTU, V_8_10, ALTERNATE, I386) : "db016f2f55ea2109b787a191b8115c67",
          (XUBUNTU, V_8_10, DESKTOP, AMD64) : "4153396adde6b210c07ef7d7ccb14231",
          (XUBUNTU, V_8_10, DESKTOP, I386) : "53c50ff06f4ad659f0abf6474b58c8e6",
          (EDUBUNTU, V_8_10, DESKTOP, AMD64) : "45c572d3bc95db05ed8ab37bae75b750",
          (EDUBUNTU, V_8_10, DESKTOP, I386): "7944aaaaf645571dd6e0a9db700394e9",
          (UBUNTU, V_8_04_2, ALTERNATE, AMD64) : "cfb001d45a8f94554af34756d0d502f4",
          (UBUNTU, V_8_04_2, ALTERNATE, I386) : "fa027fc04c5ff82a8c81b8ffd04d8eb5",
          (UBUNTU, V_8_04_2, DESKTOP, AMD64) : "ae6a2ec3b1a78481d47e7d3f59756d99",
          (UBUNTU, V_8_04_2, DESKTOP, I386) : "589f13da46e34789cb13b7dc574ccc6c",
          (UBUNTU, V_8_04_2, SERVER, AMD64) : "44891152b7799ce8312c9946c75fa1f2",
          (UBUNTU, V_8_04_2, SERVER, I386) : "28464268e34b65d535c199b92754eb84",
          (KUBUNTU, V_8_04_1, ALTERNATE, AMD64) : "957e8329f346543027a247b06cc58853",
          (KUBUNTU, V_8_04_1, ALTERNATE, I386) : "5de105f1e2acb0a7019a636c98454e0d",
          (KUBUNTU, V_8_04_1, DESKTOP, AMD64) : "e171680df385cf07e6dbe339b59f2999",
          (KUBUNTU, V_8_04_1, DESKTOP, I386) : "e0b9861df26c54acfd62bf35abe859f6",
          (XUBUNTU, V_8_04_1, ALTERNATE, AMD64) : "287f090589821fbb56c3df06b23f1b30",
          (XUBUNTU, V_8_04_1, ALTERNATE, I386) : "65e96e29439578d5c0c11a85fce075e7",
          (XUBUNTU, V_8_04_1, DESKTOP, AMD64) : "6609ac9a45f7a9b9948862355f3b30ca",
          (XUBUNTU, V_8_04_1, DESKTOP, I386) : "ea2e852642ed5dcc722d67e181eb5c89",
          (EDUBUNTU, V_8_04_1, DESKTOP, AMD64) : "eed95f7c8c6981f8a3d017dc220019a9",
          (EDUBUNTU, V_8_04_1, DESKTOP, I386) : "aadc960619548b613bf17ecb3eef333e"
          }

TUPLES = {"ea6d44667ea3fd435954d6e1f0e89122": (UBUNTU, V_8_10, ALTERNATE, AMD64), 
          "f9e0494e91abb2de4929ef6e957f7753": (UBUNTU, V_8_10, ALTERNATE, I386),
          "f9cdb7e9ad85263dde17f8fc81a6305b": (UBUNTU, V_8_10, DESKTOP, AMD64),
          "24ea1163ea6c9f5dae77de8c49ee7c03": (UBUNTU, V_8_10, DESKTOP, I386),
          "e3028a105a083339be8e5af5afbe7444": (UBUNTU, V_8_10, SERVER, AMD64),
          "a2ec9975a91e1228c8292ed9799dc302": (UBUNTU, V_8_10, SERVER, I386),
          "4dc5bad5ee18648cd9dfbb87d86880b5": (KUBUNTU, V_8_10, ALTERNATE, AMD64),
          "04a2c5c8f394175e6d6579e626995c7a": (KUBUNTU, V_8_10, ALTERNATE, I386),
          "824de6bea59d41637a41f17c00d33f7d": (KUBUNTU, V_8_10, DESKTOP, AMD64),
          "82c02dc7386dfb6858a9ec09a5059e1e": (KUBUNTU, V_8_10, DESKTOP, I386),
          "3539726b4aa58801427578bb66da5fd1": (XUBUNTU, V_8_10, ALTERNATE, AMD64),
          "db016f2f55ea2109b787a191b8115c67": (XUBUNTU, V_8_10, ALTERNATE, I386),
          "4153396adde6b210c07ef7d7ccb14231": (XUBUNTU, V_8_10, DESKTOP, AMD64),
          "53c50ff06f4ad659f0abf6474b58c8e6": (XUBUNTU, V_8_10, DESKTOP, I386),
          "45c572d3bc95db05ed8ab37bae75b750": (EDUBUNTU, V_8_10, DESKTOP, AMD64),
          "7944aaaaf645571dd6e0a9db700394e9": (EDUBUNTU, V_8_10, DESKTOP, I386),
          "cfb001d45a8f94554af34756d0d502f4": (UBUNTU, V_8_04_2, ALTERNATE, AMD64),
          "fa027fc04c5ff82a8c81b8ffd04d8eb5": (UBUNTU, V_8_04_2, ALTERNATE, I386),
          "ae6a2ec3b1a78481d47e7d3f59756d99": (UBUNTU, V_8_04_2, DESKTOP, AMD64),
          "589f13da46e34789cb13b7dc574ccc6c": (UBUNTU, V_8_04_2, DESKTOP, I386),
          "44891152b7799ce8312c9946c75fa1f2": (UBUNTU, V_8_04_2, SERVER, AMD64),
          "28464268e34b65d535c199b92754eb84": (UBUNTU, V_8_04_2, SERVER, I386),
          "957e8329f346543027a247b06cc58853": (KUBUNTU, V_8_04_1, ALTERNATE, AMD64),
          "5de105f1e2acb0a7019a636c98454e0d": (KUBUNTU, V_8_04_1, ALTERNATE, I386),
          "e171680df385cf07e6dbe339b59f2999": (KUBUNTU, V_8_04_1, DESKTOP, AMD64),
          "e0b9861df26c54acfd62bf35abe859f6": (KUBUNTU, V_8_04_1, DESKTOP, I386),
          "287f090589821fbb56c3df06b23f1b30": (XUBUNTU, V_8_04_1, ALTERNATE, AMD64),
          "65e96e29439578d5c0c11a85fce075e7": (XUBUNTU, V_8_04_1, ALTERNATE, I386),
          "6609ac9a45f7a9b9948862355f3b30ca": (XUBUNTU, V_8_04_1, DESKTOP, AMD64),
          "ea2e852642ed5dcc722d67e181eb5c89": (XUBUNTU, V_8_04_1, DESKTOP, I386),
          "eed95f7c8c6981f8a3d017dc220019a9": (EDUBUNTU, V_8_04_1, DESKTOP, AMD64),
          "aadc960619548b613bf17ecb3eef333e": (EDUBUNTU, V_8_04_1, DESKTOP, I386)
          }

def is_hash(hcode):
	return hcode in TUPLES;

def tuple2Hash(key):
	return HASHES[key]

def hash2Tuple(key):
	return TUPLES[key]

def tuple2String(tup):
    sp = " ";
    return FLAVOR_NAMES[tup[0]] + sp + VERSION_NAMES[tup[1]] + sp + EDITION_NAMES[tup[2]] + sp + ARCHITECTURE_NAMES[tup[3]]

class UbuntuDisc:	
    def __init__(self, f, v, e, a):
        self.flavor = f
        self.version = v
        self.architecture = a
        self.edition = e
        self.hash = HASHES[(f, v, e, a)]

# contents is a tuple of (UbuntuDisc, quantity)
class DiscPackage:
	def __init__(self, name, contents):
		self.name = name
		self.contents = contents


