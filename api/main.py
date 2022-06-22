import random
import warnings
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info

warnings.filterwarnings("ignore")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # USELESS in prometheus context
    html_content = """
    <html>
        <head>
            <title>Page title</title>
        </head>
        <body>
            <p>Some text<p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# WORKFLOW
# 1. Funkcja generująca jakies dane (na poczatek wykorzystamy to co Michał przygotował) -> zwraca nam dict
def gen_random_dict() -> dict[str, int]:
    return {
        "v1": random.randint(1, 100),
        "v2": random.randint(1, 100),
    }

# 2. Tworzymy metrykę
def http_random_number() -> Callable[[Info], None]:
    METRIC = Gauge(
        "http_random_number",
        "Random number",
        labelnames=("metrics", ) # labelka której wartość ustawiamy, moze byc kilka poziomow
    )
    rand_vals = gen_random_dict() # wywolujemy funkcje z pkt 1

    def instrumentation(info: Info) -> None:
        METRIC.labels(metrics="random").set(rand_vals["v1"]) # dopisujemy do jakichs kluczy wartosci ktore wyciagnelismy ze slownika
        METRIC.labels(metrics="random2").set(rand_vals["v2"])

    return instrumentation

# 3. Powtarzamy powyzsze tyle razy ile bedziemy mieli oddzielnych metryk 
# (pytanie czy wykorzystamy endpointy ktore agreguja juz dane do dni/tygodni czy tylko te ktore sa na biezaco aktualizowane, i agregacje zrobimy w prometheuszu/grafanie)

prometheus_inst = Instrumentator()

# 4. dodajemy tutaj metryki (funkcje które je generują)
prometheus_inst.add(
    http_random_number(),
    # http_info_metric(),
)

# 5. dopinamy prometeusza do apki
prometheus_inst.instrument(app).expose(app)
