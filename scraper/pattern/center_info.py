import json
from typing import Optional

from scraper.departements import to_departement_number
from scraper.pattern.center_location import CenterLocation, convert_csv_data_to_location
from scraper.pattern.scraper_request import ScraperRequest
from scraper.pattern.scraper_result import ScraperResult
from utils.vmd_logger import get_logger

logger = get_logger()


class CenterInfo:
    def __init__(self, departement: str, nom: str, url: str):
        self.departement = departement
        self.nom = nom
        self.url = url
        self.location = None
        self.metadata = None
        self.prochain_rdv = None
        self.plateforme = None

    def fill_localization(self, location: Optional[CenterLocation]):
        self.location = location

    def fill_result(self, result: ScraperResult):
        self.prochain_rdv = result.next_availability # TODO change with filters
        self.plateforme = result.platform

    def default(self):
        if type(self.location) is CenterLocation:
            self.location = self.location.default()
        return self.__dict__


def convert_csv_address(data: dict) -> str:
    adr_num = data.get('adr_num', '')
    adr_voie = data.get('adr_voie', '')
    adr_cp = data.get('com_cp', '')
    adr_nom = data.get('com_nom', '')
    return f'{adr_num} {adr_voie}, {adr_cp} {adr_nom}'

def convert_csv_business_hours(data: dict) -> str:
    keys = ["rdv_lundi", "rdv_mardi", "rdv_mercredi", "rdv_jeudi", "rdv_vendredi", "rdv_samedi", "rdv_dimanche"]
    meta = {}

    for key in data:
        if key not in keys:
            continue
        formatted_key = key.replace("rdv_", "")
        meta[formatted_key] = data[key]
    if not meta:
        return None
    return meta


def convert_csv_data_to_center_info(data: dict) -> CenterInfo:
    name = data.get('nom', None)
    departement = ''
    url = data.get('rdv_site_web', None)
    try:
        departement = to_departement_number(data.get('com_insee', None))
    except ValueError:
        logger.error(
            f"erreur lors du traitement de la ligne avec le gid {data['gid']}, com_insee={data['com_insee']}")

    center = CenterInfo(departement, name, url)
    center.fill_localization(convert_csv_data_to_location(data))
    center.metadata = dict()
    center.metadata['address'] = convert_csv_address(data)
    if data.get('rdv_tel'):
        center.metadata['phone_number'] = data.get('rdv_tel')
    center.metadata['business_hours'] = convert_csv_business_hours(data)
    return center
