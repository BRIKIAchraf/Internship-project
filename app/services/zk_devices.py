from datetime import datetime
from typing import Generator
from flask import current_app, Flask
from app.models.device import Device
from app import db
from app.services.net import get_local_network_ranges
from zk import ZK
import nmap
import concurrent.futures
from contextlib import contextmanager
from typing import Generator, Union
#i add this import to let the def access compbatile with the def access_by_id

def scan(network) -> list[str]:
    nm = nmap.PortScanner()
    nm.scan(hosts=network, arguments="-sn")
    return nm.all_hosts()


def scan_by_inets(inet_ranges: list[str], port: int):
    devices = []
    active_ips: list[str] = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        active_ips = [
            ip for range_ips in executor.map(scan, inet_ranges) for ip in range_ips
        ]
    app: Flask = current_app._get_current_object() # type: ignore
    def worker_function(inet: str) -> dict[str, object] | None:
        with app.app_context():
            return scan_by_inet(inet)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        devices = executor.map(worker_function, [f"{ip}:{port}" for ip in active_ips])
        return [dev for dev in devices if dev]


def scan_by_port(port: int):
    local_network_ranges = get_local_network_ranges()
    return scan_by_inets(local_network_ranges, port)


@contextmanager
def access(inet: str, dev: Union[Device, None] = None) -> Generator[tuple[Device, ZK], None, None]:
    ip, port_str = inet.split(":")
    port = int(port_str)
    zk = ZK(ip, port=port, timeout=5)
    conn: ZK | None = None
    try:
        conn = zk.connect()
        device: Device | None = dev or Device.query.filter_by(mac=conn.get_mac()).first()
        if not device:
            device = Device(mac=conn.get_mac(), id=conn.get_serialnumber())
            db.session.add(device)
        device.lastCheckedAt = datetime.utcnow()
        device.lastActiveAt = datetime.utcnow()
        device.inet = inet
        db.session.commit()
        yield device, conn
    finally:
        if conn:
            conn.disconnect()


@contextmanager
def access_by_id(device_id: str) -> Generator[tuple[Device, ZK], None, None]:
    device: Device | None = Device.query.filter_by(id=device_id).first()
    if not device:
        raise Exception('Device Not Found')
    with access(device.inet, device) as res:
        yield res

def scan_by_inet(inet: str, dev: Device | None = None) -> dict[str, object] | None:
    try:
        with access(inet, dev) as (device, _):
            return device.serialize()
    except Exception:
        return None

