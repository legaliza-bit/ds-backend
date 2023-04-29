import logging
from flask import Flask, request, send_file, url_for
from models.plate_reader import PlateReader, InvalidImage
import logging
import io
import json
import requests


app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')


@app.route('/images/<path:img_id>', methods=['GET', 'POST'])
def get_image(img_id):
    path = f'./images/{img_id}.jpg'
    try:
        with open(path, 'rb') as bytes:
            response = send_file(
                        io.BytesIO(bytes.read()),
                        attachment_filename=f'{img_id}.jpeg',
                        mimetype='image/jpg',
                )
    except FileNotFoundError:
        return {'error': f'no such image: {img_id}.jpg'}, 400
    
    response.direct_passthrough = False
    return response


@app.route('/readPlateNumber', methods=['GET', 'POST'])
def read_plate_number():
    if 'img_id' not in request.args:
        return {'error': 'field "img_id" not found'}, 400
    
    resp = get_image(request.args.get('img_id'))

    try:
        im = resp.get_data()
    except AttributeError:
        return resp
    im = io.BytesIO(im)

    try:
        res = plate_reader.read_text(im)
    except InvalidImage:
        logging.error('invalid image')
        return {'error': 'invalid image'}, 400

    json_file = {
        'plate_number': res,
    }
    return json.dumps(json_file, ensure_ascii=False).encode('utf-8')


# <url>:8080/readPlateNumber?img_id=9965&img_id2=10022&...
# <url>:8080 : body: {"img_id": "9965", "img_id2": "10022", ...}
# -> {"img_id": {"plate_number": "о101но750"}, "img_id2": {"plate_number": "с181мв190"}, ...}
@app.route('/readMultPlates', methods=['GET', 'POST'])
def read_multiple_plates():
    imgs = request.args.to_dict()
    if not imgs:
        return {'error': 'no arguments found'}, 400
    
    res = {}
    for arg in imgs.keys():
        abs_url = request.url_root + url_for('read_plate_number', img_id=imgs[arg])
        resp = requests.get(abs_url)
        res[arg] = resp.json()
    return json.dumps(res, ensure_ascii=False).encode('utf-8')


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.run(host='0.0.0.0', port=7878, debug=False)
