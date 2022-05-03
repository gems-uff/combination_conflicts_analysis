import os
from google_drive_downloader import GoogleDriveDownloader as gdd
from pathlib import Path

def main():

    # the directory of this script
    path = Path(os.path.dirname(__file__)).resolve()
    
    # set ../data/data.zip as the destination path
    destination_path = path.joinpath('data','dataset.zip')
    
    print(f'Downloading zip file to {destination_path} ...')

    gdd.download_file_from_google_drive(file_id='1YCepn8uNA2ec_nl2lGaEi-W2WlwOlF2f',
                                    dest_path=destination_path,
                                    unzip=True, overwrite=True)

    if os.path.exists(destination_path):
        os.remove(destination_path)
    print('Finished')

main()