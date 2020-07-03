from IPython import get_ipython
from .round_trip import RoundTrip

ip = get_ipython()
ip.register_magics(RoundTrip)
print(ip)

try:
    ip = get_ipython()
    ip.register_magics(RoundTrip)
    print(ip)
except:
    print('aaa')