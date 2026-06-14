from slowapi import Limiter
from slowapi.util import get_remote_address as GRA

limiter = Limiter(key_func=GRA)