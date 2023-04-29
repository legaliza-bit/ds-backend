import requests


class PlateReaderClient:
    def __init__(self, host: str):
        self.host = host


    def get_image(self, im_id):
        res = requests.post(
            f'{self.host}/images/{im_id}',
        )
        return res.text


    def read_plate_number(self, img):
        res = requests.post(
            f'{self.host}/readPlateNumber',
            params = img
        )
        return res.json()

    def read_multiple_plates(self, imgs):
        res = requests.post(
            f'{self.host}/readMultPlates',
            params = imgs
        )
        return res.json()


if __name__ == '__main__':
    client = PlateReaderClient(host='http://0.0.0.0:7878/')
    
    img = {'img_id': '9965'}
    print(client.read_plate_number(img))

    imgs = {'img_id': '9965', 'img_id2': '10022'}
    print(client.read_multiple_plates(imgs))