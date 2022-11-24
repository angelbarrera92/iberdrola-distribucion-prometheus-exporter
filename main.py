import argparse
import time

from oligo import Iber
from oligo.exception import IberException
from prometheus_client import Gauge, start_http_server
import logging


class IberdrolaDistribucionMetrics():

    def __init__(self, username, password) -> None:
        # Iberdrola Client
        self.conn = Iber()
        self.conn.login(username, password)
        logging.debug("Logged in")
        # Prometheus metrics config
        # Hardcoded value, it is working fine until now
        self.polling_interval_seconds = 100
        # Prometheus metrics
        self.consumption = Gauge(
            "iberdrola_distribucion_consumption", "Current consumption in watts")
        self.meter_total = Gauge(
            "iberdrola_distribucion_meter_total", "Total consumption in kWh")

    def run_metrics_loop(self):
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        succed = False
        while not succed:
            try:
                mea = self.conn.measurement()
                watt = mea["consumption"]
                kwh = mea["meter"]
                self.consumption.set(watt)
                self.meter_total.set(kwh)
                succed = True
                logging.debug("Consumption: %sW, Meter: %skWh", watt, kwh)
            except IberException:
                logging.debug("Error fetching data, retrying in 3 seconds")
                time.sleep(3)


def main():
    parser = argparse.ArgumentParser(
        description="Iberdrola Distribucion Prometheus exporter")
    parser.add_argument(
        "-s", "--server", help="Exporter server address", required=False, default="0.0.0.0")
    parser.add_argument(
        "-P", "--port", help="Exporter server port", required=False, default=9988)
    parser.add_argument("-u", "--username",
                        help="i-de username", required=True)
    parser.add_argument("-p", "--password",
                        help="i-de password", required=True)
    parser.add_argument("-v", "--verbose",
                        help="Verbose mode", action="store_true")
    args = vars(parser.parse_args())

    if args["verbose"]:
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Verbose mode enabled")
    else:
        logging.basicConfig(level=logging.INFO)

    # Print config
    logging.info("Exporter server: %s:%s", args["server"], args["port"])
    logging.info("i-de username: %s", args["username"])

    # Server address and port
    idm = IberdrolaDistribucionMetrics(args["username"], args["password"])
    logging.info("Starting exporter server")
    start_http_server(addr=args["server"], port=args["port"])
    idm.run_metrics_loop()


if __name__ == "__main__":
    main()
