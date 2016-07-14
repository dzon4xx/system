import threading

from backend.communication.communication import Communication
from backend.logic.logic import Logic

#zabezpieczyc bufory przed kolizja watkow. Tzn logika usuwa bufor a w tym samym czasie komunikacja pisze do buforu

#communication = Communication()
logic = Logic(None)

#communication.start()
logic.start()