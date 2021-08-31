import csv
import os

import yaml
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from schemas import CsvExportSchema


def load_settings(file_path='settings.yaml'):
    with open(file_path) as settings_file:
        return yaml.load(settings_file, Loader=yaml.CLoader)


def load_data(credentials_file, scopes, spreadsheet_id, range):

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        scopes,
    )
    service = build('sheets', 'v4', credentials=credentials)

    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range,
    ).execute()
    return result.get('values', [])


def check_path(path_):
    if not os.path.exists(path_):
        os.mkdir(path_)


def export_to_csv(csv_path, data_header, data, schema):
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, schema.fields)
        csv_writer.writerow(dict(zip(
            schema.fields,
            schema.fields,
        )))
        for row in data:
            row_data = dict(zip(data_header, row))
            csv_writer.writerow(
                schema.dump(row_data),
            )


if __name__ == '__main__':
    settings = load_settings()
    google_settings = settings.get('google')
    spreadsheet_settings = settings.get('spreadsheet')
    export_settings = settings.get('export')

    values = load_data(
        google_settings['credentials_file'],
        [scope['scope'] for scope in google_settings['scopes']],
        spreadsheet_settings['id'],
        spreadsheet_settings['range'],
    )
    if not values:
        raise ValueError('no data in google spreadsheet!')
    header = values[0]
    data = values[1:]

    check_path(export_settings['secret_url_part'])
    csv_path = os.path.join(
        export_settings['secret_url_part'],
        export_settings['csv_file_name'],
    )
    export_schema = CsvExportSchema()

    export_to_csv(
        csv_path,
        header,
        data,
        export_schema,
    )
