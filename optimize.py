import base64
import os

import requests
from PIL import Image
from io import BytesIO
import numpy as np
import matplotlib.pylab as plt


div = 32
pixel = 256
access = False
similarities = []
iterations = []
redirect_url = None


def check_access(tmp_image):
    image = Image.fromarray(tmp_image)
    output = BytesIO()

    image.save(output, 'PNG')
    encoded = base64.b64encode(output.getvalue())
    data = b'data:image/png;base64,' + encoded
    response = requests.post('http://localhost:5000/check', data=data)
    if response.request.method == 'POST':
        similarity = response.json()['similarity']
        return similarity
    else:
        global redirect_url
        global access
        redirect_url = response.url
        access = True
        return 80.0


def write_adversarial_image(image):
    pil_image = Image.fromarray(image).resize((pixel, pixel))
    pil_image.save(os.path.join('adversarial_image.png'))


def create_and_write_plot():
    plt.plot(iterations, similarities)
    plt.xlabel('iteration')
    plt.ylabel('similarity [%]')
    plt.title('Optimization of the similarity')
    plt.grid(True)
    plt.savefig('similarity.png')


def sample_diff_image():
    row = np.random.randint(0, pixel//div)
    column = np.random.randint(0, pixel//div)
    color = np.random.randint(0, 3)
    value = np.random.randint(0, pixel)
    diff_image = np.zeros((pixel//div, pixel//div, 3), dtype=np.uint8)
    diff_image[row, column, color] = value
    return diff_image


if __name__ == '__main__':
    image = np.ones((pixel//div, pixel//div, 3), dtype=np.uint8) * 255
    similarity = check_access(image)
    iteration = 0

    similarities.append(similarity)
    iterations.append(iteration)

    while not access:
        iteration = iteration + 1
        tmp_image = image + sample_diff_image()
        tmp_similarity = check_access(tmp_image)

        if tmp_similarity > similarity:
            similarity = tmp_similarity
            image = tmp_image

            similarities.append(similarity)
            iterations.append(iteration)
            print('similarity: {:.5f}%'.format(similarity), end='\r')

    print('\n\nredirect:')
    print(redirect_url)

    write_adversarial_image(image)
    create_and_write_plot()
